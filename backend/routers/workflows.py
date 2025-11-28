from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging

router = APIRouter(prefix="/api/workflows", tags=["workflows"])
logger = logging.getLogger(__name__)

# Global dependencies
_llm_backend = None

def set_globals(embedding_engine, vector_store, llm_backend):
    global _llm_backend
    _llm_backend = llm_backend

class WorkflowRequest(BaseModel):
    workflow_type: str  # "quick_viral", "weekly_batch", "competitor_steal", "emergency_post"
    user_id: str
    niche: str
    platform: str
    additional_params: Optional[Dict] = None

class WorkflowResult(BaseModel):
    workflow_type: str
    status: str
    content: Dict
    time_saved: str  # "30 seconds", "5 minutes"
    next_steps: List[str]

@router.post("/execute")
async def execute_workflow(request: WorkflowRequest):
    """
    Execute one-click workflows for common tasks
    """
    
    if not _llm_backend:
        raise HTTPException(status_code=503, detail="LLM not available")
    
    try:
        if request.workflow_type == "quick_viral":
            result = await workflow_quick_viral(request)
        elif request.workflow_type == "weekly_batch":
            result = await workflow_weekly_batch(request)
        elif request.workflow_type == "competitor_steal":
            result = await workflow_competitor_steal(request)
        elif request.workflow_type == "emergency_post":
            result = await workflow_emergency_post(request)
        else:
            raise HTTPException(status_code=400, detail="Unknown workflow type")
        
        return result
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def workflow_quick_viral(request: WorkflowRequest) -> WorkflowResult:
    """
    Quick Viral Video Workflow (30 seconds)
    → Analyze trending topic
    → Generate hook
    → Create script
    → Make shot list
    """
    
    # Step 1: Get trending topic
    trending_prompt = f"""Find the #1 trending topic in the {request.niche} niche on {request.platform} RIGHT NOW.

Output ONLY the topic name (max 10 words):"""

    trending_topic = _llm_backend.generate([
        {"role": "user", "content": trending_prompt}
    ], temperature=0.7).strip()

    # Step 2: Generate hook
    hook_prompt = f"""Generate 3 viral hooks for a {request.platform} video about: {trending_topic}

Niche: {request.niche}
Platform: {request.platform}

Make them:
- Attention-grabbing in first 3 seconds
- Under 15 words
- Use proven viral patterns (POV, listicle, question)

Output format:
1. [hook]
2. [hook]
3. [hook]"""

    hooks = _llm_backend.generate([
        {"role": "user", "content": hook_prompt}
    ], temperature=0.9)

    # Step 3: Generate script
    best_hook = hooks.split('\n')[0].split('. ', 1)[1] if '. ' in hooks.split('\n')[0] else hooks.split('\n')[0]
    
    script_prompt = f"""Write a 30-second script for {request.platform} based on this hook:
"{best_hook}"

Topic: {trending_topic}
Niche: {request.niche}

Include:
- Opening (3 sec)
- Main content (20 sec)
- CTA (7 sec)

Make it conversational and engaging."""

    script = _llm_backend.generate([
        {"role": "user", "content": script_prompt}
    ], temperature=0.8)

    # Step 4: Generate shot list
    shot_list_prompt = f"""Create a simple 5-shot list for this video:

Script: {script[:200]}...

Format:
Shot 1: [description]
Shot 2: [description]
...

Keep it simple and filmable with a phone."""

    shot_list = _llm_backend.generate([
        {"role": "user", "content": shot_list_prompt}
    ], temperature=0.7)

    return WorkflowResult(
        workflow_type="quick_viral",
        status="complete",
        content={
            "trending_topic": trending_topic,
            "hooks": hooks,
            "best_hook": best_hook,
            "script": script,
            "shot_list": shot_list,
        },
        time_saved="30 seconds",
        next_steps=[
            "Review and customize content",
            "Film using shot list",
            "Edit and post"
        ]
    )

async def workflow_weekly_batch(request: WorkflowRequest) -> WorkflowResult:
    """
    Weekly Content Batch Workflow (5 minutes)
    → Generate 7 days of content
    → Schedule posts
    → Export calendar
    """
    
    prompt = f"""Create 7 days of content ideas for {request.niche} on {request.platform}.

For each day, provide:
- Content idea (one sentence)
- Hook suggestion
- Best posting time

Day 1 (Monday):
Day 2 (Tuesday):
...
Day 7 (Sunday):

Make content varied and strategic."""

    weekly_content = _llm_backend.generate([
        {"role": "user", "content": prompt}
    ], temperature=0.8)

    return WorkflowResult(
        workflow_type="weekly_batch",
        status="complete",
        content={
            "weekly_plan": weekly_content,
            "calendar_format": "7 days of content ready",
        },
        time_saved="5 minutes",
        next_steps=[
            "Review content calendar",
            "Batch create content",
            "Schedule posts"
        ]
    )

async def workflow_competitor_steal(request: WorkflowRequest) -> WorkflowResult:
    """
    Competitor Steal Workflow (2 minutes)
    → Analyze competitor's viral video
    → Get remix suggestions
    → Generate your version
    """
    
    competitor_url = request.additional_params.get("competitor_url") if request.additional_params else None
    
    if not competitor_url:
        return WorkflowResult(
            workflow_type="competitor_steal",
            status="error",
            content={"error": "competitor_url required in additional_params"},
            time_saved="0",
            next_steps=["Provide competitor video URL"]
        )
    
    # Use existing viral_analyzer
    analysis_prompt = f"""Analyze this concept and create a remix:

Original idea: {competitor_url}
Your niche: {request.niche}

Provide:
1. Why it went viral
2. Your unique angle
3. Hook for your version
4. Script outline"""

    remix = _llm_backend.generate([
        {"role": "user", "content": analysis_prompt}
    ], temperature=0.9)

    return WorkflowResult(
        workflow_type="competitor_steal",
        status="complete",
        content={
            "analysis": remix,
            "original_url": competitor_url,
        },
        time_saved="2 minutes",
        next_steps=[
            "Customize your angle",
            "Create content",
            "Post and track"
        ]
    )

async def workflow_emergency_post(request: WorkflowRequest) -> WorkflowResult:
    """
    Emergency Post Workflow (60 seconds)
    → Trending topic + quick hook + script
    → Ready to record immediately
    """
    
    prompt = f"""I need to post RIGHT NOW on {request.platform}.

Niche: {request.niche}

Give me:
1. Hottest trending topic (NOW)
2. Viral hook (under 10 words)
3. 15-second script

Make it FAST and VIRAL. Output only the essentials."""

    emergency_content = _llm_backend.generate([
        {"role": "user", "content": prompt}
    ], temperature=1.0, max_tokens=200)

    return WorkflowResult(
        workflow_type="emergency_post",
        status="complete",
        content={
            "emergency_content": emergency_content,
        },
        time_saved="60 seconds",
        next_steps=[
            "Record immediately",
            "Quick edit",
            "Post now"
        ]
    )

@router.get("/list")
async def list_workflows():
    """List all available workflows"""
    return {
        "workflows": [
            {
                "id": "quick_viral",
                "name": "Quick Viral Video",
                "description": "Trending topic → Hook → Script → Shot list in 30 seconds",
                "time": "30 seconds",
                "icon": "⚡"
            },
            {
                "id": "weekly_batch",
                "name": "Weekly Content Batch",
                "description": "Generate 7 days of content ideas and schedule",
                "time": "5 minutes",
                "icon": "📅"
            },
            {
                "id": "competitor_steal",
                "name": "Competitor Steal",
                "description": "Analyze competitor → Get remix → Your version",
                "time": "2 minutes",
                "icon": "🎯"
            },
            {
                "id": "emergency_post",
                "name": "Emergency Post",
                "description": "Trending topic + hook + script in 60 seconds",
                "time": "60 seconds",
                "icon": "🚨"
            }
        ]
    }

