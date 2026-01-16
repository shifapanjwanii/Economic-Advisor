"""MCP Tools for the Economic Decision Advisor agent."""

from app.tools.fred import get_fred_data, get_inflation_rate, get_interest_rate, get_unemployment_rate
from app.tools.news import get_financial_news
from app.tools.exchange import get_exchange_rate, get_purchasing_power

__all__ = [
    "get_fred_data",
    "get_inflation_rate",
    "get_interest_rate",
    "get_unemployment_rate",
    "get_financial_news",
    "get_exchange_rate",
    "get_purchasing_power",
]
