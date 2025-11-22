"""
Strategic Hashtag Engine - Enhanced version with 30/50/20 mix
30% High-volume (viral potential)
50% Medium-volume (niche community)
20% Low-volume (highly targeted)
"""

from typing import List, Dict
from prompts.tags import TAGS_SYSTEM_PROMPT

STRATEGIC_TAGS_SYSTEM_PROMPT = """You are StrategicTagMaster, an expert at generating strategic hashtag mixes for maximum reach and engagement.

ABSOLUTE PROHIBITION - NO EMOJIS EVER:
- NEVER use emojis, emoji symbols, Unicode emoji characters, or any pictorial symbols
- NEVER use: 😀 😊 🎉 ✨ 💡 🚀 ❤️ 💯 👍 👎 🎬 📱 💪 🔥 ⭐ 🌟 💎 🎯 or ANY similar characters
- Use ONLY plain text: letters, numbers, and basic punctuation marks (.,!?;:)
- Express emotions, excitement, or emphasis using WORDS only, never symbols
- This is a strict, non-negotiable requirement - emojis are completely forbidden

STRATEGIC MIX FORMULA:
1. Viral Tags (30%): High-volume, trending, broad reach
   - Examples: Platform-wide trends, mega hashtags (#fyp, #viral, #foryou)
   - Purpose: Maximum discovery potential
   - Volume: 10M+ posts

2. Community Tags (50%): Medium-volume, niche-specific, engaged audience
   - Examples: Niche communities (#studytok, #cozyaesthetic, #fitness)
   - Purpose: Targeted, engaged viewers
   - Volume: 100K - 10M posts

3. Niche Tags (20%): Low-volume, highly targeted, less competition
   - Examples: Specific interests (#minimalistcooking, #budgettravel)
   - Purpose: Highly relevant audience, easier to rank
   - Volume: < 100K posts

PLATFORM STRATEGIES:
- TikTok: Mix trending sounds + niche + micro-niches
- Instagram: Community focus (60%), viral (25%), niche (15%)
- YouTube: Keywords + trending topics + niche communities
- LinkedIn: Professional communities + industry tags + trending topics"""

def build_strategic_tags_prompt(
    platform: str,
    niche: str,
    title: str,
    reference: str,
    goal: str = "discovery",  # "discovery", "community", "viral"
    rag_examples: List[Dict] = None
) -> List[Dict[str, str]]:
    """Build prompt for strategic hashtag generation"""
    
    # Get user's past successful tags
    past_tags = []
    if rag_examples:
        for ex in rag_examples:
            if ex.get('content_type') == 'tags' or 'tags' in ex.get('metadata', {}):
                tags_text = ex.get('content', '') or str(ex.get('metadata', {}).get('tags', ''))
                past_tags.extend(tags_text.replace('#', '').split())
        past_tags = list(set(past_tags[:10]))
    
    is_hashtag_platform = platform.lower() in ['tiktok', 'instagram_reel', 'instagram_carousel', 'linkedin', 'twitter_thread']
    tag_format = "hashtags (#format)" if is_hashtag_platform else "keywords (comma-separated, no #)"
    
    # Adjust mix based on goal
    if goal == "viral":
        viral_pct, community_pct, niche_pct = 40, 40, 20
    elif goal == "community":
        viral_pct, community_pct, niche_pct = 20, 60, 20
    else:  # discovery (default)
        viral_pct, community_pct, niche_pct = 30, 50, 20
    
    total_tags = 20  # Total tags to generate
    viral_count = int(total_tags * viral_pct / 100)
    community_count = int(total_tags * community_pct / 100)
    niche_count = total_tags - viral_count - community_count
    
    user_prompt = f"""PLATFORM: {platform.upper()}
NICHE: {niche.title()}
GOAL: {goal.upper()}

TITLE:
"{title}"

REFERENCE:
"{reference}"

YOUR PAST SUCCESSFUL TAGS (for reference):
{', '.join(f'#{tag}' if is_hashtag_platform else tag for tag in past_tags) if past_tags else 'No past tags available. Create fresh strategic tags.'}

TASK: Generate a strategic {tag_format} mix for this {platform} content.

STRATEGIC MIX (Total: {total_tags} tags):
1. VIRAL TAGS ({viral_count} tags, {viral_pct}%): High-volume, trending, maximum reach
   - Platform-wide trends
   - Mega hashtags for discovery
   - Currently trending topics
   - Volume: 10M+ posts

2. COMMUNITY TAGS ({community_count} tags, {community_pct}%): Medium-volume, niche communities, engaged audience
   - Niche-specific communities
   - Active engagement groups
   - Relevant subcommunities
   - Volume: 100K - 10M posts

3. NICHE TAGS ({niche_count} tags, {niche_pct}%): Low-volume, highly targeted, less competition
   - Specific interests within {niche}
   - Micro-niches
   - Highly relevant, easier to rank
   - Volume: < 100K posts

OUTPUT FORMAT:
Viral Tags ({viral_count}):
#tag1 #tag2 #tag3...

Community Tags ({community_count}):
#tag1 #tag2 #tag3...

Niche Tags ({niche_count}):
#tag1 #tag2 #tag3...

Total: {total_tags} tags
Strategy: Optimized for {goal} goal

FINAL REMINDER: ABSOLUTELY NO EMOJIS. Use plain text only. Express everything with words."""

    return [
        {"role": "system", "content": STRATEGIC_TAGS_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

