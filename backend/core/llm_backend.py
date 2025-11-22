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
    
    def __init__(self, model: str = "mistral:7b", base_url: str = "http://localhost:11434"):
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
            # Make streaming request directly - no pre-flight checks to minimize latency
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": True,
                    "options": {
                        "temperature": kwargs.get("temperature", 0.9),
                        "top_p": kwargs.get("top_p", 0.95),
                        "num_predict": kwargs.get("num_predict", 1024),
                    }
                },
                stream=True,
                timeout=180  # Increased timeout for slow models
            )
            response.raise_for_status()
            
            chunk_count = 0
            try:
                for line in response.iter_lines():
                    if line:
                        import json
                        try:
                            data = json.loads(line)
                            if "message" in data and "content" in data["message"]:
                                content = data["message"]["content"]
                                if content:  # Only yield non-empty content
                                    try:
                                        yield content
                                        chunk_count += 1
                                    except (BrokenPipeError, ConnectionError, OSError) as e:
                                        logger.warning(f"Client disconnected during LLM streaming: {e}")
                                        break  # Stop yielding if client disconnected
                            
                            if data.get("done"):
                                break
                        except json.JSONDecodeError:
                            continue  # Skip malformed JSON
                        except (BrokenPipeError, ConnectionError, OSError) as e:
                            logger.warning(f"Connection error during LLM streaming: {e}")
                            break
                        except Exception as e:
                            logger.warning(f"Error parsing chunk: {e}")
                            continue
            except (BrokenPipeError, ConnectionError, OSError) as e:
                logger.warning(f"Connection broken during LLM stream iteration: {e}")
                # Don't raise - just stop yielding
            except Exception as e:
                logger.error(f"Unexpected error in LLM streaming: {e}")
                raise
            
            # If no chunks received, model might not be responding
            if chunk_count == 0:
                raise Exception(f"Model {self.model} did not generate any output. Check if the model is loaded in Ollama.")
        
        except requests.exceptions.Timeout:
            logger.error(f"Ollama request timed out after 180s")
            raise Exception(f"Request timed out. The model may be too slow or not responding. Try a smaller model or check Ollama.")
        except requests.exceptions.ConnectionError:
            raise Exception(f"Cannot connect to Ollama at {self.base_url}. Make sure Ollama is running: ollama serve")
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

