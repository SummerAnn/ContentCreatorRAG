"""
Thumbnail A/B Tester API endpoints
Analyze thumbnail for click-worthiness and compare variants
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import logging
import json

from core.llm_backend import LLMBackend

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/thumbnail", tags=["thumbnail-ab"])

# Global instances (injected by main.py)
llm_backend = None

def set_globals(emb, vs, llm):
    global llm_backend
    llm_backend = llm

class ThumbnailAnalyzeRequest(BaseModel):
    thumbnail_description: str  # Description of thumbnail concept/text
    platform: str = "youtube"
    niche: str = "general"
    has_face: Optional[bool] = None
    text_overlay: Optional[str] = None
    colors: Optional[List[str]] = None

class ThumbnailCompareRequest(BaseModel):
    thumbnail_a: ThumbnailAnalyzeRequest
    thumbnail_b: ThumbnailAnalyzeRequest
    platform: str = "youtube"
    niche: str = "general"

@router.post("/analyze")
async def analyze_thumbnail(req: ThumbnailAnalyzeRequest):
    """
    Analyze thumbnail for click-worthiness
    
    Checks:
    - Face visibility (faces = +30% CTR)
    - Contrast (high contrast = better)
    - Text readability (mobile-friendly?)
    - Color psychology
    - Emotion detection
    """
    
    if not llm_backend:
        raise HTTPException(status_code=503, detail="Backend not fully initialized")
    
    try:
        user_prompt = f"""Analyze this thumbnail concept for click-worthiness:

THUMBNAIL DESCRIPTION:
{req.thumbnail_description}

PLATFORM: {req.platform.upper()}
NICHE: {req.niche.title()}

ADDITIONAL INFO:
- Has Face: {req.has_face if req.has_face is not None else 'Unknown'}
- Text Overlay: {req.text_overlay or 'None'}
- Colors: {', '.join(req.colors) if req.colors else 'Unknown'}

TASK: Score this thumbnail on click-worthiness (0-100).

SCORING FACTORS:
1. Face Visibility (0-30 points): Faces increase CTR by ~30%
   - Clear face visible: 30 points
   - Partial face: 20 points
   - No face: 0 points

2. Contrast (0-30 points): High contrast stands out in small sizes
   - Very high contrast: 30 points
   - Medium contrast: 20 points
   - Low contrast: 10 points

3. Text Readability (0-20 points): Must be readable on mobile
   - Large, clear text: 20 points
   - Medium text: 15 points
   - Small/hard to read: 5 points
   - No text: 10 points (neutral)

4. Emotional Impact (0-20 points): Emotion drives clicks
   - Strong emotion (surprise, curiosity): 20 points
   - Moderate emotion: 15 points
   - Neutral: 10 points

TOTAL SCORE: 0-100

OUTPUT FORMAT (JSON):
{{
  "score": 75,
  "face_detection": {{"present": true, "points": 30, "note": "Clear face visible"}},
  "contrast_score": {{"level": "high", "points": 25, "note": "Good contrast for visibility"}},
  "text_readability": {{"level": "good", "points": 18, "note": "Text is readable on mobile"}},
  "emotional_impact": {{"emotion": "curiosity", "points": 17, "note": "Creates curiosity"}},
  "recommendations": [
    "Add more contrast for better visibility",
    "Make text larger for mobile viewing"
  ],
  "mobile_preview": "Thumbnail will look good on mobile devices",
  "platform_specific": "Optimized for {req.platform} platform"
}}

CRITICAL: Output ONLY valid JSON. No markdown, no code blocks, no explanation. Just JSON.
ABSOLUTELY NO EMOJIS. Use plain text only."""

        messages = [
            {
                "role": "system",
                "content": "You are a thumbnail analyst expert. Analyze thumbnails for click-worthiness. Output ONLY valid JSON. NO EMOJIS - plain text only."
            },
            {"role": "user", "content": user_prompt}
        ]
        
        # Generate analysis
        async def stream_response():
            try:
                analysis_text = ""
                async for chunk in llm_backend.generate_stream(messages, temperature=0.3):
                    analysis_text += chunk
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                
                # Try to parse JSON
                try:
                    json_text = analysis_text.strip()
                    if "```json" in json_text:
                        json_text = json_text.split("```json")[1].split("```")[0].strip()
                    elif "```" in json_text:
                        json_text = json_text.split("```")[1].split("```")[0].strip()
                    
                    parsed = json.loads(json_text)
                    yield f"data: {json.dumps({'parsed': parsed})}\n\n"
                except:
                    pass
                
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                logger.error(f"Generation error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(stream_response(), media_type="text/event-stream")
    
    except Exception as e:
        logger.error(f"Error analyzing thumbnail: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compare")
async def compare_thumbnails(req: ThumbnailCompareRequest):
    """Compare up to 2 thumbnail variants and predict winner"""
    
    if not llm_backend:
        raise HTTPException(status_code=503, detail="Backend not fully initialized")
    
    try:
        user_prompt = f"""Compare these two thumbnail variants:

THUMBNAIL A:
{req.thumbnail_a.thumbnail_description}
- Has Face: {req.thumbnail_a.has_face if req.thumbnail_a.has_face is not None else 'Unknown'}
- Text Overlay: {req.thumbnail_a.text_overlay or 'None'}
- Colors: {', '.join(req.thumbnail_a.colors) if req.thumbnail_a.colors else 'Unknown'}

THUMBNAIL B:
{req.thumbnail_b.thumbnail_description}
- Has Face: {req.thumbnail_b.has_face if req.thumbnail_b.has_face is not None else 'Unknown'}
- Text Overlay: {req.thumbnail_b.text_overlay or 'None'}
- Colors: {', '.join(req.thumbnail_b.colors) if req.thumbnail_b.colors else 'Unknown'}

PLATFORM: {req.platform.upper()}
NICHE: {req.niche.title()}

TASK: Compare both thumbnails and predict which will perform better.

OUTPUT FORMAT (JSON):
{{
  "winner": "A",
  "thumbnail_a": {{"score": 82, "analysis": "Strong face visibility and contrast"}},
  "thumbnail_b": {{"score": 75, "analysis": "Good but text could be larger"}},
  "difference": 7,
  "recommendation": "Thumbnail A is predicted to perform 9% better due to better face visibility"
}}

CRITICAL: Output ONLY valid JSON. No markdown, no code blocks, no explanation. Just JSON.
ABSOLUTELY NO EMOJIS. Use plain text only."""

        messages = [
            {
                "role": "system",
                "content": "You are a thumbnail comparison expert. Compare thumbnails and predict winners. Output ONLY valid JSON. NO EMOJIS - plain text only."
            },
            {"role": "user", "content": user_prompt}
        ]
        
        # Generate comparison
        async def stream_response():
            try:
                comparison_text = ""
                async for chunk in llm_backend.generate_stream(messages, temperature=0.3):
                    comparison_text += chunk
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                
                # Try to parse JSON
                try:
                    json_text = comparison_text.strip()
                    if "```json" in json_text:
                        json_text = json_text.split("```json")[1].split("```")[0].strip()
                    elif "```" in json_text:
                        json_text = json_text.split("```")[1].split("```")[0].strip()
                    
                    parsed = json.loads(json_text)
                    yield f"data: {json.dumps({'parsed': parsed})}\n\n"
                except:
                    pass
                
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                logger.error(f"Generation error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(stream_response(), media_type="text/event-stream")
    
    except Exception as e:
        logger.error(f"Error comparing thumbnails: {e}")
        raise HTTPException(status_code=500, detail=str(e))

