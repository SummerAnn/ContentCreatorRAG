"""
Content Pre-Check API endpoints
Check content against platform guidelines before posting
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import logging
import re

from core.llm_backend import LLMBackend

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/precheck", tags=["precheck"])

# Global instances (injected by main.py)
llm_backend = None

def set_globals(emb, vs, llm):
    global llm_backend
    llm_backend = llm

class ContentPrecheckRequest(BaseModel):
    script: str
    caption: Optional[str] = ""
    platform: str
    hashtags: Optional[List[str]] = []

class Issue(BaseModel):
    type: str
    severity: str  # high, medium, low
    message: str
    suggestion: str
    auto_fix: Optional[str] = None

class PrecheckResponse(BaseModel):
    eligible_for_fyp: bool
    overall_score: int
    issues: List[Issue]
    recommendations: List[str]
    safe_to_post: bool

# Platform-specific rules
PLATFORM_RULES = {
    "tiktok": {
        "max_script_words": 150,
        "ideal_duration": "15-60s",
        "max_hashtags": 5,
        "avoid_keywords": ["subscribe", "link in bio"],
        "preferred_style": "fast-paced, Gen-Z"
    },
    "youtube_short": {
        "max_script_words": 200,
        "ideal_duration": "15-60s",
        "max_hashtags": 5,
        "avoid_keywords": [],
        "preferred_style": "conversational"
    },
    "instagram_reel": {
        "max_script_words": 180,
        "ideal_duration": "15-90s",
        "max_hashtags": 10,
        "avoid_keywords": ["follow for follow"],
        "preferred_style": "aesthetic, aspirational"
    },
    "linkedin": {
        "max_script_words": 300,
        "ideal_duration": "30-90s",
        "max_hashtags": 5,
        "avoid_keywords": ["dm me", "link in comments"],
        "preferred_style": "professional but human"
    }
}

def check_profanity(text: str) -> List[Issue]:
    """Check for profanity (simplified - can use better-profanity library)"""
    issues = []
    
    # Simple profanity check (basic words)
    profanity_words = ['damn', 'hell', 'crap', 'sucks', 'stupid', 'idiot', 'hate']
    found_words = [word for word in profanity_words if word in text.lower()]
    
    if found_words:
        issues.append(Issue(
            type="profanity",
            severity="high",
            message=f"Contains words that may trigger content filters: {', '.join(found_words[:3])}",
            suggestion="Replace flagged words with milder alternatives",
            auto_fix=None
        ))
    
    return issues

def check_length(script: str, platform: str) -> List[Issue]:
    """Check if script length is appropriate"""
    issues = []
    
    if platform not in PLATFORM_RULES:
        return issues
    
    word_count = len(script.split())
    max_words = PLATFORM_RULES[platform]["max_script_words"]
    
    if word_count > max_words:
        issues.append(Issue(
            type="length",
            severity="medium",
            message=f"Script is {word_count} words (recommended max: {max_words} for {platform})",
            suggestion=f"Trim script to under {max_words} words for better retention",
            auto_fix=None
        ))
    
    return issues

def check_promotional_content(text: str) -> List[Issue]:
    """Check if content is overly promotional"""
    issues = []
    
    # Count promotional keywords
    promo_keywords = [
        'buy', 'purchase', 'discount', 'sale', 'limited time',
        'click link', 'shop now', 'order now', 'get yours',
        'subscribe', 'follow me', 'check out'
    ]
    
    promo_count = sum(1 for keyword in promo_keywords if keyword in text.lower())
    
    # Check for too many CTAs
    cta_count = len(re.findall(r'(link in bio|dm me|comment below|tag a friend)', text.lower()))
    
    total_promotional = promo_count + cta_count
    
    if total_promotional > 3:
        issues.append(Issue(
            type="over_promotion",
            severity="high",
            message=f"Contains {total_promotional} promotional elements - may be flagged as spam",
            suggestion="Reduce promotional language to 1-2 mentions maximum",
            auto_fix=None
        ))
    elif total_promotional > 1:
        issues.append(Issue(
            type="promotional",
            severity="medium",
            message=f"Contains {total_promotional} promotional elements",
            suggestion="Consider reducing promotional language for better organic reach",
            auto_fix=None
        ))
    
    return issues

def check_clickbait(text: str, platform: str) -> List[Issue]:
    """Check for excessive clickbait"""
    issues = []
    
    clickbait_patterns = [
        r'you won\'t believe',
        r'shocking',
        r'this one trick',
        r'doctors hate',
        r'click here',
        r'wait til the end',
        r'#\d+ will shock you'
    ]
    
    clickbait_count = sum(1 for pattern in clickbait_patterns 
                          if re.search(pattern, text.lower()))
    
    # Excessive caps
    caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
    
    if clickbait_count >= 2 or caps_ratio > 0.3:
        issues.append(Issue(
            type="clickbait",
            severity="medium",
            message="Contains clickbait patterns that may reduce credibility",
            suggestion="Use curiosity-driven hooks instead of obvious clickbait",
            auto_fix=None
        ))
    
    return issues

def check_platform_specific(text: str, platform: str, hashtags: List[str]) -> List[Issue]:
    """Check platform-specific rules"""
    issues = []
    
    if platform not in PLATFORM_RULES:
        return issues
    
    rules = PLATFORM_RULES[platform]
    
    # Check for avoided keywords
    for keyword in rules["avoid_keywords"]:
        if keyword in text.lower():
            issues.append(Issue(
                type="platform_violation",
                severity="medium",
                message=f"'{keyword}' may reduce reach on {platform}",
                suggestion=f"Remove '{keyword}' - it's flagged by {platform}'s algorithm",
                auto_fix=None
            ))
    
    # Check hashtag count
    if len(hashtags) > rules["max_hashtags"]:
        issues.append(Issue(
            type="hashtag_spam",
            severity="low",
            message=f"Using {len(hashtags)} hashtags (recommended: {rules['max_hashtags']} for {platform})",
            suggestion=f"Reduce to {rules['max_hashtags']} high-quality hashtags",
            auto_fix=None
        ))
    
    return issues

def calculate_overall_score(issues: List[Issue]) -> int:
    """Calculate overall safety score (0-100)"""
    score = 100
    
    severity_penalties = {
        "high": 30,
        "medium": 15,
        "low": 5
    }
    
    for issue in issues:
        score -= severity_penalties.get(issue.severity, 10)
    
    return max(0, score)

def generate_recommendations(issues: List[Issue], score: int) -> List[str]:
    """Generate actionable recommendations"""
    recommendations = []
    
    if score < 70:
        recommendations.append("Content may have limited reach - fix high-severity issues first")
    
    # Group by type
    issue_types = {}
    for issue in issues:
        issue_types.setdefault(issue.type, []).append(issue)
    
    # Prioritize fixes
    if "profanity" in issue_types:
        recommendations.append("CRITICAL: Remove profanity to avoid content removal")
    
    if "over_promotion" in issue_types:
        recommendations.append("HIGH: Reduce promotional language to improve organic reach")
    
    if "length" in issue_types:
        recommendations.append("TIP: Trim script for better retention on short-form platforms")
    
    if score >= 90:
        recommendations.append("Content looks great! Safe to post.")
    elif score >= 70:
        recommendations.append("Content is good, but minor improvements could boost performance")
    
    return recommendations

@router.post("/", response_model=PrecheckResponse)
async def precheck_content(request: ContentPrecheckRequest):
    """
    Pre-check content against platform guidelines before posting
    
    Returns eligibility, issues, and recommendations
    """
    
    try:
        combined_text = f"{request.script} {request.caption}".strip()
        
        # Run all checks
        issues = []
        issues.extend(check_profanity(combined_text))
        issues.extend(check_length(request.script, request.platform))
        issues.extend(check_promotional_content(combined_text))
        issues.extend(check_clickbait(combined_text, request.platform))
        issues.extend(check_platform_specific(combined_text, request.platform, request.hashtags or []))
        
        # Calculate score
        overall_score = calculate_overall_score(issues)
        
        # Determine eligibility
        eligible_for_fyp = overall_score >= 70
        safe_to_post = all(issue.severity != "high" for issue in issues)
        
        # Generate recommendations
        recommendations = generate_recommendations(issues, overall_score)
        
        logger.info(f"Pre-check complete: score={overall_score}, issues={len(issues)}")
        
        return PrecheckResponse(
            eligible_for_fyp=eligible_for_fyp,
            overall_score=overall_score,
            issues=issues,
            recommendations=recommendations,
            safe_to_post=safe_to_post
        )
    
    except Exception as e:
        logger.error(f"Pre-check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Pre-check failed: {str(e)}")

