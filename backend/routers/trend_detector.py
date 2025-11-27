from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import json
import logging
from typing import List, Dict
from core.trends import trend_service

router = APIRouter(prefix="/api/trend-detector", tags=["trend-detector"])
logger = logging.getLogger(__name__)

_llm_backend = None

def set_globals(embedding_engine, vector_store, llm_backend):
    global _llm_backend
    _llm_backend = llm_backend

class TrendRequest(BaseModel):
    platform: str  # "tiktok", "youtube", "instagram"
    niche: str
    region: str = "US"

@router.post("/detect")
async def detect_real_trends(request: TrendRequest):
    """
    Detect REAL trending topics using multiple data sources and AI synthesis
    """
    
    if not _llm_backend:
        raise HTTPException(status_code=503, detail="LLM not available")
    
    # Get trends from existing trend service
    try:
        raw_trends = trend_service.get_trends(
            platform=request.platform,
            niche=request.niche,
            use_cache=False  # Get fresh data
        )
    except Exception as e:
        logger.error(f"Failed to fetch trends: {e}")
        raw_trends = []
    
    # Format trends for AI analysis
    trends_data = {
        "reddit_trends": [
            {
                "topic": t.topic,
                "popularity": t.popularity_score,
                "source": t.source
            }
            for t in raw_trends if t.source == "reddit"
        ],
        "common_patterns": [
            {
                "topic": t.topic,
                "popularity": t.popularity_score,
                "source": t.source
            }
            for t in raw_trends if t.source == "common_patterns"
        ],
        "all_trends": [
            {
                "topic": t.topic,
                "popularity": t.popularity_score,
                "source": t.source
            }
            for t in raw_trends[:10]
        ]
    }
    
    # Get niche-specific curated trends
    niche_trends = get_niche_specific_trends(request.niche)
    
    # Synthesize with AI
    synthesis_prompt = f"""Analyze these REAL trending topics for {request.platform} in the {request.niche} niche:

REDDIT TRENDS:
{json.dumps(trends_data['reddit_trends'][:5], indent=2)}

COMMON PATTERNS:
{json.dumps(trends_data['common_patterns'][:5], indent=2)}

NICHE-SPECIFIC TRENDS:
{json.dumps(niche_trends.get('current_trends', [])[:5], indent=2)}

Based on this REAL DATA, identify:

1. Top 5 trending topics RIGHT NOW (not generic)
2. Why each is trending
3. Content ideas for each trend
4. Estimated trend lifespan (days/weeks)

Output as JSON:
{{
  "trending_now": [
    {{
      "topic": "specific trending topic",
      "why_trending": "reason",
      "content_ideas": ["idea1", "idea2", "idea3"],
      "lifespan": "X days/weeks",
      "platforms": ["{request.platform}"]
    }}
  ]
}}

ONLY output valid JSON, no markdown formatting."""

    try:
        response = _llm_backend.generate([
            {"role": "user", "content": synthesis_prompt}
        ], temperature=0.7)
        
        # Parse JSON
        response_clean = response.strip()
        if "```json" in response_clean:
            response_clean = response_clean.split("```json")[1].split("```")[0].strip()
        elif "```" in response_clean:
            response_clean = response_clean.split("```")[1].split("```")[0].strip()
        
        try:
            trending_data = json.loads(response_clean)
        except json.JSONDecodeError:
            # Fallback: try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_clean, re.DOTALL)
            if json_match:
                trending_data = json.loads(json_match.group())
            else:
                # Create fallback structure
                trending_data = {
                    "trending_now": [
                        {
                            "topic": trend.topic,
                            "why_trending": "Currently trending on social media",
                            "content_ideas": [f"Create content about {trend.topic}"],
                            "lifespan": "1-2 weeks",
                            "platforms": [request.platform]
                        }
                        for trend in raw_trends[:5]
                    ]
                }
        
        return {
            "platform": request.platform,
            "niche": request.niche,
            "last_updated": datetime.now().isoformat(),
            "raw_data": trends_data,
            "niche_trends": niche_trends,
            "ai_analysis": trending_data
        }
        
    except Exception as e:
        logger.error(f"Trend detection failed: {e}")
        # Return raw trends as fallback
        return {
            "platform": request.platform,
            "niche": request.niche,
            "last_updated": datetime.now().isoformat(),
            "raw_data": trends_data,
            "niche_trends": niche_trends,
            "ai_analysis": {
                "trending_now": [
                    {
                        "topic": trend.topic,
                        "why_trending": "Currently trending",
                        "content_ideas": [f"Create content about {trend.topic}"],
                        "lifespan": "1-2 weeks",
                        "platforms": [request.platform]
                    }
                    for trend in raw_trends[:5]
                ]
            }
        }

def get_niche_specific_trends(niche: str) -> Dict:
    """
    Get curated trends for specific niches
    """
    
    # Curated trend data (update weekly)
    NICHE_TRENDS = {
        "dark academia": {
            "current_trends": [
                "chaotic academia aesthetic",
                "light academia vs dark academia",
                "romanticism x dark academia",
                "winter term studying vibes",
                "classical music study sessions"
            ],
            "rising_trends": [
                "academic weapon era",
                "study like hermione granger",
                "bookstore haul aesthetics"
            ],
            "content_ideas": [
                "POV: winter term at Oxford",
                "Playlist for annotating classics",
                "Romanticizing exam season"
            ]
        },
        "study": {
            "current_trends": [
                "study with me",
                "productive morning routine",
                "aesthetic study setup",
                "exam season prep"
            ],
            "rising_trends": [
                "study techniques",
                "productivity hacks",
                "academic motivation"
            ],
            "content_ideas": [
                "Study routine for finals",
                "How I study effectively",
                "Productive study session"
            ]
        },
        "music": {
            "current_trends": [
                "study playlist",
                "aesthetic music",
                "vibe playlist",
                "lo-fi beats"
            ],
            "rising_trends": [
                "focus music",
                "ambient sounds",
                "classical study music"
            ],
            "content_ideas": [
                "Playlist for studying",
                "Music to focus to",
                "Aesthetic music vibes"
            ]
        }
    }
    
    # Try to match niche (case-insensitive, partial match)
    niche_lower = niche.lower()
    for key, value in NICHE_TRENDS.items():
        if key in niche_lower or niche_lower in key:
            return value
    
    # Default return
    return {
        "current_trends": [],
        "rising_trends": [],
        "content_ideas": [],
        "message": "Add this niche to our database for curated trends"
    }

@router.get("/niche-trends/{niche}")
async def get_niche_specific_trends_endpoint(niche: str):
    """
    Get curated trends for specific niches
    """
    return get_niche_specific_trends(niche)

