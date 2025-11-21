from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import json
import logging

from core.rag_engine import RAGEngine
from prompts import hooks, scripts, shots, music

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Globals will be injected
embedding_engine = None
vector_store = None
llm_backend = None

def set_globals(emb, vs, llm):
    global embedding_engine, vector_store, llm_backend
    embedding_engine = emb
    vector_store = vs
    llm_backend = llm

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    type: Optional[str] = None  # Content type if assistant message

class ChatRequest(BaseModel):
    user_id: str = "default_user"
    platform: str
    niche: str
    goal: str
    personality: str
    audience: List[str]
    reference_text: Optional[str] = None
    conversation_history: List[ChatMessage] = []  # Full conversation history
    user_message: str  # New user message
    context_content: Optional[str] = None  # Latest generated content for context

@router.post("/continue")
async def continue_chat(req: ChatRequest):
    """Continue conversation with follow-up messages"""
    
    if not llm_backend or not embedding_engine or not vector_store:
        raise HTTPException(status_code=503, detail="Backend not fully initialized")
    
    try:
        # Build context from conversation history
        conversation_context = []
        
        # Add system message
        conversation_context.append({
            "role": "system",
            "content": f"""You are a creative content assistant helping with {req.platform} content creation in the {req.niche} niche.

Your role:
- Help refine and improve generated content
- Suggest variations and improvements
- Answer questions about content strategy
- Provide creative suggestions
- Help with revisions and edits

Personality: {req.personality}
Target Audience: {', '.join(req.audience)}

CRITICAL RULES - YOU MUST FOLLOW THESE:
1. NEVER use emojis, emoji symbols, or any Unicode emoji characters in your responses
2. NEVER use symbols like 😀 😊 🎉 ✨ 💡 🚀 ❤️ 💯 or any similar characters
3. Use ONLY plain text, letters, numbers, and basic punctuation (.,!?;:)
4. If you need to express emotion, use words instead of symbols
5. This is a strict requirement - emojis are not allowed under any circumstances

Be conversational, helpful, and creative. Reference the conversation history when making suggestions. Use descriptive words to convey tone and emotion instead of emojis."""
        })
        
        # Add conversation history (last 10 messages for context)
        recent_history = req.conversation_history[-10:] if req.conversation_history else []
        for msg in recent_history:
            conversation_context.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add the new user message
        conversation_context.append({
            "role": "user",
            "content": req.user_message
        })
        
        # Generate response (streaming)
        async def stream_response():
            try:
                for chunk in llm_backend.generate_stream(conversation_context, temperature=0.8):
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                logger.error(f"Chat error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(stream_response(), media_type="text/event-stream")
    
    except Exception as e:
        logger.error(f"Error in continue_chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

