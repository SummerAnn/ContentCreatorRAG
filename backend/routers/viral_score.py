"""
Viral Score Analyzer API endpoints
Real-time viral potential scoring as user types
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import logging
import json

from core.rag_engine import RAGEngine
from core.embeddings import EmbeddingEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/viral-score", tags=["viral-score"])

# Global instances (injected by main.py)
embedding_engine = None
vector_store = None
llm_backend = None

def set_globals(emb, vs, llm):
    global embedding_engine, vector_store, llm_backend
    embedding_engine = emb
    vector_store = vs
    llm_backend = llm

class ViralScoreRequest(BaseModel):
    user_id: str = "default_user"
    content: str
    content_type: str = "hook"  # "hook", "script", "caption"
    platform: str = "tiktok"
    niche: str = "general"

@router.post("/live")
async def calculate_viral_score_live(req: ViralScoreRequest):
    """
    As user types, calculate viral potential in real-time
    
    Scores:
    1. Hook strength (0-100)
    2. Pattern match with viral content (0-100)
    3. Emotional impact (0-100)
    4. Clarity/simplicity (0-100)
    5. Platform fit (0-100)
    
    Overall Viral Score: 0-100
    """
    
    if not llm_backend or not embedding_engine or not vector_store:
        raise HTTPException(status_code=503, detail="Backend not fully initialized")
    
    try:
        rag = RAGEngine(embedding_engine, vector_store, llm_backend)
        
        # Get user's best content for comparison
        user_best = []
        try:
            query_text = f"{req.platform} {req.niche} {req.content_type}"
            rag_results = rag.retrieve_context(
                user_id=req.user_id,
                query=query_text,
                platform=req.platform,
                content_type=req.content_type,
                top_k=5
            )
            user_best = [r.get('content', '') for r in rag_results[:3] if r.get('content')]
        except Exception as e:
            logger.warning(f"Could not retrieve user best: {e}")
        
        # Analyze with LLM
        user_prompt = f"""Analyze this {req.content_type} for viral potential:

CONTENT:
{req.content}

CONTEXT:
- Platform: {req.platform}
- Niche: {req.niche}
- Content Type: {req.content_type}

USER'S BEST PERFORMERS:
{chr(10).join(f'- {best[:100]}...' for best in user_best) if user_best else 'No past performance data available.'}

TASK: Score this content on viral potential (0-100 for each metric).

METRICS TO SCORE:
1. Hook Strength (0-100): Attention-grabbing, curiosity gap, first 3 seconds impact
2. Pattern Match (0-100): Similarity to viral patterns, proven structures
3. Emotional Impact (0-100): Evokes emotion (curiosity, shock, inspiration, humor)
4. Clarity/Simplicity (0-100): Easy to understand, not confusing
5. Platform Fit (0-100): Matches {req.platform} culture and format

OUTPUT FORMAT (JSON):
{{
  "hook_strength": 75,
  "pattern_match": 82,
  "emotional_impact": 68,
  "clarity": 85,
  "platform_fit": 90,
  "overall": 80,
  "suggestions": [
    {{
      "issue": "Weak hook",
      "fix": "Start with a question or bold statement",
      "example": "Try: 'You won't believe what happened...'"
    }}
  ],
  "comparison": {{
    "vs_user_best": "Similar style to your top performers (85% match)",
    "vs_platform_avg": "Above average for {req.platform} (top 20%)"
  }}
}}

CRITICAL: Output ONLY valid JSON. No markdown, no code blocks, no explanation. Just JSON.
ABSOLUTELY NO EMOJIS. Use plain text only."""

        messages = [
            {
                "role": "system",
                "content": "You are a viral content analyzer. Score content on viral potential metrics. Output ONLY valid JSON. NO EMOJIS - plain text only."
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
                
                # Try to parse JSON from response
                try:
                    # Extract JSON from response (handle markdown code blocks if present)
                    json_text = analysis_text.strip()
                    if "```json" in json_text:
                        json_text = json_text.split("```json")[1].split("```")[0].strip()
                    elif "```" in json_text:
                        json_text = json_text.split("```")[1].split("```")[0].strip()
                    
                    parsed = json.loads(json_text)
                    yield f"data: {json.dumps({'parsed': parsed})}\n\n"
                except:
                    # If JSON parsing fails, return raw text
                    pass
                
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                logger.error(f"Generation error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(stream_response(), media_type="text/event-stream")
    
    except Exception as e:
        logger.error(f"Error calculating viral score: {e}")
        raise HTTPException(status_code=500, detail=str(e))
