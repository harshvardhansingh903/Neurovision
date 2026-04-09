"""
App configuration - settings from environment variables.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration for the app."""
    
    # Server setup
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    debug: bool = True
    
    # Database
    database_url: str = "postgresql://neurovision:password@localhost:5432/neurovision_db"
    
    # CORS for frontend
    frontend_url: str = "http://localhost:3000"
    
    # Alert thresholds - tune these based on testing
    fatigue_eye_closure_threshold_ms: int = 2000  # How long eyes closed before alert
    fatigue_blink_rate_threshold: int = 15  # Blinks per minute threshold
    stress_action_unit_threshold: float = 0.6  # Confidence for stress detection
    emotion_confidence_threshold: float = 0.7  # Only use confident emotion predictions
    
    # Model files
    emotion_model_path: str = "models/emotion_model.h5"
    face_detector_path: str = "models/haarcascade_frontalface_default.xml"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Load settings
settings = Settings()
