from typing import List, Dict
import logging

from .embeddings import EmbeddingEngine
from .vector_store import VectorStore
from .llm_backend import LLMBackend

logger = logging.getLogger(__name__)

class RAGEngine:
    """Orchestrates RAG pipeline: embed → retrieve → generate"""
    
    def __init__(self, 
                 embedding_engine: EmbeddingEngine,
                 vector_store: VectorStore,
                 llm_backend: LLMBackend):
        self.embedder = embedding_engine
        self.vector_store = vector_store
        self.llm = llm_backend
        logger.info("RAG Engine initialized")
    
    def index_user_content(self,
                          user_id: str,
                          content_items: List[Dict]) -> int:
        """
        Index a batch of user's past content for RAG.
        
        Args:
            user_id: User identifier
            content_items: List of dicts with keys:
                - content: The text content
                - platform: e.g., 'youtube_short'
                - niche: e.g., 'travel'
                - content_type: e.g., 'hook', 'script'
                - performance: dict with metrics (views, likes, etc.)
                - metadata: additional data
        
        Returns:
            Number of items indexed
        """
        logger.info(f"Indexing {len(content_items)} items for user {user_id}")
        
        # Extract all content texts for batch embedding
        texts = [item['content'] for item in content_items]
        embeddings = self.embedder.embed_texts(texts)
        
        # Add each item to vector store
        count = 0
        for item, embedding in zip(content_items, embeddings):
            # Calculate normalized performance score
            performance = item.get('performance', {})
            score = self._calculate_performance_score(performance)
            
            self.vector_store.add(
                user_id=user_id,
                content=item['content'],
                embedding=embedding,
                platform=item.get('platform', 'unknown'),
                niche=item.get('niche', 'general'),
                content_type=item.get('content_type', 'text'),
                metadata=item.get('metadata', {}),
                performance_score=score
            )
            count += 1
        
        logger.info(f"✅ Indexed {count} items for user {user_id}")
        return count
    
    def retrieve_context(self,
                        user_id: str,
                        query: str,
                        platform: str = None,
                        niche: str = None,
                        content_type: str = None,
                        top_k: int = 10) -> List[Dict]:
        """
        Retrieve relevant context from user's past content.
        
        Args:
            user_id: User identifier
            query: Search query
            platform: Filter by platform
            niche: Filter by niche
            content_type: Filter by content type
            top_k: Number of results
        
        Returns:
            List of relevant content items
        """
        # Embed query
        query_embedding = self.embedder.embed_text(query)
        
        # Build filters
        filters = {}
        if platform:
            filters['platform'] = platform
        if niche:
            filters['niche'] = niche
        if content_type:
            filters['content_type'] = content_type
        
        # Only retrieve high-performing content
        filters['min_performance'] = 0.5
        
        # Search vector store
        results = self.vector_store.search(
            query_embedding=query_embedding,
            user_id=user_id,
            filters=filters,
            top_k=top_k
        )
        
        logger.debug(f"Retrieved {len(results)} context items for query: {query[:50]}")
        return results
    
    def _calculate_performance_score(self, performance: Dict) -> float:
        """
        Normalize performance metrics to 0-1 score.
        
        This is a simple heuristic - can be made more sophisticated.
        """
        if not performance:
            return 0.5  # Neutral score for no data
        
        # Example scoring logic
        views = performance.get('views', 0)
        likes = performance.get('likes', 0)
        comments = performance.get('comments', 0)
        shares = performance.get('shares', 0)
        
        # Simple weighted sum (adjust weights as needed)
        score = min(1.0, (
            views / 100000 * 0.4 +
            likes / 5000 * 0.3 +
            comments / 500 * 0.2 +
            shares / 200 * 0.1
        ))
        
        return score

