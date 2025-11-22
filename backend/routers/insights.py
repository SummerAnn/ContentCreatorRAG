"""
Search Insights Integration API endpoints
Show trending searches and content opportunities
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import logging
import json

from core.llm_backend import LLMBackend

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/insights", tags=["insights"])

# Global instances (injected by main.py)
llm_backend = None

def set_globals(emb, vs, llm):
    global llm_backend
    llm_backend = llm

class SearchInsightsRequest(BaseModel):
    niche: str
    platform: str = "tiktok"
    region: str = "US"
    timeframe: str = "now 7-d"  # last 7 days

class TrendingTopic(BaseModel):
    topic: str
    search_volume: str  # "rising", "high", "medium"
    content_ideas: List[str]
    hashtag_suggestions: List[str]
    viral_potential: int  # 0-100

class SearchInsightsResponse(BaseModel):
    niche: str
    trending_searches: List[str]
    rising_topics: List[TrendingTopic]
    content_opportunities: List[Dict]
    seasonal_relevance: Optional[str]
    recommended_posting_times: List[str]

def get_current_season() -> str:
    """Get current season"""
    month = datetime.now().month
    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    else:
        return "fall"

def analyze_seasonal_relevance(niche: str) -> str:
    """Determine if there's seasonal relevance"""
    current_month = datetime.now().strftime("%B")
    current_season = get_current_season()
    
    seasonal_niches = {
        "winter": ["skiing", "winter fashion", "holiday", "cozy", "soup recipes"],
        "spring": ["gardening", "spring cleaning", "allergies", "easter", "outdoor"],
        "summer": ["beach", "bbq", "vacation", "swimming", "outdoor sports"],
        "fall": ["pumpkin", "halloween", "thanksgiving", "sweater weather", "back to school"]
    }
    
    for season, keywords in seasonal_niches.items():
        if any(keyword in niche.lower() for keyword in keywords):
            if season == current_season:
                return f"PEAK SEASON: {current_month} is prime time for {niche} content"
            else:
                return f"OFF-SEASON: Consider pivoting or planning for {season}"
    
    return "EVERGREEN: Content works year-round"

def get_optimal_posting_times(platform: str) -> List[str]:
    """Get optimal posting times by platform"""
    optimal_times = {
        "tiktok": ["6-10 AM", "7-11 PM"],
        "youtube_short": ["12-3 PM", "7-10 PM"],
        "instagram_reel": ["11 AM-1 PM", "7-9 PM"],
        "linkedin": ["7-9 AM", "5-6 PM"],
        "twitter": ["8-10 AM", "6-9 PM"]
    }
    
    return optimal_times.get(platform, ["12-3 PM", "7-10 PM"])

@router.post("/search", response_model=SearchInsightsResponse)
async def get_search_insights(request: SearchInsightsRequest):
    """
    Get search insights and trending topics for a niche
    
    Sources:
    - Google Trends (via LLM analysis)
    - Seasonal analysis
    - AI-generated content ideas
    """
    
    if not llm_backend:
        raise HTTPException(status_code=503, detail="Backend not fully initialized")
    
    try:
        logger.info(f"Getting insights for niche: {request.niche}, platform: {request.platform}")
        
        # Use LLM to analyze trends and generate insights
        user_prompt = f"""Analyze trending searches and content opportunities for this niche:

NICHE: {request.niche}
PLATFORM: {request.platform}
REGION: {request.region}
TIMEFRAME: Last 7 days

TASK: Generate search insights and trending topics.

Consider:
1. What people are searching for in {request.niche} right now
2. Trending topics that align with this niche
3. Content opportunities with viral potential
4. Seasonal relevance (current month: {datetime.now().strftime('%B')})

OUTPUT FORMAT (JSON):
{{
  "trending_searches": ["search 1", "search 2", "search 3"],
  "rising_topics": [
    {{
      "topic": "topic name",
      "search_volume": "rising",
      "content_ideas": ["idea 1", "idea 2"],
      "hashtag_suggestions": ["#tag1", "#tag2"],
      "viral_potential": 75
    }}
  ],
  "content_opportunities": [
    {{
      "rank": 1,
      "opportunity": "opportunity name",
      "why_now": "why it's trending now",
      "quick_win": "quick content idea",
      "estimated_views": "1000-2000"
    }}
  ]
}}

Generate 5-10 trending searches and 3-5 rising topics.
Focus on topics that are actually trending right now for {request.niche}.

CRITICAL: Output ONLY valid JSON. No markdown, no code blocks, no explanation. Just JSON.
ABSOLUTELY NO EMOJIS. Use plain text only."""

        messages = [
            {
                "role": "system",
                "content": "You are a search insights expert. Analyze trending topics and generate content opportunities. Output ONLY valid JSON. NO EMOJIS - plain text only."
            },
            {"role": "user", "content": user_prompt}
        ]
        
        # Generate insights
        async def stream_response():
            try:
                insights_text = ""
                async for chunk in llm_backend.generate_stream(messages, temperature=0.8):
                    insights_text += chunk
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                
                # Try to parse JSON
                try:
                    json_text = insights_text.strip()
                    if "```json" in json_text:
                        json_text = json_text.split("```json")[1].split("```")[0].strip()
                    elif "```" in json_text:
                        json_text = json_text.split("```")[1].split("```")[0].strip()
                    
                    insights_data = json.loads(json_text)
                    
                    # Add seasonal relevance and posting times
                    result = SearchInsightsResponse(
                        niche=request.niche,
                        trending_searches=insights_data.get("trending_searches", [])[:15],
                        rising_topics=[TrendingTopic(**topic) for topic in insights_data.get("rising_topics", [])[:5]],
                        content_opportunities=insights_data.get("content_opportunities", [])[:5],
                        seasonal_relevance=analyze_seasonal_relevance(request.niche),
                        recommended_posting_times=get_optimal_posting_times(request.platform)
                    )
                    
                    yield f"data: {json.dumps({'parsed': result.dict()})}\n\n"
                except Exception as e:
                    logger.warning(f"Failed to parse insights JSON: {e}")
                    # Return basic structure if parsing fails
                    result = SearchInsightsResponse(
                        niche=request.niche,
                        trending_searches=[],
                        rising_topics=[],
                        content_opportunities=[],
                        seasonal_relevance=analyze_seasonal_relevance(request.niche),
                        recommended_posting_times=get_optimal_posting_times(request.platform)
                    )
                    yield f"data: {json.dumps({'parsed': result.dict()})}\n\n"
                
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                logger.error(f"Generation error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(stream_response(), media_type="text/event-stream")
    
    except Exception as e:
        logger.error(f"Search insights failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get insights: {str(e)}")

