from typing import List, Dict

SCRIPT_SYSTEM_PROMPT = """You are ScriptPro, an expert short-form video scriptwriter.

ABSOLUTE PROHIBITION - NO EMOJIS EVER:
- NEVER use emojis, emoji symbols, Unicode emoji characters, or any pictorial symbols
- NEVER use: 😀 😊 🎉 ✨ 💡 🚀 ❤️ 💯 👍 👎 🎬 📱 💪 🔥 ⭐ 🌟 💎 🎯 or ANY similar characters
- Use ONLY plain text: letters, numbers, and basic punctuation marks (.,!?;:)
- Express emotions, excitement, or emphasis using WORDS only, never symbols
- This is a strict, non-negotiable requirement - emojis are completely forbidden

You write scripts that:
- Are spoken naturally (not read like an essay or TV ad)
- Keep viewers hooked every 3 seconds
- Use short sentences (5-10 words ideal)
- Include visual cues in [brackets]
- Match the platform's pacing
- Match the creator's personality perfectly
- Sound like a real person talking, not a commercial

Structure: HOOK → VALUE → CTA
- Hook (0-3s): Grab attention, promise value
- Value (bulk): Deliver on promise, keep pacing fast
- CTA (last 5s): Clear next step

You write for SPOKEN delivery:
✓ "Here's what happened" 
✓ "So I was thinking..."
✓ "Let me tell you about..."
✗ "The following events transpired"
✗ "In today's video, we will discuss..."

Platform pacing:
- TikTok: 150-180 words/min (FAST)
- YouTube Shorts: 130-150 words/min
- Instagram Reels: 120-140 words/min

    PERSONALITY STYLES:
    - friendly: "Hi girly!", "Hey everyone!", warm, conversational, like talking to a friend
    - educational: "Have you heard...", "Let me explain...", informative, expert but approachable
    - motivational: Inspiring, empowering, "You can do this!", uplifting
    - funny: Humorous, playful, "Wait until you see...", entertaining
    - rage_bait: Provocative, "Hot take:", controversial but honest
    - storytelling: "So I was...", "Let me tell you about...", narrative-driven
    - authentic: "Real talk:", "I need to be honest...", raw, unfiltered
    - luxury: High-end, premium, aspirational, sophisticated
    - minimalist: Simple, clean, focused, refined
    - energetic: High energy, fast-paced, enthusiastic, exciting
    - calm: Peaceful, zen, soothing, meditative
    - quirky: Unique, eccentric, unconventional, offbeat
    - professional: Business-like, formal, polished, corporate
    - relatable: Everyday person, relatable struggles, normal life"""

def build_script_prompt(
    platform: str,
    niche: str,
    duration: int,
    hook: str,
    personality: str,
    audience: List[str],
    reference: str,
    rag_examples: List[Dict],
    has_voiceover: bool = True
) -> List[Dict[str, str]]:
    
    # Get user's past scripts
    past_scripts = [ex['content'] for ex in rag_examples if ex.get('content_type') == 'script'][:3]
    
    wpm_map = {
        "tiktok": 165,
        "youtube_short": 140,
        "instagram_reel": 130,
        "instagram_carousel": 100,  # Slower for reading slides
        "youtube": 130,
        "linkedin": 120,
        "twitter_thread": 150,  # Punchy, fast reading
        "pinterest": 110,  # Descriptive, searchable
        "podcast_clip": 145  # Conversational pace
    }
    wpm = wpm_map.get(platform.lower(), 140)
    target_words = int((duration / 60) * wpm)
    
    personality_guides = {
        "friendly": "Use warm, conversational language. Start with 'Hi girly!', 'Hey everyone!', or 'So I was thinking...'. Make it feel like you're talking to a friend, not making an ad.",
        "educational": "Sound like an expert sharing knowledge. Use 'Have you heard...', 'Did you know...', 'Let me explain...'. Informative but approachable.",
        "motivational": "Inspiring and empowering. Use uplifting language. 'You can do this!', 'Here's how to...'. Make them feel capable.",
        "funny": "Humorous and playful. 'Wait until you see...', 'This is wild!'. Entertaining and light-hearted throughout.",
        "rage_bait": "Provocative but honest. 'Hot take:', 'Unpopular opinion:', 'This will make you angry...'. Controversial but authentic.",
        "storytelling": "Narrative-driven. 'So I was...', 'Let me tell you about...', 'This happened to me...'. Personal stories and experiences.",
        "authentic": "Raw and unfiltered. 'Real talk:', 'I need to be honest...', 'No BS, here's...'. Vulnerable and genuine, no fluff."
    }
    
    audience_guides = {
        "gen_z": "Use Gen-Z language, fast-paced, trend references. Keep it fresh and relatable.",
        "millennials": "Nostalgic references, value-driven. Relatable to their life stage.",
        "gen_x": "Practical, no-nonsense, independent. Authentic and straightforward.",
        "professionals": "Career-focused, productivity-oriented, efficient.",
        "students": "Study-focused, budget-conscious, relatable struggles.",
        "parents": "Family-focused, time-constrained, practical advice.",
        "creators": "Industry-focused, growth-minded, trend-aware.",
        "general": "Broad appeal, accessible language.",
        "female": "Consider female perspectives, interests, and communication styles. Use inclusive language.",
        "male": "Consider male perspectives, interests, and communication styles. Use inclusive language.",
        "all": "Gender-neutral language, appeal to all genders equally."
    }
    
    # Separate age/demographic audiences from gender
    age_audiences = [a for a in audience if a in ["gen_z", "millennials", "gen_x", "professionals", "students", "parents", "creators", "general"]]
    gender_audiences = [a for a in audience if a in ["female", "male", "all"]]
    
    # Build audience description
    age_desc = ", ".join([audience_guides.get(a, "") for a in age_audiences]) if age_audiences else "Broad demographic appeal"
    gender_desc = ", ".join([audience_guides.get(a, "") for a in gender_audiences]) if gender_audiences else "All genders"
    
    personality_guide = personality_guides.get(personality, "Be authentic and conversational")
    audience_guide = f"{age_desc}. {gender_desc}."
    
    user_prompt = f"""PLATFORM: {platform.upper()}
NICHE: {niche}
DURATION: {duration} seconds
TARGET WORD COUNT: ~{target_words} words
PERSONALITY: {personality.upper()} - {personality_guide}
AUDIENCE: {", ".join(audience).upper()} - {audience_guide}

CHOSEN HOOK:
"{hook}"

CONTENT REFERENCE:
"{reference}"

YOUR PAST SCRIPT STYLE (for reference):
{chr(10).join(f'--- Example {i+1} ---{chr(10)}{script[:200]}...' for i, script in enumerate(past_scripts)) if past_scripts else "No past scripts available. Write in a natural, conversational style."}

TASK: {'Write a voiceover script' if has_voiceover else 'Create text overlays and captions'} for this {duration}-second {platform} video.

{'VOICEOVER MODE:' if has_voiceover else 'SILENT MODE (NO TALKING):'}
{('Write a spoken script with voiceover/narration. The script will be read aloud.' if has_voiceover else 'Create text overlays and captions. NO voiceover or talking. Use on-screen text, captions, and visual storytelling. Format as text overlays with timing.')}

CRITICAL REQUIREMENTS:
1. Start with the hook (you can refine it slightly to match personality)
2. Match the {personality} personality: {personality_guide}
3. Target audiences: {", ".join(audience)} - {audience_guide}
{('4. Natural, conversational language - NOT like a TV ad or commercial' if has_voiceover else '4. Text overlays should be short, punchy, and easy to read (3-7 words per overlay)')}
{('5. Short sentences, easy to speak' if has_voiceover else '5. Use text overlays, captions, and on-screen text only')}
6. Include [visual cues] for what's on screen
7. Add (timestamp) markers every few lines
8. Build to a clear CTA at the end
{('9. Sound like a real person talking, not reading a script' if has_voiceover else '9. NO voiceover or narration - text and visuals only')}
10. Use personality-appropriate phrases naturally

{('Target ' + str(target_words) + ' words for ' + str(duration) + 's at ' + str(wpm) + ' WPM.' if has_voiceover else 'Create 8-15 text overlays with timing. Each overlay should be 3-7 words.')}

Output: {'Just the script, formatted with timestamps.' if has_voiceover else 'Text overlays with timestamps, formatted as: [0:00] Text overlay here'}

FINAL REMINDER: ABSOLUTELY NO EMOJIS. Use plain text only. Express everything with words."""

    return [
        {"role": "system", "content": SCRIPT_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]
