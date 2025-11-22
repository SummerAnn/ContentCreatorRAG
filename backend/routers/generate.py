from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import json
import logging
import asyncio
from pathlib import Path
import errno

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
from core.trends import trend_service
from prompts import hooks, scripts, shots, music, titles, descriptions, tags, thumbnails, beatmap, cta, tools
from prompts import strategic_tags

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/generate", tags=["generate"])

# Agent file path (shared with agents.py)
AGENTS_FILE = "data/agents.json"

def load_agent(agent_id: str) -> Optional[Dict]:
    """Load a specific agent by ID"""
    if not Path(AGENTS_FILE).exists():
        return None
    try:
        with open(AGENTS_FILE, 'r') as f:
            agents = json.load(f)
            return next((a for a in agents if a.get('id') == agent_id), None)
    except Exception as e:
        logger.error(f"Error loading agent {agent_id}: {e}")
        return None

def get_agent_for_content_type(content_type: str, agent_id: Optional[str] = None) -> Optional[Dict]:
    """
    Get agent for content generation.
    If agent_id provided, load that agent.
    Otherwise, tries to find an agent matching the content type.
    """
    if not agent_id:
        return None
    
    agent = load_agent(agent_id)
    if not agent:
        logger.warning(f"Agent {agent_id} not found")
        return None
    
    # Map content types to agent capabilities
    content_type_to_capabilities = {
        "hooks": ["hook_creation", "pattern_interrupts", "psychology_application"],
        "script": ["script_writing", "retention_optimization", "visual_direction", "pacing"],
        "shotlist": ["visual_direction", "pacing"],
        "music": [],  # No specific agent for music
        "titles": ["seo_optimization", "keyword_strategy"],
        "description": ["caption_writing", "copy_optimization", "engagement_writing"],
        "tags": ["hashtag_research", "seo_optimization", "keyword_strategy", "discoverability"],
        "thumbnails": ["thumbnail_design", "ctr_optimization", "visual_strategy"],
        "beatmap": ["retention_optimization", "pacing"],
        "cta": ["cta_creation", "copy_optimization", "engagement_writing"],
        "tools": []  # No specific agent for tools
    }
    
    # Check if agent has relevant capabilities (optional validation)
    required_caps = content_type_to_capabilities.get(content_type, [])
    agent_caps = agent.get("capabilities", [])
    
    # If agent has no matching capabilities but was explicitly requested, still use it
    if required_caps and not any(cap in agent_caps for cap in required_caps):
        logger.info(f"Agent {agent_id} capabilities don't match {content_type}, but using it anyway")
    
    return agent

def apply_agent_to_messages(
    messages: List[Dict],
    agent: Optional[Dict],
    default_system_prompt: str,
    default_temperature: float = 0.8
) -> tuple[List[Dict], float]:
    """
    Apply agent's system prompt and temperature to messages.
    Returns (updated_messages, temperature)
    """
    system_prompt = default_system_prompt
    temperature = default_temperature
    
    if agent:
        agent_system_prompt = agent.get("system_prompt")
        if agent_system_prompt:
            system_prompt = agent_system_prompt
            logger.info(f"Using agent '{agent.get('name')}' system prompt")
        temperature = agent.get("temperature", default_temperature)
    
    # Replace system prompt in messages
    updated_messages = [
        {"role": "system", "content": system_prompt},
        messages[1] if len(messages) > 1 else {"role": "user", "content": ""}
    ]
    
    return updated_messages, temperature

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
    agent_id: Optional[str] = None  # NEW: Agent to use for generation

@router.post("/hooks")
async def generate_hooks(req: GenerateRequest):
    """Generate viral hooks using RAG + local LLM"""
    
    if not llm_backend or not embedding_engine or not vector_store:
        raise HTTPException(status_code=503, detail="Backend not fully initialized")
    
    try:
        # Generate (streaming) - start immediately with progress updates
        async def stream_response():
            try:
                # Send initial status IMMEDIATELY
                yield f"data: {json.dumps({'status': 'starting', 'message': 'Initializing...'})}\n\n"
                
                # Initialize RAG engine (non-blocking)
                rag = RAGEngine(embedding_engine, vector_store, llm_backend)
                
                # Build query
                query_text = f"{req.platform} {req.niche} {req.goal} {req.reference_text or ''}"
                
                yield f"data: {json.dumps({'status': 'retrieving', 'message': 'Finding relevant examples...'})}\n\n"
                
                # RAG retrieval - limit to 3 for speed, timeout quickly
                rag_results = []
                try:
                    rag_results = await asyncio.wait_for(
                        asyncio.to_thread(
                            rag.retrieve_context,
                            user_id=req.user_id,
                            query=query_text,
                            platform=req.platform,
                            top_k=3  # Reduced for speed
                        ),
                        timeout=3.0  # 3 second max for RAG
                    )
                except asyncio.TimeoutError:
                    logger.warning("RAG retrieval timed out, continuing without RAG")
                    rag_results = []
                except Exception as e:
                    logger.warning(f"RAG retrieval failed: {e}, continuing without RAG")
                    rag_results = []
                
                yield f"data: {json.dumps({'status': 'trends', 'message': 'Checking trends...'})}\n\n"
                
                # Get trending topics (skip if taking too long - use cache only or skip entirely)
                trends_text = ""
                try:
                    # Try to get trends, but timeout quickly if Reddit is slow
                    trends = await asyncio.wait_for(
                        asyncio.to_thread(
                            trend_service.get_trends,
                            platform=req.platform,
                            niche=req.niche,
                            use_cache=True
                        ),
                        timeout=2.0  # 2 second max for trends
                    )
                    trends_text = trend_service.format_trends_for_prompt(trends, max_count=3)
                except asyncio.TimeoutError:
                    logger.warning("Trend fetching timed out, continuing without trends")
                    trends_text = ""
                except Exception as e:
                    logger.warning(f"Trend fetching failed: {e}, continuing without trends")
                    trends_text = ""
                
                yield f"data: {json.dumps({'status': 'generating', 'message': 'Generating hooks with AI...'})}\n\n"
                
                # Load agent if provided
                agent = get_agent_for_content_type("hooks", req.agent_id)
                system_prompt = hooks.HOOK_SYSTEM_PROMPT  # Default generic prompt
                temperature = 0.95  # Default temperature
                max_tokens = None  # Use default
                
                if agent:
                    agent_system_prompt = agent.get("system_prompt")
                    if agent_system_prompt:
                        system_prompt = agent_system_prompt
                        logger.info(f"Using agent '{agent.get('name')}' system prompt for hooks generation")
                    temperature = agent.get("temperature", 0.95)
                    max_tokens = agent.get("max_tokens")
                    agent_name = agent.get("name", "agent")
                    yield f"data: {json.dumps({'status': 'agent', 'message': f'Using {agent_name} agent...'})}\n\n"
                
                # Build prompt with RAG context and trends
                base_messages = hooks.build_hook_prompt(
                    platform=req.platform,
                    niche=req.niche,
                    goal=req.goal,
                    personality=req.personality,
                    audience=req.audience,
                    reference=req.reference_text or "No specific reference",
                    rag_examples=rag_results,
                    trends=trends_text
                )
                
                # Replace system prompt with agent's prompt if available
                messages = [
                    {"role": "system", "content": system_prompt},
                    base_messages[1] if len(base_messages) > 1 else {"role": "user", "content": ""}
                ]
                
                # Generate with streaming
                for chunk in llm_backend.generate_stream(messages, temperature=temperature):
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
        async def stream_response():
            try:
                yield f"data: {json.dumps({'status': 'starting', 'message': 'Initializing script generation...'})}\n\n"
                
                rag = RAGEngine(embedding_engine, vector_store, llm_backend)
                
                # Get RAG context (fast, limited results)
                yield f"data: {json.dumps({'status': 'retrieving', 'message': 'Finding relevant scripts...'})}\n\n"
                
                try:
                    query_text = f"{req.platform} {req.niche} script"
                    rag_results = rag.retrieve_context(
                        user_id=req.user_id,
                        query=query_text,
                        platform=req.platform,
                        content_type="script",
                        top_k=3  # Reduced for speed
                    )
                except Exception as e:
                    logger.warning(f"RAG retrieval failed: {e}")
                    rag_results = []
                
                yield f"data: {json.dumps({'status': 'generating', 'message': 'Generating script with AI...'})}\n\n"
                
                # Load agent if provided
                agent = get_agent_for_content_type("script", req.agent_id)
                system_prompt = scripts.SCRIPT_SYSTEM_PROMPT
                temperature = 0.8
                
                if agent:
                    agent_system_prompt = agent.get("system_prompt")
                    if agent_system_prompt:
                        system_prompt = agent_system_prompt
                        logger.info(f"Using agent '{agent.get('name')}' system prompt for script generation")
                    temperature = agent.get("temperature", 0.8)
                    agent_name = agent.get("name", "agent")
                    yield f"data: {json.dumps({'status': 'agent', 'message': f'Using {agent_name} agent...'})}\n\n"
                
                # Build prompt
                has_voiceover = req.options.get("has_voiceover", True)
                base_messages = scripts.build_script_prompt(
                    platform=req.platform,
                    niche=req.niche,
                    duration=req.options.get("duration", 60),
                    hook=req.options.get("chosen_hook", ""),
                    personality=req.personality,
                    audience=req.audience,
                    reference=req.reference_text or "",
                    rag_examples=rag_results,
                    has_voiceover=has_voiceover
                )
                
                # Replace system prompt with agent's prompt if available
                messages = [
                    {"role": "system", "content": system_prompt},
                    base_messages[1] if len(base_messages) > 1 else {"role": "user", "content": ""}
                ]
                
                # Generate with error handling for broken pipes
                try:
                    for chunk in llm_backend.generate_stream(messages, temperature=temperature):
                        try:
                            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                        except (BrokenPipeError, ConnectionError, OSError) as e:
                            logger.warning(f"Client disconnected during streaming: {e}")
                            break
                    yield f"data: {json.dumps({'done': True})}\n\n"
                except (BrokenPipeError, ConnectionError, OSError) as e:
                    logger.warning(f"Connection broken during generation: {e}")
                    return
                except Exception as e:
                    logger.error(f"Generation error: {e}")
                    try:
                        yield f"data: {json.dumps({'error': str(e)})}\n\n"
                    except (BrokenPipeError, ConnectionError, OSError):
                        pass
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
        
        # Load agent if provided
        agent = get_agent_for_content_type("titles", req.agent_id)
        base_messages = titles.build_title_prompt(
            platform=req.platform,
            niche=req.niche,
            hook=req.options.get("hook", ""),
            script=req.options.get("script", ""),
            reference=req.reference_text or "",
            rag_examples=rag_results
        )
        
        messages, temperature = apply_agent_to_messages(
            base_messages,
            agent,
            titles.TITLE_SYSTEM_PROMPT,
            default_temperature=0.9
        )
        
        async def stream_response():
            try:
                if agent:
                    agent_name = agent.get("name", "agent")
                    yield f"data: {json.dumps({'status': 'agent', 'message': f'Using {agent_name} agent...'})}\n\n"
                for chunk in llm_backend.generate_stream(messages, temperature=temperature):
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
        # Load agent if provided
        agent = get_agent_for_content_type("description", req.agent_id)
        base_messages = descriptions.build_description_prompt(
            platform=req.platform,
            niche=req.niche,
            title=req.options.get("title", ""),
            script=req.options.get("script", ""),
            reference=req.reference_text or ""
        )
        
        messages, temperature = apply_agent_to_messages(
            base_messages,
            agent,
            descriptions.DESCRIPTION_SYSTEM_PROMPT,
            default_temperature=0.8
        )
        
        async def stream_response():
            try:
                if agent:
                    agent_name = agent.get("name", "agent")
                    yield f"data: {json.dumps({'status': 'agent', 'message': f'Using {agent_name} agent...'})}\n\n"
                for chunk in llm_backend.generate_stream(messages, temperature=temperature):
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
        
        # Load agent if provided
        agent = get_agent_for_content_type("tags", req.agent_id)
        
        # Use strategic tags if requested, otherwise basic tags
        use_strategic = req.options.get("strategic", True)
        
        if use_strategic:
            base_messages = strategic_tags.build_strategic_tags_prompt(
                platform=req.platform,
                niche=req.niche,
                title=req.options.get("title", ""),
                reference=req.reference_text or "",
                goal=req.goal,
                rag_examples=rag_results
            )
            default_system_prompt = strategic_tags.STRATEGIC_TAGS_SYSTEM_PROMPT if hasattr(strategic_tags, 'STRATEGIC_TAGS_SYSTEM_PROMPT') else tags.TAGS_SYSTEM_PROMPT
        else:
            base_messages = tags.build_tags_prompt(
                platform=req.platform,
                niche=req.niche,
                title=req.options.get("title", ""),
                reference=req.reference_text or "",
                rag_examples=rag_results
            )
            default_system_prompt = tags.TAGS_SYSTEM_PROMPT
        
        messages, temperature = apply_agent_to_messages(
            base_messages,
            agent,
            default_system_prompt,
            default_temperature=0.85
        )
        
        async def stream_response():
            try:
                if agent:
                    agent_name = agent.get("name", "agent")
                    yield f"data: {json.dumps({'status': 'agent', 'message': f'Using {agent_name} agent...'})}\n\n"
                for chunk in llm_backend.generate_stream(messages, temperature=temperature):
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
        # Load agent if provided
        agent = get_agent_for_content_type("thumbnails", req.agent_id)
        base_messages = thumbnails.build_thumbnail_prompt(
            platform=req.platform,
            niche=req.niche,
            title=req.options.get("title", ""),
            hook=req.options.get("hook", ""),
            reference=req.reference_text or ""
        )
        
        messages, temperature = apply_agent_to_messages(
            base_messages,
            agent,
            thumbnails.THUMBNAIL_SYSTEM_PROMPT,
            default_temperature=0.8
        )
        
        async def stream_response():
            try:
                if agent:
                    agent_name = agent.get("name", "agent")
                    yield f"data: {json.dumps({'status': 'agent', 'message': f'Using {agent_name} agent...'})}\n\n"
                for chunk in llm_backend.generate_stream(messages, temperature=temperature):
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
        # Load agent if provided
        agent = get_agent_for_content_type("beatmap", req.agent_id)
        base_messages = beatmap.build_beatmap_prompt(
            platform=req.platform,
            duration=req.options.get("duration", 60),
            script=req.options.get("script", ""),
            hook=req.options.get("hook", "")
        )
        
        messages, temperature = apply_agent_to_messages(
            base_messages,
            agent,
            beatmap.BEATMAP_SYSTEM_PROMPT,
            default_temperature=0.7
        )
        
        async def stream_response():
            try:
                if agent:
                    agent_name = agent.get("name", "agent")
                    yield f"data: {json.dumps({'status': 'agent', 'message': f'Using {agent_name} agent...'})}\n\n"
                for chunk in llm_backend.generate_stream(messages, temperature=temperature):
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
        # Load agent if provided
        agent = get_agent_for_content_type("cta", req.agent_id)
        base_messages = cta.build_cta_prompt(
            platform=req.platform,
            niche=req.niche,
            script=req.options.get("script", ""),
            tone=req.options.get("tone", "conversational")
        )
        
        messages, temperature = apply_agent_to_messages(
            base_messages,
            agent,
            cta.CTA_SYSTEM_PROMPT,
            default_temperature=0.85
        )
        
        async def stream_response():
            try:
                if agent:
                    agent_name = agent.get("name", "agent")
                    yield f"data: {json.dumps({'status': 'agent', 'message': f'Using {agent_name} agent...'})}\n\n"
                for chunk in llm_backend.generate_stream(messages, temperature=temperature):
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
        async def stream_response():
            try:
                # Send initial status IMMEDIATELY
                yield f"data: {json.dumps({'status': 'starting', 'message': 'Finding tools...'})}\n\n"
                
                # Get content type from options or infer from last generated content
                content_type = req.options.get("content_type", "general")
                
                # Get RAG context (quick, optional)
                rag_examples = []
                if embedding_engine and vector_store:
                    try:
                        rag = RAGEngine(embedding_engine, vector_store, llm_backend)
                        rag_examples = rag.retrieve_context(
                            user_id=req.user_id,
                            query=req.reference_text or f"{req.platform} {req.niche} content",
                            platform=req.platform,
                            top_k=3  # Reduced for speed
                        )
                    except Exception as e:
                        logger.warning(f"RAG retrieval failed for tools: {e}")
                
                yield f"data: {json.dumps({'status': 'generating', 'message': 'Generating tool recommendations...'})}\n\n"
                
                messages = tools.build_tools_prompt(
                    platform=req.platform,
                    niche=req.niche,
                    goal=req.goal,
                    personality=req.personality,
                    audience=req.audience,
                    reference=req.reference_text or "",
                    content_type=content_type
                )
                
                # Generate with streaming
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

