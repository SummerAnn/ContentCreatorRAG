"""
Competitor Analysis Tool API endpoints
Analyze competitor strategies and find content gaps
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import logging
import json

from core.llm_backend import LLMBackend

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analyze", tags=["competitor-analysis"])

# Global instances (injected by main.py)
llm_backend = None

def set_globals(emb, vs, llm):
    global llm_backend
    llm_backend = llm

class CompetitorAnalysisRequest(BaseModel):
    competitor_url: str  # Their TikTok/YouTube profile URL
    competitor_profile_data: Optional[Dict] = None  # Scraped profile data (optional)
    analysis_depth: str = "full"  # "quick" or "full"
    niche: str = "general"
    platform: str = "tiktok"

class GapAnalysisRequest(BaseModel):
    user_id: str = "default_user"
    competitor_ids: List[str]  # Competitor profile URLs or identifiers
    niche: str = "general"
    platform: str = "tiktok"

@router.post("/competitor")
async def analyze_competitor(req: CompetitorAnalysisRequest):
    """
    Analyze a competitor's content strategy
    
    Returns:
    - Top performing videos
    - Common hooks/patterns
    - Posting frequency
    - Content themes
    - What you can learn/adapt
    """
    
    if not llm_backend:
        raise HTTPException(status_code=503, detail="Backend not fully initialized")
    
    try:
        # Use provided competitor data or generate analysis
        competitor_data = req.competitor_profile_data or {
            "videos": [],
            "profile_info": {}
        }
        
        user_prompt = f"""Analyze this competitor's content strategy:

COMPETITOR PROFILE:
URL: {req.competitor_url}
Platform: {req.platform}
Niche: {req.niche}

PROVIDED DATA:
{json.dumps(competitor_data, indent=2) if competitor_data else 'No profile data provided. Generate general analysis based on platform and niche.'}

TASK: Analyze competitor strategy and provide insights.

ANALYSIS AREAS:
1. Content Patterns: What types of content do they create?
2. Hook Patterns: Common hook structures/patterns
3. Posting Schedule: Frequency, best times
4. Content Themes: Main topics/themes
5. Engagement Patterns: What resonates with their audience?
6. Opportunities: What gaps exist? What can you learn?

OUTPUT FORMAT:
Competitor Analysis: {req.competitor_url}

TOP PATTERNS:
- Hook style: [pattern]
- Content types: [types]
- Posting frequency: [frequency]
- Best performing format: [format]

CONTENT THEMES:
1. [Theme 1]
2. [Theme 2]
3. [Theme 3]

HOOK EXAMPLES:
1. [Example hook pattern 1]
2. [Example hook pattern 2]
3. [Example hook pattern 3]

WHAT YOU CAN LEARN:
- [Learning point 1]
- [Learning point 2]
- [Learning point 3]

OPPORTUNITIES TO DIFFERENTIATE:
- [Opportunity 1]
- [Opportunity 2]

RECOMMENDATIONS:
[Strategic recommendations based on analysis]

ABSOLUTELY NO EMOJIS. Use plain text only."""

        messages = [
            {
                "role": "system",
                "content": "You are a competitor analysis expert. Analyze competitor strategies and identify opportunities. ABSOLUTELY NO EMOJIS - plain text only."
            },
            {"role": "user", "content": user_prompt}
        ]
        
        # Generate analysis
        async def stream_response():
            try:
                async for chunk in llm_backend.generate_stream(messages, temperature=0.7):
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                logger.error(f"Generation error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(stream_response(), media_type="text/event-stream")
    
    except Exception as e:
        logger.error(f"Error analyzing competitor: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/gap-analysis")
async def content_gap_analysis(req: GapAnalysisRequest):
    """
    Find content gaps: what competitors cover that you don't
    
    Returns:
    - Topics they cover (you don't)
    - Formats they use (you don't)
    - Opportunities to differentiate
    """
    
    if not llm_backend:
        raise HTTPException(status_code=503, detail="Backend not fully initialized")
    
    try:
        user_prompt = f"""Find content gaps between you and your competitors:

YOUR NICHE: {req.niche}
PLATFORM: {req.platform}
COMPETITORS: {', '.join(req.competitor_ids)}

TASK: Identify content gaps - what competitors are doing that you're not, and opportunities to differentiate.

ANALYSIS:
1. Topics they cover that you don't
2. Formats they use that you don't
3. Hooks/styles they use that you don't
4. Opportunities to fill gaps or differentiate

OUTPUT FORMAT:
Content Gap Analysis

TOPICS THEY COVER (YOU DON'T):
1. [Topic 1] - Opportunity: [Why this matters]
2. [Topic 2] - Opportunity: [Why this matters]

FORMATS THEY USE (YOU DON'T):
1. [Format 1] - Opportunity: [Why this works]
2. [Format 2] - Opportunity: [Why this works]

HOOK PATTERNS YOU'RE MISSING:
1. [Pattern 1]
2. [Pattern 2]

OPPORTUNITIES TO DIFFERENTIATE:
1. [Opportunity 1]
2. [Opportunity 2]

STRATEGIC RECOMMENDATIONS:
[Recommendations for filling gaps or differentiating]

ABSOLUTELY NO EMOJIS. Use plain text only."""

        messages = [
            {
                "role": "system",
                "content": "You are a content gap analysis expert. Identify gaps and opportunities. ABSOLUTELY NO EMOJIS - plain text only."
            },
            {"role": "user", "content": user_prompt}
        ]
        
        # Generate gap analysis
        async def stream_response():
            try:
                async for chunk in llm_backend.generate_stream(messages, temperature=0.7):
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                logger.error(f"Generation error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(stream_response(), media_type="text/event-stream")
    
    except Exception as e:
        logger.error(f"Error in gap analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

