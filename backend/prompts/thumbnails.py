from typing import List, Dict

THUMBNAIL_SYSTEM_PROMPT = """You are ThumbnailDesigner, an expert at creating thumbnail concepts for video content.

CRITICAL: DO NOT USE EMOJIS OR EMOJI SYMBOLS IN YOUR OUTPUT. Use plain text only. No emojis, no symbols, just words.

CORE PRINCIPLES:
1. Thumbnails are click magnets - must stand out
2. Clear focal point (face, product, text)
3. High contrast for small sizes
4. Emotion-driven (curiosity, surprise, relatability)
5. Platform-optimized (YouTube vs TikTok vs IG)

PLATFORM RULES:
- YouTube: 1280x720, can have text overlay, face optional
- TikTok/Instagram: 9:16 vertical, minimal text, aesthetic focus
- LinkedIn: Professional, clean, text-friendly

THUMBNAIL ELEMENTS:
1. Visual: Main image/subject
2. Text overlay: 2-4 words max
3. Colors: High contrast, emotion-driven
4. Composition: Rule of thirds, focal point
5. Emotion: What feeling does it evoke?"""

def build_thumbnail_prompt(
    platform: str,
    niche: str,
    title: str,
    hook: str,
    reference: str
) -> List[Dict[str, str]]:
    
    platform_rules = {
        "youtube": "1280x720 horizontal. Text overlay ok (2-4 words). Face optional but recommended.",
        "youtube_short": "9:16 vertical. Minimal text. Aesthetic focus.",
        "tiktok": "9:16 vertical. No text overlay. Visual-first.",
        "instagram_reel": "9:16 vertical. Aesthetic, lifestyle. Minimal text.",
        "instagram_carousel": "1:1 or 4:5 vertical. Text-heavy cover slide. Educational aesthetic.",
        "linkedin": "1200x627 or square. Professional. Text overlay ok.",
        "twitter_thread": "16:9 or square. Bold text overlay. Eye-catching for feed scroll.",
        "pinterest": "2:3 vertical (1000x1500). Text overlay important. Search-friendly design.",
        "podcast_clip": "1:1 square. Waveform visual or speaker photo. Show name prominent."
    }
    
    user_prompt = f"""PLATFORM: {platform.upper()}
NICHE: {niche.title()}

TITLE:
"{title}"

HOOK:
"{hook}"

REFERENCE:
"{reference}"

TASK: Generate 5 thumbnail concept ideas for this {platform} video.

For each concept, provide:
1. Main Visual: What's the focal point? (face, product, scene, etc.)
2. Text Overlay: 2-4 words (if applicable)
3. Color Palette: Primary colors and mood
4. Composition: Layout description
5. Emotion: What feeling does it evoke?
6. Why It Works: Brief rationale

Requirements:
- {platform_rules.get(platform.lower(), "Optimize for platform")}
- High contrast for visibility
- Clear focal point
- Emotion-driven
- Stand out in feed/search

Output format: Numbered list with detailed descriptions."""

    return [
        {"role": "system", "content": THUMBNAIL_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

