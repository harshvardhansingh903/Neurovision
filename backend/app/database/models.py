"""
SQLAlchemy database models for NeuroVision.
Defines structures for storing health events and analysis logs.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class HealthEvent(Base):
    """
    Model for storing individual health events detected during analysis.
    Records emotion, fatigue level, stress level, and alerts.
    """
    __tablename__ = "health_events"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Emotion detection
    detected_emotion = Column(String(50), nullable=True)
    emotion_confidence = Column(Float, default=0.0)
    
    # Fatigue detection
    fatigue_score = Column(Float, default=0.0)  # 0-100
    eye_closure_duration_ms = Column(Integer, default=0)
    blink_rate = Column(Float, default=0.0)
    
    # Stress detection
    stress_level = Column(String(20), default="LOW")  # LOW, MEDIUM, HIGH
    stress_score = Column(Float, default=0.0)  # 0-1.0
    
    # Alerts
    fatigue_alert = Column(Boolean, default=False)
    stress_alert = Column(Boolean, default=False)
    
    # Metadata
    frame_id = Column(Integer, nullable=True)
    extra_notes = Column(String(500), nullable=True)
    
    def __repr__(self):
        return f"<HealthEvent(id={self.id}, emotion={self.detected_emotion}, stress={self.stress_level})>"


class AlertLog(Base):
    """
    Model for storing generated alerts.
    Tracks alert history with severity and action taken.
    """
    __tablename__ = "alert_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    alert_type = Column(String(50), nullable=False)  # FATIGUE, STRESS, EMOTION
    severity = Column(String(20), default="WARNING")  # INFO, WARNING, CRITICAL
    message = Column(String(500), nullable=False)
    
    # Context
    emotion = Column(String(50), nullable=True)
    fatigue_score = Column(Float, nullable=True)
    stress_level = Column(String(20), nullable=True)
    
    # Resolution
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<AlertLog(id={self.id}, type={self.alert_type}, severity={self.severity})>"
