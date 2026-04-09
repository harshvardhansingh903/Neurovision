"""
REST API routes for NeuroVision frame analysis.
Handles health event logging and alert retrieval.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from ..database.database import get_db
from ..database.models import HealthEvent, AlertLog
from typing import List

router = APIRouter(prefix="/api", tags=["analysis"])


@router.post("/health-event")
async def log_health_event(
    emotion: str,
    emotion_confidence: float,
    fatigue_score: float,
    stress_level: str,
    fatigue_alert: bool = False,
    stress_alert: bool = False,
    db: Session = Depends(get_db)
):
    """
    Log a health event from frame analysis.
    Called after each frame is analyzed.
    
    Args:
        emotion: Detected emotion label
        emotion_confidence: Confidence score (0-1)
        fatigue_score: Fatigue score (0-100)
        stress_level: Stress level (LOW/MEDIUM/HIGH)
        fatigue_alert: Whether fatigue alert triggered
        stress_alert: Whether stress alert triggered
        db: Database session
    
    Returns:
        Created health event
    """
    try:
        # Create health event
        event = HealthEvent(
            timestamp=datetime.utcnow(),
            detected_emotion=emotion,
            emotion_confidence=emotion_confidence,
            fatigue_score=fatigue_score,
            stress_level=stress_level,
            stress_score=0.0 if stress_level == "LOW" else (0.5 if stress_level == "MEDIUM" else 1.0),
            fatigue_alert=fatigue_alert,
            stress_alert=stress_alert
        )
        
        db.add(event)
        db.commit()
        db.refresh(event)
        
        return {
            "id": event.id,
            "timestamp": event.timestamp.isoformat(),
            "emotion": event.detected_emotion,
            "emotion_confidence": event.emotion_confidence,
            "fatigue_score": event.fatigue_score,
            "stress_level": event.stress_level
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error logging health event: {str(e)}")


@router.post("/alert")
async def log_alert(
    alert_type: str,
    severity: str,
    message: str,
    emotion: str = None,
    fatigue_score: float = None,
    stress_level: str = None,
    db: Session = Depends(get_db)
):
    """
    Log a health alert to the database.
    
    Args:
        alert_type: Type of alert (FATIGUE, STRESS, EMOTION)
        severity: Severity level (INFO, WARNING, CRITICAL)
        message: Alert message
        emotion: Associated emotion if applicable
        fatigue_score: Associated fatigue score if applicable
        stress_level: Associated stress level if applicable
        db: Database session
    
    Returns:
        Created alert log entry
    """
    try:
        alert_log = AlertLog(
            timestamp=datetime.utcnow(),
            alert_type=alert_type,
            severity=severity,
            message=message,
            emotion=emotion,
            fatigue_score=fatigue_score,
            stress_level=stress_level,
            resolved=False
        )
        
        db.add(alert_log)
        db.commit()
        db.refresh(alert_log)
        
        return {
            "id": alert_log.id,
            "timestamp": alert_log.timestamp.isoformat(),
            "type": alert_log.alert_type,
            "severity": alert_log.severity
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error logging alert: {str(e)}")


@router.get("/health-events")
async def get_health_events(
    minutes: int = 5,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get recent health events.
    
    Args:
        minutes: Time window in minutes (default 5)
        limit: Maximum number of events to return
        db: Database session
    
    Returns:
        List of health events
    """
    try:
        # Calculate time window
        since = datetime.utcnow() - timedelta(minutes=minutes)
        
        # Query events
        events = db.query(HealthEvent).filter(
            HealthEvent.timestamp >= since
        ).order_by(desc(HealthEvent.timestamp)).limit(limit).all()
        
        return [
            {
                "id": event.id,
                "timestamp": event.timestamp.isoformat(),
                "emotion": event.detected_emotion,
                "emotion_confidence": event.emotion_confidence,
                "fatigue_score": event.fatigue_score,
                "stress_level": event.stress_level,
                "fatigue_alert": event.fatigue_alert,
                "stress_alert": event.stress_alert
            }
            for event in events
        ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving health events: {str(e)}")


@router.get("/alerts")
async def get_recent_alerts(
    minutes: int = 10,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get recent alerts.
    
    Args:
        minutes: Time window in minutes
        limit: Maximum number of alerts to return
        db: Database session
    
    Returns:
        List of recent alerts
    """
    try:
        since = datetime.utcnow() - timedelta(minutes=minutes)
        
        alerts = db.query(AlertLog).filter(
            AlertLog.timestamp >= since
        ).order_by(desc(AlertLog.timestamp)).limit(limit).all()
        
        return [
            {
                "id": alert.id,
                "timestamp": alert.timestamp.isoformat(),
                "type": alert.alert_type,
                "severity": alert.severity,
                "message": alert.message,
                "resolved": alert.resolved
            }
            for alert in alerts
        ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving alerts: {str(e)}")


@router.get("/health-summary")
async def get_health_summary(
    minutes: int = 5,
    db: Session = Depends(get_db)
):
    """
    Get summary statistics for recent health analysis.
    
    Args:
        minutes: Time window in minutes
        db: Database session
    
    Returns:
        Summary statistics
    """
    try:
        since = datetime.utcnow() - timedelta(minutes=minutes)
        
        events = db.query(HealthEvent).filter(
            HealthEvent.timestamp >= since
        ).all()
        
        if not events:
            return {
                "total_events": 0,
                "avg_fatigue_score": 0,
                "avg_emotion_confidence": 0,
                "stress_distribution": {},
                "emotion_distribution": {},
                "total_alerts": 0
            }
        
        # Calculate statistics
        avg_fatigue = sum(e.fatigue_score for e in events) / len(events)
        avg_confidence = sum(e.emotion_confidence for e in events) / len(events)
        
        stress_dist = {}
        emotion_dist = {}
        total_alerts = 0
        
        for event in events:
            # Stress distribution
            if event.stress_level:
                stress_dist[event.stress_level] = stress_dist.get(event.stress_level, 0) + 1
            
            # Emotion distribution
            if event.detected_emotion:
                emotion_dist[event.detected_emotion] = emotion_dist.get(event.detected_emotion, 0) + 1
            
            # Alert counting
            if event.fatigue_alert or event.stress_alert:
                total_alerts += 1
        
        return {
            "total_events": len(events),
            "avg_fatigue_score": round(avg_fatigue, 2),
            "avg_emotion_confidence": round(avg_confidence, 2),
            "stress_distribution": stress_dist,
            "emotion_distribution": emotion_dist,
            "total_alerts": total_alerts
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting health summary: {str(e)}")


@router.get("/status")
async def get_status():
    """
    Get API status and health check.
    
    Returns:
        Status information
    """
    return {
        "status": "healthy",
        "service": "NeuroVision Health Analyzer",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }
