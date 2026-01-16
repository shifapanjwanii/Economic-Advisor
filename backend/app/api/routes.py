"""FastAPI routes for the Economic Decision Advisor."""

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agent import get_agent

router = APIRouter()


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    user_id: str = Field(..., description="Unique identifier for the user")
    message: str = Field(..., description="User's message to the advisor")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    response: str = Field(..., description="Advisor's response")
    tool_calls: list = Field(default_factory=list, description="Tools used during response")
    agent_id: str = Field(..., description="Agent identifier")


class UserProfile(BaseModel):
    """Model for user profile data."""

    income_range: Optional[str] = Field(None, description="User's income range (e.g., '$50k-$75k')")
    debt_level: Optional[str] = Field(None, description="Debt level (e.g., 'Low', 'Moderate', 'High')")
    savings: Optional[str] = Field(None, description="Savings amount or range")
    risk_tolerance: Optional[str] = Field(
        "Moderate",
        description="Risk tolerance: 'Conservative', 'Moderate', or 'Aggressive'",
    )
    financial_goals: Optional[str] = Field(
        None,
        description="User's financial goals (e.g., 'Retirement savings, pay off mortgage')",
    )
    preferences: Optional[str] = Field(
        "Standard explanation depth",
        description="Communication preferences",
    )


class UpdateProfileRequest(BaseModel):
    """Request model for profile update endpoint."""

    user_id: str = Field(..., description="Unique identifier for the user")
    profile: UserProfile = Field(..., description="Profile data to update")


class ConversationHistoryRequest(BaseModel):
    """Request model for conversation history endpoint."""

    user_id: str = Field(..., description="Unique identifier for the user")
    limit: int = Field(50, description="Maximum number of messages to retrieve")


class MessageItem(BaseModel):
    """Model for a single conversation message."""

    role: str
    content: str
    timestamp: Optional[str] = None


class ConversationHistoryResponse(BaseModel):
    """Response model for conversation history endpoint."""

    messages: list[MessageItem]
    user_id: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Send a message to the Economic Decision Advisor.

    The advisor will analyze your question, fetch relevant economic data
    from sources like FRED, financial news, and exchange rates, and
    provide personalized financial guidance.
    """
    try:
        agent = get_agent()
        result = agent.send_message(
            user_id=request.user_id,
            message=request.message,
        )
        return ChatResponse(
            response=result["response"],
            tool_calls=result.get("tool_calls", []),
            agent_id=result["agent_id"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")


@router.post("/profile/update")
async def update_profile(request: UpdateProfileRequest) -> dict:
    """Update a user's financial profile.

    The advisor uses this profile to personalize recommendations
    based on your financial situation, goals, and risk tolerance.
    """
    try:
        agent = get_agent()
        agent.update_user_profile(
            user_id=request.user_id,
            profile_data=request.profile.model_dump(exclude_none=True),
        )
        return {"status": "success", "message": "Profile updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")


@router.get("/profile/{user_id}")
async def get_profile(user_id: str) -> dict:
    """Get a user's current profile information."""
    try:
        agent = get_agent()
        # Ensure agent exists for user
        agent.get_or_create_agent(user_id)
        return {
            "user_id": user_id,
            "message": "Profile retrieved. Check conversation for stored context.",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get profile: {str(e)}")


@router.post("/history", response_model=ConversationHistoryResponse)
async def get_history(request: ConversationHistoryRequest) -> ConversationHistoryResponse:
    """Get conversation history for a user.

    Returns the past messages between the user and the Economic
    Decision Advisor for context and reference.
    """
    try:
        agent = get_agent()
        history = agent.get_conversation_history(
            user_id=request.user_id,
            limit=request.limit,
        )
        return ConversationHistoryResponse(
            messages=[MessageItem(**msg) for msg in history],
            user_id=request.user_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Economic Decision Advisor",
        "version": "0.1.0",
    }
