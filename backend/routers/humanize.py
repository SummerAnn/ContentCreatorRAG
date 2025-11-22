"""
AI Humanizer API endpoints
Rewrite AI-generated content to sound natural and prevent AI detection
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import logging
import re
import json
import numpy as np

from core.llm_backend import LLMBackend

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/humanize", tags=["humanize"])

# Global instances (injected by main.py)
llm_backend = None

def set_globals(emb, vs, llm):
    global llm_backend
    llm_backend = llm

class HumanizeRequest(BaseModel):
    content: str
    style: str = "natural"  # natural, casual, professional
    preserve_meaning: bool = True

class HumanizeResponse(BaseModel):
    original: str
    humanized: str
    changes_count: int
    improvements: List[str]
    ai_score_before: float
    ai_score_after: float

# AI detection patterns
AI_PHRASES = [
    "It's important to note that",
    "It is worth noting",
    "In conclusion",
    "Furthermore",
    "Moreover",
    "Additionally",
    "However, it's crucial to",
    "On the other hand",
    "In summary",
    "To summarize",
    "In light of this",
    "With that being said",
    "As previously mentioned",
    "As a result",
    "Consequently",
    "Therefore, it follows that",
    "It should be emphasized",
    "One must consider",
    "It can be argued that"
]

def calculate_ai_score(text: str) -> float:
    """Calculate how AI-sounding the text is (0-100)"""
    score = 0
    
    # Check for AI phrases
    ai_phrase_count = sum(1 for phrase in AI_PHRASES if phrase.lower() in text.lower())
    score += min(ai_phrase_count * 10, 40)
    
    # Check sentence uniformity
    sentences = re.split(r'[.!?]+', text)
    sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
    if sentence_lengths:
        if len(sentence_lengths) > 1:
            length_variance = np.std(sentence_lengths)
        else:
            length_variance = 0
        if length_variance < 5:  # Very uniform = AI-like
            score += 20
    
    # Check for excessive formality
    formal_words = ['utilize', 'facilitate', 'implement', 'demonstrate', 'indicates']
    formal_count = sum(1 for word in formal_words if word in text.lower())
    score += min(formal_count * 5, 20)
    
    # Check for lack of contractions
    contraction_count = len(re.findall(r"\b\w+n't\b|\b\w+'ll\b|\b\w+'re\b|\b\w+'ve\b", text))
    word_count = len(text.split())
    if word_count > 0:
        contraction_ratio = contraction_count / word_count
        if contraction_ratio < 0.02:  # Less than 2% contractions
            score += 20
    
    return min(score, 100)

def detect_changes(original: str, humanized: str) -> List[str]:
    """Detect what was changed"""
    improvements = []
    
    # Check for removed AI phrases
    removed_phrases = [p for p in AI_PHRASES if p.lower() in original.lower() and p.lower() not in humanized.lower()]
    if removed_phrases:
        improvements.append(f"Removed {len(removed_phrases)} AI-sounding phrases")
    
    # Check for added contractions
    original_contractions = len(re.findall(r"\b\w+n't\b|\b\w+'ll\b|\b\w+'re\b|\b\w+'ve\b", original))
    humanized_contractions = len(re.findall(r"\b\w+n't\b|\b\w+'ll\b|\b\w+'re\b|\b\w+'ve\b", humanized))
    if humanized_contractions > original_contractions:
        improvements.append(f"Added {humanized_contractions - original_contractions} contractions")
    
    # Check for sentence variety
    original_sentences = [len(s.split()) for s in re.split(r'[.!?]+', original) if s.strip()]
    humanized_sentences = [len(s.split()) for s in re.split(r'[.!?]+', humanized) if s.strip()]
    
    if len(humanized_sentences) > 1 and len(original_sentences) > 1:
        original_variance = np.std(original_sentences) if len(original_sentences) > 1 else 0
        humanized_variance = np.std(humanized_sentences) if len(humanized_sentences) > 1 else 0
        if humanized_variance > original_variance * 1.3:
            improvements.append("Increased sentence variety")
    
    # Check for casual language
    casual_markers = ['you know', 'like', 'actually', 'basically', 'honestly', 'literally']
    added_casual = sum(1 for marker in casual_markers if marker in humanized.lower() and marker not in original.lower())
    if added_casual > 0:
        improvements.append("Added conversational elements")
    
    return improvements

@router.post("/", response_model=HumanizeResponse)
async def humanize_content(request: HumanizeRequest):
    """
    Humanize AI-generated content to sound more natural
    
    Styles:
    - natural: Balanced, authentic
    - casual: Very conversational, like texting a friend
    - professional: Polished but human
    """
    
    if not llm_backend:
        raise HTTPException(status_code=503, detail="Backend not fully initialized")
    
    try:
        # Build humanization prompt based on style
        style_instructions = {
            "natural": """
- Use contractions naturally (don't, can't, you'll)
- Mix sentence lengths (some short, some longer)
- Add occasional conversational elements
- Remove overly formal language
- Keep it genuine and authentic
""",
            "casual": """
- Heavy use of contractions
- Short, punchy sentences mixed with longer ones
- Add casual fillers: "you know", "like", "actually"
- Use everyday language
- Sound like you're talking to a friend
""",
            "professional": """
- Use contractions sparingly but naturally
- Maintain professionalism but add warmth
- Vary sentence structure
- Remove academic/robotic phrasing
- Sound like a knowledgeable colleague
"""
        }
        
        system_prompt = """You are an expert at rewriting AI-generated content to sound authentically human.

ABSOLUTE PROHIBITION - NO EMOJIS EVER:
- NEVER use emojis, emoji symbols, Unicode emoji characters, or any pictorial symbols
- NEVER use: 😀 😊 🎉 ✨ 💡 🚀 ❤️ 💯 👍 👎 🎬 📱 💪 🔥 ⭐ 🌟 💎 🎯 or ANY similar characters
- Use ONLY plain text: letters, numbers, and basic punctuation marks (.,!?;:)
- Express emotions, excitement, or emphasis using WORDS only, never symbols
- This is a strict, non-negotiable requirement - emojis are completely forbidden

CRITICAL RULES:
1. NEVER use these AI-sounding phrases:
   - "It's important to note that"
   - "In conclusion" / "In summary"
   - "Furthermore" / "Moreover"
   - "However, it's crucial to"
   - "One must consider"

2. DO use these human patterns:
   - Mix short punchy sentences with longer ones
   - Use contractions naturally
   - Start sentences with "And" or "But" sometimes
   - Add personality and voice
   - Use simple, everyday words

3. Preserve the core message completely
4. Match the requested style exactly"""

        user_prompt = f"""Rewrite this content to sound completely human and natural:

ORIGINAL:
{request.content}

STYLE: {request.style}
{style_instructions[request.style]}

REQUIREMENTS:
- Remove ALL AI-sounding phrases
- Vary sentence length dramatically
- {('Keep the exact same meaning' if request.preserve_meaning else 'You can adjust meaning slightly for naturalness')}
- Sound like a real person wrote this from scratch

Output ONLY the rewritten content, nothing else.

FINAL REMINDER: ABSOLUTELY NO EMOJIS. Use plain text only."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Generate humanized version
        humanized_text = ""
        async def stream_response():
            nonlocal humanized_text
            try:
                async for chunk in llm_backend.generate_stream(messages, temperature=0.8):
                    humanized_text += chunk
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                
                # Calculate scores
                ai_score_before = calculate_ai_score(request.content)
                ai_score_after = calculate_ai_score(humanized_text)
                
                # Detect improvements
                improvements = detect_changes(request.content, humanized_text)
                
                # Count changes (simple word difference)
                original_words = set(request.content.lower().split())
                humanized_words = set(humanized_text.lower().split())
                changes_count = len(original_words.symmetric_difference(humanized_words))
                
                result = {
                    "original": request.content,
                    "humanized": humanized_text.strip(),
                    "changes_count": changes_count,
                    "improvements": improvements,
                    "ai_score_before": round(ai_score_before, 1),
                    "ai_score_after": round(ai_score_after, 1)
                }
                
                yield f"data: {json.dumps({'parsed': result})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                logger.error(f"Generation error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(stream_response(), media_type="text/event-stream")
    
    except Exception as e:
        logger.error(f"Humanization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Humanization failed: {str(e)}")

