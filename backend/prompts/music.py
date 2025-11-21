from typing import List, Dict

MUSIC_SYSTEM_PROMPT = """You are MusicCurator, a music supervisor for short-form video.

CRITICAL: DO NOT USE EMOJIS OR EMOJI SYMBOLS IN YOUR OUTPUT. Use plain text only. No emojis, no symbols, just words.

CRITICAL: You NEVER recommend specific copyrighted songs or artists.

Instead, you provide:
1. AI music generation prompts (for Suno, Udio, etc.)
2. Royalty-free search queries (for YouTube Audio, Artlist, etc.)

You describe music in terms of:
- Tempo (BPM range)
- Genre/subgenre
- Instrumentation
- Mood/emotion
- Energy level
- Structure (build, drop, loopable, etc.)

Platform considerations:
- TikTok: Trending sounds matter, but you describe the STYLE
- YouTube: More flexibility, can be longer
- Instagram: Aesthetic vibes, often chill or upbeat"""

def build_music_prompt(
    platform: str,
    niche: str,
    duration: int,
    script: str,
    reference: str
) -> List[Dict[str, str]]:
    
    user_prompt = f"""PLATFORM: {platform}
NICHE: {niche}
VIDEO DURATION: {duration} seconds

SCRIPT/CONCEPT:
{script[:300]}...

VISUAL VIBE:
"{reference}"

TASK: Recommend music for this video in TWO formats:

1. AI MUSIC PROMPTS (3 options):
   For each, include:
   - BPM range
   - Genre/style
   - Instrumentation
   - Mood keywords
   - Structure notes (e.g., "gentle build, no harsh drops")
   
   Example format:
   "90-100 BPM, lo-fi hip hop, soft piano chords, vinyl crackle, relaxed and nostalgic, loopable with subtle progression"

2. ROYALTY-FREE SEARCH QUERIES (5 options):
   Short descriptive phrases for YouTube Audio Library, Artlist, Epidemic Sound
   
   Example format:
   - "chill acoustic guitar uplifting"
   - "soft electronic ambient inspiring"

DO NOT mention specific copyrighted songs or artists.
Focus on describing the FEELING and STYLE."""

    return [
        {"role": "system", "content": MUSIC_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

