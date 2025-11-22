"""
Content Calendar AI Prompt Templates
Generate strategic content calendars with themed weeks and content mix
"""

from typing import List, Dict
from datetime import datetime, timedelta

CALENDAR_SYSTEM_PROMPT = """You are ContentCalendarPro, an expert at strategic content planning for creators.

ABSOLUTE PROHIBITION - NO EMOJIS EVER:
- NEVER use emojis, emoji symbols, Unicode emoji characters, or any pictorial symbols
- NEVER use: 😀 😊 🎉 ✨ 💡 🚀 ❤️ 💯 👍 👎 🎬 📱 💪 🔥 ⭐ 🌟 💎 🎯 or ANY similar characters
- Use ONLY plain text: letters, numbers, and basic punctuation marks (.,!?;:)
- Express emotions, excitement, or emphasis using WORDS only, never symbols
- This is a strict, non-negotiable requirement - emojis are completely forbidden

CORE PRINCIPLES:
1. Balance content types (80% value, 20% promotional)
2. Create themed weeks for cohesion
3. Mix formats (tutorials, stories, behind-the-scenes, educational)
4. Include trending topic opportunities
5. Suggest optimal posting times based on platform
6. Maintain consistency while avoiding burnout

CONTENT MIX STRATEGY:
- Educational (40%): Teach something valuable
- Entertaining (30%): Stories, humor, relatable content
- Behind-the-Scenes (15%): Show the process, authentic moments
- Promotional (10%): Products, services, partnerships
- Community (5%): Q&A, polls, engagement-focused

THEME OPPORTUNITIES:
- Weekly themes: "Transformation Week", "Behind-the-Scenes Week", "Educational Series Week"
- Monthly arcs: Long-form content that builds over time
- Event-based: Holidays, trending moments, platform features"""

def build_calendar_prompt(
    platform: str,
    niche: str,
    duration_days: int,
    frequency: int,
    themes: List[str] = None,
    user_patterns: Dict = None
) -> List[Dict[str, str]]:
    """Build prompt for generating content calendar"""
    
    # Analyze user patterns if available
    pattern_analysis = ""
    if user_patterns:
        top_types = user_patterns.get('top_types', [])
        best_days = user_patterns.get('best_days', [])
        successful_hooks = user_patterns.get('successful_hooks', [])[:3]
        
        pattern_analysis = f"""
USER'S TOP PERFORMING PATTERNS:
- Best performing content types: {', '.join(top_types) if top_types else 'Varied'}
- Peak engagement days: {', '.join(best_days) if best_days else 'All days'}
- Successful hook examples:
  {chr(10).join(f'  • {hook[:100]}' for hook in successful_hooks) if successful_hooks else '  • None available'}
"""
    
    # Calculate posting schedule
    total_posts = duration_days * frequency
    weeks = duration_days // 7
    remaining_days = duration_days % 7
    
    # Build themed weeks
    theme_suggestions = themes or []
    if not theme_suggestions:
        theme_suggestions = [
            "Educational Week",
            "Behind-the-Scenes Week", 
            "Community Engagement Week",
            "Trending Topics Week",
            "Personal Stories Week"
        ]
    
    user_prompt = f"""PLATFORM: {platform.upper()}
NICHE: {niche.title()}
DURATION: {duration_days} days ({weeks} weeks, {remaining_days} days)
FREQUENCY: {frequency} posts per day
TOTAL POSTS: {total_posts}
{pattern_analysis}
THEMES: {', '.join(theme_suggestions) if theme_suggestions else 'Varied'}

TASK: Create a strategic {duration_days}-day content calendar for {platform}.

REQUIREMENTS:
1. Daily content ideas with dates
2. Balance content types (80% value, 20% promotional)
3. Create themed weeks for cohesion
4. Mix formats (tutorials, stories, behind-the-scenes, educational)
5. Include trending topic opportunities
6. Suggest posting times based on {platform} best practices
7. Strategic variety (avoid repetition, build momentum)

CONTENT MIX:
- Educational (40%): {int(total_posts * 0.4)} posts
- Entertaining (30%): {int(total_posts * 0.3)} posts
- Behind-the-Scenes (15%): {int(total_posts * 0.15)} posts
- Promotional (10%): {int(total_posts * 0.1)} posts
- Community (5%): {int(total_posts * 0.05)} posts

For each day, provide:
1. Date (Day, Month DD)
2. Content type (Educational, Entertaining, Behind-the-Scenes, Promotional, Community)
3. Hook idea (attention-grabbing first line)
4. Topic/theme
5. Suggested posting time (if {frequency} posts/day, suggest times)
6. Strategic note (why this fits the calendar, theme connection, etc.)

Format as a structured calendar with daily entries.

FINAL REMINDER: ABSOLUTELY NO EMOJIS. Use plain text only. Express everything with words."""

    return [
        {"role": "system", "content": CALENDAR_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

