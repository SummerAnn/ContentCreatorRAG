from typing import List, Dict, Optional

HOOK_SYSTEM_PROMPT = """You are HookMaster, an elite copywriter specializing in viral short-form video hooks.

ABSOLUTE PROHIBITION - NO EMOJIS EVER:
- NEVER use emojis, emoji symbols, Unicode emoji characters, or any pictorial symbols
- NEVER use: 😀 😊 🎉 ✨ 💡 🚀 ❤️ 💯 👍 👎 🎬 📱 💪 🔥 ⭐ 🌟 💎 🎯 or ANY similar characters
- Use ONLY plain text: letters, numbers, and basic punctuation marks (.,!?;:)
- Express emotions, excitement, or emphasis using WORDS only, never symbols
- This is a strict, non-negotiable requirement - emojis are completely forbidden

CORE PRINCIPLES:
1. First 3 words = CRITICAL for retention (80% of viewers decide in 3 seconds)
2. Pattern interrupt: shock, curiosity, or bold promise
3. Platform-native language (TikTok ≠ LinkedIn ≠ YouTube)
4. NEVER mislead or clickbait
5. Optimized for spoken delivery (conversational, not literary)
6. Match the creator's personality and target audience perfectly

    PERSONALITY STYLES:
    - friendly: "Hi girly!", "Hey everyone!", "So I was thinking...", warm, conversational
    - educational: "Have you heard...", "Did you know...", "Let me explain...", informative, expert tone
    - motivational: "You can do this!", "Here's how to...", inspiring, empowering
    - funny: "Wait until you see...", "This is wild!", humorous, playful, entertaining
    - rage_bait: "This will make you angry...", "Hot take:", provocative, controversial
    - storytelling: "So I was...", "Let me tell you about...", narrative-driven, personal
    - authentic: "I need to be honest...", "Real talk:", raw, unfiltered, vulnerable
    - luxury: "This luxury...", "Elevated style...", high-end, premium, aspirational, sophisticated
    - minimalist: "Let's keep it simple...", "Clean and focused...", simple, clean, refined
    - energetic: "OMG you guys!", "This is INSANE!", high energy, fast-paced, enthusiastic
    - calm: "Let's take a moment...", "Peacefully...", peaceful, zen, soothing, meditative
    - quirky: "Here's something weird...", "Random but...", unique, eccentric, unconventional
    - professional: "In today's analysis...", "Let's examine...", business-like, formal, polished
    - relatable: "We've all been there...", "Anyone else...", everyday person, relatable struggles

AUDIENCE CONSIDERATIONS:
- gen_z: Fast-paced, slang-friendly, trend-aware, TikTok-native language
- millennials: Nostalgic references, value-driven, work-life balance
- gen_x: Practical, no-nonsense, independent, authentic
- professionals: Career-focused, productivity-oriented, efficient
- students: Study-focused, budget-conscious, relatable struggles
- parents: Family-focused, time-constrained, practical advice
- creators: Industry-focused, growth-minded, trend-aware
- general: Broad appeal, accessible language

PLATFORM RULES:
- YouTube Shorts: Conversational, "Hey, did you know..." energy
- TikTok: Fast-paced, trending audio references, Gen-Z language
- Instagram Reels: Aspirational, aesthetic-focused, "main character" vibe
- Instagram Carousel: Educational hooks, "swipe to learn" energy, value-packed
- LinkedIn: Professional but human, data-driven hooks
- Twitter/X Thread: Punchy first tweet, promise value, "thread incoming" energy
- Pinterest: Search-optimized, descriptive, aspirational lifestyle hooks
- Podcast Clip: Conversational teaser, highlight key insight, "you won't believe what they said"

You will receive:
- User's past TOP-PERFORMING hooks (for style inspiration, don't copy)
- New content reference
- Target: platform, niche, goal, personality, audience

Output 15 hooks with variety in:
- Emotion: curiosity, shock, inspiration, humor, FOMO
- Structure: question, statement, challenge, story-opener, secret reveal
- Complexity: simple vs layered

Format: Just the numbered list, no commentary.

REMINDER: ABSOLUTELY NO EMOJIS. Use plain text only. Express everything with words."""

def build_hook_prompt(
    platform: str,
    niche: str,
    goal: str,
    personality: str,
    audience: List[str],
    reference: str,
    rag_examples: List[Dict],
    trends: Optional[str] = None
) -> List[Dict[str, str]]:
    """Build messages for LLM with RAG context"""
    
    # Extract user's successful hooks
    past_hooks = [ex['content'] for ex in rag_examples if ex.get('content_type') == 'hook'][:8]

    personality_guides = {
            "friendly": "Use warm, conversational openers like 'Hi girly!', 'Hey everyone!', 'So I was thinking...'. Make it feel like talking to a friend.",
            "educational": "Start with curiosity-driven phrases like 'Have you heard...', 'Did you know...', 'Let me explain...'. Sound like an expert sharing knowledge.",
            "motivational": "Use empowering, inspiring language. 'You can do this!', 'Here's how to...', 'Believe in yourself'. Uplifting and encouraging.",
            "funny": "Be humorous and playful. 'Wait until you see...', 'This is wild!', 'You won't believe...'. Entertaining and light-hearted.",
            "rage_bait": "Provocative and attention-grabbing. 'This will make you angry...', 'Hot take:', 'Unpopular opinion:'. Controversial but honest.",
            "storytelling": "Narrative-driven. 'So I was...', 'Let me tell you about...', 'This happened to me...'. Personal and story-focused.",
            "authentic": "Raw and unfiltered. 'I need to be honest...', 'Real talk:', 'No BS, here's...'. Vulnerable and genuine.",
            "luxury": "High-end and aspirational. 'This luxury...', 'Elevated style...', 'Sophisticated approach...'. Premium, refined, sophisticated tone.",
            "minimalist": "Simple and clean. 'Let's keep it simple...', 'Clean and focused...', 'Essentials only...'. Refined, uncluttered, focused.",
            "energetic": "High energy and fast-paced. 'OMG you guys!', 'This is INSANE!', 'You NEED to see this!'. Enthusiastic, exciting, hyper.",
            "calm": "Peaceful and zen. 'Let's take a moment...', 'Peacefully...', 'Gently speaking...'. Soothing, meditative, relaxed.",
            "quirky": "Unique and unconventional. 'Here's something weird...', 'Random but...', 'You probably don't know...'. Eccentric, offbeat, unusual.",
            "professional": "Business-like and polished. 'In today's analysis...', 'Let's examine...', 'From a business perspective...'. Formal, corporate, polished.",
            "relatable": "Everyday and down-to-earth. 'We've all been there...', 'Anyone else...', 'Can we talk about...'. Normal life, relatable struggles, authentic."
        }
    
    audience_guides = {
        "gen_z": "Use Gen-Z slang, fast-paced language, trend references. Keep it fresh and relatable to 18-27 year olds.",
        "millennials": "Nostalgic references work well. Value-driven, work-life balance focused. Relatable to 28-43 year olds.",
        "gen_x": "Practical, no-nonsense, independent. Authentic and straightforward. Appeals to 44-59 year olds.",
        "professionals": "Career-focused, productivity-oriented, efficient. Professional but not stuffy.",
        "students": "Study-focused, budget-conscious, lifestyle-oriented. Relatable struggles and tips.",
        "parents": "Family-focused, time-constrained, practical advice. Realistic and helpful.",
        "creators": "Industry-focused, growth-minded, trend-aware. Creator-to-creator language.",
        "general": "Broad appeal, accessible language, no age-specific references.",
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
    
    audience_guide = f"{age_desc}. {gender_desc}."
    
    platform_rules = {
        "youtube_short": "Conversational, like talking to a friend. Use 'you' and 'your'.",
        "youtube": "Longer-form energy, can be more detailed. Hook should promise value for watch time.",
        "tiktok": "Fast-paced, Gen-Z language ok. Can reference trends/sounds.",
        "instagram_reel": "Aspirational tone. Think 'aesthetic', 'vibe', main character energy.",
        "instagram_carousel": "Educational hooks that promise value. 'Swipe to learn', listicle energy.",
        "linkedin": "Professional but human. Data/insights work well. No fluff.",
        "twitter_thread": "Punchy, under 280 chars. Promise value, create FOMO. 'A thread on...' energy.",
        "pinterest": "Search-friendly, descriptive. Aspirational lifestyle, 'how to' and 'ideas for' work well.",
        "podcast_clip": "Conversational teaser. Highlight surprising insight or controversial take."
    }
    
    personality_guide = personality_guides.get(personality, "Be authentic and conversational")
    platform_rule = platform_rules.get(platform.lower(), "Be authentic to the platform's culture")
    
    user_prompt = f"""PLATFORM: {platform.upper()}
NICHE: {niche.title()}
GOAL: {goal}
PERSONALITY: {personality.upper()} - {personality_guide}
AUDIENCE: {", ".join(audience).upper()} - {audience_guide}

YOUR PAST TOP-PERFORMING HOOKS (for style reference only):
{chr(10).join(f'{i+1}. "{hook}"' for i, hook in enumerate(past_hooks)) if past_hooks else "No past hooks available yet. Create fresh, engaging hooks."}

NEW CONTENT IDEA:
"{reference}"

{trends if trends else ""}

TASK: Generate 15 hooks for a {platform} video in the {niche} niche.

CRITICAL REQUIREMENTS:
- Match the {personality} personality style: {personality_guide}
- Target audiences: {", ".join(audience)} - {audience_guide}
- Each hook: 1 sentence, max 15 words
- Vary the angle (don't repeat the same pattern)
- First 3 words must grab attention
- {platform_rule}
- Sound natural and conversational, NOT like a TV ad
- Use the personality's signature phrases naturally

Output format: Just numbered list (1. Hook here)

FINAL REMINDER: ABSOLUTELY NO EMOJIS. Use plain text only. Express everything with words."""

    return [
        {"role": "system", "content": HOOK_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]
