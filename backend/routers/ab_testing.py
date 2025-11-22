"""
A/B Testing Simulator API endpoints
Compare variants and predict which performs better
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import logging
import json

from core.rag_engine import RAGEngine
from core.embeddings import EmbeddingEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/test", tags=["ab-testing"])

# Global instances (injected by main.py)
embedding_engine = None
vector_store = None
llm_backend = None

def set_globals(emb, vs, llm):
    global embedding_engine, vector_store, llm_backend
    embedding_engine = emb
    vector_store = vs
    llm_backend = llm

class ABTestRequest(BaseModel):
    user_id: str = "default_user"
    variant_a: str
    variant_b: str
    content_type: str = "hook"  # "hook", "thumbnail_text", "caption", "script"
    platform: str = "tiktok"
    niche: str = "general"

@router.post("/ab-predict")
async def ab_test_simulator(req: ABTestRequest):
    """
    Compare two variants and predict which performs better
    
    Based on:
    1. User's historical data (what worked for them)
    2. Similarity to high-performers
    3. Pattern analysis (hook structure, length, etc.)
    """
    
    if not llm_backend or not embedding_engine or not vector_store:
        raise HTTPException(status_code=503, detail="Backend not fully initialized")
    
    try:
        rag = RAGEngine(embedding_engine, vector_store, llm_backend)
        
        # Get user's performance data
        user_history = []
        try:
            query_text = f"{req.platform} {req.niche} {req.content_type}"
            rag_results = rag.retrieve_context(
                user_id=req.user_id,
                query=query_text,
                platform=req.platform,
                content_type=req.content_type,
                top_k=20
            )
            
            # Filter for high performers
            user_history = [
                r for r in rag_results 
                if r.get('performance', {}).get('score', 0) > 0.7
            ][:10]
        except Exception as e:
            logger.warning(f"Could not retrieve user history: {e}")
        
        # Embed both variants
        embed_a = embedding_engine.embed_text(req.variant_a)
        embed_b = embedding_engine.embed_text(req.variant_b)
        
        # Calculate similarity scores
        similarity_a = 0.0
        similarity_b = 0.0
        
        if user_history:
            # Compare embeddings to user's top performers
            for perf in user_history:
                perf_embed = embedding_engine.embed_text(perf.get('content', ''))
                if perf_embed is not None:
                    # Simple cosine similarity (dot product for normalized vectors)
                    sim_a = sum(a * b for a, b in zip(embed_a, perf_embed)) if len(embed_a) == len(perf_embed) else 0
                    sim_b = sum(a * b for a, b in zip(embed_b, perf_embed)) if len(embed_b) == len(perf_embed) else 0
                    similarity_a += sim_a / len(user_history)
                    similarity_b += sim_b / len(user_history)
        else:
            # Default similarity if no history
            similarity_a = 0.5
            similarity_b = 0.5
        
        # Analyze with LLM
        user_prompt = f"""Compare these two variants for a {req.content_type}:

VARIANT A: {req.variant_a}
VARIANT B: {req.variant_b}

CONTEXT:
- Platform: {req.platform}
- Niche: {req.niche}
- Content Type: {req.content_type}

USER'S TOP PERFORMERS:
{chr(10).join(f'- {p.get("content", "")[:100]}...' for p in user_history[:5]) if user_history else 'No past performance data available.'}

SIMILARITY SCORES:
- Variant A similarity to top performers: {similarity_a:.2%}
- Variant B similarity to top performers: {similarity_b:.2%}

TASK: Predict which variant is more likely to perform well.

Analyze:
1. Which is more likely to perform well?
2. Why? (Hook strength, emotional impact, clarity, platform fit)
3. Suggested improvements for the weaker one
4. Score each variant 0-100 based on:
   - Hook strength / attention-grabbing
   - Pattern match with top performers
   - Emotional impact
   - Clarity / simplicity
   - Platform alignment

Provide:
- Winner (A or B)
- Score A: X/100
- Score B: Y/100
- Analysis (why winner wins)
- Improvements for weaker variant

ABSOLUTE PROHIBITION - NO EMOJIS EVER. Use plain text only."""

        messages = [
            {
                "role": "system",
                "content": "You are an expert content analyst who predicts performance based on data patterns. Compare content variants and predict winners. ABSOLUTELY NO EMOJIS - use plain text only."
            },
            {"role": "user", "content": user_prompt}
        ]
        
        # Generate analysis
        analysis_text = ""
        async def stream_response():
            nonlocal analysis_text
            try:
                async for chunk in llm_backend.generate_stream(messages, temperature=0.7):
                    analysis_text += chunk
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                logger.error(f"Generation error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(stream_response(), media_type="text/event-stream")
    
    except Exception as e:
        logger.error(f"Error in A/B test: {e}")
        raise HTTPException(status_code=500, detail=str(e))
