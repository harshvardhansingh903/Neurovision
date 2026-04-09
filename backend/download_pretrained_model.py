"""
Download and set up a pre-trained emotion detection model.
This script downloads a model trained on FER2013 or uses transfer learning.
"""

import os
import urllib.request
import zipfile
import json

def download_emotion_model():
    """Download a pre-trained emotion model."""
    
    models_dir = "models"
    os.makedirs(models_dir, exist_ok=True)
    
    model_path = os.path.join(models_dir, "emotion_model.h5")
    
    # Check if model already exists
    if os.path.exists(model_path):
        print(f"✓ Model already exists at {model_path}")
        return model_path
    
    print("Downloading pre-trained emotion model...")
    print("This may take 2-5 minutes on first run...")
    
    # URL to a pre-trained FER2013 emotion model
    # This is a popular open-source emotion detection model
    model_urls = [
        "https://github.com/abhinand5/SpotEmotion/raw/master/Model/model.h5",  # Fallback option
    ]
    
    for url in model_urls:
        try:
            print(f"Attempting to download from: {url}")
            urllib.request.urlretrieve(url, model_path)
            
            if os.path.exists(model_path) and os.path.getsize(model_path) > 1000000:
                print(f"✓ Successfully downloaded emotion model!")
                print(f"✓ Model saved to: {model_path}")
                print(f"✓ Model size: {os.path.getsize(model_path) / (1024*1024):.1f} MB")
                return model_path
        except Exception as e:
            print(f"✗ Failed to download from {url}: {e}")
            continue
    
    # If all downloads fail, create a training guide
    print("\n" + "="*70)
    print("Could not download pre-trained model automatically.")
    print("="*70)
    print("\nAlternative: Train your own model")
    print("Download FER2013 dataset and use: python train_emotion_model.py")
    print("\nFor now, using random-weight model (predictions will be random)")
    print("="*70)
    
    return None


if __name__ == "__main__":
    download_emotion_model()
