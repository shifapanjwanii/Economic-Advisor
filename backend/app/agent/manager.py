"""Letta agent manager for the Economic Decision Advisor."""

from typing import Optional
from letta_client import Letta
from letta_client.types import MessageCreate, TextContent

from app.agent.prompts import (
    ECONOMIC_ADVISOR_SYSTEM_PROMPT,
    MEMORY_PERSONA,
    DEFAULT_HUMAN_DESCRIPTION,
)
from app.config import get_settings


class EconomicAdvisorAgent:
    """Manager for the Economic Decision Advisor Letta agent."""

    def __init__(self, base_url: str = "http://localhost:8283"):
        """Initialize the agent manager.

        Args:
            base_url: URL of the Letta server. Defaults to local server.
        """
        self.client = Letta(base_url=base_url)
        self.settings = get_settings()
        self._agent_id: Optional[str] = None
        self._tools_registered = False

    def get_or_create_agent(self, user_id: str) -> str:
        """Get existing agent for user or create a new one.

        Args:
            user_id: Unique identifier for the user.

        Returns:
            The agent ID.
        """
        agent_name = f"economic_advisor_{user_id}"

        # Try to find existing agent
        agents = self.client.agents.list()
        for agent in agents:
            if agent.name == agent_name:
                self._agent_id = agent.id
                return agent.id

        # Create new agent if not found
        agent = self.client.agents.create(
            name=agent_name,
            system=ECONOMIC_ADVISOR_SYSTEM_PROMPT,
            memory_blocks=[
                {
                    "label": "persona",
                    "value": MEMORY_PERSONA,
                },
                {
                    "label": "human",
                    "value": DEFAULT_HUMAN_DESCRIPTION,
                },
                {
                    "label": "user_profile",
                    "value": self._get_default_user_profile(),
                },
            ],
            llm="openai/gpt-4o",
            embedding="openai/text-embedding-3-small",
        )

        self._agent_id = agent.id

        # Register tools with the agent
        self._register_tools(agent.id)

        return agent.id

    def _get_default_user_profile(self) -> str:
        """Get default user profile for new users."""
        return """User Profile:
- Income Range: Not specified
- Debt Level: Not specified
- Savings: Not specified
- Risk Tolerance: Moderate (default)
- Financial Goals: Not specified
- Preferences: Standard explanation depth

Past Interactions: None yet
"""

    def _register_tools(self, agent_id: str) -> None:
        """Register economic tools with the agent.

        Args:
            agent_id: The agent ID to register tools with.
        """
        if self._tools_registered:
            return

        # Import tools
        from app.tools import (
            get_fred_data,
            get_inflation_rate,
            get_interest_rate,
            get_unemployment_rate,
            get_financial_news,
            get_exchange_rate,
            get_purchasing_power,
        )

        tools = [
            get_fred_data,
            get_inflation_rate,
            get_interest_rate,
            get_unemployment_rate,
            get_financial_news,
            get_exchange_rate,
            get_purchasing_power,
        ]

        for tool_func in tools:
            try:
                tool = self.client.tools.create_from_function(function=tool_func)
                self.client.agents.tools.attach(agent_id=agent_id, tool_id=tool.id)
            except Exception as e:
                # Tool might already exist
                print(f"Note: Could not register tool {tool_func.__name__}: {e}")

        self._tools_registered = True

    def send_message(self, user_id: str, message: str) -> dict:
        """Send a message to the agent and get a response.

        Args:
            user_id: The user's unique identifier.
            message: The user's message.

        Returns:
            Dict containing the response and metadata.
        """
        agent_id = self.get_or_create_agent(user_id)

        response = self.client.agents.messages.create(
            agent_id=agent_id,
            messages=[
                MessageCreate(
                    role="user",
                    content=[TextContent(text=message)],
                )
            ],
        )

        # Extract the assistant's response
        assistant_messages = []
        tool_calls = []

        for msg in response.messages:
            if hasattr(msg, 'message_type'):
                if msg.message_type == 'assistant_message':
                    if hasattr(msg, 'content'):
                        assistant_messages.append(msg.content)
                elif msg.message_type == 'tool_call_message':
                    if hasattr(msg, 'tool_call'):
                        tool_calls.append({
                            'name': msg.tool_call.name if hasattr(msg.tool_call, 'name') else 'unknown',
                            'arguments': msg.tool_call.arguments if hasattr(msg.tool_call, 'arguments') else {},
                        })

        return {
            'response': '\n\n'.join(assistant_messages) if assistant_messages else "I couldn't generate a response.",
            'tool_calls': tool_calls,
            'agent_id': agent_id,
        }

    def update_user_profile(self, user_id: str, profile_data: dict) -> None:
        """Update the user's profile in agent memory.

        Args:
            user_id: The user's unique identifier.
            profile_data: Dict containing profile updates.
        """
        agent_id = self.get_or_create_agent(user_id)

        # Get current memory
        memory = self.client.agents.memory.get(agent_id=agent_id)

        # Find and update user_profile block
        for block in memory.blocks:
            if block.label == "user_profile":
                # Build updated profile string
                profile_str = "User Profile:\n"
                profile_str += f"- Income Range: {profile_data.get('income_range', 'Not specified')}\n"
                profile_str += f"- Debt Level: {profile_data.get('debt_level', 'Not specified')}\n"
                profile_str += f"- Savings: {profile_data.get('savings', 'Not specified')}\n"
                profile_str += f"- Risk Tolerance: {profile_data.get('risk_tolerance', 'Moderate')}\n"
                profile_str += f"- Financial Goals: {profile_data.get('financial_goals', 'Not specified')}\n"
                profile_str += f"- Preferences: {profile_data.get('preferences', 'Standard explanation depth')}\n"

                self.client.agents.memory.update_block(
                    agent_id=agent_id,
                    block_id=block.id,
                    value=profile_str,
                )
                break

    def get_conversation_history(self, user_id: str, limit: int = 50) -> list:
        """Get conversation history for a user.

        Args:
            user_id: The user's unique identifier.
            limit: Maximum number of messages to retrieve.

        Returns:
            List of message dictionaries.
        """
        agent_id = self.get_or_create_agent(user_id)

        messages = self.client.agents.messages.list(
            agent_id=agent_id,
            limit=limit,
        )

        history = []
        for msg in messages:
            if hasattr(msg, 'message_type'):
                if msg.message_type in ['user_message', 'assistant_message']:
                    history.append({
                        'role': 'user' if msg.message_type == 'user_message' else 'assistant',
                        'content': msg.content if hasattr(msg, 'content') else '',
                        'timestamp': msg.created_at if hasattr(msg, 'created_at') else None,
                    })

        return history


# Singleton instance
_agent_instance: Optional[EconomicAdvisorAgent] = None


def get_agent(base_url: str = "http://localhost:8283") -> EconomicAdvisorAgent:
    """Get or create the singleton agent instance.

    Args:
        base_url: URL of the Letta server.

    Returns:
        The EconomicAdvisorAgent instance.
    """
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = EconomicAdvisorAgent(base_url=base_url)
    return _agent_instance
