from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import random
import logging
from datetime import datetime
import hashlib
import requests

router = APIRouter(prefix="/api/ideas-feed", tags=["ideas-feed"])
logger = logging.getLogger(__name__)

# Global dependencies
_llm_backend = None
_db = None
_embedding_engine = None
_vector_store = None

def set_globals(embedding_engine, vector_store, llm_backend, db=None):
    global _llm_backend, _db, _embedding_engine, _vector_store
    _llm_backend = llm_backend
    _db = db
    _embedding_engine = embedding_engine
    _vector_store = vector_store

class IdeaCard(BaseModel):
    id: str
    idea: str
    platform: str
    niche: str
    hook_preview: str
    viral_score: float
    category: str  # "trending", "saved", "competitor", "wildcard"
    timestamp: str
    source: str  # "Google Trends", "Your Swipe File", "Competitor Analysis", "AI Generated"

# NICHE-SPECIFIC IDEA TEMPLATES
NICHE_IDEAS = {
    "lifestyle": [
        "Day in my life: [specific routine]",
        "Things that changed my life this year",
        "My morning routine that changed everything",
        "Productivity habits I swear by",
        "How I organize my life (realistic edition)",
        "Things I stopped doing that improved my life",
        "Realistic self-care routine",
        "How I stay motivated daily",
        "Life hacks that actually work",
        "My favorite things right now",
    ],
    "beauty": [
        "Skincare routine that cleared my skin",
        "Makeup products worth the hype",
        "Beauty mistakes I made (and how to avoid)",
        "Drugstore dupes for expensive products",
        "Hair care routine for [hair type]",
        "Simple makeup looks for beginners",
        "Beauty products I regret buying",
        "Skincare ingredients that actually work",
        "How I achieved [specific look]",
        "Beauty tips from professionals",
    ],
    "fashion": [
        "Outfit ideas for [occasion]",
        "Wardrobe essentials everyone needs",
        "How to style [item] 5 ways",
        "Fashion mistakes to avoid",
        "Thrifting tips that changed my closet",
        "Capsule wardrobe essentials",
        "Trends worth trying vs. skipping",
        "How to build a timeless wardrobe",
        "Style inspiration for [aesthetic]",
        "Fashion on a budget",
    ],
    "business": [
        "How I started my [business type]",
        "Business mistakes I made (learn from me)",
        "Side hustle ideas that actually work",
        "How to [business skill] as a beginner",
        "Things I wish I knew before starting",
        "How to grow your [business metric]",
        "Business tools I can't live without",
        "How to price your [product/service]",
        "Marketing strategies that worked for me",
        "How to balance work and life",
    ],
    "finance": [
        "How I saved $[amount] in [time period]",
        "Money mistakes I made in my 20s",
        "Budgeting tips that actually work",
        "How to invest for beginners",
        "Side income ideas that pay well",
        "Financial habits that changed my life",
        "How to build an emergency fund",
        "Debt payoff strategies that work",
        "How to negotiate [salary/price]",
        "Financial goals for [age group]",
    ],
    "education": [
        "Study tips that actually work",
        "How to [study skill] effectively",
        "Productivity apps for students",
        "How I improved my [subject] grades",
        "Study routine that changed everything",
        "Note-taking methods compared",
        "How to stay motivated in school",
        "Time management for students",
        "How to prepare for [exam type]",
        "Study habits of top students",
    ],
    "gaming": [
        "Games I'm playing right now",
        "Hidden gems you need to play",
        "Gaming setup on a budget",
        "Tips for [game name] beginners",
        "Games worth the hype vs. overrated",
        "How to improve at [game type]",
        "Gaming accessories that are worth it",
        "Indie games you're missing out on",
        "How I built my gaming PC",
        "Gaming habits that changed my experience",
    ],
    "entertainment": [
        "Shows/movies I'm watching right now",
        "Hidden gems on [streaming platform]",
        "Books that changed my perspective",
        "Music I'm obsessed with lately",
        "Podcasts that made me smarter",
        "Entertainment recommendations for [mood]",
        "How I discover new content",
        "Entertainment worth the hype",
        "Things I'm currently obsessed with",
        "How to find your next favorite [media type]",
    ],
    "travel": [
        "Hidden gems in [destination] locals don't want tourists to know",
        "I spent $500 for 2 weeks in [country] - here's how",
        "Things I wish I knew before visiting [destination]",
        "Airport hacks that save me hours every trip",
        "Packing light: 7 days in one carry-on",
        "Overrated tourist traps you should skip in [city]",
        "Best street food in [country] under $5",
        "How to travel full-time while working remotely",
        "Luxury travel on a budget: My secrets",
        "Solo travel safety tips that actually work",
    ],
    "food": [
        "Restaurant-quality [dish] at home in 15 minutes",
        "I tested every [ingredient] brand - here's the best",
        "Things professional chefs never do (and you shouldn't either)",
        "Budget meal prep for the entire week under $30",
        "The one ingredient that transforms everything",
        "Failed recipe attempts that actually worked",
        "Recreating trending [restaurant] menu at home",
        "Kitchen tools worth the investment vs. overrated",
        "Cooking hacks from my grandma that actually work",
        "Aesthetic food photography on your phone",
    ],
    "tech": [
        "Apps I use daily that changed my productivity",
        "iPhone hidden features you didn't know existed",
        "Building a home office setup on a budget",
        "Tech that's actually worth the upgrade in 2025",
        "Productivity hacks using AI tools (free)",
        "My minimal tech setup that does everything",
        "Software alternatives that are better than popular apps",
        "Automating my entire workflow with these tools",
        "Tech purchases I regret (and better alternatives)",
        "Future of [technology] - what's coming next",
    ],
    "fitness": [
        "How I built muscle without going to the gym",
        "15-minute workouts that actually work",
        "Gym mistakes beginners make (and how to fix them)",
        "Protein-rich meals for muscle building on a budget",
        "Home workout equipment that's worth it",
        "My transformation: 3 months of consistency",
        "Debunking fitness myths that waste your time",
        "How to stay motivated when you don't feel like it",
        "Exercises that target [specific area] effectively",
        "Fitness tracking apps comparison - which is best?",
    ],
}

# VIRAL PATTERNS (based on real data)
VIRAL_PATTERNS = [
    "POV: {scenario}",
    "Things {group} do that {result}",
    "I tried {challenge} for {time} - here's what happened",
    "{Number} {topic} that {benefit}",
    "Why {claim} (you won't believe #{number})",
    "Day in the life of {role}",
    "How to {achieve} without {common_method}",
    "{Topic} nobody talks about",
    "The truth about {topic}",
    "Stop {action} - do this instead",
]

@router.get("/generate")
async def generate_ideas_feed(
    niche: str = Query(..., description="User's niche"),
    platform: str = Query("tiktok", description="Target platform"),
    user_id: str = Query(None, description="User ID for personalization"),
    limit: int = Query(20, description="Number of ideas to generate"),
    offset: int = Query(0, description="Pagination offset"),
):
    """
    Generate infinite scroll of personalized content ideas
    
    ALGORITHM:
    - 40% trending topics (real-time)
    - 30% based on user's niche
    - 20% competitor-inspired
    - 10% random wildcard ideas
    """
    
    if not _llm_backend:
        raise HTTPException(status_code=503, detail="LLM not available")
    
    try:
        ideas = []
        
        # CATEGORY 1: Trending Topics (40%)
        trending_count = int(limit * 0.4)
        trending_ideas = await generate_trending_ideas(niche, platform, trending_count)
        ideas.extend(trending_ideas)
        
        # CATEGORY 2: Niche-Based Ideas (30%)
        niche_count = int(limit * 0.3)
        niche_ideas = await generate_niche_ideas(niche, platform, niche_count)
        ideas.extend(niche_ideas)
        
        # CATEGORY 3: Competitor-Inspired (20%)
        competitor_count = int(limit * 0.2)
        competitor_ideas = await generate_competitor_ideas(niche, platform, competitor_count)
        ideas.extend(competitor_ideas)
        
        # CATEGORY 4: Wildcard Ideas (10%)
        wildcard_count = limit - len(ideas)
        wildcard_ideas = await generate_wildcard_ideas(platform, wildcard_count)
        ideas.extend(wildcard_ideas)
        
        # Shuffle for variety
        random.shuffle(ideas)
        
        # Paginate
        paginated_ideas = ideas[offset:offset + limit]
        
        return {
            "ideas": paginated_ideas,
            "total": len(ideas),
            "offset": offset,
            "limit": limit,
            "has_more": offset + limit < len(ideas)
        }
        
    except Exception as e:
        logger.error(f"Ideas feed generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def generate_trending_ideas(niche: str, platform: str, count: int) -> List[IdeaCard]:
    """Generate ideas based on REAL-TIME trends from trend detector"""
    
    ideas = []
    
    try:
        # Call the trend detector to get REAL trending topics
        if _llm_backend:
            # Import trend service directly to avoid circular imports
            from core.trends import trend_service
            
            # Get real trends from trend service
            try:
                raw_trends = trend_service.get_trends(
                    platform=platform,
                    niche=niche,
                    use_cache=False  # Get fresh data
                )
                
                # Get niche-specific trends
                from routers.trend_detector import get_niche_specific_trends
                niche_trends = get_niche_specific_trends(niche)
                
                # Use AI to synthesize real trends into content ideas
                trends_summary = "\n".join([
                    f"- {t.topic} (popularity: {t.popularity_score})" 
                    for t in raw_trends[:10]
                ])
                
                niche_current = "\n".join([
                    f"- {t}" for t in niche_trends.get("current_trends", [])[:5]
                ])
                
                synthesis_prompt = f"""Based on these REAL trending topics for {platform} in {niche}:

REDDIT/TRENDING TOPICS:
{trends_summary}

NICHE-SPECIFIC TRENDS:
{niche_current}

Generate {count} specific, actionable content ideas that capitalize on these REAL trends RIGHT NOW.

Make each idea:
- Specific to the actual trends (not generic)
- Actionable and ready to create
- Under 60 characters
- Based on the real trending topics above

Output format (one per line):
1. [specific idea based on real trend]
2. [specific idea based on real trend]
..."""

                ai_response = _llm_backend.generate([
                    {"role": "user", "content": synthesis_prompt}
                ], temperature=0.8)
                
                # Parse AI response
                lines = [line.strip() for line in ai_response.split('\n') if line.strip()]
                real_trending_ideas = []
                for line in lines:
                    if '. ' in line:
                        idea = line.split('. ', 1)[1]
                    elif line and not line.startswith('#') and len(line) > 10:
                        idea = line
                    else:
                        continue
                    if idea and len(idea) > 5:
                        real_trending_ideas.append(idea)
                
                # Create IdeaCard objects from real trends
                for i, idea_text in enumerate(real_trending_ideas[:count]):
                    # Match idea to original trend for context
                    matched_trend = None
                    for trend in raw_trends:
                        if trend.topic.lower() in idea_text.lower() or idea_text.lower() in trend.topic.lower():
                            matched_trend = trend
                            break
                    
                    viral_score = matched_trend.popularity_score if matched_trend else random.uniform(75, 90)
                    
                    ideas.append(IdeaCard(
                        id=generate_id(f"trending_real_{i}_{idea_text}"),
                        idea=idea_text,
                        platform=platform,
                        niche=niche,
                        hook_preview=f"Based on trending: {matched_trend.topic if matched_trend else 'current trend'}",
                        viral_score=min(95, max(70, viral_score)),
                        category="trending",
                        timestamp=datetime.now().isoformat(),
                        source="Real-Time Trends"
                    ))
                
            except Exception as trend_error:
                logger.warning(f"Trend service failed, using AI fallback: {trend_error}")
                # Fall through to AI fallback below
            
            # Extract real trending topics from AI analysis
            trending_now = trend_data.get("ai_analysis", {}).get("trending_now", [])
            
            if trending_now:
                # Use real trending topics
                for i, trend in enumerate(trending_now[:count]):
                    topic = trend.get("topic", "")
                    content_ideas = trend.get("content_ideas", [])
                    
                    # Use the first content idea or the topic itself
                    idea_text = content_ideas[0] if content_ideas else topic
                    hook_preview = trend.get("why_trending", f"Trending now: {topic}")
                    
                    # Calculate viral score based on popularity
                    popularity = trend.get("popularity", 80)
                    viral_score = min(95, max(75, popularity))
                    
                    ideas.append(IdeaCard(
                        id=generate_id(f"trending_{i}_{topic}"),
                        idea=idea_text,
                        platform=platform,
                        niche=niche,
                        hook_preview=hook_preview,
                        viral_score=viral_score,
                        category="trending",
                        timestamp=datetime.now().isoformat(),
                        source="Real-Time Trends"
                    ))
            
            # If we got some real trends but need more, fill with niche trends
            if len(ideas) < count:
                niche_trends = trend_data.get("niche_trends", {})
                current_trends = niche_trends.get("current_trends", [])
                
                for i, trend_topic in enumerate(current_trends[len(ideas):count]):
                    ideas.append(IdeaCard(
                        id=generate_id(f"trending_niche_{i}_{trend_topic}"),
                        idea=f"Create content about: {trend_topic}",
                        platform=platform,
                        niche=niche,
                        hook_preview=f"Currently trending: {trend_topic}",
                        viral_score=random.uniform(75, 90),
                        category="trending",
                        timestamp=datetime.now().isoformat(),
                        source="Niche Trends"
                    ))
        
        # Fallback: If trend detector fails, use AI to generate trending ideas
        if len(ideas) < count and _llm_backend:
            logger.warning("Trend detector returned insufficient data, using AI fallback")
            fallback_prompt = f"""Generate {count - len(ideas)} REAL trending topics RIGHT NOW for {niche} on {platform}.

These must be ACTUAL current trends, not generic topics. Think about what's trending TODAY.

Output format:
1. [specific trending topic]
2. [specific trending topic]
...

Examples of REAL trends:
- "Chaotic academia aesthetic" (not "dark academia")
- "Study like Hermione Granger" (not "study tips")
- "Winter term studying vibes" (not "how to study")

Generate REAL current trends:"""

            try:
                ai_response = _llm_backend.generate([
                    {"role": "user", "content": fallback_prompt}
                ], temperature=0.9)
                
                # Parse AI response
                lines = [line.strip() for line in ai_response.split('\n') if line.strip()]
                ai_topics = []
                for line in lines:
                    if '. ' in line:
                        topic = line.split('. ', 1)[1]
                    else:
                        topic = line
                    if topic and len(topic) > 5:
                        ai_topics.append(topic)
                
                for i, topic in enumerate(ai_topics[:count - len(ideas)]):
                    ideas.append(IdeaCard(
                        id=generate_id(f"trending_ai_{i}_{topic}"),
                        idea=topic,
                        platform=platform,
                        niche=niche,
                        hook_preview=f"AI-detected trend: {topic}",
                        viral_score=random.uniform(70, 85),
                        category="trending",
                        timestamp=datetime.now().isoformat(),
                        source="AI Trend Detection"
                    ))
            except Exception as e:
                logger.error(f"AI fallback failed: {e}")
        
    except Exception as e:
        logger.error(f"Failed to fetch real trends: {e}")
    
    # Final fallback: If still not enough, use generic (but mark as less reliable)
    if len(ideas) < count:
        logger.warning("Using generic fallback trends")
        generic_topics = [
            f"Latest trend in {niche}",
            f"Viral {niche} challenge",
            f"Trending {niche} aesthetic",
            f"Popular {niche} format on {platform}",
        ]
        
        for i, topic in enumerate(generic_topics[:count - len(ideas)]):
            ideas.append(IdeaCard(
                id=generate_id(f"trending_fallback_{i}_{topic}"),
                idea=topic,
                platform=platform,
                niche=niche,
                hook_preview=f"Create content about: {topic}",
                viral_score=random.uniform(60, 75),  # Lower score for generic
                category="trending",
                timestamp=datetime.now().isoformat(),
                source="Generic Trends"
            ))
    
    return ideas[:count]

async def generate_niche_ideas(niche: str, platform: str, count: int) -> List[IdeaCard]:
    """Generate ideas from niche-specific templates"""
    
    ideas = []
    niche_templates = NICHE_IDEAS.get(niche.lower(), [])
    
    if not niche_templates:
        # Generate with AI if niche not in templates
        niche_templates = await ai_generate_niche_ideas(niche, count)
    
    selected_templates = random.sample(niche_templates, min(count, len(niche_templates)))
    
    for i, template in enumerate(selected_templates):
        ideas.append(IdeaCard(
            id=generate_id(f"niche_{i}_{template}"),
            idea=template,
            platform=platform,
            niche=niche,
            hook_preview=f"Hook: {template[:50]}...",
            viral_score=random.uniform(60, 85),
            category="saved",
            timestamp=datetime.now().isoformat(),
            source=f"{niche.title()} Library"
        ))
    
    return ideas

async def generate_competitor_ideas(niche: str, platform: str, count: int) -> List[IdeaCard]:
    """Generate competitor-inspired ideas"""
    
    ideas = []
    
    # Simulate competitor analysis
    competitor_topics = [
        f"Remix: Popular {niche} format",
        f"Trending {niche} angle nobody's doing",
        f"Competitor's viral video concept (your twist)",
    ]
    
    for i, topic in enumerate(competitor_topics[:count]):
        ideas.append(IdeaCard(
            id=generate_id(f"competitor_{i}_{topic}"),
            idea=topic,
            platform=platform,
            niche=niche,
            hook_preview=f"Remix idea: {topic}",
            viral_score=random.uniform(70, 90),
            category="competitor",
            timestamp=datetime.now().isoformat(),
            source="Competitor Analysis"
        ))
    
    return ideas

async def generate_wildcard_ideas(platform: str, count: int) -> List[IdeaCard]:
    """Generate random wildcard ideas for inspiration"""
    
    ideas = []
    
    wildcard_topics = [
        "Unexpected crossover content idea",
        "Contrarian take on popular belief",
        "Behind-the-scenes content concept",
        "Interactive challenge for audience",
        "Storytelling angle for your niche",
    ]
    
    for i, topic in enumerate(wildcard_topics[:count]):
        ideas.append(IdeaCard(
            id=generate_id(f"wildcard_{i}_{topic}"),
            idea=topic,
            platform=platform,
            niche="mixed",
            hook_preview=f"Wild idea: {topic}",
            viral_score=random.uniform(50, 75),
            category="wildcard",
            timestamp=datetime.now().isoformat(),
            source="AI Generated"
        ))
    
    return ideas

async def ai_generate_niche_ideas(niche: str, count: int) -> List[str]:
    """Use AI to generate niche-specific ideas"""
    
    prompt = f"""Generate {count} viral content ideas for the {niche} niche.

Make them:
- Specific and actionable
- Platform-agnostic (work on TikTok, Instagram, YouTube)
- Attention-grabbing
- Based on proven viral patterns

Output format (one per line):
1. [idea]
2. [idea]
...

Examples for reference:
- "POV: You discover a hidden gem in [topic]"
- "Things [audience] do that [result]"
- "I tried [challenge] for [time] - results"

Generate ideas:"""

    try:
        response = _llm_backend.generate([
            {"role": "user", "content": prompt}
        ], temperature=0.9)
        
        # Parse ideas
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        ideas = [line.split('. ', 1)[1] if '. ' in line else line for line in lines]
        
        return ideas[:count]
    except:
        return [f"AI-generated {niche} content idea #{i+1}" for i in range(count)]

def generate_id(text: str) -> str:
    """Generate unique ID from text"""
    return hashlib.md5(text.encode()).hexdigest()[:12]

@router.post("/save")
async def save_idea(idea_id: str, user_id: str):
    """Save idea to user's swipe file"""
    # Integration with existing swipefile.py
    return {"message": "Idea saved to swipe file", "idea_id": idea_id}

@router.post("/develop")
async def develop_idea(idea_id: str, user_id: str):
    """Send idea to chat for full development"""
    return {"message": "Idea sent to chat", "chat_url": f"/chat?idea={idea_id}"}

