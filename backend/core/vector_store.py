import faiss
import numpy as np
import sqlite3
from typing import List, Dict, Optional
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class VectorStore:
    """Free vector store using FAISS + SQLite for metadata"""
    
    def __init__(self, db_path: str = "data/creatorflow.db", dimension: int = 384):
        self.db_path = db_path
        self.dimension = dimension
        
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # FAISS index (L2 distance)
        self.index = faiss.IndexFlatL2(dimension)
        
        # SQLite for metadata
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()
        
        logger.info(f"Initialized vector store with dimension {dimension}")
    
    def _init_db(self):
        """Create database schema"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                faiss_id INTEGER,
                user_id TEXT NOT NULL,
                platform TEXT,
                niche TEXT,
                content_type TEXT,
                content TEXT,
                metadata TEXT,
                performance_score REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_platform 
            ON embeddings(user_id, platform)
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_niche 
            ON embeddings(user_id, niche)
        """)
        
        self.conn.commit()
        logger.info("Database schema initialized")
    
    def add(self, 
            user_id: str, 
            content: str, 
            embedding: List[float],
            platform: str,
            niche: str,
            content_type: str,
            metadata: Dict = None,
            performance_score: float = 0.0) -> int:
        """
        Add content and its embedding to the store.
        
        Args:
            user_id: User identifier
            content: The actual content text
            embedding: Vector embedding
            platform: e.g., 'youtube_short', 'tiktok'
            niche: e.g., 'travel', 'food'
            content_type: e.g., 'hook', 'script'
            metadata: Additional metadata dict
            performance_score: 0.0-1.0 normalized score
        
        Returns:
            ID of inserted record
        """
        # Add to FAISS
        vector = np.array([embedding], dtype=np.float32)
        self.index.add(vector)
        faiss_id = self.index.ntotal - 1
        
        # Add metadata to SQLite
        cursor = self.conn.execute("""
            INSERT INTO embeddings 
            (faiss_id, user_id, platform, niche, content_type, content, metadata, performance_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            faiss_id,
            user_id,
            platform,
            niche,
            content_type,
            content,
            json.dumps(metadata or {}),
            performance_score
        ))
        self.conn.commit()
        
        logger.debug(f"Added content for user {user_id}: {content[:50]}...")
        return cursor.lastrowid
    
    def search(self,
               query_embedding: List[float],
               user_id: str,
               filters: Optional[Dict] = None,
               top_k: int = 10) -> List[Dict]:
        """
        Search for similar content.
        
        Args:
            query_embedding: Query vector
            user_id: User to search within
            filters: Optional filters (platform, niche, min_performance, etc.)
            top_k: Number of results to return
        
        Returns:
            List of matching content dicts
        """
        if self.index.ntotal == 0:
            logger.debug("Vector store is empty, returning no results")
            return []
        
        # FAISS similarity search (get more than needed for filtering)
        query_vector = np.array([query_embedding], dtype=np.float32)
        search_k = min(top_k * 5, self.index.ntotal)
        distances, indices = self.index.search(query_vector, search_k)
        
        # Build SQL query with filters
        if len(indices[0]) > 0:
            placeholders = ','.join('?' * len(indices[0]))
            sql = f"SELECT * FROM embeddings WHERE user_id = ? AND faiss_id IN ({placeholders})"
            params = [user_id] + indices[0].tolist()
        else:
            sql = "SELECT * FROM embeddings WHERE user_id = ?"
            params = [user_id]
        
        if filters:
            if 'platform' in filters:
                sql += " AND platform = ?"
                params.append(filters['platform'])
            
            if 'niche' in filters:
                sql += " AND niche = ?"
                params.append(filters['niche'])
            
            if 'content_type' in filters:
                sql += " AND content_type = ?"
                params.append(filters['content_type'])
            
            if 'min_performance' in filters:
                sql += " AND performance_score >= ?"
                params.append(filters['min_performance'])
        
        sql += " ORDER BY performance_score DESC LIMIT ?"
        params.append(top_k)
        
        # Execute query
        cursor = self.conn.execute(sql, params)
        results = []
        
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'faiss_id': row[1],
                'user_id': row[2],
                'platform': row[3],
                'niche': row[4],
                'content_type': row[5],
                'content': row[6],
                'metadata': json.loads(row[7]) if row[7] else {},
                'performance_score': row[8],
                'created_at': row[9]
            })
        
        logger.debug(f"Found {len(results)} results for user {user_id}")
        return results
    
    def save_index(self, path: str = "data/faiss.index"):
        """Save FAISS index to disk"""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, path)
        logger.info(f"Saved FAISS index to {path}")
    
    def load_index(self, path: str = "data/faiss.index"):
        """Load FAISS index from disk"""
        if Path(path).exists():
            self.index = faiss.read_index(path)
            logger.info(f"Loaded FAISS index from {path}")
        else:
            logger.warning(f"No index found at {path}, using empty index")
    
    def count_user_content(self, user_id: str) -> int:
        """Count how many content items a user has indexed"""
        cursor = self.conn.execute(
            "SELECT COUNT(*) FROM embeddings WHERE user_id = ?",
            (user_id,)
        )
        return cursor.fetchone()[0]

