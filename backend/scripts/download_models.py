#!/usr/bin/env python3
"""
Script to download embedding models for offline use.
Run this if you want to pre-download models before starting the server.
"""

import os
from sentence_transformers import SentenceTransformer
from transformers import CLIPProcessor, CLIPModel

def download_text_model():
    """Download text embedding model"""
    print("📥 Downloading text embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("✅ Text model downloaded")

def download_image_model():
    """Download image embedding model (CLIP)"""
    print("📥 Downloading image embedding model (CLIP)...")
    try:
        model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        print("✅ Image model downloaded")
    except Exception as e:
        print(f"⚠️  Could not download CLIP model: {e}")
        print("   Image embeddings will be disabled")

if __name__ == "__main__":
    print("🚀 Downloading embedding models...")
    print("")
    download_text_model()
    print("")
    download_image_model()
    print("")
    print("✅ All models downloaded!")

