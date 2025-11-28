from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum

router = APIRouter(prefix="/api/autopilot", tags=["autopilot"])
logger = logging.getLogger(__name__)

# Global dependencies
_llm_backend = None
_db = None

def set_globals(embedding_engine, vector_store, llm_backend, db=None):
    global _llm_backend, _db
    _llm_backend = llm_backend
    _db = db

class AutopilotStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"

class ContentGoal(str, Enum):
    DAILY = "daily"  # 1 post/day
    FREQUENT = "frequent"  # 3 posts/week
    WEEKLY = "weekly"  # 1 post/week

class AutopilotConfig(BaseModel):
    user_id: str
    status: AutopilotStatus
    content_goal: ContentGoal
    platforms: List[str]
    niches: List[str]
    post_times: List[str]  # ["09:00", "15:00", "20:00"]
    auto_approve: bool = False
    notification_enabled: bool = True

class GeneratedContent(BaseModel):
    id: str
    date: str
    platform: str
    niche: str
    hook: str
    script: str
    status: str  # "pending", "approved", "rejected"
    viral_score: float
    created_at: str

# In-memory storage (replace with DB in production)
_autopilot_configs: Dict[str, AutopilotConfig] = {}
_content_queue: Dict[str, List[GeneratedContent]] = {}

@router.post("/setup")
async def setup_autopilot(config: AutopilotConfig):
    """
    Setup autopilot configuration for a user
    """
    
    if not _llm_backend:
        raise HTTPException(status_code=503, detail="LLM not available")
    
    # Validate config
    if config.content_goal == ContentGoal.DAILY and len(config.platforms) > 3:
        raise HTTPException(
            status_code=400, 
            detail="Daily goal limited to 3 platforms max"
        )
    
    # Store config
    _autopilot_configs[config.user_id] = config
    
    # Initialize content queue if needed
    if config.user_id not in _content_queue:
        _content_queue[config.user_id] = []
    
    # Generate initial content
    await generate_autopilot_content(config.user_id)
    
    return {
        "message": "Autopilot configured successfully",
        "config": config,
        "next_generation": "Tomorrow at 06:00 AM"
    }

@router.get("/config/{user_id}")
async def get_autopilot_config(user_id: str):
    """
    Get autopilot configuration for a user
    """
    config = _autopilot_configs.get(user_id)
    if not config:
        raise HTTPException(status_code=404, detail="Autopilot not configured")
    
    return config

@router.post("/toggle/{user_id}")
async def toggle_autopilot(user_id: str, status: AutopilotStatus):
    """
    Toggle autopilot on/off
    """
    config = _autopilot_configs.get(user_id)
    if not config:
        raise HTTPException(status_code=404, detail="Autopilot not configured")
    
    config.status = status
    _autopilot_configs[user_id] = config
    
    return {
        "message": f"Autopilot {status.value}",
        "config": config
    }

@router.get("/queue/{user_id}")
async def get_content_queue(user_id: str, limit: int = 10):
    """
    Get pending content in user's queue
    """
    queue = _content_queue.get(user_id, [])
    
    # Filter by status
    pending = [c for c in queue if c.status == "pending"]
    approved = [c for c in queue if c.status == "approved"]
    
    return {
        "pending": pending[:limit],
        "approved": approved[:limit],
        "total_pending": len(pending),
        "total_approved": len(approved)
    }

@router.post("/approve/{content_id}")
async def approve_content(user_id: str, content_id: str):
    """
    Approve generated content
    """
    queue = _content_queue.get(user_id, [])
    
    for content in queue:
        if content.id == content_id:
            content.status = "approved"
            return {"message": "Content approved", "content": content}
    
    raise HTTPException(status_code=404, detail="Content not found")

@router.post("/reject/{content_id}")
async def reject_content(user_id: str, content_id: str):
    """
    Reject generated content
    """
    queue = _content_queue.get(user_id, [])
    
    for content in queue:
        if content.id == content_id:
            content.status = "rejected"
            return {"message": "Content rejected"}
    
    raise HTTPException(status_code=404, detail="Content not found")

@router.post("/regenerate/{content_id}")
async def regenerate_content(user_id: str, content_id: str):
    """
    Regenerate specific content
    """
    queue = _content_queue.get(user_id, [])
    config = _autopilot_configs.get(user_id)
    
    if not config:
        raise HTTPException(status_code=404, detail="Autopilot not configured")
    
    # Find original content
    original = None
    for content in queue:
        if content.id == content_id:
            original = content
            break
    
    if not original:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Generate new version
    new_content = await generate_single_content(
        platform=original.platform,
        niche=original.niche,
        user_id=user_id
    )
    
    # Replace in queue
    for i, content in enumerate(queue):
        if content.id == content_id:
            queue[i] = new_content
            break
    
    _content_queue[user_id] = queue
    
    return {
        "message": "Content regenerated",
        "content": new_content
    }

async def generate_autopilot_content(user_id: str):
    """
    Generate content based on autopilot config
    """
    config = _autopilot_configs.get(user_id)
    if not config or config.status != AutopilotStatus.ACTIVE:
        return
    
    # Determine how many pieces to generate
    posts_per_week = {
        ContentGoal.DAILY: 7,
        ContentGoal.FREQUENT: 3,
        ContentGoal.WEEKLY: 1
    }
    
    num_posts = posts_per_week[config.content_goal]
    
    # Generate content for next week
    queue = _content_queue.get(user_id, [])
    
    for i in range(num_posts):
        for platform in config.platforms:
            for niche in config.niches:
                content = await generate_single_content(platform, niche, user_id)
                queue.append(content)
    
    _content_queue[user_id] = queue
    
    logger.info(f"Generated {len(queue)} content pieces for user {user_id}")

async def generate_single_content(platform: str, niche: str, user_id: str) -> GeneratedContent:
    """
    Generate a single piece of content
    """
    
    # Get trending topic
    topic_prompt = f"""Generate 1 trending content idea for {platform} in the {niche} niche.

Output ONLY the idea (max 15 words):"""

    topic = _llm_backend.generate([
        {"role": "user", "content": topic_prompt}
    ], temperature=0.9, max_tokens=50).strip()

    # Generate hook
    hook_prompt = f"""Generate a viral hook for {platform} about: {topic}

Niche: {niche}
Make it attention-grabbing in 3 seconds.

Output ONLY the hook (max 12 words):"""

    hook = _llm_backend.generate([
        {"role": "user", "content": hook_prompt}
    ], temperature=0.9, max_tokens=50).strip()

    # Generate script
    script_prompt = f"""Write a 30-second script for {platform} using this hook:
"{hook}"

Topic: {topic}
Niche: {niche}

Keep it concise and conversational."""

    script = _llm_backend.generate([
        {"role": "user", "content": script_prompt}
    ], temperature=0.8, max_tokens=200).strip()

    # Calculate viral score (simplified)
    viral_score = calculate_viral_score(hook, platform, niche)
    
    return GeneratedContent(
        id=f"content_{datetime.now().timestamp()}",
        date=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        platform=platform,
        niche=niche,
        hook=hook,
        script=script,
        status="pending",
        viral_score=viral_score,
        created_at=datetime.now().isoformat()
    )

def calculate_viral_score(hook: str, platform: str, niche: str) -> float:
    """
    Simple viral score calculation
    """
    import random
    
    score = 50.0
    
    # Hook length
    if len(hook.split()) <= 12:
        score += 10
    
    # Platform-specific patterns
    if platform.lower() == "tiktok" and hook.lower().startswith("pov"):
        score += 15
    
    # Randomize a bit
    score += random.uniform(-5, 15)
    
    return min(100, max(0, score))

# Background task to run daily
async def autopilot_daily_task():
    """
    Daily task to generate content for all active autopilots
    """
    while True:
        # Run at 6 AM
        now = datetime.now()
        target = now.replace(hour=6, minute=0, second=0, microsecond=0)
        if now > target:
            target += timedelta(days=1)
        
        wait_seconds = (target - now).total_seconds()
        await asyncio.sleep(wait_seconds)
        
        # Generate content for all active users
        for user_id, config in _autopilot_configs.items():
            if config.status == AutopilotStatus.ACTIVE:
                await generate_autopilot_content(user_id)
                logger.info(f"Autopilot generated content for user {user_id}")

