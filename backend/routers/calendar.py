"""
Content Calendar AI API endpoints
Generate strategic content calendars with themed weeks and content mix
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import logging
import json

from core.rag_engine import RAGEngine
from prompts.calendar import build_calendar_prompt

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/calendar", tags=["calendar"])

# Global instances (injected by main.py)
embedding_engine = None
vector_store = None
llm_backend = None

def set_globals(emb, vs, llm):
    global embedding_engine, vector_store, llm_backend
    embedding_engine = emb
    vector_store = vs
    llm_backend = llm

class CalendarRequest(BaseModel):
    user_id: str = "default_user"
    duration_days: int = 30  # 7, 14, 30 days
    frequency: int = 1  # posts per day
    platforms: List[str] = ["tiktok"]
    niche: str
    themes: Optional[List[str]] = None

@router.post("/generate")
async def generate_content_calendar(req: CalendarRequest):
    """
    Generate a strategic content calendar
    
    Returns:
    - Daily content ideas
    - Themed weeks
    - Content mix strategy
    - Best posting times
    """
    
    if not llm_backend or not embedding_engine or not vector_store:
        raise HTTPException(status_code=503, detail="Backend not fully initialized")
    
    try:
        rag = RAGEngine(embedding_engine, vector_store, llm_backend)
        
        # Analyze user's patterns from RAG
        user_patterns = {}
        try:
            query_text = f"{req.niche} content"
            rag_results = rag.retrieve_context(
                user_id=req.user_id,
                query=query_text,
                platform=req.platforms[0] if req.platforms else "tiktok",
                top_k=10
            )
            
            # Analyze patterns from RAG results
            if rag_results:
                content_types = {}
                for result in rag_results:
                    ct = result.get('content_type', 'general')
                    content_types[ct] = content_types.get(ct, 0) + 1
                
                user_patterns = {
                    'top_types': sorted(content_types.items(), key=lambda x: x[1], reverse=True)[:5],
                    'best_days': ['Monday', 'Wednesday', 'Friday'],  # Default, could be enhanced
                    'successful_hooks': [r.get('content', '')[:100] for r in rag_results[:3] if r.get('content')]
                }
        except Exception as e:
            logger.warning(f"Could not analyze user patterns: {e}")
        
            # Generate calendar for primary platform (or combine for multiple)
            primary_platform = req.platforms[0] if req.platforms else "tiktok"
            messages = build_calendar_prompt(
                platform=primary_platform,
                niche=req.niche,
                duration_days=req.duration_days,
                frequency=req.frequency,
                themes=req.themes,
                user_patterns=user_patterns
            )
            
            # Stream response
            async def stream_response():
                try:
                    async for chunk in llm_backend.generate_stream(messages, temperature=0.85):
                        yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                    yield f"data: {json.dumps({'done': True})}\n\n"
                except Exception as e:
                    logger.error(f"Generation error: {e}")
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"
            
            return StreamingResponse(stream_response(), media_type="text/event-stream")
    
    except Exception as e:
        logger.error(f"Error generating calendar: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/{format}")
async def export_calendar(format: str):
    """Export calendar to different formats (CSV, ICS, JSON)"""
    # Implementation for exporting to Google Calendar, Notion, CSV, etc.
    pass

