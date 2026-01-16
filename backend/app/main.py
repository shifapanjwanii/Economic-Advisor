"""Main FastAPI application for the Economic Decision Advisor."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    settings = get_settings()
    print(f"Starting Economic Decision Advisor API on {settings.host}:{settings.port}")
    yield
    # Shutdown
    print("Shutting down Economic Decision Advisor API")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Economic Decision Advisor",
        description="""
        An AI-powered financial advisor that helps users make better everyday
        economic decisions by interpreting live macroeconomic data.

        ## Features

        - **Personalized Advice**: Recommendations tailored to your financial profile
        - **Real-Time Data**: Integrates with FRED, financial news, and exchange rates
        - **Long-Term Memory**: Remembers your goals and preferences across sessions
        - **Transparent Reasoning**: Shows which data sources inform each recommendation

        ## Getting Started

        1. Send a chat message with your financial question
        2. Optionally update your profile for personalized advice
        3. Review conversation history to track your financial journey
        """,
        version="0.1.0",
        lifespan=lifespan,
    )

    # Configure CORS for frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",  # React dev server
            "http://localhost:5173",  # Vite dev server
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(router, prefix="/api/v1", tags=["advisor"])

    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
