from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging
import requests
from io import BytesIO
from PIL import Image
import base64
import re

# Import will be injected at runtime
embedding_engine = None
vector_store = None
llm_backend = None

def set_globals(emb, vs, llm):
    global embedding_engine, vector_store, llm_backend
    embedding_engine = emb
    vector_store = vs
    llm_backend = llm
from core.rag_engine import RAGEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/upload", tags=["upload"])

class ContentItem(BaseModel):
    content: str
    platform: str
    niche: str
    content_type: str  # "hook", "script", "caption", etc.
    performance: Optional[Dict] = None
    metadata: Optional[Dict] = None

class IndexContentRequest(BaseModel):
    user_id: str = "default_user"
    items: List[ContentItem]

@router.post("/index")
async def index_content(req: IndexContentRequest):
    """Index user's past content for RAG"""
    
    if not embedding_engine or not vector_store or not llm_backend:
        raise HTTPException(status_code=503, detail="Backend not fully initialized")
    
    try:
        rag = RAGEngine(embedding_engine, vector_store, llm_backend)
        
        # Convert to dict format
        content_items = [
            {
                "content": item.content,
                "platform": item.platform,
                "niche": item.niche,
                "content_type": item.content_type,
                "performance": item.performance or {},
                "metadata": item.metadata or {}
            }
            for item in req.items
        ]
        
        count = rag.index_user_content(req.user_id, content_items)
        
        return {
            "status": "success",
            "indexed_count": count,
            "message": f"Successfully indexed {count} content items"
        }
    
    except Exception as e:
        logger.error(f"Error indexing content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/{user_id}")
async def get_user_stats(user_id: str):
    """Get statistics about user's indexed content"""
    
    if not vector_store:
        raise HTTPException(status_code=503, detail="Backend not fully initialized")
    
    try:
        count = vector_store.count_user_content(user_id)
        
        return {
            "user_id": user_id,
            "total_content_items": count,
            "status": "ready" if count > 0 else "needs_content"
        }
    
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class LinkExtractRequest(BaseModel):
    url: str

@router.post("/extract-link")
async def extract_link(req: LinkExtractRequest):
    """Extract content from a webpage URL"""
    
    if not llm_backend:
        raise HTTPException(status_code=503, detail="Backend not fully initialized")
    
    try:
        # Fetch the webpage
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(req.url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Extract text content (simple extraction)
        html_content = response.text
        
        # Remove scripts and styles
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Extract text from HTML
        text_content = re.sub(r'<[^>]+>', ' ', html_content)
        text_content = ' '.join(text_content.split())
        
        # Limit to first 2000 characters
        text_content = text_content[:2000]
        
        # Use LLM to summarize/extract relevant content
        summary_prompt = f"""Extract and summarize the key content from this webpage. Focus on:
- Main topic/theme
- Key points or ideas
- Style/vibe/aesthetic (if visible)
- Target audience
- Useful details for content creation inspiration

Webpage content (first 2000 chars):
{text_content}

Provide a concise summary that would be useful as reference material for creating content similar to this page."""

        summary = llm_backend.generate([
            {"role": "system", "content": "You are a content extraction assistant. Extract key information from web pages for content creation inspiration."},
            {"role": "user", "content": summary_prompt}
        ])
        
        return {
            "status": "success",
            "url": req.url,
            "extracted_content": summary,
            "raw_preview": text_content[:500] + "..." if len(text_content) > 500 else text_content
        }
    
    except requests.RequestException as e:
        logger.error(f"Error fetching URL: {e}")
        raise HTTPException(status_code=400, detail=f"Could not fetch URL: {str(e)}")
    except Exception as e:
        logger.error(f"Error extracting link: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """Upload and process an image file for reference"""
    
    if not embedding_engine:
        raise HTTPException(status_code=503, detail="Backend not fully initialized")
    
    try:
        # Check file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Only image files are supported")
        
        # Read file
        contents = await file.read()
        image = Image.open(BytesIO(contents))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Get image description using CLIP or LLM vision
        # For now, use LLM to describe the image
        # Convert image to base64 for description
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # Use LLM to describe the image
        description_prompt = f"""Describe this image in detail, focusing on:
- Visual style/aesthetic/vibe
- Colors, mood, lighting
- Composition and framing
- Key elements or subjects
- Overall feel/atmosphere

This description will be used as reference for creating similar content."""

        # For now, we'll create a simple description based on image properties
        # In a full implementation, you'd use a vision model
        width, height = image.size
        description = f"Image ({width}x{height}px). Uploaded for visual reference. Please describe the style, colors, mood, and key elements you see to use as inspiration for content creation."
        
        # If we have a vision-capable LLM, use it here
        # For MVP, return basic info and let user add description
        
        return {
            "status": "success",
            "filename": file.filename,
            "file_type": file.content_type,
            "size": len(contents),
            "dimensions": f"{width}x{height}",
            "description": description,
            "suggestion": "Please add a description of what you see in this image (style, vibe, colors, mood) to use as reference."
        }
    
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

