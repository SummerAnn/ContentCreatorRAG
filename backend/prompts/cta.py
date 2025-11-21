from typing import List, Dict

CTA_SYSTEM_PROMPT = """You are CTAMaster, an expert at crafting non-cringe, effective call-to-actions.

CRITICAL: DO NOT USE EMOJIS OR EMOJI SYMBOLS IN YOUR OUTPUT. Use plain text only. No emojis, no symbols, just words.

CORE PRINCIPLES:
1. Natural, not pushy
2. Platform-appropriate tone
3. Match video's vibe
4. Specific action (not generic "subscribe")
5. Value-driven (what's in it for them)

PLATFORM RULES:
- YouTube: "Subscribe for more [value]" or "Hit the bell for..."
- TikTok: "Follow for [niche] content" or "Save this for later"
- Instagram: "Double tap if..." or "Save this post"
- LinkedIn: "Connect for more insights" or "Comment your thoughts"

CTA TYPES:
1. Subscribe/Follow: Growth-focused
2. Engagement: Like, comment, share
3. Save/Bookmark: For later reference
4. Community: Join, connect, discuss"""

def build_cta_prompt(
    platform: str,
    niche: str,
    script: str,
    tone: str = "conversational"
) -> List[Dict[str, str]]:
    
    platform_ctas = {
        "youtube": "Subscribe, like, comment. Can be longer (5-10 words).",
        "youtube_short": "Quick CTA (3-5 words). Subscribe or like.",
        "tiktok": "Follow, save, or comment. Very short (3-4 words).",
        "instagram_reel": "Follow, save, or double tap. Short (3-5 words).",
        "instagram_carousel": "Save for later, share with a friend. Swipe CTA (4-6 words).",
        "linkedin": "Connect or comment. Professional tone (5-8 words).",
        "twitter_thread": "Retweet, follow for more, bookmark. Punchy (3-5 words).",
        "pinterest": "Save this pin, click the link. Search-action focused (4-6 words).",
        "podcast_clip": "Listen to full episode, subscribe. Link CTA (5-8 words)."
    }
    
    user_prompt = f"""PLATFORM: {platform.upper()}
NICHE: {niche.title()}
TONE: {tone}

SCRIPT CONTEXT:
{script[:200]}...

TASK: Generate 8-10 CTA variations for this {platform} video in the {niche} niche.

Requirements:
- {platform_ctas.get(platform.lower(), "Platform-appropriate format")}
- Natural, not cringe or pushy
- Match the {tone} tone
- Specific to {niche} audience
- Value-driven (what's in it for viewer)
- Mix of subscribe/follow, engagement, and save/bookmark

Examples of good CTAs:
- "If this feels like your kind of [niche], hit follow for more"
- "Save this for when you need [value]"
- "Comment your favorite [thing] below"
- "Subscribe for weekly [niche] tips"

Output: Just numbered list of CTA variations."""

    return [
        {"role": "system", "content": CTA_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

