"""
Trends API endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from core.trends import trend_service, Trend
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/trends", tags=["trends"])

class TrendsRequest(BaseModel):
    platform: str
    niche: Optional[str] = None
    use_cache: bool = True

@router.get("/")
async def get_trends(platform: str, niche: Optional[str] = None, use_cache: bool = True):
    """
    Get trending topics for a platform and optional niche.
    
    Args:
        platform: Platform name (tiktok, youtube, instagram, etc.)
        niche: Optional niche filter (beauty, tech, food, etc.)
        use_cache: Whether to use cached results (default: True)
    
    Returns:
        List of trending topics with metadata
    """
    try:
        trends = trend_service.get_trends(
            platform=platform,
            niche=niche,
            use_cache=use_cache
        )
        
        # Convert to dict for JSON response
        trends_data = [
            {
                "topic": trend.topic,
                "platform": trend.platform,
                "category": trend.category,
                "popularity_score": trend.popularity_score,
                "source": trend.source,
                "metadata": trend.metadata or {}
            }
            for trend in trends
        ]
        
        return {
            "status": "success",
            "platform": platform,
            "niche": niche,
            "trends": trends_data,
            "count": len(trends_data)
        }
    
    except Exception as e:
        logger.error(f"Error fetching trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/formatted")
async def get_formatted_trends(platform: str, niche: Optional[str] = None, max_count: int = 5):
    """
    Get formatted trends ready for prompt inclusion.
    
    Args:
        platform: Platform name
        niche: Optional niche filter
        max_count: Maximum number of trends to return
    
    Returns:
        Formatted string ready for prompt inclusion
    """
    try:
        trends = trend_service.get_trends(
            platform=platform,
            niche=niche,
            use_cache=True
        )
        
        formatted = trend_service.format_trends_for_prompt(trends, max_count=max_count)
        
        return {
            "status": "success",
            "formatted": formatted,
            "trend_count": len(trends)
        }
    
    except Exception as e:
        logger.error(f"Error formatting trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

