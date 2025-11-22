"""
A/B Testing Simulator Prompt Templates
Compare two variants and predict which performs better
"""

from typing import List, Dict

AB_TEST_SYSTEM_PROMPT = """You are ABTestPro, an expert at predicting content performance through comparative analysis.

ABSOLUTE PROHIBITION - NO EMOJIS EVER:
- NEVER use emojis, emoji symbols, Unicode emoji characters, or any pictorial symbols
- NEVER use: 😀 😊 🎉 ✨ 💡 🚀 ❤️ 💯 👍 👎 🎬 📱 💪 🔥 ⭐ 🌟 💎 🎯 or ANY similar characters
- Use ONLY plain text: letters, numbers, and basic punctuation marks (.,!?;:)
- Express emotions, excitement, or emphasis using WORDS only, never symbols
- This is a strict, non-negotiable requirement - emojis are completely forbidden

CORE PRINCIPLES:
1. Compare variants based on user's historical performance patterns
2. Analyze hook structure, emotional impact, clarity
3. Consider platform-specific best practices
4. Predict winner with confidence score
5. Suggest improvements for weaker variant

ANALYSIS FACTORS:
- Hook strength: First 3 seconds impact, curiosity gap, pattern interrupt
- Emotional impact: Does it evoke strong emotion?
- Clarity: Is the message clear and understandable?
- Platform fit: Does it match platform culture?
- Pattern match: Similarity to user's top performers
- Length: Appropriate for content type
- CTA: Clear call-to-action (if applicable)"""

def build_ab_test_prompt(
    variant_a: str,
    variant_b: str,
    content_type: str,
    platform: str,
    niche: str,
    user_top_performers: List[Dict] = None
) -> List[Dict[str, str]]:
    """Build prompt for A/B testing comparison"""
    
    # Analyze user's top performers
    top_performer_analysis = ""
    if user_top_performers:
        examples = "\n".join([
            f"Example {i+1}: {p.get('content', '')[:150]}"
            for i, p in enumerate(user_top_performers[:5])
        ])
        top_performer_analysis = f"""
USER'S TOP PERFORMERS (for reference):
{examples}
"""
    
    user_prompt = f"""PLATFORM: {platform.upper()}
NICHE: {niche.title()}
CONTENT TYPE: {content_type.upper()}
{top_performer_analysis}
VARIANT A:
"{variant_a}"

VARIANT B:
"{variant_b}"

TASK: Compare these two variants and predict which will perform better.

ANALYSIS REQUIREMENTS:
1. Hook Strength (0-100):
   - First 3 words impact
   - Curiosity gap
   - Pattern interrupt
   - Platform-native language

2. Emotional Impact (0-100):
   - Does it evoke emotion?
   - Is it relatable/engaging?
   - Does it connect with audience?

3. Clarity (0-100):
   - Is the message clear?
   - Easy to understand?
   - No ambiguity?

4. Platform Fit (0-100):
   - Matches platform culture?
   - Appropriate length/format?
   - Platform best practices?

5. Pattern Match (0-100):
   - Similarity to user's top performers
   - Follows successful patterns?
   - Maintains user's style?

SCORE EACH VARIANT:
- Provide score (0-100) for each factor above
- Calculate overall score (average)
- Declare winner (A or B)
- Confidence level (Low/Medium/High)

IMPROVEMENTS:
- For the weaker variant, suggest 3 specific improvements
- For the winner, suggest 1-2 enhancements

FORMAT:
VARIANT A ANALYSIS:
- Hook Strength: [score]/100
- Emotional Impact: [score]/100
- Clarity: [score]/100
- Platform Fit: [score]/100
- Pattern Match: [score]/100
- Overall Score: [score]/100

VARIANT B ANALYSIS:
- Hook Strength: [score]/100
- Emotional Impact: [score]/100
- Clarity: [score]/100
- Platform Fit: [score]/100
- Pattern Match: [score]/100
- Overall Score: [score]/100

WINNER: [A or B]
CONFIDENCE: [Low/Medium/High]

IMPROVEMENTS FOR [LOSER]:
1. [specific improvement]
2. [specific improvement]
3. [specific improvement]

FINAL REMINDER: ABSOLUTELY NO EMOJIS. Use plain text only. Express everything with words."""

    return [
        {"role": "system", "content": AB_TEST_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

