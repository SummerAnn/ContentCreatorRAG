from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import json
import logging

# Import will be injected at runtime
embedding_engine = None
vector_store = None
llm_backend = None

def set_globals(emb, vs, llm):
    global embedding_engine, vector_store, llm_backend
    embedding_engine = emb
    vector_store = vs
    llm_backend = llm
from core.rag_engine import RAGEngine
from prompts import hooks, scripts, shots, music, titles, descriptions, tags, thumbnails, beatmap, cta, tools

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/generate", tags=["generate"])

class GenerateRequest(BaseModel):
    user_id: str = "default_user"  # For MVP, use default
    platform: str
    niche: str
    goal: str
    personality: str = "friendly"  # friendly, educational, motivational, funny, rage_bait, storytelling, authentic
    audience: List[str] = ["gen_z"]  # List of: gen_z, millennials, gen_x, professionals, students, parents, creators, general, female, male, all
    reference_text: Optional[str] = None
    reference_image: Optional[str] = None
    content_type: str  # "hooks", "script", "shotlist", "music"
    options: dict = {}

@router.post("/hooks")
async def generate_hooks(req: GenerateRequest):
    """Generate viral hooks using RAG + local LLM"""
    
    if not llm_backend or not embedding_engine or not vector_store:
        raise HTTPException(status_code=503, detail="Backend not fully initialized")
    
    try:
        # Initialize RAG engine
        rag = RAGEngine(embedding_engine, vector_store, llm_backend)
        
        # Build query
        query_text = f"{req.platform} {req.niche} {req.goal} {req.reference_text or ''}"
        
        # RAG retrieval
        rag_results = rag.retrieve_context(
            user_id=req.user_id,
            query=query_text,
            platform=req.platform,
            top_k=10
        )
        
        # Build prompt with RAG context
        messages = hooks.build_hook_prompt(
            platform=req.platform,
            niche=req.niche,
            goal=req.goal,
            personality=req.personality,
            audience=req.audience,
            reference=req.reference_text or "No specific reference",
            rag_examples=rag_results
        )
        
        # Generate (streaming)
        async def stream_response():
            try:
                for chunk in llm_backend.generate_stream(messages, temperature=0.95):
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                logger.error(f"Generation error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(stream_response(), media_type="text/event-stream")
    
    except Exception as e:
        logger.error(f"Error generating hooks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/script")
async def generate_script(req: GenerateRequest):
    """Generate full video script"""
    
    if not llm_backend or not embedding_engine or not vector_store:
        raise HTTPException(status_code=503, detail="Backend not fully initialized")
    
    try:
        rag = RAGEngine(embedding_engine, vector_store, llm_backend)
        
        # Get RAG context
        query_text = f"{req.platform} {req.niche} script"
        rag_results = rag.retrieve_context(
            user_id=req.user_id,
            query=query_text,
            platform=req.platform,
            content_type="script",
            top_k=5
        )
        
        # Build prompt
        messages = scripts.build_script_prompt(
            platform=req.platform,
            niche=req.niche,
            duration=req.options.get("duration", 60),
            hook=req.options.get("chosen_hook", ""),
            personality=req.personality,
            audience=req.audience,
            reference=req.reference_text or "",
            rag_examples=rag_results
        )
        
        # Generate
        async def stream_response():
            try:
                for chunk in llm_backend.generate_stream(messages, temperature=0.8):
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                logger.error(f"Generation error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(stream_response(), media_type="text/event-stream")
    
    except Exception as e:
        logger.error(f"Error generating script: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/shotlist")
async def generate_shotlist(req: GenerateRequest):
    """Generate shot list"""
    
    if not llm_backend:
        raise HTTPException(status_code=503, detail="Backend not fully initialized")
    
    try:
        messages = shots.build_shotlist_prompt(
            platform=req.platform,
            duration=req.options.get("duration", 60),
            script=req.options.get("script", ""),
            reference=req.reference_text or ""
        )
        
        async def stream_response():
            try:
                for chunk in llm_backend.generate_stream(messages, temperature=0.7):
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                logger.error(f"Generation error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(stream_response(), media_type="text/event-stream")
    
    except Exception as e:
        logger.error(f"Error generating shotlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/music")
async def generate_music(req: GenerateRequest):
    """Generate music recommendations"""
    
    if not llm_backend:
        raise HTTPException(status_code=503, detail="Backend not fully initialized")
    
    try:
        messages = music.build_music_prompt(
            platform=req.platform,
            niche=req.niche,
            duration=req.options.get("duration", 60),
            script=req.options.get("script", ""),
            reference=req.reference_text or ""
        )
        
        async def stream_response():
            try:
                for chunk in llm_backend.generate_stream(messages, temperature=0.8):
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                logger.error(f"Generation error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(stream_response(), media_type="text/event-stream")
    
    except Exception as e:
        logger.error(f"Error generating music: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/titles")
async def generate_titles(req: GenerateRequest):
    """Generate SEO-optimized titles"""
    
    if not llm_backend or not embedding_engine or not vector_store:
        raise HTTPException(status_code=503, detail="Backend not fully initialized")
    
    try:
        rag = RAGEngine(embedding_engine, vector_store, llm_backend)
        
        query_text = f"{req.platform} {req.niche} title"
        rag_results = rag.retrieve_context(
            user_id=req.user_id,
            query=query_text,
            platform=req.platform,
            content_type="title",
            top_k=5
        )
        
        messages = titles.build_title_prompt(
            platform=req.platform,
            niche=req.niche,
            hook=req.options.get("hook", ""),
            script=req.options.get("script", ""),
            reference=req.reference_text or "",
            rag_examples=rag_results
        )
        
        async def stream_response():
            try:
                for chunk in llm_backend.generate_stream(messages, temperature=0.9):
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                logger.error(f"Generation error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(stream_response(), media_type="text/event-stream")
    
    except Exception as e:
        logger.error(f"Error generating titles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/description")
async def generate_description(req: GenerateRequest):
    """Generate video description"""
    
    if not llm_backend:
        raise HTTPException(status_code=503, detail="Backend not fully initialized")
    
    try:
        messages = descriptions.build_description_prompt(
            platform=req.platform,
            niche=req.niche,
            title=req.options.get("title", ""),
            script=req.options.get("script", ""),
            reference=req.reference_text or ""
        )
        
        async def stream_response():
            try:
                for chunk in llm_backend.generate_stream(messages, temperature=0.8):
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                logger.error(f"Generation error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(stream_response(), media_type="text/event-stream")
    
    except Exception as e:
        logger.error(f"Error generating description: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tags")
async def generate_tags(req: GenerateRequest):
    """Generate tags/hashtags"""
    
    if not llm_backend or not embedding_engine or not vector_store:
        raise HTTPException(status_code=503, detail="Backend not fully initialized")
    
    try:
        rag = RAGEngine(embedding_engine, vector_store, llm_backend)
        
        query_text = f"{req.platform} {req.niche} tags"
        rag_results = rag.retrieve_context(
            user_id=req.user_id,
            query=query_text,
            platform=req.platform,
            top_k=5
        )
        
        messages = tags.build_tags_prompt(
            platform=req.platform,
            niche=req.niche,
            title=req.options.get("title", ""),
            reference=req.reference_text or "",
            rag_examples=rag_results
        )
        
        async def stream_response():
            try:
                for chunk in llm_backend.generate_stream(messages, temperature=0.85):
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                logger.error(f"Generation error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(stream_response(), media_type="text/event-stream")
    
    except Exception as e:
        logger.error(f"Error generating tags: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/thumbnails")
async def generate_thumbnails(req: GenerateRequest):
    """Generate thumbnail concepts"""
    
    if not llm_backend:
        raise HTTPException(status_code=503, detail="Backend not fully initialized")
    
    try:
        messages = thumbnails.build_thumbnail_prompt(
            platform=req.platform,
            niche=req.niche,
            title=req.options.get("title", ""),
            hook=req.options.get("hook", ""),
            reference=req.reference_text or ""
        )
        
        async def stream_response():
            try:
                for chunk in llm_backend.generate_stream(messages, temperature=0.8):
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                logger.error(f"Generation error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(stream_response(), media_type="text/event-stream")
    
    except Exception as e:
        logger.error(f"Error generating thumbnails: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/beatmap")
async def generate_beatmap(req: GenerateRequest):
    """Generate beat map / retention structure"""
    
    if not llm_backend:
        raise HTTPException(status_code=503, detail="Backend not fully initialized")
    
    try:
        messages = beatmap.build_beatmap_prompt(
            platform=req.platform,
            duration=req.options.get("duration", 60),
            script=req.options.get("script", ""),
            hook=req.options.get("hook", "")
        )
        
        async def stream_response():
            try:
                for chunk in llm_backend.generate_stream(messages, temperature=0.7):
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                logger.error(f"Generation error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(stream_response(), media_type="text/event-stream")
    
    except Exception as e:
        logger.error(f"Error generating beatmap: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cta")
async def generate_cta(req: GenerateRequest):
    """Generate call-to-action variations"""
    
    if not llm_backend:
        raise HTTPException(status_code=503, detail="Backend not fully initialized")
    
    try:
        messages = cta.build_cta_prompt(
            platform=req.platform,
            niche=req.niche,
            script=req.options.get("script", ""),
            tone=req.options.get("tone", "conversational")
        )
        
        async def stream_response():
            try:
                for chunk in llm_backend.generate_stream(messages, temperature=0.85):
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                logger.error(f"Generation error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(stream_response(), media_type="text/event-stream")
    
    except Exception as e:
        logger.error(f"Error generating CTA: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tools")
async def generate_tools(req: GenerateRequest):
    """Recommend tools based on platform, niche, and content type"""
    
    if not llm_backend:
        raise HTTPException(status_code=503, detail="Backend not fully initialized")
    
    try:
        # Get content type from options or infer from last generated content
        content_type = req.options.get("content_type", "general")
        
        # Get RAG context for similar past content (optional)
        rag_examples = []
        if embedding_engine and vector_store:
            try:
                rag = RAGEngine(embedding_engine, vector_store, llm_backend)
                rag_examples = rag.retrieve_context(
                    user_id=req.user_id,
                    query=req.reference_text or f"{req.platform} {req.niche} content",
                    platform=req.platform,
                    top_k=5
                )
            except Exception as e:
                logger.warning(f"RAG retrieval failed for tools: {e}")
        
        messages = tools.build_tools_prompt(
            platform=req.platform,
            niche=req.niche,
            goal=req.goal,
            personality=req.personality,
            audience=req.audience,
            reference=req.reference_text or "",
            content_type=content_type
        )
        
        async def stream_response():
            try:
                for chunk in llm_backend.generate_stream(messages, temperature=0.7):
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                logger.error(f"Generation error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(stream_response(), media_type="text/event-stream")
    
    except Exception as e:
        logger.error(f"Error generating tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))

