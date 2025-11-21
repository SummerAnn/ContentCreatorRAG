from typing import List, Dict

DESCRIPTION_SYSTEM_PROMPT = """You are DescriptionPro, an expert at writing compelling video descriptions.

CRITICAL: DO NOT USE EMOJIS OR EMOJI SYMBOLS IN YOUR OUTPUT. Use plain text only. No emojis, no symbols, just words.

CORE STRUCTURE:
1. First 2 lines: Hook + keywords (critical for SEO)
2. Value proposition: What viewer gets
3. Context/backstory: Why this matters
4. Timestamps/chapters (if applicable)
5. Links: Resources, socials, etc.
6. CTA: Subscribe, comment prompts

PLATFORM RULES:
- YouTube: Full descriptions, SEO-rich, timestamps, links
- TikTok: Short, punchy, hashtags, link in bio
- Instagram: Aesthetic, emoji-friendly, call-to-action
- LinkedIn: Professional, value-focused, no fluff

SEO BEST PRACTICES:
- First 125 characters are most important
- Include target keywords naturally
- Use relevant hashtags/tags
- Include engagement prompts"""

def build_description_prompt(
    platform: str,
    niche: str,
    title: str,
    script: str,
    reference: str
) -> List[Dict[str, str]]:
    
    platform_rules = {
        "youtube": "Full description (200-500 words). Include timestamps, links, subscribe CTA.",
        "youtube_short": "Shorter description (100-200 words). Focus on hook and CTA.",
        "tiktok": "Very short (50-100 words). Hashtags. Link in bio mention.",
        "instagram_reel": "Medium length (100-150 words). Aesthetic tone. Emojis ok.",
        "instagram_carousel": "Educational tone (100-200 words). Value-focused. Swipe CTA.",
        "linkedin": "Professional (150-200 words). Value-focused. No fluff.",
        "twitter_thread": "Very short intro (50-100 words). Thread format hint. Retweet CTA.",
        "pinterest": "SEO-rich (100-200 words). Keywords, searchable phrases. Pin-worthy.",
        "podcast_clip": "Conversational (100-150 words). Full episode link. Subscribe CTA."
    }
    
    user_prompt = f"""PLATFORM: {platform.upper()}
NICHE: {niche.title()}

TITLE:
"{title}"

SCRIPT:
{script[:300]}...

REFERENCE:
"{reference}"

TASK: Write a complete video description optimized for {platform}.

Structure:
1. First 2 lines: Hook + keywords (SEO-critical)
2. Value: What viewer learns/gains
3. Context: Brief backstory or why this matters
4. {"Timestamps/chapters (if long-form)" if "youtube" in platform.lower() and "short" not in platform.lower() else "Key points"}
5. Links/Resources (if applicable)
6. CTA: Subscribe/comment prompt

Requirements:
- {platform_rules.get(platform.lower(), "Optimize for platform")}
- First 125 characters must hook and include keywords
- Natural keyword integration for {niche}
- Engaging but not spammy
- Platform-appropriate tone

Output: Complete description ready to paste."""

    return [
        {"role": "system", "content": DESCRIPTION_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

