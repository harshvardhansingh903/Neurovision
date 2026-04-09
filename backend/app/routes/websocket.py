"""
Real-time WebSocket handler for video frame analysis.
Takes in frames from the frontend and runs emotion detection on them.
Sends back results with confidence scores and health metrics.
"""

import json
import cv2
import numpy as np
from collections import deque
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..utils.frame_processor import decode_base64_frame, extract_face_roi
from ..utils.health_analyzer import HealthMetricsAggregator
from ..utils.alert_manager import AlertManager
from ..models.model_manager import model_manager
from ..config import settings
import asyncio

router = APIRouter(tags=["websocket"])


class StreamManager:
    """
    Handles all active WebSocket connections and processes frames.
    Keeps a sliding window of emotion predictions to smooth out the model's noise.
    """
    
    def __init__(self, smoothing_window=7):
        self.active_connections: dict[str, WebSocket] = {}
        self.frame_count = 0
        self.health_aggregator = HealthMetricsAggregator()
        self.alert_manager = AlertManager()
        
        # Temporal smoothing: store last N predictions to vote on emotion
        # helps avoid the model flipping between emotions constantly
        self.smoothing_window = smoothing_window
        self.emotion_history = deque(maxlen=smoothing_window)
        self.confidence_history = deque(maxlen=smoothing_window)
    
    def add_emotion_prediction(self, emotion: str, confidence: float):
        """Save this frame's emotion prediction to history."""
        self.emotion_history.append(emotion)
        self.confidence_history.append(confidence)
    
    def get_smoothed_emotion(self):
        """
        Returns the most common emotion from recent frames.
        Also returns average confidence for that emotion.
        Should reduce jitter when model is uncertain.
        """
        if not self.emotion_history:
            return None, 0.0
        
        # Count how many times each emotion appeared
        emotions_list = list(self.emotion_history)
        emotion_counts = {}
        for emotion in emotions_list:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # Get the most common one
        smoothed_emotion = max(emotion_counts, key=emotion_counts.get)
        
        # Calculate avg confidence for the smoothed emotion
        avg_confidence = np.mean([
            conf for emotion, conf in zip(self.emotion_history, self.confidence_history)
            if emotion == smoothed_emotion
        ])
        
        return smoothed_emotion, avg_confidence
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept WebSocket connection."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        print(f"Client {client_id} connected")
    
    def disconnect(self, client_id: str):
        """Remove WebSocket connection."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            print(f"Client {client_id} disconnected")
    
    async def send_analysis_result(self, websocket: WebSocket, result: dict):
        """Send analysis result back to client."""
        try:
            await websocket.send_json(result)
        except Exception as e:
            print(f"Error sending analysis result: {e}")


# Global stream manager instance
stream_manager = StreamManager()


@router.websocket("/ws/stream/{client_id}")
async def websocket_frame_endpoint(websocket: WebSocket, client_id: str):
    """
    Main WebSocket endpoint. Client sends frames, we send back emotion predictions.
    """
    await stream_manager.connect(websocket, client_id)
    
    try:
        while True:
            # Wait for frame data from frontend
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                
                if message.get("type") == "frame":
                    # Process the frame and get emotion
                    result = await process_frame(message.get("frame"))
                    # Send results back immediately
                    await stream_manager.send_analysis_result(websocket, result)
                
                elif message.get("type") == "ping":
                    # Just a heartbeat check
                    await websocket.send_json({"type": "pong", "timestamp": message.get("timestamp")})
            
            except json.JSONDecodeError:
                print("Invalid JSON received")
            except Exception as e:
                print(f"Error processing message: {e}")
    
    except WebSocketDisconnect:
        stream_manager.disconnect(client_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        stream_manager.disconnect(client_id)


async def process_frame(frame_data: str) -> dict:
    """
    Analyzes a single frame for emotion and health metrics.
    Returns all the detected info back to the frontend.
    """
    try:
        response = {
            "success": False,
            "frame_id": stream_manager.frame_count,
            "timestamp": None,
            "emotion": None,
            "emotion_confidence": 0.0,
            "fatigue_score": 0.0,
            "stress_level": "LOW",
            "alerts": [],
            "error": None
        }
        
        stream_manager.frame_count += 1
        
        # Decode the base64 frame
        frame = decode_base64_frame(frame_data)
        if frame is None:
            response["error"] = "Failed to decode frame"
            return response
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces in the frame
        faces = model_manager.detect_faces(gray)
        
        if len(faces) == 0:
            response["success"] = True
            response["error"] = "No faces detected"
            response["emotion"] = "No Face"
            response["emotion_confidence"] = 0.0
            response["faces_count"] = 0
            return response
        
        # Take the first face found
        x, y, w, h = faces[0]
        
        # Extract just the face region
        face_roi = extract_face_roi(gray, faces[0])
        
        if face_roi is None or face_roi.size == 0:
            response["error"] = "Failed to extract face ROI"
            return response
        
        # Run emotion prediction on face
        emotion_result = model_manager.predict_emotion(face_roi)
        emotion = emotion_result.get("emotion", "Unknown")
        emotion_confidence = emotion_result.get("confidence", 0.0)
        
        # Add to our smoothing buffer for stability
        stream_manager.add_emotion_prediction(emotion, emotion_confidence)
        
        # Get the smoothed emotion (voting across last N frames)
        smoothed_emotion, smoothed_confidence = stream_manager.get_smoothed_emotion()
        if smoothed_emotion:
            emotion = smoothed_emotion
            emotion_confidence = smoothed_confidence
        
        # Check for eye closure (crude estimate using brightness)
        upper_face = face_roi[:h//2, :]
        eye_brightness = np.mean(upper_face)
        eye_closed = eye_brightness < 100
        
        # Update health metrics
        metrics = stream_manager.health_aggregator.update_metrics(
            eye_closed=eye_closed,
            emotion=emotion,
            emotion_confidence=emotion_confidence
        )
        
        fatigue_score = metrics["fatigue"]["score"]
        fatigue_alert = metrics["fatigue"]["alert"]
        stress_level = metrics["stress"]["level"]
        stress_score = metrics["stress"]["score"]
        
        # Check for any alerts
        alerts = []
        
        fatigue_alert_obj = stream_manager.alert_manager.check_fatigue_alert(
            fatigue_score, fatigue_alert
        )
        if fatigue_alert_obj:
            alerts.append(fatigue_alert_obj)
        
        stress_alert_obj = stream_manager.alert_manager.check_stress_alert(
            stress_level, stress_score
        )
        if stress_alert_obj:
            alerts.append(stress_alert_obj)
        
        emotion_alert_obj = stream_manager.alert_manager.check_emotion_alert(
            emotion, emotion_confidence
        )
        if emotion_alert_obj:
            alerts.append(emotion_alert_obj)
        
        # Build the response with all data
        response.update({
            "success": True,
            "timestamp": metrics["timestamp"],
            "emotion": emotion,
            "emotion_confidence": round(emotion_confidence, 3),
            "fatigue_score": round(fatigue_score, 2),
            "stress_level": stress_level,
            "stress_score": round(stress_score, 3),
            "face_detected": True,
            "faces_count": len(faces),
            "face_rectangle": {"x": int(x), "y": int(y), "w": int(w), "h": int(h)},
            "alerts": alerts,
            "error": None
        })
    
    except Exception as e:
        print(f"Error processing frame: {e}")
        response["error"] = f"Frame processing error: {str(e)}"
    
    return response


@router.get("/ws/stats")
async def get_stream_stats():
    """
    Get statistics about WebSocket streaming.
    
    Returns:
        Streaming statistics
    """
    return {
        "active_connections": len(stream_manager.active_connections),
        "total_frames_processed": stream_manager.frame_count,
        "alerts_summary": stream_manager.alert_manager.get_alert_statistics()
    }
