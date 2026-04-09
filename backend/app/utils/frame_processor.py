"""
Frame processing utilities for NeuroVision.
Handles frame decoding, preprocessing, and face extraction.
"""

import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image


def decode_base64_frame(frame_data: str) -> np.ndarray:
    """
    Decode a base64-encoded image frame from the frontend.
    
    Args:
        frame_data: Base64-encoded image string
    
    Returns:
        OpenCV image (BGR format)
    """
    try:
        # Remove data URL prefix if present
        if ',' in frame_data:
            frame_data = frame_data.split(',')[1]
        
        # Decode base64
        frame_bytes = base64.b64decode(frame_data)
        
        # Convert to numpy array
        nparr = np.frombuffer(frame_bytes, np.uint8)
        
        # Decode image
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        return frame
    
    except Exception as e:
        print(f"Error decoding frame: {e}")
        return None


def encode_frame_to_base64(frame: np.ndarray) -> str:
    """
    Encode an OpenCV frame to base64 string.
    
    Args:
        frame: OpenCV image (BGR format)
    
    Returns:
        Base64-encoded image string with PNG encoding
    """
    try:
        # Encode frame to PNG
        _, buffer = cv2.imencode('.png', frame)
        
        # Convert to base64
        b64_frame = base64.b64encode(buffer).decode('utf-8')
        
        return f"data:image/png;base64,{b64_frame}"
    
    except Exception as e:
        print(f"Error encoding frame: {e}")
        return None


def preprocess_frame(frame: np.ndarray, target_height: int = 480) -> np.ndarray:
    """
    Preprocess a frame for analysis (resize and format).
    
    Args:
        frame: Raw OpenCV frame
        target_height: Target height for resized frame
    
    Returns:
        Preprocessed frame
    """
    try:
        # Calculate aspect ratio and resize
        if frame is None:
            return None
        
        height, width = frame.shape[:2]
        target_width = int(target_height * width / height)
        
        # Resize frame
        resized = cv2.resize(frame, (target_width, target_height))
        
        return resized
    
    except Exception as e:
        print(f"Error preprocessing frame: {e}")
        return frame


def extract_face_roi(frame: np.ndarray, face_rect) -> np.ndarray:
    """
    Extract face region of interest from a frame.
    
    Args:
        frame: Grayscale frame
        face_rect: Face rectangle (x, y, w, h) from detector
    
    Returns:
        Cropped face region
    """
    try:
        x, y, w, h = face_rect
        
        # Ensure coordinates are within bounds
        x = max(0, x)
        y = max(0, y)
        
        if y + h > frame.shape[0]:
            h = frame.shape[0] - y
        if x + w > frame.shape[1]:
            w = frame.shape[1] - x
        
        # Extract ROI
        roi = frame[y:y+h, x:x+w]
        
        return roi
    
    except Exception as e:
        print(f"Error extracting face ROI: {e}")
        return None


def draw_face_rectangle(frame: np.ndarray, face_rect, color=(0, 255, 0), thickness=2) -> np.ndarray:
    """
    Draw a rectangle around detected face.
    
    Args:
        frame: OpenCV frame
        face_rect: Face rectangle (x, y, w, h)
        color: BGR color tuple
        thickness: Line thickness
    
    Returns:
        Frame with rectangle drawn
    """
    try:
        x, y, w, h = face_rect
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, thickness)
        return frame
    
    except Exception as e:
        print(f"Error drawing rectangle: {e}")
        return frame


def draw_emotion_text(frame: np.ndarray, emotion: str, confidence: float, 
                     face_rect, font_scale=1.0) -> np.ndarray:
    """
    Draw detected emotion and confidence score on frame.
    
    Args:
        frame: OpenCV frame
        emotion: Detected emotion label
        confidence: Confidence score (0-1)
        face_rect: Face rectangle (x, y, w, h)
        font_scale: Font scale for text
    
    Returns:
        Frame with text drawn
    """
    try:
        x, y, w, h = face_rect
        
        # Prepare text
        text = f"{emotion} ({confidence:.2f})"
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Draw background rectangle for text
        text_size = cv2.getTextSize(text, font, font_scale, 2)[0]
        text_x = x
        text_y = y - 10
        
        cv2.rectangle(frame, (text_x, text_y - text_size[1] - 5),
                     (text_x + text_size[0], text_y + 5), (0, 0, 0), -1)
        
        # Draw text
        cv2.putText(frame, text, (text_x, text_y),
                   font, font_scale, (0, 255, 0), 2)
        
        return frame
    
    except Exception as e:
        print(f"Error drawing emotion text: {e}")
        return frame


def get_frame_stats(frame: np.ndarray) -> dict:
    """
    Get statistics about a frame.
    
    Args:
        frame: OpenCV frame
    
    Returns:
        Dictionary with frame statistics
    """
    try:
        if frame is None:
            return {}
        
        height, width = frame.shape[:2]
        
        return {
            "width": width,
            "height": height,
            "channels": frame.shape[2] if len(frame.shape) > 2 else 1,
            "size_bytes": frame.nbytes
        }
    
    except Exception as e:
        print(f"Error getting frame stats: {e}")
        return {}
