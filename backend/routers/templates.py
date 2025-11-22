"""
Templates API endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from prompts.templates import get_templates, get_template
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/templates", tags=["templates"])

class TemplateGenerateRequest(BaseModel):
    template_id: str
    user_id: str = "default_user"
    platform: str
    niche: str
    goal: str
    personality: str
    audience: List[str]
    reference_text: Optional[str] = None
    content_type: str = "hooks"  # hooks or script

@router.get("/")
async def list_templates(
    platform: Optional[str] = None,
    niche: Optional[str] = None,
    category: Optional[str] = None
):
    """
    Get all templates, optionally filtered by platform, niche, or category.
    
    Args:
        platform: Optional platform filter (tiktok, youtube, etc.)
        niche: Optional niche filter (beauty, tech, etc.)
        category: Optional category filter (Hooks, Scripts, etc.)
    
    Returns:
        List of matching templates with metadata
    """
    try:
        # Get filtered templates
        from prompts.templates import TEMPLATES
        
        filtered = {}
        for template_id, template in TEMPLATES.items():
            if platform and platform.lower() not in [p.lower() for p in template.get('platforms', [])]:
                continue
            if niche and niche.lower() not in [n.lower() for n in template.get('niches', [])]:
                continue
            if category and template.get('category', '').lower() != category.lower():
                continue
            filtered[template_id] = template
        
        # Format for frontend
        templates_data = [
            {
                "id": template_id,
                "name": template["name"],
                "description": template["description"],
                "category": template["category"],
                "platforms": template["platforms"],
                "niches": template["niches"],
            }
            for template_id, template in filtered.items()
        ]
        
        return {
            "status": "success",
            "templates": templates_data,
            "count": len(templates_data)
        }
    
    except Exception as e:
        logger.error(f"Error listing templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{template_id}")
async def get_template_by_id(template_id: str):
    """
    Get a specific template by ID.
    
    Args:
        template_id: Template ID (e.g., 'storytime_hook')
    
    Returns:
        Template details including system prompt
    """
    try:
        template = get_template(template_id)
        
        if not template:
            raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")
        
        return {
            "status": "success",
            "template": {
                "id": template_id,
                "name": template["name"],
                "description": template["description"],
                "category": template["category"],
                "platforms": template["platforms"],
                "niches": template["niches"],
                "system_prompt": template["system_prompt"]
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

