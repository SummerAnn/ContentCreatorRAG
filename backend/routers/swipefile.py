"""
Swipe File API endpoints
Personal inspiration library - inspired by Blort's viral library
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from core.swipefile import SwipeFile
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/swipefile", tags=["swipefile"])

# Initialize swipe file instance
swipefile = SwipeFile()

class SaveVideoRequest(BaseModel):
    user_id: str = "default_user"
    url: str
    title: Optional[str] = None
    platform: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    performance_estimate: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: Optional[int] = None

class UpdateVideoRequest(BaseModel):
    user_id: str = "default_user"
    video_id: int
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    performance_estimate: Optional[str] = None

class DeleteVideoRequest(BaseModel):
    user_id: str = "default_user"
    video_id: int

@router.post("/save")
async def save_video(request: SaveVideoRequest):
    """
    Save a video URL to user's personal swipe file.
    
    No video storage - just URL + metadata.
    Tag by niche, platform, mood for quick reference later.
    """
    try:
        result = swipefile.save_video(
            user_id=request.user_id,
            url=request.url,
            title=request.title,
            platform=request.platform,
            tags=request.tags,
            notes=request.notes,
            performance_estimate=request.performance_estimate,
            thumbnail_url=request.thumbnail_url,
            duration=request.duration
        )
        return result
    
    except Exception as e:
        logger.error(f"Error saving video: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_swipefile(
    user_id: str = "default_user",
    platform: Optional[str] = None,
    tags: Optional[str] = None,  # Comma-separated tags
    limit: int = 50
):
    """
    Retrieve saved videos from swipe file.
    
    Filter by tags/platform.
    Returns: List of URLs with metadata.
    """
    try:
        tag_list = [tag.strip() for tag in tags.split(",")] if tags else None
        
        videos = swipefile.get_swipefile(
            user_id=user_id,
            platform=platform,
            tags=tag_list,
            limit=limit
        )
        
        return {
            "status": "success",
            "videos": videos,
            "count": len(videos)
        }
    
    except Exception as e:
        logger.error(f"Error retrieving swipe file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/update")
async def update_video(request: UpdateVideoRequest):
    """Update video metadata (tags, notes, performance estimate)"""
    try:
        result = swipefile.update_video(
            user_id=request.user_id,
            video_id=request.video_id,
            tags=request.tags,
            notes=request.notes,
            performance_estimate=request.performance_estimate
        )
        return result
    
    except Exception as e:
        logger.error(f"Error updating video: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete")
async def delete_video(user_id: str = "default_user", video_id: int = None):
    """Delete a video from swipe file"""
    try:
        if video_id is None:
            raise HTTPException(status_code=400, detail="video_id is required")
        
        result = swipefile.delete_video(user_id=user_id, video_id=video_id)
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting video: {e}")
        raise HTTPException(status_code=500, detail=str(e))

