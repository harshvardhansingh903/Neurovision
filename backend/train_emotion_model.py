"""
Train emotion detection model using transfer learning.
Uses MobileNetV2 (lightweight) pre-trained on ImageNet.
Trains on FER2013 dataset for emotion classification.
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
import os
import cv2
from tqdm import tqdm
import pickle

def get_fer2013_data():
    """
    Download and load FER2013 dataset.
    Alternative: Use CSV file directly if downloaded.
    """
    print("Attempting to load FER2013 dataset...")
    
    # Check if we have the CSV file
    csv_path = "fer2013.csv"
    
    if not os.path.exists(csv_path):
        print("\n" + "="*70)
        print("FER2013 dataset not found!")
        print("="*70)
        print("\nTo train the emotion model:")
        print("1. Download FER2013 from: https://www.kaggle.com/datasets/murnommurno/fer2013")
        print("2. Extract to: backend/fer2013.csv")
        print("3. Run this script again: python train_emotion_model.py")
        print("\nFor now, using random-weight model.")
        print("="*70 + "\n")
        return None, None
    
    print("Loading FER2013 dataset...")
    
    # Read CSV
    data = np.loadtxt(csv_path, delimiter=',', dtype='int', skiprows=1)
    
    X = []
    y = []
    
    for i in tqdm(range(len(data)), desc="Processing images"):
        pixels = data[i, :-2]  # All but last 2 columns
        emotion = data[i, -2]   # Emotion label
        usage = data[i, -1]     # Train/Test split
        
        # Reshape to 48x48
        img = pixels.reshape(48, 48, 1).astype('float32') / 255.0
        X.append(img)
        y.append(emotion)
    
    X = np.array(X)
    y = keras.utils.to_categorical(y, 7)
    
    print(f"✓ Loaded {len(X)} images with {y.shape[1]} emotion classes")
    
    return X, y


def create_transfer_learning_model():
    """
    Create emotion detection model using MobileNetV2 transfer learning.
    MobileNetV2 is lightweight and fast for mobile deployment.
    """
    print("\nBuilding transfer learning model...")
    
    # Load MobileNetV2 pre-trained on ImageNet (exclude top layers)
    base_model = keras.applications.MobileNetV2(
        input_shape=(48, 48, 3),
        include_top=False,
        weights='imagenet'
    )
    
    # Freeze base model weights
    base_model.trainable = False
    
    # Create model
    model = models.Sequential([
        # Input layer for 48x48 grayscale -> convert to RGB
        layers.Lambda(lambda x: tf.image.grayscale_to_rgb(x), input_shape=(48, 48, 1)),
        
        # Normalize ImageNet style
        keras.applications.mobilenet_v2.preprocess_input,
        
        # Pre-trained base
        base_model,
        
        # Global average pooling
        layers.GlobalAveragePooling2D(),
        
        # Custom top layers for emotion classification
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(7, activation='softmax')  # 7 emotion classes
    ])
    
    # Compile
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print("✓ Model built successfully")
    return model


def train_emotion_model():
    """Main training function."""
    
    print("\n" + "="*70)
    print("EMOTION MODEL TRAINING - Transfer Learning")
    print("="*70 + "\n")
    
    # Load data
    X, y = get_fer2013_data()
    
    if X is None:
        print("\n⚠ Cannot train without FER2013 dataset. Using random-weight model.")
        return False
    
    # Split data
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    # Create model
    model = create_transfer_learning_model()
    
    # Train
    print("\nTraining model...")
    print("This may take 10-30 minutes depending on your GPU\n")
    
    history = model.fit(
        X_train, y_train,
        epochs=50,
        batch_size=32,
        validation_split=0.2,
        verbose=1
    )
    
    # Evaluate
    print("\nEvaluating model...")
    loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
    print(f"✓ Test Accuracy: {accuracy*100:.2f}%")
    print(f"✓ Test Loss: {loss:.4f}")
    
    # Save model
    os.makedirs("models", exist_ok=True)
    model_path = "models/emotion_model.h5"
    model.save(model_path)
    
    print(f"\n✓ Model saved to: {model_path}")
    print(f"✓ Model size: {os.path.getsize(model_path) / (1024*1024):.1f} MB")
    
    return True


if __name__ == "__main__":
    success = train_emotion_model()
    
    if success:
        print("\n" + "="*70)
        print("✓ Training complete! Restart the application to use the trained model.")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("⚠ Training not completed. Check requirements above.")
        print("="*70)
