"""
Personal Swipe File - Save and organize inspiration videos
Inspired by Blort's viral library feature
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

class SwipeFile:
    """Personal inspiration library - saves URLs and metadata"""
    
    def __init__(self, db_path: str = "data/swipefile.db"):
        """Initialize SQLite database for swipe file"""
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Create swipefile table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS swipefile (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                url TEXT NOT NULL,
                title TEXT,
                platform TEXT,
                tags TEXT,  -- JSON array of tags
                notes TEXT,
                performance_estimate TEXT,
                thumbnail_url TEXT,
                duration INTEGER,
                saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, url)
            )
        """)
        
        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_id ON swipefile(user_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tags ON swipefile(tags)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_platform ON swipefile(platform)
        """)
        
        conn.commit()
        conn.close()
    
    def save_video(
        self,
        user_id: str,
        url: str,
        title: Optional[str] = None,
        platform: Optional[str] = None,
        tags: Optional[List[str]] = None,
        notes: Optional[str] = None,
        performance_estimate: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
        duration: Optional[int] = None
    ) -> Dict:
        """Save a video URL to user's swipe file"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if URL already exists for this user
            cursor.execute(
                "SELECT id FROM swipefile WHERE user_id = ? AND url = ?",
                (user_id, url)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Update existing entry
                cursor.execute("""
                    UPDATE swipefile SET
                        title = COALESCE(?, title),
                        platform = COALESCE(?, platform),
                        tags = COALESCE(?, tags),
                        notes = COALESCE(?, notes),
                        performance_estimate = COALESCE(?, performance_estimate),
                        thumbnail_url = COALESCE(?, thumbnail_url),
                        duration = COALESCE(?, duration),
                        saved_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (
                    title, platform, json.dumps(tags or []), notes,
                    performance_estimate, thumbnail_url, duration, existing[0]
                ))
                video_id = existing[0]
            else:
                # Insert new entry
                cursor.execute("""
                    INSERT INTO swipefile 
                    (user_id, url, title, platform, tags, notes, performance_estimate, thumbnail_url, duration)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id, url, title, platform,
                    json.dumps(tags or []), notes, performance_estimate,
                    thumbnail_url, duration
                ))
                video_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            return {
                "status": "success",
                "id": video_id,
                "message": "Saved to swipe file"
            }
        
        except Exception as e:
            logger.error(f"Error saving to swipe file: {e}")
            raise
    
    def get_swipefile(
        self,
        user_id: str,
        platform: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Retrieve saved videos from swipe file"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM swipefile WHERE user_id = ?"
            params = [user_id]
            
            if platform:
                query += " AND platform = ?"
                params.append(platform)
            
            if tags:
                # SQLite JSON search (simple contains check)
                for tag in tags:
                    query += " AND tags LIKE ?"
                    params.append(f'%"{tag}"%')
            
            query += " ORDER BY saved_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            videos = []
            for row in rows:
                videos.append({
                    "id": row["id"],
                    "url": row["url"],
                    "title": row["title"],
                    "platform": row["platform"],
                    "tags": json.loads(row["tags"]) if row["tags"] else [],
                    "notes": row["notes"],
                    "performance_estimate": row["performance_estimate"],
                    "thumbnail_url": row["thumbnail_url"],
                    "duration": row["duration"],
                    "saved_at": row["saved_at"]
                })
            
            conn.close()
            return videos
        
        except Exception as e:
            logger.error(f"Error retrieving swipe file: {e}")
            return []
    
    def delete_video(self, user_id: str, video_id: int) -> Dict:
        """Delete a video from swipe file"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "DELETE FROM swipefile WHERE id = ? AND user_id = ?",
                (video_id, user_id)
            )
            
            deleted = cursor.rowcount > 0
            conn.commit()
            conn.close()
            
            if deleted:
                return {"status": "success", "message": "Video deleted"}
            else:
                return {"status": "error", "message": "Video not found"}
        
        except Exception as e:
            logger.error(f"Error deleting video: {e}")
            raise
    
    def update_video(
        self,
        user_id: str,
        video_id: int,
        tags: Optional[List[str]] = None,
        notes: Optional[str] = None,
        performance_estimate: Optional[str] = None
    ) -> Dict:
        """Update video metadata in swipe file"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if tags is not None:
                updates.append("tags = ?")
                params.append(json.dumps(tags))
            
            if notes is not None:
                updates.append("notes = ?")
                params.append(notes)
            
            if performance_estimate is not None:
                updates.append("performance_estimate = ?")
                params.append(performance_estimate)
            
            if not updates:
                return {"status": "error", "message": "No updates provided"}
            
            params.extend([video_id, user_id])
            
            cursor.execute(
                f"UPDATE swipefile SET {', '.join(updates)} WHERE id = ? AND user_id = ?",
                params
            )
            
            updated = cursor.rowcount > 0
            conn.commit()
            conn.close()
            
            if updated:
                return {"status": "success", "message": "Video updated"}
            else:
                return {"status": "error", "message": "Video not found"}
        
        except Exception as e:
            logger.error(f"Error updating video: {e}")
            raise

