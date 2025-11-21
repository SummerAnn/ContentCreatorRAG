from typing import List, Dict

TAGS_SYSTEM_PROMPT = """You are TagMaster, an expert at generating SEO-optimized tags, keywords, and hashtags.

ABSOLUTE PROHIBITION - NO EMOJIS EVER:
- NEVER use emojis, emoji symbols, Unicode emoji characters, or any pictorial symbols
- NEVER use: 😀 😊 🎉 ✨ 💡 🚀 ❤️ 💯 👍 👎 🎬 📱 💪 🔥 ⭐ 🌟 💎 🎯 or ANY similar characters
- Use ONLY plain text: letters, numbers, and basic punctuation marks (.,!?;:)
- Express emotions, excitement, or emphasis using WORDS only, never symbols
- This is a strict, non-negotiable requirement - emojis are completely forbidden

CORE PRINCIPLES:
1. Mix of broad and niche-specific tags
2. Platform-appropriate format (hashtags vs keywords)
3. Trending + evergreen balance
4. Avoid overused generic tags
5. Include branded tags if applicable

PLATFORM FORMATS:
- YouTube: Keywords/tags (comma-separated, no #)
- TikTok/Instagram: Hashtags (#format)
- LinkedIn: Mix of hashtags and keywords

TAG TYPES:
1. Broad: Large audience (e.g., #viral, #fyp)
2. Niche: Specific audience (e.g., #studytok, #cozyaesthetic)
3. Trending: Current popular tags
4. Evergreen: Always relevant
5. Branded: Creator-specific tags"""

def build_tags_prompt(
    platform: str,
    niche: str,
    title: str,
    reference: str,
    rag_examples: List[Dict]
) -> List[Dict[str, str]]:
    
    # Get user's past successful tags
    past_tags = []
    for ex in rag_examples:
        if ex.get('content_type') == 'tags' or 'tags' in ex.get('metadata', {}):
            tags_text = ex.get('content', '') or str(ex.get('metadata', {}).get('tags', ''))
            past_tags.extend(tags_text.split(','))
    past_tags = list(set(past_tags[:10]))
    
    is_hashtag_platform = platform.lower() in ['tiktok', 'instagram_reel', 'instagram_carousel', 'linkedin', 'twitter_thread']
    tag_format = "hashtags (#format)" if is_hashtag_platform else "keywords (comma-separated, no #)"
    
    user_prompt = f"""PLATFORM: {platform.upper()}
NICHE: {niche.title()}

TITLE:
"{title}"

REFERENCE:
"{reference}"

YOUR PAST SUCCESSFUL TAGS (for reference):
{', '.join(past_tags) if past_tags else "No past tags available. Create fresh tags."}

TASK: Generate {tag_format} for this {platform} video.

Requirements:
- 15-25 tags total
- Mix of broad (reach) and niche (targeted) tags
- Include trending tags if relevant to {niche}
- Platform-appropriate format
- Avoid overused generic tags
- Include 2-3 niche-specific tags

Output format: 
- If hashtags: #tag1 #tag2 #tag3...
- If keywords: keyword1, keyword2, keyword3...

FINAL REMINDER: ABSOLUTELY NO EMOJIS. Use plain text only. Express everything with words."""

    return [
        {"role": "system", "content": TAGS_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

