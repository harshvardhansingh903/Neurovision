"""
Alert management system for NeuroVision.
Handles alert generation, deduplication, and logging.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import deque


class AlertManager:
    """
    Manages health alerts with deduplication and throttling.
    """
    
    def __init__(self, alert_cooldown_seconds: int = 10):
        """
        Initialize alert manager.
        
        Args:
            alert_cooldown_seconds: Minimum time between duplicate alerts
        """
        self.alert_cooldown_seconds = alert_cooldown_seconds
        self.alert_history = deque(maxlen=1000)  # Keep last 1000 alerts
        self.last_alert_time = {}  # Track last alert time by type
        self.active_alerts = {}  # Track active alerts
    
    def check_fatigue_alert(self, fatigue_score: float, should_alert: bool) -> Optional[Dict]:
        """
        Check and generate fatigue alert if needed.
        
        Args:
            fatigue_score: Fatigue score (0-100)
            should_alert: Boolean from fatigue analyzer
        
        Returns:
            Alert dict if alert should be generated, None otherwise
        """
        if should_alert:
            alert = self._create_alert(
                alert_type="FATIGUE",
                severity="WARNING",
                message=f"Fatigue detected: Eyes closed too long (score: {fatigue_score:.1f})",
                metadata={
                    "fatigue_score": fatigue_score
                }
            )
            return alert
        return None
    
    def check_stress_alert(self, stress_level: str, stress_score: float) -> Optional[Dict]:
        """
        Check and generate stress alert if needed.
        
        Args:
            stress_level: Stress level (LOW/MEDIUM/HIGH)
            stress_score: Stress score (0-1)
        
        Returns:
            Alert dict if alert should be generated, None otherwise
        """
        # Only alert on HIGH stress
        if stress_level == "HIGH":
            alert = self._create_alert(
                alert_type="STRESS",
                severity="WARNING",
                message=f"High stress detected (score: {stress_score:.2f})",
                metadata={
                    "stress_level": stress_level,
                    "stress_score": stress_score
                }
            )
            return alert
        return None
    
    def check_emotion_alert(self, emotion: str, confidence: float) -> Optional[Dict]:
        """
        Check and generate emotion-based alert if needed.
        
        Args:
            emotion: Detected emotion label
            confidence: Confidence score
        
        Returns:
            Alert dict if alert should be generated, None otherwise
        """
        # Alert on negative emotions with high confidence
        if emotion in ["Angry", "Sad", "Fear", "Disgust"] and confidence > 0.8:
            alert = self._create_alert(
                alert_type="EMOTION",
                severity="INFO",
                message=f"Detected strong {emotion.lower()} emotion",
                metadata={
                    "emotion": emotion,
                    "confidence": confidence
                }
            )
            return alert
        return None
    
    def _create_alert(self, alert_type: str, severity: str, message: str, 
                     metadata: Dict = None) -> Optional[Dict]:
        """
        Create an alert with deduplication and throttling.
        
        Args:
            alert_type: Type of alert (FATIGUE, STRESS, EMOTION)
            severity: Severity level (INFO, WARNING, CRITICAL)
            message: Alert message
            metadata: Additional metadata
        
        Returns:
            Alert dict if it should be emitted, None if throttled
        """
        current_time = datetime.now()
        
        # Check cooldown
        last_time = self.last_alert_time.get(alert_type)
        if last_time and (current_time - last_time).total_seconds() < self.alert_cooldown_seconds:
            return None
        
        # Create alert
        alert = {
            "id": len(self.alert_history) + 1,
            "type": alert_type,
            "severity": severity,
            "message": message,
            "timestamp": current_time.isoformat(),
            "metadata": metadata or {}
        }
        
        # Record alert
        self.alert_history.append(alert)
        self.last_alert_time[alert_type] = current_time
        self.active_alerts[alert_type] = alert
        
        return alert
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict]:
        """
        Get recent alerts.
        
        Args:
            limit: Maximum number of alerts to return
        
        Returns:
            List of recent alerts
        """
        return list(self.alert_history)[-limit:]
    
    def get_active_alerts(self) -> List[Dict]:
        """
        Get currently active alerts.
        
        Returns:
            List of active alerts
        """
        return list(self.active_alerts.values())
    
    def clear_alert(self, alert_type: str):
        """
        Clear an active alert.
        
        Args:
            alert_type: Type of alert to clear
        """
        if alert_type in self.active_alerts:
            del self.active_alerts[alert_type]
    
    def get_alert_statistics(self) -> Dict:
        """
        Get statistics about alerts.
        
        Returns:
            Dictionary with alert statistics
        """
        if not self.alert_history:
            return {
                "total_alerts": 0,
                "alerts_by_type": {},
                "alerts_by_severity": {}
            }
        
        alerts_by_type = {}
        alerts_by_severity = {}
        
        for alert in self.alert_history:
            alert_type = alert["type"]
            severity = alert["severity"]
            
            alerts_by_type[alert_type] = alerts_by_type.get(alert_type, 0) + 1
            alerts_by_severity[severity] = alerts_by_severity.get(severity, 0) + 1
        
        return {
            "total_alerts": len(self.alert_history),
            "alerts_by_type": alerts_by_type,
            "alerts_by_severity": alerts_by_severity
        }
    
    def reset(self):
        """Reset alert manager."""
        self.alert_history.clear()
        self.last_alert_time.clear()
        self.active_alerts.clear()
