from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # LLM Settings
    LLM_BACKEND: str = "ollama"
    DEFAULT_MODEL: str = "mistral:7b"  # Using available model
    OLLAMA_URL: str = "http://localhost:11434"
    
    # Embedding Settings
    EMBED_MODEL: str = "all-MiniLM-L6-v2"
    IMAGE_EMBED_MODEL: str = "openai/clip-vit-base-patch32"
    
    # Database
    DATABASE_URL: str = "sqlite:///data/creatorflow.db"
    
    # Vector Store
    VECTOR_DIMENSION: int = 384  # For all-MiniLM-L6-v2
    FAISS_INDEX_PATH: str = "data/faiss.index"
    
    # Optional API Keys (for future paid model support)
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()

