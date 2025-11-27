from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import instaloader
from TikTokApi import TikTokApi
import pandas as pd
from typing import List, Dict
import logging
import os
import traceback
import yt_dlp
import re

router = APIRouter(prefix="/api/content-sorter", tags=["content-sorter"])
logger = logging.getLogger(__name__)

# Globals will be injected
embedding_engine = None
vector_store = None
llm_backend = None

def set_globals(emb, vs, llm):
    global embedding_engine, vector_store, llm_backend
    embedding_engine = emb
    vector_store = vs
    llm_backend = llm

class ContentSortRequest(BaseModel):
    username: str
    platform: str  # "instagram", "tiktok", "youtube"
    sort_by: str = "views"  # "views", "likes", "comments", "engagement_rate", "date"
    limit: int = 50

class ContentItem(BaseModel):
    id: str
    caption: str
    views: int
    likes: int
    comments: int
    shares: int
    engagement_rate: float
    created_at: str
    url: str
    thumbnail: str

@router.post("/sort-content")
async def sort_user_content(request: ContentSortRequest):
    """
    Sort user's content by performance metrics
    FREE alternative to Sort Feed
    """
    
    try:
        if request.platform == "instagram":
            return await sort_instagram_content(request)
        elif request.platform == "tiktok":
            return await sort_tiktok_content(request)
        elif request.platform == "youtube":
            return await sort_youtube_content(request)
        else:
            raise HTTPException(status_code=400, detail="Platform not supported. Supported: instagram, tiktok, youtube")
            
    except Exception as e:
        logger.error(f"Content sorting failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def sort_instagram_content(request: ContentSortRequest):
    """
    Sort Instagram content using Instaloader (FREE!)
    Optimized for speed - limits data fetching
    """
    
    # Clean username - remove @ if present
    username = request.username.strip().lstrip('@')
    
    if not username:
        raise HTTPException(status_code=400, detail="Username cannot be empty")
    
    # Limit to reasonable number for performance
    limit = min(request.limit, 100)  # Cap at 100 for performance
    
    L = instaloader.Instaloader()
    
    # Configure Instaloader for maximum speed
    L.download_pictures = False
    L.download_videos = False
    L.download_video_thumbnails = False
    L.download_geotags = False
    L.download_comments = False
    L.save_metadata = False
    L.compress_json = False
    L.request_timeout = 30  # Timeout after 30 seconds
    
    try:
        # Load profile
        logger.info(f"Loading Instagram profile: {username}")
        profile = instaloader.Profile.from_username(L.context, username)
        
        # Check if profile exists
        if not profile.is_private:
            logger.info(f"Profile {username} is public, proceeding...")
        else:
            logger.warning(f"Profile {username} is private. Some data may be unavailable.")
        
        posts_data = []
        post_count = 0
        followers = profile.followers if profile.followers > 0 else 1
        
        # Get posts with error handling and timeout protection
        try:
            import time
            start_time = time.time()
            timeout = 45  # 45 second timeout for fetching posts (reduced for faster feedback)
            
            # Use a more efficient approach - get posts with limit
            posts_iterator = profile.get_posts()
            
            for post in posts_iterator:
                # Check timeout
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    logger.warning(f"Timeout reached after {timeout}s, stopping at {post_count} posts")
                    break
                
                if post_count >= limit:
                    break
                
                # Skip if we're taking too long per post
                if post_count > 0 and elapsed > 0:
                    avg_time_per_post = elapsed / post_count
                    if avg_time_per_post > 3 and post_count >= 10:  # If >3s per post and we have 10+, stop
                        logger.warning(f"Too slow ({avg_time_per_post:.1f}s/post), stopping early with {post_count} posts")
                        break
                
                try:
                    # Quick data extraction - skip expensive operations
                    engagement = post.likes + post.comments
                    engagement_rate = (engagement / followers) * 100 if followers > 0 else 0
                    
                    # Get video views if available (skip if takes too long)
                    views = 0
                    if post.is_video:
                        try:
                            views = post.video_view_count if hasattr(post, 'video_view_count') else 0
                        except:
                            views = 0
                    
                    # Skip thumbnail fetching for speed
                    thumbnail = ""
                    
                    posts_data.append({
                        'id': post.shortcode,
                        'caption': (post.caption[:100] if post.caption else '') or '',
                        'views': views,
                        'likes': post.likes,
                        'comments': post.comments,
                        'shares': 0,  # Instagram doesn't provide this
                        'engagement_rate': round(engagement_rate, 2),
                        'created_at': post.date_utc.isoformat() if post.date_utc else '',
                        'url': f"https://instagram.com/p/{post.shortcode}",
                        'thumbnail': thumbnail
                    })
                    post_count += 1
                    
                    # Log progress every 5 posts for better feedback
                    if post_count % 5 == 0:
                        elapsed = time.time() - start_time
                        logger.info(f"Processed {post_count}/{limit} posts in {elapsed:.1f}s...")
                        
                except Exception as post_error:
                    logger.warning(f"Error processing post {post_count}: {post_error}")
                    continue
                    
        except instaloader.exceptions.LoginRequiredException:
            raise HTTPException(
                status_code=403, 
                detail="This profile requires login. Please note that private profiles or rate-limited requests may need authentication."
            )
        except instaloader.exceptions.PrivateProfileNotFollowedException:
            raise HTTPException(
                status_code=403,
                detail="This is a private profile. Public profiles work best."
            )
        except instaloader.exceptions.ConnectionException as e:
            raise HTTPException(
                status_code=503,
                detail=f"Connection error: {str(e)}. Instagram may be rate-limiting requests. Please try again later."
            )
        
        if not posts_data:
            raise HTTPException(
                status_code=404,
                detail=f"No posts found for @{username}. The profile may be empty, private, or the username may be incorrect."
            )
        
        # Convert to DataFrame for easy sorting
        df = pd.DataFrame(posts_data)
        
        # Ensure all numeric columns are numeric
        numeric_cols = ['views', 'likes', 'comments', 'shares', 'engagement_rate']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Sort based on request
        if request.sort_by == "engagement_rate":
            df = df.sort_values('engagement_rate', ascending=False)
        elif request.sort_by == "date":
            df = df.sort_values('created_at', ascending=False)
        elif request.sort_by in df.columns:
            df = df.sort_values(request.sort_by, ascending=False)
        else:
            # Default to likes if sort_by column doesn't exist
            df = df.sort_values('likes', ascending=False)
        
        return {
            "username": username,
            "platform": "instagram",
            "total_posts": len(df),
            "sorted_by": request.sort_by,
            "content": df.to_dict('records')
        }
        
    except HTTPException:
        raise
    except instaloader.exceptions.ProfileNotExistsException:
        raise HTTPException(status_code=404, detail=f"Profile @{username} does not exist. Please check the username.")
    except instaloader.exceptions.PrivateProfileNotFollowedException:
        raise HTTPException(status_code=403, detail=f"Profile @{username} is private. Public profiles work best.")
    except instaloader.exceptions.LoginRequiredException:
        raise HTTPException(status_code=403, detail="Instagram requires login for this profile. Please use a public profile.")
    except instaloader.exceptions.ConnectionException as e:
        raise HTTPException(status_code=503, detail=f"Connection error: {str(e)}. Instagram may be rate-limiting requests.")
    except Exception as e:
        logger.error(f"Instagram sorting failed: {e}", exc_info=True)
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to sort Instagram content: {str(e)}")

async def sort_tiktok_content(request: ContentSortRequest):
    """
    Sort TikTok content using TikTok API (FREE!)
    NOTE: TikTok scraping requires browser sessions and may be rate-limited.
    This is a best-effort implementation.
    """

    # Clean username - remove @ if present
    username = request.username.strip().lstrip('@')

    if not username:
        raise HTTPException(status_code=400, detail="Username cannot be empty")

    # Limit to reasonable number for performance
    limit = min(request.limit, 50)  # Cap at 50 for TikTok (slower than Instagram)

    try:
        # TikTokApi v6+ requires async context manager with sessions
        async with TikTokApi() as api:
            # Create sessions (required for TikTokApi v6+)
            await api.create_sessions(ms_tokens=[None], num_sessions=1, sleep_after=3)

            # Get user and videos
            user = api.user(username=username)
            videos = []

            # Fetch videos with count limit
            video_count = 0
            async for video in user.videos(count=limit):
                if video_count >= limit:
                    break

                try:
                    # Extract stats safely
                    stats = video.stats if hasattr(video, 'stats') else {}
                    play_count = stats.get('playCount', 0)
                    digg_count = stats.get('diggCount', 0)
                    comment_count = stats.get('commentCount', 0)
                    share_count = stats.get('shareCount', 0)

                    engagement = digg_count + comment_count + share_count
                    engagement_rate = (engagement / play_count) * 100 if play_count > 0 else 0

                    # Get video metadata safely
                    video_id = video.id if hasattr(video, 'id') else ''
                    description = video.desc[:100] if hasattr(video, 'desc') and video.desc else ''
                    create_time = str(video.create_time) if hasattr(video, 'create_time') else ''

                    # Get thumbnail safely
                    thumbnail = ''
                    if hasattr(video, 'video') and hasattr(video.video, 'cover'):
                        thumbnail = video.video.cover

                    videos.append({
                        'id': video_id,
                        'caption': description,
                        'views': play_count,
                        'likes': digg_count,
                        'comments': comment_count,
                        'shares': share_count,
                        'engagement_rate': round(engagement_rate, 2),
                        'created_at': create_time,
                        'url': f"https://tiktok.com/@{username}/video/{video_id}",
                        'thumbnail': thumbnail
                    })
                    video_count += 1

                    # Log progress
                    if video_count % 5 == 0:
                        logger.info(f"Processed {video_count}/{limit} TikTok videos...")

                except Exception as video_error:
                    logger.warning(f"Error processing TikTok video: {video_error}")
                    continue

        if not videos:
            raise HTTPException(
                status_code=404,
                detail=f"No videos found for @{username}. The account may be private, empty, or the username may be incorrect."
            )

        # Convert to DataFrame for sorting
        df = pd.DataFrame(videos)

        # Ensure all numeric columns are numeric
        numeric_cols = ['views', 'likes', 'comments', 'shares', 'engagement_rate']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Sort based on request
        if request.sort_by == "engagement_rate":
            df = df.sort_values('engagement_rate', ascending=False)
        elif request.sort_by == "date":
            df = df.sort_values('created_at', ascending=False)
        elif request.sort_by in df.columns:
            df = df.sort_values(request.sort_by, ascending=False)
        else:
            # Default to views if sort_by column doesn't exist
            df = df.sort_values('views', ascending=False)

        return {
            "username": username,
            "platform": "tiktok",
            "total_videos": len(df),
            "sorted_by": request.sort_by,
            "content": df.to_dict('records')
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TikTok sorting failed: {e}", exc_info=True)

        # Provide more helpful error messages
        error_msg = str(e)
        if "bot" in error_msg.lower() or "empty response" in error_msg.lower():
            raise HTTPException(
                status_code=503,
                detail="TikTok detected automated access and blocked the request. TikTok has strong anti-bot protections that prevent content scraping. Please use Instagram instead - it works reliably!"
            )
        elif "session" in error_msg.lower():
            raise HTTPException(
                status_code=503,
                detail="TikTok session initialization failed. TikTok may be blocking scraping requests. Please try again later or use Instagram instead."
            )
        elif "not found" in error_msg.lower() or "doesn't exist" in error_msg.lower():
            raise HTTPException(
                status_code=404,
                detail=f"TikTok user @{username} not found. Please check the username."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch TikTok content: {error_msg}. Note: TikTok scraping is experimental and may not always work due to anti-bot protections."
            )

@router.post("/export-data")
async def export_content_data(data: List[ContentItem], format: str = "csv"):
    """
    Export sorted content data
    """
    
    df = pd.DataFrame([item.dict() for item in data])
    
    if format == "csv":
        csv_path = f"/tmp/content_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
        os.makedirs('/tmp', exist_ok=True)
        df.to_csv(csv_path, index=False)
        return {"file_path": csv_path, "format": "csv"}
    
    elif format == "json":
        json_path = f"/tmp/content_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs('/tmp', exist_ok=True)
        df.to_json(json_path, orient='records', indent=2)
        return {"file_path": json_path, "format": "json"}
    
    elif format == "excel":
        excel_path = f"/tmp/content_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        os.makedirs('/tmp', exist_ok=True)
        df.to_excel(excel_path, index=False)
        return {"file_path": excel_path, "format": "excel"}

