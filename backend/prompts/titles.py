from typing import List, Dict

TITLE_SYSTEM_PROMPT = """You are TitleMaster, an expert at crafting viral, SEO-optimized titles for video content.

ABSOLUTE PROHIBITION - NO EMOJIS EVER:
- NEVER use emojis, emoji symbols, Unicode emoji characters, or any pictorial symbols
- NEVER use: 😀 😊 🎉 ✨ 💡 🚀 ❤️ 💯 👍 👎 🎬 📱 💪 🔥 ⭐ 🌟 💎 🎯 or ANY similar characters
- Use ONLY plain text: letters, numbers, and basic punctuation marks (.,!?;:)
- Express emotions, excitement, or emphasis using WORDS only, never symbols
- This is a strict, non-negotiable requirement - emojis are completely forbidden

CORE PRINCIPLES:
1. First 50 characters are CRITICAL (what shows in search/feeds)
2. Include target keywords naturally
3. Create curiosity gap without clickbait
4. Platform-optimized length and style
5. Multiple variations for A/B testing

PLATFORM RULES:
- YouTube: 50-60 chars ideal, SEO-focused, can be longer
- TikTok: Short, punchy, trending keywords
- Instagram: Aesthetic, lifestyle-focused, text-only (NO emojis)
- LinkedIn: Professional, value-driven, no fluff

TITLE TYPES:
1. Search-Optimized: Keywords first, clear value
2. Curiosity-Driven: Question or mystery
3. Emotional: Feelings and relatability
4. Direct Value: "How to..." or "X Ways to..."
5. Controversial: Bold statement (but honest)

Output 10-15 title variations with variety."""

def build_title_prompt(
    platform: str,
    niche: str,
    hook: str,
    script: str,
    reference: str,
    rag_examples: List[Dict]
) -> List[Dict[str, str]]:
    
    # Get user's past successful titles
    past_titles = [ex['content'] for ex in rag_examples if ex.get('content_type') == 'title'][:5]
    
    platform_rules = {
        "youtube": "50-60 characters ideal. SEO-focused. Include keywords naturally.",
        "youtube_short": "Short, punchy. 40-50 chars. Hook-driven.",
        "tiktok": "Very short, trending keywords. 30-40 chars max.",
        "instagram_reel": "Aesthetic, lifestyle. 40-50 chars. Text-only, NO emojis.",
        "instagram_carousel": "Value-driven, educational. 40-50 chars. Listicle-style works.",
        "linkedin": "Professional, value-driven. 50-60 chars. No fluff.",
        "twitter_thread": "Punchy, attention-grabbing. 50-70 chars. Thread hook.",
        "pinterest": "SEO-heavy, descriptive. 60-100 chars. Search-friendly keywords.",
        "podcast_clip": "Conversational, intriguing. 40-60 chars. Highlight key insight."
    }
    
    user_prompt = f"""PLATFORM: {platform.upper()}
NICHE: {niche.title()}

HOOK:
"{hook}"

SCRIPT SUMMARY:
{script[:200]}...

REFERENCE:
"{reference}"

YOUR PAST TOP-PERFORMING TITLES (for style reference):
{chr(10).join(f'{i+1}. "{title}"' for i, title in enumerate(past_titles)) if past_titles else "No past titles available. Create fresh, engaging titles."}

TASK: Generate 12-15 title variations for this {platform} video.

Requirements:
- {platform_rules.get(platform.lower(), "Optimize for platform best practices")}
- Mix of search-optimized, curiosity-driven, and emotional titles
- Include relevant keywords for {niche}
- First 50 characters must grab attention
- Vary the angle (don't repeat same pattern)

Output format: Just numbered list (1. Title here)

FINAL REMINDER: ABSOLUTELY NO EMOJIS. Use plain text only. Express everything with words."""

    return [
        {"role": "system", "content": TITLE_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

