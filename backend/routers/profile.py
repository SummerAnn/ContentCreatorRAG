"""
User Profile API endpoints
Save and manage user preferences for personalization
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from pydantic import BaseModel
import logging
import json

from core.database import get_db
from models.user_profile import UserProfile, UserProfileCreate, UserProfileResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/profile", tags=["profile"])

@router.post("/save", response_model=UserProfileResponse)
async def save_profile(
    profile_data: UserProfileCreate,
    db: Session = Depends(get_db)
):
    """
    Save user profile (can be called from SettingsPanel)
    This acts as both onboarding and profile update
    """
    
    try:
        # Check if profile exists
        existing_profile = db.query(UserProfile).filter(
            UserProfile.user_id == profile_data.user_id
        ).first()
        
        if existing_profile:
            # Update existing profile
            for key, value in profile_data.dict(exclude_unset=True).items():
                setattr(existing_profile, key, value)
            existing_profile.profile_completed = True
            profile = existing_profile
        else:
            # Create new profile
            profile = UserProfile(
                **profile_data.dict(),
                profile_completed=True
            )
            db.add(profile)
        
        db.commit()
        db.refresh(profile)
        
        logger.info(f"Profile saved for user {profile_data.user_id}")
        
        # Convert to dict for response
        return UserProfileResponse(
            user_id=profile.user_id,
            name=profile.name,
            creator_type=profile.creator_type,
            primary_platforms=profile.primary_platforms or [],
            primary_niches=profile.primary_niches or [],
            default_personality=profile.default_personality,
            default_audience=profile.default_audience or [],
            default_goal=profile.default_goal,
            default_has_voiceover=profile.default_has_voiceover if profile.default_has_voiceover is not None else True,
            brand_voice=profile.brand_voice or {},
            content_style=profile.content_style,
            personality_traits=profile.personality_traits or [],
            primary_goals=profile.primary_goals or [],
            profile_completed=profile.profile_completed
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Profile save failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_profile(user_id: str, db: Session = Depends(get_db)):
    """Get user profile"""
    
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    if not profile:
        # Return default profile if not found
        return UserProfileResponse(
            user_id=user_id,
            primary_platforms=[],
            primary_niches=[],
            default_audience=[],
            default_has_voiceover=True,
            brand_voice={},
            personality_traits=[],
            primary_goals=[],
            profile_completed=False
        )
    
    return UserProfileResponse(
        user_id=profile.user_id,
        name=profile.name,
        creator_type=profile.creator_type,
        primary_platforms=profile.primary_platforms or [],
        primary_niches=profile.primary_niches or [],
        default_personality=profile.default_personality,
        default_audience=profile.default_audience or [],
        default_goal=profile.default_goal,
        default_has_voiceover=profile.default_has_voiceover if profile.default_has_voiceover is not None else True,
        brand_voice=profile.brand_voice or {},
        content_style=profile.content_style,
        personality_traits=profile.personality_traits or [],
        primary_goals=profile.primary_goals or [],
        profile_completed=profile.profile_completed
    )

class SaveSettingsRequest(BaseModel):
    user_id: str
    platform: str
    niche: str
    goal: str
    personality: str
    audience: List[str]
    has_voiceover: bool

@router.post("/save-settings")
async def save_settings(
    request: SaveSettingsRequest,
    db: Session = Depends(get_db)
):
    """
    Save current settings as defaults (called from SettingsPanel)
    """
    
    try:
        profile = db.query(UserProfile).filter(UserProfile.user_id == request.user_id).first()
        
        if not profile:
            # Create profile with settings
            profile = UserProfile(
                user_id=request.user_id,
                primary_platforms=[request.platform],
                primary_niches=[request.niche],
                default_personality=request.personality,
                default_audience=request.audience,
                default_goal=request.goal,
                default_has_voiceover=request.has_voiceover,
                profile_completed=True
            )
            db.add(profile)
        else:
            # Update defaults
            if request.platform not in (profile.primary_platforms or []):
                profile.primary_platforms = (profile.primary_platforms or []) + [request.platform]
            if request.niche not in (profile.primary_niches or []):
                profile.primary_niches = (profile.primary_niches or []) + [request.niche]
            profile.default_personality = request.personality
            profile.default_audience = request.audience
            profile.default_goal = request.goal
            profile.default_has_voiceover = request.has_voiceover
            profile.profile_completed = True
        
        db.commit()
        db.refresh(profile)
        
        return {
            "status": "success",
            "message": "Settings saved as defaults",
            "profile": {
                "user_id": profile.user_id,
                "name": profile.name,
                "primary_platforms": profile.primary_platforms or [],
                "primary_niches": profile.primary_niches or [],
                "profile_completed": profile.profile_completed
            }
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Settings save failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/defaults")
async def get_defaults(user_id: str, db: Session = Depends(get_db)):
    """
    Get default settings from user profile
    Used to auto-fill SettingsPanel
    """
    
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    if not profile or not profile.profile_completed:
        return {
            "has_profile": False,
            "defaults": {}
        }
    
    return {
        "has_profile": True,
        "defaults": {
            "platform": profile.primary_platforms[0] if profile.primary_platforms else "",
            "niche": profile.primary_niches[0] if profile.primary_niches else "",
            "goal": profile.default_goal or "grow_followers",
            "personality": profile.default_personality or "friendly",
            "audience": profile.default_audience or ["gen_z"],
            "has_voiceover": profile.default_has_voiceover if profile.default_has_voiceover is not None else True
        },
        "profile": {
            "name": profile.name,
            "creator_type": profile.creator_type,
            "primary_platforms": profile.primary_platforms or [],
            "primary_niches": profile.primary_niches or [],
            "primary_goals": profile.primary_goals or []
        }
    }

