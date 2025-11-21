from typing import List, Dict

SHOTLIST_SYSTEM_PROMPT = """You are ShotDirector, a cinematographer for short-form video creators.

CRITICAL: DO NOT USE EMOJIS OR EMOJI SYMBOLS IN YOUR OUTPUT. Use plain text only. No emojis, no symbols, just words.

You design shot lists that are:
- Simple enough for solo creators with a phone
- Vertically framed (9:16 aspect ratio)
- 3-8 shots per short (too many = jarring)
- Realistic (no crane shots, just phone + tripod/gimbal)

Shot types:
- WIDE: Establish scene/setting
- MEDIUM: Waist-up, main action
- CLOSE-UP: Face, hands, product details
- POV: First-person view
- B-ROLL: Supporting visuals, cutaways

Camera movements (keep simple):
- Static: Locked on tripod
- Slow push-in: Gimbal move toward subject
- Pan: Horizontal sweep
- Handheld: Natural movement, following action

Each shot needs:
1. Shot number
2. Type + framing
3. Camera position & movement
4. What we see (subject + action)
5. Duration (seconds)"""

def build_shotlist_prompt(
    platform: str,
    duration: int,
    script: str,
    reference: str
) -> List[Dict[str, str]]:
    
    user_prompt = f"""PLATFORM: {platform}
VIDEO DURATION: {duration} seconds

SCRIPT:
{script}

VISUAL REFERENCE:
"{reference}"

TASK: Create a shot list for this video.

Requirements:
- Total duration = {duration}s
- 4-7 distinct shots (don't over-cut)
- All shots are 9:16 vertical (phone format)
- Simple setups (phone on tripod/gimbal, no complex rigs)
- Match the script's pacing and content

For each shot, provide:
1. Shot # (e.g., "Shot 1")
2. Type & Framing (e.g., "CLOSE-UP")
3. Camera Setup (e.g., "Phone on tripod, static")
4. Description (what we see, what happens)
5. Duration (in seconds)

Be specific but achievable for a solo creator."""

    return [
        {"role": "system", "content": SHOTLIST_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

