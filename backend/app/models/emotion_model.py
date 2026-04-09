"""
Emotion classification CNN model based on FER2013 dataset structure.
7 emotion classes: angry, disgust, fear, happy, sad, surprise, neutral
Input shape: 48x48 grayscale images
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, optimizers
import os


def build_emotion_model(input_shape=(48, 48, 1), num_classes=7):
    """
    Build and compile a CNN model for emotion classification.
    
    Args:
        input_shape: Tuple of (height, width, channels) for input images
        num_classes: Number of emotion classes (default 7)
    
    Returns:
        Compiled Keras model ready for training
    """
    model = models.Sequential([
        # Block 1
        layers.Conv2D(64, kernel_size=3, padding='same', activation='relu', input_shape=input_shape),
        layers.BatchNormalization(),
        layers.Conv2D(64, kernel_size=3, padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D(pool_size=2),
        layers.Dropout(0.25),
        
        # Block 2
        layers.Conv2D(128, kernel_size=3, padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.Conv2D(128, kernel_size=3, padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D(pool_size=2),
        layers.Dropout(0.25),
        
        # Block 3
        layers.Conv2D(256, kernel_size=3, padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.Conv2D(256, kernel_size=3, padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D(pool_size=2),
        layers.Dropout(0.25),
        
        # Block 4
        layers.Conv2D(512, kernel_size=3, padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.Conv2D(512, kernel_size=3, padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D(pool_size=2),
        layers.Dropout(0.25),
        
        # Flatten and Dense layers
        layers.Flatten(),
        layers.Dense(512, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        
        # Output layer
        layers.Dense(num_classes, activation='softmax')
    ])
    
    # Compile model
    model.compile(
        optimizer=optimizers.Adam(learning_rate=0.0001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model


def get_emotion_labels():
    """
    Returns the list of emotion class labels.
    Testing label order: [Angry, Disgust, Fear, Neutral, Happy, Sad, Surprise]
    
    Returns:
        List of emotion names in order of model output
    """
    # When index 4 (highest) this should be Happy in smiling face scenario
    return ['Angry', 'Disgust', 'Fear', 'Neutral', 'Happy', 'Sad', 'Surprise']


def create_pretrained_emotion_model():
    """
    Create a pre-initialized emotion model with placeholder weights.
    In production, this would load weights from a trained model.
    
    Returns:
        Keras model with initialized weights
    """
    model = build_emotion_model()
    
    # Build the model to initialize weights
    model.build(input_shape=(None, 48, 48, 1))
    
    return model
