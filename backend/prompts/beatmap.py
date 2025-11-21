from typing import List, Dict

BEATMAP_SYSTEM_PROMPT = """You are BeatMaster, an expert at structuring videos for maximum retention.

ABSOLUTE PROHIBITION - NO EMOJIS EVER:
- NEVER use emojis, emoji symbols, Unicode emoji characters, or any pictorial symbols
- NEVER use: 😀 😊 🎉 ✨ 💡 🚀 ❤️ 💯 👍 👎 🎬 📱 💪 🔥 ⭐ 🌟 💎 🎯 or ANY similar characters
- Use ONLY plain text: letters, numbers, and basic punctuation marks (.,!?;:)
- Express emotions, excitement, or emphasis using WORDS only, never symbols
- This is a strict, non-negotiable requirement - emojis are completely forbidden

CORE PRINCIPLES:
1. First 3 seconds = CRITICAL (80% decide here)
2. Pattern interrupt in first 3s
3. Value delivery every 3-5 seconds
4. Build to satisfying conclusion or loop
5. Platform-optimized pacing

RETENTION STRUCTURE:
- 0-3s: Pattern interrupt / Hook
- 3-8s: Promise / Value prop
- 8-20s: Delivery / Main content
- Last 3-5s: CTA or satisfying loop

BEAT MAP FORMAT:
Each beat needs:
- Timestamp
- What happens
- Why it keeps watching
- Visual cue (if applicable)"""

def build_beatmap_prompt(
    platform: str,
    duration: int,
    script: str,
    hook: str
) -> List[Dict[str, str]]:
    
    platform_pacing = {
        "tiktok": "FAST - New beat every 2-3 seconds",
        "youtube_short": "Medium-fast - Beat every 3-4 seconds",
        "instagram_reel": "Medium - Beat every 4-5 seconds",
        "instagram_carousel": "Slide-based - Each slide is a beat (5-7 seconds per slide)",
        "youtube": "Variable - Can be slower, build narrative",
        "linkedin": "Professional pacing - Beat every 5-6 seconds",
        "twitter_thread": "Tweet-paced - Each tweet is a beat (quick, punchy)",
        "pinterest": "Visual-focused - Beat every 4-5 seconds",
        "podcast_clip": "Conversational - Natural speech pacing, key moments as beats"
    }
    
    user_prompt = f"""PLATFORM: {platform.upper()}
DURATION: {duration} seconds

HOOK:
"{hook}"

SCRIPT:
{script}

TASK: Create a beat map / retention structure for this {duration}-second {platform} video.

Structure:
- {platform_pacing.get(platform.lower(), "Optimize pacing for platform")}
- Break into 4-8 distinct beats
- Each beat: timestamp, what happens, why it keeps watching

Required beats:
1. 0-3s: Pattern interrupt / Hook
2. 3-8s: Promise / Value proposition
3. 8-{duration-5}s: Main content delivery
4. Last 3-5s: CTA or satisfying conclusion

For each beat, provide:
- Timestamp range
- What happens (action/content)
- Why it keeps watching (retention hook)
- Visual cue suggestion (if applicable)

Output format: Structured beat map with timestamps.

FINAL REMINDER: ABSOLUTELY NO EMOJIS. Use plain text only. Express everything with words."""

    return [
        {"role": "system", "content": BEATMAP_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

