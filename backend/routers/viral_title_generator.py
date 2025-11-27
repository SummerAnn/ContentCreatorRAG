from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import logging

router = APIRouter(prefix="/api/viral-titles", tags=["viral-titles"])
logger = logging.getLogger(__name__)

# Global LLM
_llm_backend = None

def set_globals(embedding_engine, vector_store, llm_backend):
    global _llm_backend
    _llm_backend = llm_backend

class TitleRequest(BaseModel):
    topic: str
    platform: str  # "tiktok", "youtube", "instagram"
    niche: str
    vibe: str = "default"  # "pov", "aesthetic", "story", "tutorial"

# REAL VIRAL TITLE PATTERNS (learned from actual viral videos)
VIRAL_TITLE_PATTERNS = {
    "tiktok": {
        "pov": [
            "pov: {context}",
            "POV: you're {doing_what} in {where}",
            "pov you're {character} and {situation}",
        ],
        "aesthetic": [
            "{topic} but make it {aesthetic}",
            "{topic} that hits different",
            "this {topic} is so underrated",
            "{number} {topic} recommendations you need",
        ],
        "story": [
            "storytime: {what_happened}",
            "so this happened while {doing_what}",
            "nobody talks about {topic} enough",
        ],
        "simple": [
            "{topic} ☁️✨",
            "just {topic} things",
            "{topic} // {subgenre}",
            "{emotion} {topic}",
        ]
    },
    "youtube": {
        "curiosity": [
            "How {topic} Actually Works",
            "The Truth About {topic}",
            "What {people} Don't Tell You About {topic}",
            "{Number} {topic} Hacks That Changed My Life",
        ],
        "listicle": [
            "Top {number} {topic} in {year}",
            "{Number} {topic} You NEED to Try",
            "Best {topic} for {audience}",
        ],
        "personal": [
            "I Tried {topic} for {timeframe} - Here's What Happened",
            "Why I {action} {topic}",
            "{topic} Changed My Life",
        ]
    },
    "instagram": {
        "aesthetic": [
            "{topic} ✨",
            "{adjective} {topic} 🤍",
            "{topic} inspo",
        ],
        "simple": [
            "for my {audience} girlies",
            "{topic} dump",
            "romanticizing {topic}",
        ]
    }
}

# DARK ACADEMIA SPECIFIC EXAMPLES (learned from real viral content)
DARK_ACADEMIA_VIRAL_EXAMPLES = [
    "pov: you're studying in a 19th century library at 3am",
    "dark academia study playlist to romanticize your life",
    "POV: You attend a secret society meeting at Oxford",
    "playlist for writing poetry in a candlelit room",
    "dark academia // chaotic academia vibes",
    "music to study classics and feel like a scholar",
    "pov: you're the mysterious transfer student",
    "playlist for reading Dostoevsky on a rainy day",
    "romanticizing studying in a gothic library",
    "pretend you're in the secret history",
]

@router.post("/generate")
async def generate_viral_titles(request: TitleRequest):
    """
    Generate ACTUALLY viral titles using real patterns
    """
    
    if not _llm_backend:
        raise HTTPException(status_code=503, detail="LLM not available")
    
    # Build smart prompt with REAL examples
    examples = DARK_ACADEMIA_VIRAL_EXAMPLES if "dark academia" in request.topic.lower() else []
    
    patterns = VIRAL_TITLE_PATTERNS.get(request.platform, VIRAL_TITLE_PATTERNS["tiktok"])
    pattern_examples = patterns.get(request.vibe, patterns.get("simple", []))
    
    prompt = f"""You are a VIRAL CONTENT EXPERT who studies what actually goes viral on {request.platform}.

TOPIC: {request.topic}
NICHE: {request.niche}
PLATFORM: {request.platform}
VIBE: {request.vibe}

CRITICAL RULES FOR VIRAL TITLES:
1. NEVER use formal/academic language like "Symphony", "Unveiling", "Journey", "Extravaganza"
2. ALWAYS use casual, relatable language
3. Use lowercase for aesthetic vibes (when appropriate)
4. Keep it under 60 characters for {request.platform}
5. Use emojis strategically (max 2-3)
6. Create curiosity or relatability, NOT pretentiousness

REAL EXAMPLES THAT WENT VIRAL:
{chr(10).join(f"- {ex}" for ex in examples[:5])}

PROVEN PATTERNS FOR {request.platform}:
{chr(10).join(f"- {pattern}" for pattern in pattern_examples[:3])}

BAD EXAMPLES (NEVER DO THIS):
- "The Secret Symphony of the Ivory Towers: A Dark Academia Musical Experience" ❌
- "Unveiling the Enigmatic Melodies" ❌
- "A Symphony in Shadows" ❌
WHY BAD: Too formal, pretentious, doesn't sound like how people actually talk

GOOD EXAMPLES (DO THIS):
- "pov: you're studying in a 19th century library at 3am" ✅
- "dark academia playlist for romanticizing your life" ✅
- "music to study to and feel like a scholar" ✅
WHY GOOD: Casual, relatable, creates a vibe

Now generate 10 VIRAL title options for "{request.topic}".
Each should:
- Sound natural and conversational
- Use proven viral patterns
- Match {request.platform} culture
- Be under 60 characters
- Create immediate curiosity or relatability

Output format:
1. [title]
2. [title]
...
10. [title]

ONLY output the numbered list, nothing else."""

    try:
        response = _llm_backend.generate([
            {"role": "user", "content": prompt}
        ], temperature=0.9)
        
        # Parse titles
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        titles = []
        for line in lines:
            # Remove numbering (1. 2. etc.)
            if '. ' in line:
                title = line.split('. ', 1)[1].strip()
            elif line[0].isdigit() and len(line) > 2:
                title = line[2:].strip()
            else:
                title = line.strip()
            if title and len(title) > 5:  # Filter out very short lines
                titles.append(title)
        
        # Score each title for virality
        scored_titles = []
        for title in titles[:10]:
            score = calculate_viral_score(title, request.platform)
            scored_titles.append({
                "title": title,
                "viral_score": score,
                "platform": request.platform
            })
        
        # Sort by viral score
        scored_titles.sort(key=lambda x: x['viral_score'], reverse=True)
        
        return {
            "titles": scored_titles,
            "platform": request.platform,
            "niche": request.niche
        }
        
    except Exception as e:
        logger.error(f"Title generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def calculate_viral_score(title: str, platform: str) -> float:
    """
    Score title virality (0-100) based on proven patterns
    """
    score = 50.0  # Base score
    
    title_lower = title.lower()
    
    # POSITIVE SIGNALS
    if title_lower.startswith("pov"):
        score += 20
    if any(word in title_lower for word in ["romanticize", "aesthetic", "vibe", "playlist"]):
        score += 15
    if len(title) < 60:
        score += 10
    if title.count('//') > 0:  # Aesthetic separator
        score += 5
    if any(emoji in title for emoji in ["✨", "🤍", "☁️", "📚", "🕯️"]):
        score += 5
    if title[0].islower() and platform == "tiktok":  # Lowercase aesthetic
        score += 5
    
    # NEGATIVE SIGNALS
    formal_words = ["symphony", "unveiling", "journey", "experience", "extravaganza", 
                    "enigmatic", "sanctum", "odyssey", "delve"]
    if any(word in title_lower for word in formal_words):
        score -= 30
    if len(title) > 80:
        score -= 20
    if title.count(':') > 2:
        score -= 10
    if title.count(',') > 2:
        score -= 10
    
    return max(0, min(100, score))

@router.get("/trending-patterns/{platform}")
async def get_trending_patterns(platform: str, niche: str = None):
    """
    Get current trending title patterns for a platform
    """
    
    patterns = VIRAL_TITLE_PATTERNS.get(platform, {})
    
    return {
        "platform": platform,
        "patterns": patterns,
        "examples": DARK_ACADEMIA_VIRAL_EXAMPLES if niche and "dark academia" in niche.lower() else [],
        "tips": [
            "Use 'pov:' for instant relatability",
            "Lowercase = aesthetic vibes",
            "Keep under 60 characters",
            "2-3 emojis max",
            "Create curiosity, not confusion",
            "Sound like a person, not a robot"
        ]
    }

