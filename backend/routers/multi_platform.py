"""
Multi-Platform Optimizer API endpoints
Adapt ONE piece of content for multiple platforms automatically
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import logging
import json

from core.llm_backend import LLMBackend

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/optimize", tags=["multi-platform"])

# Global instances (injected by main.py)
llm_backend = None

def set_globals(emb, vs, llm):
    global llm_backend
    llm_backend = llm

class MultiPlatformRequest(BaseModel):
    original_content: Dict  # Original content (script, hook, etc.)
    original_platform: str  # Original platform
    target_platforms: List[str]  # Platforms to adapt for
    niche: str = "general"
    personality: str = "friendly"

@router.post("/multi-platform")
async def optimize_for_platforms(req: MultiPlatformRequest):
    """
    Take ONE piece of content and auto-optimize for multiple platforms
    
    Example:
    YouTube video → TikTok, IG Reel, YT Short, LinkedIn, Twitter
    
    Auto-adjusts:
    - Aspect ratio (16:9 → 9:16)
    - Length (10min → 60s clips)
    - Captions/copy
    - Hashtags
    - Thumbnails
    """
    
    if not llm_backend:
        raise HTTPException(status_code=503, detail="Backend not fully initialized")
    
    try:
        original_script = req.original_content.get('script', '')
        original_hook = req.original_content.get('hook', '')
        original_title = req.original_content.get('title', '')
        
        # Generate optimizations for each target platform
        optimized = {}
        
        for target_platform in req.target_platforms:
            user_prompt = f"""Adapt this content for {target_platform}:

ORIGINAL PLATFORM: {req.original_platform}
TARGET PLATFORM: {target_platform}
NICHE: {req.niche}
PERSONALITY: {req.personality}

ORIGINAL CONTENT:
Title: {original_title}
Hook: {original_hook}
Script: {original_script[:500]}...

TASK: Create a {target_platform}-optimized version that:

1. Matches platform culture and format
2. Uses appropriate length for {target_platform}
3. Maintains core message and value
4. Adapts tone/format for platform

PLATFORM REQUIREMENTS:
- {target_platform}: Format details, length, style requirements

OUTPUT FORMAT:
Title: [Optimized title for {target_platform}]
Hook: [Optimized hook for {target_platform}]
Script: [Adapted script for {target_platform}, appropriate length]
Captions: [Platform-specific captions/copy]
Hashtags: [Platform-appropriate hashtags/tags]
Best Posting Time: [Optimal time for {target_platform}]
Description: [Platform-optimized description]

Make it feel native to {target_platform}, not just copied from {req.original_platform}.

ABSOLUTELY NO EMOJIS. Use plain text only."""

            messages = [
                {
                    "role": "system",
                    "content": f"You are a multi-platform content optimizer. Adapt content from {req.original_platform} to {target_platform} while maintaining the core message. ABSOLUTELY NO EMOJIS - plain text only."
                },
                {"role": "user", "content": user_prompt}
            ]
            
            # Generate optimization (streaming for first platform, then batch others)
            optimization_text = ""
            async for chunk in llm_backend.generate_stream(messages, temperature=0.85):
                optimization_text += chunk
            
            optimized[target_platform] = optimization_text
        
        # Return all optimizations
        async def stream_response():
            try:
                # Stream all optimizations as JSON
                result = {
                    "original_platform": req.original_platform,
                    "target_platforms": req.target_platforms,
                    "optimized_content": optimized,
                    "posting_schedule": {
                        platform: "Best time for platform" for platform in req.target_platforms
                    }
                }
                
                yield f"data: {json.dumps({'result': result})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(stream_response(), media_type="text/event-stream")
    
    except Exception as e:
        logger.error(f"Error optimizing for platforms: {e}")
        raise HTTPException(status_code=500, detail=str(e))

