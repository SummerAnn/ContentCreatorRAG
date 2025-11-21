from sentence_transformers import SentenceTransformer
from transformers import CLIPProcessor, CLIPModel
import torch
from PIL import Image
from typing import List, Union
import logging

logger = logging.getLogger(__name__)

class EmbeddingEngine:
    """Handles text and image embeddings for RAG"""
    
    def __init__(self, text_model: str = "all-MiniLM-L6-v2", image_model: str = "openai/clip-vit-base-patch32"):
        logger.info(f"Loading text embedding model: {text_model}")
        self.text_model = SentenceTransformer(text_model)
        
        logger.info(f"Loading image embedding model: {image_model}")
        try:
            self.clip_model = CLIPModel.from_pretrained(image_model)
            self.clip_processor = CLIPProcessor.from_pretrained(image_model)
            self.has_image_support = True
        except Exception as e:
            logger.warning(f"Could not load CLIP model: {e}. Image embeddings disabled.")
            self.has_image_support = False
        
        logger.info("✅ Embedding models loaded successfully")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Embed a single text string.
        
        Args:
            text: Input text
        
        Returns:
            List of floats (384-dimensional for all-MiniLM-L6-v2)
        """
        embedding = self.text_model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Batch embed multiple texts for efficiency.
        
        Args:
            texts: List of text strings
        
        Returns:
            List of embedding vectors
        """
        embeddings = self.text_model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings.tolist()
    
    def embed_image(self, image_path: str) -> List[float]:
        """
        Embed an image using CLIP.
        
        Args:
            image_path: Path to image file
        
        Returns:
            Image embedding vector
        """
        if not self.has_image_support:
            raise RuntimeError("Image embeddings not available (CLIP model not loaded)")
        
        try:
            image = Image.open(image_path).convert('RGB')
            inputs = self.clip_processor(images=image, return_tensors="pt")
            
            with torch.no_grad():
                image_features = self.clip_model.get_image_features(**inputs)
                # Normalize the features
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
                embedding = image_features.squeeze().numpy()
            
            return embedding.tolist()
        
        except Exception as e:
            logger.error(f"Failed to embed image {image_path}: {e}")
            raise
    
    def get_dimension(self) -> int:
        """Get the dimension of text embeddings"""
        return self.text_model.get_sentence_embedding_dimension()

