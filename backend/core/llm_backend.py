import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Generator
import logging

logger = logging.getLogger(__name__)

class LLMBackend(ABC):
    """Abstract base class for LLM backends"""
    
    @abstractmethod
    def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate a response from messages"""
        pass
    
    @abstractmethod
    def generate_stream(self, messages: List[Dict[str, str]], **kwargs) -> Generator[str, None, None]:
        """Generate a streaming response"""
        pass

class OllamaBackend(LLMBackend):
    """Local LLM via Ollama"""
    
    def __init__(self, model: str = "llama3.1:8b-instruct", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        logger.info(f"Initialized Ollama backend with model: {model}")
    
    def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate a complete response.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional options (temperature, top_p, etc.)
        
        Returns:
            Generated text
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": kwargs.get("temperature", 0.9),
                        "top_p": kwargs.get("top_p", 0.95),
                        "num_predict": kwargs.get("max_tokens", 1024),
                    }
                },
                timeout=120
            )
            response.raise_for_status()
            return response.json()["message"]["content"]
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama request failed: {e}")
            raise Exception(f"Failed to generate response: {str(e)}")
    
    def generate_stream(self, messages: List[Dict[str, str]], **kwargs) -> Generator[str, None, None]:
        """
        Generate a streaming response for real-time UI updates.
        
        Yields:
            Text chunks as they're generated
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": True,
                    "options": {
                        "temperature": kwargs.get("temperature", 0.9),
                        "top_p": kwargs.get("top_p", 0.95),
                    }
                },
                stream=True,
                timeout=120
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    import json
                    try:
                        data = json.loads(line)
                        if "message" in data and "content" in data["message"]:
                            yield data["message"]["content"]
                        
                        if data.get("done"):
                            break
                    except json.JSONDecodeError:
                        continue
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama streaming failed: {e}")
            raise Exception(f"Failed to stream response: {str(e)}")

class OpenAIBackend(LLMBackend):
    """OpenAI API backend (optional, for paid tier)"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        logger.info(f"Initialized OpenAI backend with model: {model}")
    
    def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        # Implementation for OpenAI API
        # Left as stub for now
        raise NotImplementedError("OpenAI backend not yet implemented")
    
    def generate_stream(self, messages: List[Dict[str, str]], **kwargs) -> Generator[str, None, None]:
        raise NotImplementedError("OpenAI streaming not yet implemented")

def get_llm_backend(backend_type: str = "ollama", **kwargs) -> LLMBackend:
    """
    Factory function to get the appropriate LLM backend.
    
    Args:
        backend_type: 'ollama', 'openai', etc.
        **kwargs: Backend-specific configuration
    
    Returns:
        LLMBackend instance
    """
    if backend_type == "ollama":
        return OllamaBackend(**kwargs)
    elif backend_type == "openai":
        return OpenAIBackend(**kwargs)
    else:
        raise ValueError(f"Unknown backend type: {backend_type}")

