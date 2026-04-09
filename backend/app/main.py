"""
NeuroVision Backend - FastAPI Server
Handles real-time emotion detection and health metrics from webcam.
Can detect fatigue, stress levels, and emotional state.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database.database import engine
from app.database.models import Base
from app.routes import analysis, websocket

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    App startup and shutdown handler.
    """
    # Startup logic
    logger.info("Starting up NeuroVision...")
    
    # Create tables if they don't exist
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database ready")
    except Exception as e:
        logger.error(f"DB error: {e}")
    
    yield
    
    # Cleanup on shutdown
    logger.info("Shutting down...")


# Create the FastAPI app
app = FastAPI(
    title="NeuroVision API",
    description="Real-time health analyzer - detects emotion, fatigue, and stress",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trust all hosts (needed for WebSocket)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# Register routes
app.include_router(analysis.router)
app.include_router(websocket.router)


@app.get("/")
async def root():
    """API info - what can you do here?"""
    return {
        "name": "NeuroVision",
        "version": "1.0.0",
        "status": "Health analyzer with emotion detection",
        "endpoints": {
            "stream": "/ws/stream/{client_id} (WebSocket)",
            "events": "/api/health-events",
            "alerts": "/api/alerts",
            "check": "/api/status",
            "docs": "/docs",
        }
    }


@app.get("/health")
async def health_check():
    """System health check."""
    return {
        "status": "healthy",
        "service": "NeuroVision",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.debug,
        log_level="info"
    )
