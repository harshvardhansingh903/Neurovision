"""
Train emotion detection model from local image folders.
Dataset should be in archive/processed_data with subdirs for each emotion.
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import cv2
from pathlib import Path
from tqdm import tqdm

# Config
DATASET_PATH = "archive/processed_data"
EMOTIONS = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']
IMG_SIZE = (48, 48)
BATCH_SIZE = 32
EPOCHS = 150  # Train for more epochs to improve accuracy
VALIDATION_SPLIT = 0.2
TEST_SPLIT = 0.1


def load_images_from_folders():
    """Load all images from emotion folders."""
    print("\n" + "="*70)
    print("LOADING IMAGES")
    print("="*70 + "\n")
    
    X = []
    y = []
    
    for emotion_idx, emotion in enumerate(EMOTIONS):
        emotion_path = os.path.join(DATASET_PATH, emotion)
        
        if not os.path.exists(emotion_path):
            print(f"⚠ Folder not found: {emotion_path}")
            continue
        
        image_files = [f for f in os.listdir(emotion_path) 
                      if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        
        print(f"Loading {emotion}... ({len(image_files)} images)")
        
        for img_file in tqdm(image_files, desc=f"  {emotion}", leave=False):
            try:
                img_path = os.path.join(emotion_path, img_file)
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                
                if img is not None:
                    # Resize to 48x48
                    img = cv2.resize(img, IMG_SIZE)
                    # Normalize
                    img = img.astype('float32') / 255.0
                    # Add channel dimension
                    img = np.expand_dims(img, axis=-1)
                    
                    X.append(img)
                    y.append(emotion_idx)
            except Exception as e:
                print(f"    Error loading {img_file}: {e}")
    
    X = np.array(X)
    y = keras.utils.to_categorical(y, len(EMOTIONS))
    
    print(f"\n✓ Loaded {len(X)} images with {len(EMOTIONS)} emotion classes")
    print(f"✓ Dataset shape: {X.shape}")
    print(f"✓ Labels shape: {y.shape}")
    
    return X, y


def create_model():
    """Build CNN model for emotion classification."""
    print("\n" + "="*70)
    print("BUILDING CNN")
    print("="*70 + "\n")
    
    model = models.Sequential([
        # Input layer
        layers.Input(shape=(48, 48, 1)),
        
        # Block 1
        layers.Conv2D(64, kernel_size=3, padding='same', activation='relu'),
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
        
        # Flatten and Dense
        layers.Flatten(),
        layers.Dense(512, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        
        # Output
        layers.Dense(len(EMOTIONS), activation='softmax')
    ])
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.0001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print("✓ Model built successfully")
    model.summary()
    
    return model


def train_model():
    """Main training pipeline."""
    print("\n" + "="*70)
    print("TRAINING EMOTION MODEL")
    print("="*70)
    
    # Load dataset
    X, y = load_images_from_folders()
    
    # Split data: 70% train, 10% validation, 20% test
    total_samples = len(X)
    test_size = int(total_samples * TEST_SPLIT)
    train_size = int((total_samples - test_size) * (1 - VALIDATION_SPLIT))
    
    indices = np.random.permutation(total_samples)
    
    train_indices = indices[:train_size]
    val_indices = indices[train_size:train_size + int((total_samples - test_size) * VALIDATION_SPLIT)]
    test_indices = indices[-test_size:]
    
    X_train, y_train = X[train_indices], y[train_indices]
    X_val, y_val = X[val_indices], y[val_indices]
    X_test, y_test = X[test_indices], y[test_indices]
    
    print(f"\n✓ Train: {len(X_train)}, Validation: {len(X_val)}, Test: {len(X_test)}")
    
    # Data augmentation for training - ENHANCED for better generalization
    train_datagen = ImageDataGenerator(
        rotation_range=25,          # Increased from 10
        width_shift_range=0.15,     # Increased from 0.1
        height_shift_range=0.15,    # Increased from 0.1
        zoom_range=0.15,            # Increased from 0.1
        brightness_range=[0.8, 1.2],  # New: brightness variation
        horizontal_flip=True,
        shear_range=0.1,            # New: shear transformation
        fill_mode='nearest'
    )
    
    # Set validation data generator without augmentation
    val_datagen = ImageDataGenerator()
    
    # Create model
    model = create_model()
    
    # Callbacks
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=15,  # Increased from 5 to allow longer training
            restore_best_weights=True,
            verbose=1
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,  # Increased from 3
            min_lr=1e-7,  # Lowered min_lr for finer tuning
            verbose=1
        )
    ]
    
    # Train
    print("\n" + "="*70)
    print("TRAINING")
    print("="*70 + "\n")
    
    history = model.fit(
        train_datagen.flow(X_train, y_train, batch_size=BATCH_SIZE),
        epochs=EPOCHS,
        validation_data=val_datagen.flow(X_val, y_val, batch_size=BATCH_SIZE),
        callbacks=callbacks,
        verbose=1
    )
    
    # Evaluate
    print("\n" + "="*70)
    print("EVALUATION")
    print("="*70 + "\n")
    
    val_loss, val_accuracy = model.evaluate(X_val, y_val, verbose=0)
    test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
    
    print(f"✓ Validation Accuracy: {val_accuracy*100:.2f}%")
    print(f"✓ Validation Loss: {val_loss:.4f}")
    print(f"✓ Test Accuracy: {test_accuracy*100:.2f}%")
    print(f"✓ Test Loss: {test_loss:.4f}")
    
    # Save model
    os.makedirs("models", exist_ok=True)
    model_path = "models/emotion_model.h5"
    model.save(model_path)
    
    print(f"\n✓ Model saved to: {model_path}")
    print(f"✓ Model size: {os.path.getsize(model_path) / (1024*1024):.1f} MB")
    
    # Print emotion labels for reference
    print(f"\n✓ Emotion labels (in order): {EMOTIONS}")
    
    return model, history


def save_training_config():
    """Save training configuration for reference."""
    config = {
        "emotions": EMOTIONS,
        "img_size": IMG_SIZE,
        "dataset_path": DATASET_PATH,
        "epochs_trained": EPOCHS,
        "batch_size": BATCH_SIZE
    }
    
    import json
    with open("models/training_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Training config saved to: models/training_config.json")


if __name__ == "__main__":
    try:
        model, history = train_model()
        save_training_config()
        
        print("\n" + "="*70)
        print("✓ TRAINING COMPLETE!")
        print("="*70)
        print("\nNext steps:")
        print("1. Rebuild Docker: cd ..")
        print("2. Run: docker-compose down && docker-compose up --build")
        print("3. Open: http://localhost:3000")
        print("4. Test your emotion detection model!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n✗ Training failed: {e}")
        import traceback
        traceback.print_exc()
