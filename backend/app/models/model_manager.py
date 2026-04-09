"""
Loads and manages the emotion detection and face detection models.
Singleton so we only load models once.
"""

import numpy as np
import cv2
import os

# Setup OpenCV for server environment
cv2.setUseOptimized(True)
try:
    cv2.ocl.setUseOpenCL(False)
except:
    pass

import tensorflow as tf
from tensorflow import keras
from .emotion_model import build_emotion_model, get_emotion_labels, create_pretrained_emotion_model


class ModelManager:
    """
    Handles all ML model loading and inference.
    Uses singleton pattern so models are loaded only once.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Load models on first initialization."""
        if self._initialized:
            return
        
        self._initialized = True
        self.emotion_model = None
        self.face_cascade = None
        self.emotion_labels = get_emotion_labels()
        
        self._load_models()
    
    def _load_models(self):
        """
        Load emotion and face detection models.
        """
        try:
            # Load trained emotion model
            model_path = "models/emotion_model.h5"
            
            if os.path.exists(model_path):
                print(f"✓ Loading model from {model_path}")
                self.emotion_model = keras.models.load_model(model_path)
                print("✓ Model loaded")
            else:
                print(f"⚠ Model not found at {model_path}")
                print("   Using random weights (dev mode)")
                print("   Train with: python train_emotion_model.py")
                # Fallback to random model
                self.emotion_model = create_pretrained_emotion_model()
            
            # Load face detector
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            
            if self.face_cascade.empty():
                print("⚠ Face cascade not found")
                self.face_cascade = cv2.CascadeClassifier()
            else:
                print("✓ Face detector ready")
            
            print("✓ Models initialized")
            
        except Exception as e:
            print(f"⚠ Error loading models: {e}")
            # Create fallback model
            if self.emotion_model is None:
                self.emotion_model = create_pretrained_emotion_model()
                print("✓ Fallback emotion model created")
    
    def detect_faces(self, gray_frame):
        """
        Detect faces in a grayscale frame using Haar Cascade.
        
        Args:
            gray_frame: Grayscale image (numpy array)
        
        Returns:
            List of face rectangles (x, y, w, h)
        """
        try:
            faces = self.face_cascade.detectMultiScale(
                gray_frame,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            return faces
        except Exception as e:
            print(f"Error detecting faces: {e}")
            return []
    
    def predict_emotion(self, face_roi):
        """
        Predict emotion from a face ROI.
        
        Args:
            face_roi: Cropped face region (numpy array, 48x48 or will be resized)
        
        Returns:
            Dict with emotion label and confidence score
        """
        try:
            # Resize to model input size
            if face_roi.shape != (48, 48):
                face_roi = cv2.resize(face_roi, (48, 48))
            
            # Normalize pixel values
            face_roi = face_roi.astype('float32') / 255.0
            
            # Add batch dimension if needed
            if len(face_roi.shape) == 2:
                face_roi = face_roi[:, :, np.newaxis]
            
            # Add batch dimension for model
            input_data = np.expand_dims(face_roi, axis=0)
            
            # Make prediction (TensorFlow/Keras - no need for no_grad context)
            predictions = self.emotion_model.predict(input_data, verbose=0)
            
            # Get emotion and confidence
            emotion_idx = np.argmax(predictions[0])
            emotion_label = self.emotion_labels[emotion_idx]
            confidence = float(predictions[0][emotion_idx])
            
            # Debug: Print all predictions
            print(f"DEBUG - Raw predictions: {predictions[0]}")
            print(f"DEBUG - Emotion index: {emotion_idx}, Label: {emotion_label}, Confidence: {confidence:.4f}")
            print(f"DEBUG - All emotions: {dict(zip(self.emotion_labels, predictions[0].tolist()))}")
            
            return {
                "emotion": emotion_label,
                "confidence": confidence,
                "all_predictions": {
                    self.emotion_labels[i]: float(predictions[0][i])
                    for i in range(len(self.emotion_labels))
                }
            }
        
        except Exception as e:
            print(f"Error predicting emotion: {e}")
            return {
                "emotion": "Unknown",
                "confidence": 0.0,
                "all_predictions": {label: 0.0 for label in self.emotion_labels}
            }
    
    def get_emotion_labels(self):
        """
        Get the list of emotion labels.
        
        Returns:
            List of emotion class names
        """
        return self.emotion_labels


# Create singleton instance
model_manager = ModelManager()
