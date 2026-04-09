"""
Health analysis utilities for NeuroVision.
Calculates fatigue, stress, and emotion-related health metrics.
"""

import numpy as np
from collections import deque
from datetime import datetime, timedelta


class FatigueAnalyzer:
    """
    Analyzes fatigue level based on eye closure duration and blink rate.
    """
    
    def __init__(self, eye_closure_threshold_ms: int = 2000, blink_rate_threshold: int = 15):
        """
        Initialize fatigue analyzer.
        
        Args:
            eye_closure_threshold_ms: Milliseconds of continuous eye closure to trigger alert
            blink_rate_threshold: Minimum blinks per minute for healthy state
        """
        self.eye_closure_threshold_ms = eye_closure_threshold_ms
        self.blink_rate_threshold = blink_rate_threshold
        
        # Rolling windows for tracking
        self.blink_history = deque(maxlen=300)  # Last 5 seconds at 60fps
        self.eye_closure_start_time = None
        self.current_eye_closure_duration = 0
    
    def update_eye_state(self, eyes_closed: bool, timestamp: datetime = None):
        """
        Update eye state (open/closed).
        
        Args:
            eyes_closed: Boolean indicating if eyes are currently closed
            timestamp: Datetime of current frame
        
        Returns:
            Tuple of (fatigue_score, alert_triggered)
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Track eye closure
        if eyes_closed:
            if self.eye_closure_start_time is None:
                self.eye_closure_start_time = timestamp
            
            # Calculate duration
            self.current_eye_closure_duration = int(
                (timestamp - self.eye_closure_start_time).total_seconds() * 1000
            )
        else:
            self.current_eye_closure_duration = 0
            self.eye_closure_start_time = None
        
        # Record blink
        self.blink_history.append(1 if eyes_closed else 0)
        
        # Calculate fatigue score
        fatigue_score = self._calculate_fatigue_score()
        
        # Check if alert should be triggered
        alert_triggered = self.current_eye_closure_duration > self.eye_closure_threshold_ms
        
        return fatigue_score, alert_triggered
    
    def _calculate_fatigue_score(self) -> float:
        """
        Calculate fatigue score (0-100) based on eye closure and blink rate.
        
        Returns:
            Fatigue score from 0 (alert) to 100 (very tired)
        """
        if len(self.blink_history) < 30:  # Need at least 0.5 seconds of data
            return 0.0
        
        # Calculate blink rate (blinks per minute)
        frame_count = len(self.blink_history)
        blink_count = sum(1 for i in range(1, len(self.blink_history)) 
                         if self.blink_history[i-1] == 0 and self.blink_history[i] == 1)
        
        # Estimate blinks per minute (assuming 30fps)
        blinks_per_minute = (blink_count / frame_count) * 60 * 30 if frame_count > 0 else 0
        
        # Score based on blink rate (healthy: 15-20 blinks/min)
        if blinks_per_minute < self.blink_rate_threshold:
            blink_score = max(0, 100 * (1 - blinks_per_minute / self.blink_rate_threshold))
        else:
            blink_score = 0
        
        # Score based on eye closure duration
        closure_score = min(100, max(0, self.current_eye_closure_duration / self.eye_closure_threshold_ms * 100))
        
        # Combined score (weighted average)
        fatigue_score = (blink_score * 0.4 + closure_score * 0.6)
        
        return fatigue_score
    
    def get_metrics(self) -> dict:
        """
        Get current fatigue metrics.
        
        Returns:
            Dictionary with fatigue metrics
        """
        blink_rate = 0
        if len(self.blink_history) > 0:
            blink_count = sum(1 for i in range(1, len(self.blink_history)) 
                             if self.blink_history[i-1] == 0 and self.blink_history[i] == 1)
            blink_rate = blink_count * 2  # Rough estimate for display
        
        return {
            "fatigue_score": self._calculate_fatigue_score(),
            "eye_closure_duration_ms": self.current_eye_closure_duration,
            "blink_rate": blink_rate
        }


class StressAnalyzer:
    """
    Analyzes stress level based on facial action units and emotional state.
    """
    
    def __init__(self, au_threshold: float = 0.6):
        """
        Initialize stress analyzer.
        
        Args:
            au_threshold: Confidence threshold for action units indicating stress
        """
        self.au_threshold = au_threshold
        self.emotion_history = deque(maxlen=100)  # Last few seconds
    
    def update_from_emotion(self, emotion: str, confidence: float):
        """
        Update stress from detected emotion.
        
        Args:
            emotion: Detected emotion label
            confidence: Confidence score (0-1)
        
        Returns:
            Stress level (LOW, MEDIUM, HIGH) and stress score (0-1)
        """
        self.emotion_history.append({
            "emotion": emotion,
            "confidence": confidence,
            "timestamp": datetime.now()
        })
        
        return self._calculate_stress_level()
    
    def _calculate_stress_level(self) -> tuple:
        """
        Calculate stress level from emotion history.
        
        Returns:
            Tuple of (stress_level, stress_score) where level is LOW/MEDIUM/HIGH and score is 0-1
        """
        if len(self.emotion_history) == 0:
            return "LOW", 0.0
        
        # Count stress-related emotions
        stress_emotions = {"Angry", "Fear", "Sad", "Disgust"}
        stress_count = sum(1 for item in self.emotion_history 
                          if item["emotion"] in stress_emotions)
        
        stress_ratio = stress_count / len(self.emotion_history) if self.emotion_history else 0
        
        # Calculate average confidence of stress emotions
        stress_confidence = np.mean([
            item["confidence"] for item in self.emotion_history
            if item["emotion"] in stress_emotions
        ]) if stress_count > 0 else 0
        
        # Determine stress level
        stress_score = stress_ratio * stress_confidence
        
        if stress_score < 0.2:
            stress_level = "LOW"
        elif stress_score < 0.5:
            stress_level = "MEDIUM"
        else:
            stress_level = "HIGH"
        
        return stress_level, stress_score
    
    def get_metrics(self) -> dict:
        """
        Get current stress metrics.
        
        Returns:
            Dictionary with stress metrics
        """
        stress_level, stress_score = self._calculate_stress_level()
        
        return {
            "stress_level": stress_level,
            "stress_score": stress_score,
            "emotion_history_count": len(self.emotion_history)
        }


class HealthMetricsAggregator:
    """
    Aggregates all health metrics for unified reporting.
    """
    
    def __init__(self):
        """Initialize the metrics aggregator."""
        self.fatigue_analyzer = FatigueAnalyzer()
        self.stress_analyzer = StressAnalyzer()
    
    def update_metrics(self, eye_closed: bool, emotion: str, emotion_confidence: float) -> dict:
        """
        Update all metrics with new frame data.
        
        Args:
            eye_closed: Boolean indicating if eyes are closed
            emotion: Detected emotion label
            emotion_confidence: Confidence of emotion detection
        
        Returns:
            Dictionary with all health metrics
        """
        # Update analyzers
        fatigue_score, fatigue_alert = self.fatigue_analyzer.update_eye_state(eye_closed)
        stress_level, stress_score = self.stress_analyzer.update_from_emotion(emotion, emotion_confidence)
        
        return {
            "fatigue": {
                "score": fatigue_score,
                "alert": fatigue_alert,
                "metrics": self.fatigue_analyzer.get_metrics()
            },
            "stress": {
                "level": stress_level,
                "score": stress_score,
                "metrics": self.stress_analyzer.get_metrics()
            },
            "emotion": {
                "detected": emotion,
                "confidence": emotion_confidence
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def reset(self):
        """Reset all analyzers."""
        self.fatigue_analyzer = FatigueAnalyzer()
        self.stress_analyzer = StressAnalyzer()
