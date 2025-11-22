"""
Engagement Predictor API endpoints
Predict views/engagement before posting based on content quality and historical data
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import logging
import json

from core.rag_engine import RAGEngine
from core.embeddings import EmbeddingEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/predict", tags=["engagement-predictor"])

# Global instances (injected by main.py)
embedding_engine = None
vector_store = None
llm_backend = None

def set_globals(emb, vs, llm):
    global embedding_engine, vector_store, llm_backend
    embedding_engine = emb
    vector_store = vs
    llm_backend = llm

class EngagementPredictRequest(BaseModel):
    user_id: str = "default_user"
    content: Dict  # hook, script, platform, posting_time, etc.
    platform: str = "tiktok"
    niche: str = "general"
    posting_time: Optional[str] = None  # Optional posting time
    historical_context: bool = True

@router.post("/engagement")
async def predict_engagement(req: EngagementPredictRequest):
    """
    Predict engagement metrics based on:
    1. User's historical performance
    2. Content quality indicators
    3. Posting time
    4. Platform trends
    """
    
    if not llm_backend or not embedding_engine or not vector_store:
        raise HTTPException(status_code=503, detail="Backend not fully initialized")
    
    try:
        rag = RAGEngine(embedding_engine, vector_store, llm_backend)
        
        # Get user's historical data
        user_stats = {}
        try:
            query_text = f"{req.platform} {req.niche} content"
            rag_results = rag.retrieve_context(
                user_id=req.user_id,
                query=query_text,
                platform=req.platform,
                top_k=20
            )
            
            if rag_results:
                # Calculate average metrics
                performances = [r.get('performance', {}) for r in rag_results if r.get('performance')]
                if performances:
                    avg_views = sum(p.get('views', 0) for p in performances) / len(performances)
                    avg_engagement = sum(p.get('engagement_rate', 0) for p in performances) / len(performances)
                    
                    user_stats = {
                        'avg_views': int(avg_views) if avg_views > 0 else 1000,
                        'avg_engagement_rate': avg_engagement if avg_engagement > 0 else 0.05,
                        'best_time': '6PM EST',  # Could be calculated from data
                        'audience_timezone': 'EST'
                    }
        except Exception as e:
            logger.warning(f"Could not retrieve user stats: {e}")
            user_stats = {
                'avg_views': 1000,
                'avg_engagement_rate': 0.05,
                'best_time': '6PM EST',
                'audience_timezone': 'EST'
            }
        
        # Analyze content quality
        content_text = req.content.get('hook', '') or req.content.get('script', '') or req.content.get('content', '')
        
        # Analyze with LLM
        user_prompt = f"""Predict engagement for this content:

CONTENT:
Hook: {req.content.get('hook', 'N/A')}
Script: {req.content.get('script', 'N/A')[:200]}...
Platform: {req.platform}
Niche: {req.niche}
Posting Time: {req.posting_time or 'Not specified'}

USER'S HISTORICAL PERFORMANCE:
- Average Views: {user_stats.get('avg_views', 1000):,}
- Average Engagement Rate: {user_stats.get('avg_engagement_rate', 0.05):.2%}
- Best Posting Time: {user_stats.get('best_time', '6PM EST')}
- Audience Timezone: {user_stats.get('audience_timezone', 'EST')}

TASK: Predict engagement metrics based on content quality, historical performance, and posting time.

ANALYSIS FACTORS:
1. Content Quality: Hook strength, clarity, emotional impact
2. Historical Context: Compare to user's average performance
3. Time of Day: Best posting times for {req.platform}
4. Platform Trends: Current trending topics/patterns

OUTPUT FORMAT (JSON):
{{
  "views": {{
    "low": 500,
    "likely": 1200,
    "high": 2000
  }},
  "engagement_rate": 0.065,
  "confidence": 0.75,
  "factors": {{
    "content_quality": 0.85,
    "time_of_day": 0.90,
    "historical_avg": {user_stats.get('avg_views', 1000)},
    "platform_fit": 0.80
  }},
  "recommendations": [
    "Post at {user_stats.get('best_time', '6PM EST')} for maximum reach",
    "Content quality is above average for your niche"
  ],
  "comparison": {{
    "vs_avg": "15% above your average",
    "vs_niche": "Top 30% for {req.niche} content"
  }}
}}

CRITICAL: Output ONLY valid JSON. No markdown, no code blocks, no explanation. Just JSON.
ABSOLUTELY NO EMOJIS. Use plain text only."""

        messages = [
            {
                "role": "system",
                "content": "You are an engagement prediction expert. Predict views and engagement based on content quality and historical data. Output ONLY valid JSON. NO EMOJIS - plain text only."
            },
            {"role": "user", "content": user_prompt}
        ]
        
        # Generate prediction
        async def stream_response():
            try:
                prediction_text = ""
                async for chunk in llm_backend.generate_stream(messages, temperature=0.3):
                    prediction_text += chunk
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                
                # Try to parse JSON
                try:
                    json_text = prediction_text.strip()
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
        logger.error(f"Error predicting engagement: {e}")
        raise HTTPException(status_code=500, detail=str(e))

