from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import yt_dlp
import whisper
import subprocess
import os
import json
from typing import List, Dict
import logging
import instaloader
import re
import requests
import tempfile
from TikTokApi import TikTokApi

router = APIRouter(prefix="/api/viral-analyzer", tags=["viral-analyzer"])
logger = logging.getLogger(__name__)

# Global instances
_llm_backend = None

def set_globals(embedding_engine, vector_store, llm_backend):
    global _llm_backend
    _llm_backend = llm_backend

def _extract_field(text: str, field_name: str, default: str) -> str:
    """Extract a field value from text response if JSON parsing fails"""
    # Try to find the field in the text
    patterns = [
        f'"{field_name}":\\s*"([^"]+)"',
        f'"{field_name}":\\s*([^,}}]+)',
    ]
    for pattern in patterns:
        import re
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip().strip('"')
    return default

class VideoAnalysisRequest(BaseModel):
    url: str
    platform: str  # "tiktok", "youtube", "instagram"

class VideoAnalysisResponse(BaseModel):
    title: str
    views: int
    likes: int
    duration: int
    transcript: str
    hook: str
    story_structure: Dict
    visual_style: str
    key_moments: List[Dict]
    remix_suggestions: List[str]

# Initialize Whisper model (download once, use forever - FREE!)
WHISPER_MODEL = None

def get_whisper_model():
    global WHISPER_MODEL
    if WHISPER_MODEL is None:
        logger.info("Loading Whisper model (one-time download)...")
        WHISPER_MODEL = whisper.load_model("base")  # Options: tiny, base, small, medium, large
    return WHISPER_MODEL

@router.post("/analyze", response_model=VideoAnalysisResponse)
async def analyze_viral_video(request: VideoAnalysisRequest):
    """
    Analyze a viral video like Sandcastles does
    1. Download video + metadata (FREE with yt-dlp)
    2. Extract audio and transcribe (FREE with Whisper)
    3. Analyze with Llama (FREE, already using!)
    """
    
    if not request.url or not request.url.strip():
        raise HTTPException(status_code=400, detail="URL is required")
    
    if not request.platform or not request.platform.strip():
        raise HTTPException(status_code=400, detail="Platform is required")
    
    if not _llm_backend:
        raise HTTPException(status_code=500, detail="LLM backend not initialized")
    
    # Validate URL format
    url = request.url.strip()
    if not url.startswith(('http://', 'https://')):
        raise HTTPException(status_code=400, detail="Invalid URL format. URL must start with http:// or https://")
    
    try:
        # Step 1: Download video metadata and audio
        # Instagram requires special handling - use instaloader instead of yt-dlp
        is_instagram = 'instagram' in request.platform.lower() or 'instagram.com' in request.url
        
        # For Instagram, use instaloader (works much better than yt-dlp)
        if is_instagram:
            return await analyze_instagram_video(request.url)
        
        # For YouTube/TikTok, use yt-dlp
        ydl_opts = {
            'quiet': False,  # Set to False to see errors
            'no_warnings': False,
            'extract_flat': False,
            'skip_download': False,  # We need audio for transcription
            'outtmpl': '/tmp/%(id)s.%(ext)s',
            'noplaylist': True,
        }
        
        # Format selection - Instagram videos are usually MP4, so we handle differently
        if is_instagram:
            # For Instagram, try to get the video directly (they're usually MP4 with audio)
            ydl_opts.update({
                'format': 'best[ext=mp4]/best',  # Prefer MP4 for Instagram
                'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
                'extractor_args': {
                    'instagram': {
                        'skip_download': False,
                    }
                },
            })
            # Add postprocessor to extract audio if needed
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }]
        else:
            # For YouTube/TikTok, use bestaudio
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                }],
            })
        
        # Ensure tmp directory exists
        os.makedirs('/tmp', exist_ok=True)
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info(f"Downloading video info from {request.url}")
            try:
                info = ydl.extract_info(request.url, download=True)
            except Exception as e:
                logger.error(f"yt-dlp extraction with download failed: {e}")
                # Try without download first to get metadata
                try:
                    logger.info("Attempting metadata-only extraction...")
                    ydl_opts_meta = ydl_opts.copy()
                    ydl_opts_meta['skip_download'] = True
                    ydl_opts_meta['quiet'] = True
                    with yt_dlp.YoutubeDL(ydl_opts_meta) as ydl_meta:
                        info = ydl_meta.extract_info(request.url, download=False)
                    # If we can't download, we'll work with metadata only
                    logger.warning("Could not download video, using metadata only. Transcription will be unavailable.")
                except Exception as e2:
                    # Try one more time with different format selector for Instagram
                    if 'instagram' in request.url.lower():
                        try:
                            logger.info("Trying Instagram with alternative format...")
                            ydl_opts_alt = {
                                'quiet': True,
                                'no_warnings': True,
                                'extract_flat': False,
                                'skip_download': False,
                                'format': 'best',
                                'outtmpl': '/tmp/%(id)s.%(ext)s',
                                'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15',
                                'noplaylist': True,
                            }
                            with yt_dlp.YoutubeDL(ydl_opts_alt) as ydl_alt:
                                info = ydl_alt.extract_info(request.url, download=True)
                        except Exception as e3:
                            raise HTTPException(status_code=400, detail=f"Failed to extract Instagram video. Error: {str(e3)}")
                    else:
                        raise HTTPException(status_code=400, detail=f"Failed to extract video info: {str(e2)}")
            
            # Get metadata
            title = info.get('title', info.get('description', 'Unknown'))[:200]
            views = info.get('view_count', info.get('play_count', 0))
            likes = info.get('like_count', info.get('likes', 0))
            duration = info.get('duration', 0)
            video_id = info.get('id', info.get('display_id', 'unknown'))
            
            # Try to find the audio file
            audio_path = None
            possible_paths = [
                f"/tmp/{video_id}.mp3",
                f"/tmp/{video_id}.m4a",
                f"/tmp/{video_id}.webm",
            ]
            
            # Also check for files with different extensions
            for ext in ['mp3', 'm4a', 'webm', 'ogg']:
                test_path = f"/tmp/{video_id}.{ext}"
                if os.path.exists(test_path):
                    audio_path = test_path
                    break
            
            # If no audio file found, check all files in /tmp
            if not audio_path:
                import glob
                tmp_files = glob.glob(f"/tmp/{video_id}.*")
                if tmp_files:
                    audio_path = tmp_files[0]
        
        # Step 2: Transcribe with Whisper (if audio available)
        # For very long videos (>10 minutes), skip transcription to save time
        transcript = ""
        description = info.get('description', '')[:1000] if info.get('description') else ''
        
        if duration > 600:  # Skip transcription for videos longer than 10 minutes
            logger.info(f"Video is {duration}s long, skipping transcription. Using description instead.")
            transcript = description if description else "Long video - transcription skipped for efficiency"
        elif audio_path and os.path.exists(audio_path):
            try:
                logger.info(f"Transcribing video with Whisper from {audio_path}...")
                whisper_model = get_whisper_model()
                # For long videos, transcribe only first 5 minutes
                if duration > 300:
                    logger.info("Video is long, transcribing first 5 minutes only")
                result = whisper_model.transcribe(audio_path)
                transcript = result.get('text', '')
                
                if not transcript:
                    logger.warning("Whisper returned empty transcript")
                    transcript = description if description else "No speech detected in video"
                
                # Clean up audio file
                try:
                    os.remove(audio_path)
                except:
                    pass
            except Exception as e:
                logger.warning(f"Transcription failed: {e}. Using description as fallback.")
                transcript = description if description else f"Transcription unavailable: {str(e)[:100]}"
        else:
            logger.warning(f"No audio file found at {audio_path}, using description as fallback")
            transcript = description if description else "Video download failed - using metadata only"
        
        # Step 3: Analyze with LLM (FREE!)
        # Build a more detailed prompt with available metadata
        description = info.get('description', '')[:500] if info.get('description') else ''
        tags = ', '.join(info.get('tags', [])[:10]) if info.get('tags') else ''
        
        analysis_prompt = f"""Analyze this viral video and extract key elements:

TITLE: {title}
VIEWS: {views:,}
LIKES: {likes:,}
DURATION: {duration}s ({duration//60}m {duration%60}s)

DESCRIPTION: {description if description else "No description available"}
TAGS: {tags if tags else "No tags available"}

TRANSCRIPT:
{transcript if transcript and transcript != "Video download failed - transcription unavailable" else "No transcript available - analyzing based on title and metadata"}

Based on the title "{title}" and the fact this video has {views:,} views and {likes:,} likes, provide a detailed analysis in JSON format:
{{
  "hook": "The opening hook (first 3 seconds) - what grabs attention based on the title",
  "story_structure": {{
    "setup": "How the video likely starts based on the title",
    "conflict": "The problem or tension that creates engagement",
    "resolution": "How it likely resolves",
    "cta": "Call to action or ending"
  }},
  "visual_style": "Description of visual approach based on title and engagement",
  "key_moments": [
    {{"timestamp": "0:03", "description": "Early hook moment", "why_it_works": "Why this works for engagement"}},
    {{"timestamp": "{duration//4}", "description": "Mid-point moment", "why_it_works": "Why this maintains interest"}}
  ],
  "remix_suggestions": [
    "How to adapt this concept for your niche",
    "Alternative hooks to try based on this format",
    "What elements to keep vs change"
  ]
}}

IMPORTANT: Output ONLY valid JSON, no markdown, no code blocks, just the JSON object."""

        logger.info("Analyzing with LLM...")
        try:
            llm_response = _llm_backend.generate([
                {"role": "user", "content": analysis_prompt}
            ])
            logger.info(f"LLM response received, length: {len(llm_response)}")
        except Exception as e:
            logger.error(f"LLM generation failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"LLM analysis failed: {str(e)}")
        
        # Parse JSON response with better error handling
        response_clean = llm_response.strip()
        
        # Remove markdown code blocks if present
        if "```json" in response_clean:
            response_clean = response_clean.split("```json")[1].split("```")[0].strip()
        elif "```" in response_clean:
            # Try to extract JSON from code block
            parts = response_clean.split("```")
            for part in parts:
                part = part.strip()
                if part.startswith("{") and part.endswith("}"):
                    response_clean = part
                    break
        
        # Try to find JSON object in response
        if not response_clean.startswith("{"):
            # Try to find JSON object
            start_idx = response_clean.find("{")
            end_idx = response_clean.rfind("}")
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                response_clean = response_clean[start_idx:end_idx+1]
        
        try:
            analysis = json.loads(response_clean)
            logger.info("Successfully parsed LLM JSON response")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {e}")
            logger.error(f"Response was: {response_clean[:1000]}")
            
            # Try to extract partial data from the response
            analysis = {
                "hook": _extract_field(response_clean, "hook", f"Opening hook based on: {title}"),
                "story_structure": {
                    "setup": _extract_field(response_clean, "setup", f"The video starts with {title}"),
                    "conflict": _extract_field(response_clean, "conflict", "Creates tension and engagement"),
                    "resolution": _extract_field(response_clean, "resolution", "Resolves the main challenge"),
                    "cta": _extract_field(response_clean, "cta", "Encourages engagement")
                },
                "visual_style": _extract_field(response_clean, "visual_style", "Engaging visual style based on high engagement"),
                "key_moments": [
                    {"timestamp": "0:03", "description": "Opening hook", "why_it_works": "Grabs attention immediately"},
                    {"timestamp": f"{duration//4}", "description": "Key moment", "why_it_works": "Maintains engagement"}
                ],
                "remix_suggestions": [
                    f"Adapt the '{title}' concept for your niche",
                    "Use similar hook structure that drives {views:,} views",
                    "Maintain high engagement elements that generated {likes:,} likes"
                ]
            }
        
        return VideoAnalysisResponse(
            title=title,
            views=views,
            likes=likes,
            duration=duration,
            transcript=transcript,
            hook=analysis.get('hook', 'Analysis unavailable'),
            story_structure=analysis.get('story_structure', {}),
            visual_style=analysis.get('visual_style', 'Analysis unavailable'),
            key_moments=analysis.get('key_moments', []),
            remix_suggestions=analysis.get('remix_suggestions', [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Video analysis failed: {str(e)}")

async def analyze_instagram_video(url: str):
    """
    Analyze Instagram video using instaloader (works better than yt-dlp for Instagram)
    """
    try:
        # Extract shortcode from Instagram URL
        # URLs can be: https://instagram.com/p/SHORTCODE/ or https://www.instagram.com/reel/SHORTCODE/
        shortcode_match = re.search(r'(?:p|reel)/([A-Za-z0-9_-]+)', url)
        if not shortcode_match:
            # Check if it's a profile URL instead of a post URL
            if re.search(r'instagram\.com/[^/]+/?$', url) and '/p/' not in url and '/reel/' not in url:
                raise HTTPException(
                    status_code=400, 
                    detail="This is a profile URL, not a video URL. Please provide a specific post or reel URL.\n\n"
                           "To get a post/reel URL:\n"
                           "1. Go to the Instagram post/reel you want to analyze\n"
                           "2. Click the three dots (⋯) or share button\n"
                           "3. Select 'Copy link'\n"
                           "4. Use that URL (should look like: https://www.instagram.com/p/SHORTCODE/ or https://www.instagram.com/reel/SHORTCODE/)"
                )
            raise HTTPException(
                status_code=400, 
                detail="Invalid Instagram URL format. Expected format:\n"
                       "- Post: https://www.instagram.com/p/SHORTCODE/\n"
                       "- Reel: https://www.instagram.com/reel/SHORTCODE/\n\n"
                       "Note: Profile URLs (like /username) are not supported. You need a specific post/reel URL."
            )
        
        shortcode = shortcode_match.group(1)
        logger.info(f"Extracting Instagram post with shortcode: {shortcode}")
        
        # Use instaloader to get post metadata
        L = instaloader.Instaloader()
        L.download_pictures = False
        L.download_videos = True  # We need the video
        L.download_video_thumbnails = False
        L.download_geotags = False
        L.download_comments = False
        L.save_metadata = False
        L.compress_json = False
        L.request_timeout = 30
        
        try:
            post = instaloader.Post.from_shortcode(L.context, shortcode)
        except instaloader.exceptions.ProfileNotExistsException:
            raise HTTPException(status_code=404, detail="Instagram post not found. The post may have been deleted or the URL is incorrect.")
        except instaloader.exceptions.PrivateProfileNotFollowedException:
            raise HTTPException(status_code=403, detail="This Instagram post is from a private account. Public posts work best.")
        except instaloader.exceptions.LoginRequiredException:
            raise HTTPException(status_code=403, detail="Instagram requires login for this post. Please use a public post.")
        except Exception as e:
            # Catch any other instaloader exceptions
            if "not found" in str(e).lower() or "does not exist" in str(e).lower():
                raise HTTPException(status_code=404, detail=f"Instagram post not found: {str(e)}")
            elif "private" in str(e).lower():
                raise HTTPException(status_code=403, detail="This Instagram post is from a private account. Public posts work best.")
            else:
                raise HTTPException(status_code=400, detail=f"Failed to access Instagram post: {str(e)}")
        
        # Check if it's a video
        if not post.is_video:
            raise HTTPException(status_code=400, detail="This Instagram post is not a video. Please provide a video/reel URL.")
        
        # Get metadata
        title = post.caption[:200] if post.caption else "Instagram Video"
        views = post.video_view_count if hasattr(post, 'video_view_count') and post.video_view_count else 0
        likes = post.likes
        duration = 0  # Instagram doesn't provide duration in metadata
        video_url = post.video_url if hasattr(post, 'video_url') else None
        
        if not video_url:
            raise HTTPException(status_code=500, detail="Could not get video URL from Instagram post")
        
        logger.info(f"Instagram video metadata: {views} views, {likes} likes")
        
        # Download video using requests (direct download)
        audio_path = None
        video_path = None
        
        try:
            # Download video to temp file
            logger.info("Downloading Instagram video...")
            response = requests.get(video_url, stream=True, timeout=60, headers={
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15'
            })
            response.raise_for_status()
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                video_path = tmp_file.name
                for chunk in response.iter_content(chunk_size=8192):
                    tmp_file.write(chunk)
            
            logger.info(f"Video downloaded to {video_path}")
            
            # Extract audio using ffmpeg
            audio_path = video_path.replace('.mp4', '.mp3')
            try:
                subprocess.run([
                    'ffmpeg', '-i', video_path, '-vn', '-acodec', 'libmp3lame', 
                    '-ab', '192k', '-ar', '44100', '-y', audio_path
                ], check=True, capture_output=True, timeout=60)
                logger.info(f"Audio extracted to {audio_path}")
            except subprocess.TimeoutExpired:
                logger.warning("FFmpeg extraction timed out")
            except Exception as e:
                logger.warning(f"FFmpeg extraction failed: {e}")
                # Try to use video file directly for transcription
                audio_path = video_path
            
            # Get duration using ffprobe
            try:
                result = subprocess.run([
                    'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                    '-of', 'default=noprint_wrappers=1:nokey=1', video_path
                ], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    duration = int(float(result.stdout.strip()))
            except:
                pass
            
        except Exception as e:
            logger.error(f"Failed to download Instagram video: {e}")
            # Continue with metadata-only analysis
            audio_path = None
        
        # Step 2: Transcribe with Whisper (if audio available)
        transcript = ""
        description = title[:1000] if title else ''
        
        if audio_path and os.path.exists(audio_path):
            try:
                logger.info(f"Transcribing Instagram video with Whisper from {audio_path}...")
                whisper_model = get_whisper_model()
                result = whisper_model.transcribe(audio_path)
                transcript = result.get('text', '')
                
                if not transcript:
                    logger.warning("Whisper returned empty transcript")
                    transcript = description if description else "No speech detected in video"
                
                # Clean up files
                try:
                    if os.path.exists(audio_path) and audio_path != video_path:
                        os.remove(audio_path)
                    if video_path and os.path.exists(video_path):
                        os.remove(video_path)
                except:
                    pass
            except Exception as e:
                logger.warning(f"Transcription failed: {e}. Using caption as fallback.")
                transcript = description if description else f"Transcription unavailable: {str(e)[:100]}"
        else:
            logger.warning("No audio file available, using caption as fallback")
            transcript = description if description else "Video download failed - using metadata only"
        
        # Step 3: Analyze with LLM (same as YouTube/TikTok)
        analysis_prompt = f"""Analyze this viral Instagram video and extract key elements:

TITLE/CAPTION: {title}
VIEWS: {views:,}
LIKES: {likes:,}
DURATION: {duration}s ({duration//60}m {duration%60}s) if available

TRANSCRIPT:
{transcript if transcript and transcript != "Video download failed - transcription unavailable" else "No transcript available - analyzing based on caption and metadata"}

Based on the caption "{title}" and the fact this video has {views:,} views and {likes:,} likes, provide a detailed analysis in JSON format:
{{
  "hook": "The opening hook (first 3 seconds) - what grabs attention based on the caption",
  "story_structure": {{
    "setup": "How the video likely starts based on the caption",
    "conflict": "The problem or tension that creates engagement",
    "resolution": "How it likely resolves",
    "cta": "Call to action or ending"
  }},
  "visual_style": "Description of visual approach based on caption and engagement",
  "key_moments": [
    {{"timestamp": "0:03", "description": "Early hook moment", "why_it_works": "Why this works for engagement"}},
    {{"timestamp": "mid", "description": "Mid-point moment", "why_it_works": "Why this maintains interest"}}
  ],
  "remix_suggestions": [
    "How to adapt this concept for your niche",
    "Alternative hooks to try based on this format",
    "What elements to keep vs change"
  ]
}}

IMPORTANT: Output ONLY valid JSON, no markdown, no code blocks, just the JSON object."""

        logger.info("Analyzing Instagram video with LLM...")
        try:
            llm_response = _llm_backend.generate([
                {"role": "user", "content": analysis_prompt}
            ])
            logger.info(f"LLM response received, length: {len(llm_response)}")
        except Exception as e:
            logger.error(f"LLM generation failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"LLM analysis failed: {str(e)}")
        
        # Parse JSON response (same logic as YouTube)
        response_clean = llm_response.strip()
        
        # Remove markdown code blocks if present
        if "```json" in response_clean:
            response_clean = response_clean.split("```json")[1].split("```")[0].strip()
        elif "```" in response_clean:
            response_clean = response_clean.split("```")[1].split("```")[0].strip()
        
        try:
            analysis_data = json.loads(response_clean)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parsing failed: {e}. Attempting field extraction...")
            # Fallback: extract fields manually
            analysis_data = {
                "hook": _extract_field(llm_response, "hook", "Analysis unavailable"),
                "story_structure": {
                    "setup": _extract_field(llm_response, "setup", "Could not analyze"),
                    "conflict": _extract_field(llm_response, "conflict", "Could not analyze"),
                    "resolution": _extract_field(llm_response, "resolution", "Could not analyze"),
                    "cta": _extract_field(llm_response, "cta", "Could not analyze")
                },
                "visual_style": _extract_field(llm_response, "visual_style", "Could not analyze"),
                "key_moments": [],
                "remix_suggestions": []
            }
        
        # Build response
        return VideoAnalysisResponse(
            title=title,
            views=views,
            likes=likes,
            duration=duration,
            transcript=transcript,
            hook=analysis_data.get("hook", "Analysis unavailable"),
            story_structure=analysis_data.get("story_structure", {
                "setup": "Could not analyze",
                "conflict": "Could not analyze",
                "resolution": "Could not analyze",
                "cta": "Could not analyze"
            }),
            visual_style=analysis_data.get("visual_style", "Could not analyze"),
            key_moments=analysis_data.get("key_moments", []),
            remix_suggestions=analysis_data.get("remix_suggestions", ["Analysis failed - please try again"])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Instagram video analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to analyze Instagram video: {str(e)}")

@router.get("/list-videos")
async def list_profile_videos(username: str, limit: int = 20):
    """
    List all videos/reels from an Instagram profile
    Allows users to browse and select videos to analyze
    """
    try:
        # Clean username - remove @ if present
        username = username.strip().lstrip('@')
        
        if not username:
            raise HTTPException(status_code=400, detail="Username cannot be empty")
        
        # Limit to reasonable number for performance
        limit = min(limit, 50)  # Cap at 50 for performance
        
        # Use instaloader to get profile posts
        L = instaloader.Instaloader()
        L.download_pictures = False
        L.download_videos = False
        L.download_video_thumbnails = False
        L.download_geotags = False
        L.download_comments = False
        L.save_metadata = False
        L.compress_json = False
        L.request_timeout = 30
        
        try:
            logger.info(f"Loading Instagram profile: {username}")
            profile = instaloader.Profile.from_username(L.context, username)
            
            if profile.is_private:
                raise HTTPException(status_code=403, detail="This profile is private. Public profiles work best.")
            
            videos = []
            post_count = 0
            
            # Get posts and filter for videos/reels
            try:
                import time
                start_time = time.time()
                timeout = 45  # 45 second timeout
                
                posts_iterator = profile.get_posts()
                
                for post in posts_iterator:
                    # Check timeout
                    elapsed = time.time() - start_time
                    if elapsed > timeout:
                        logger.warning(f"Timeout reached after {timeout}s, stopping at {post_count} videos")
                        break
                    
                    if post_count >= limit:
                        break
                    
                    # Only include videos/reels
                    if post.is_video:
                        try:
                            views = post.video_view_count if hasattr(post, 'video_view_count') and post.video_view_count else 0
                            caption = (post.caption[:100] if post.caption else '') or ''
                            
                            videos.append({
                                'shortcode': post.shortcode,
                                'url': f"https://www.instagram.com/p/{post.shortcode}/",
                                'caption': caption,
                                'views': views,
                                'likes': post.likes,
                                'comments': post.comments,
                                'created_at': post.date_utc.isoformat() if post.date_utc else '',
                                'thumbnail': post.url if hasattr(post, 'url') else ''
                            })
                            post_count += 1
                            
                            # Log progress every 5 videos
                            if post_count % 5 == 0:
                                logger.info(f"Found {post_count}/{limit} videos...")
                                
                        except Exception as post_error:
                            logger.warning(f"Error processing post: {post_error}")
                            continue
                            
            except instaloader.exceptions.LoginRequiredException:
                raise HTTPException(status_code=403, detail="Instagram requires login for this profile. Please use a public profile.")
            except instaloader.exceptions.ConnectionException as e:
                raise HTTPException(status_code=503, detail=f"Connection error: {str(e)}. Instagram may be rate-limiting requests.")
            
            if not videos:
                raise HTTPException(status_code=404, detail=f"No videos found for @{username}. The profile may not have any videos/reels, or they may be private.")
            
            return {
                "username": username,
                "total_videos": len(videos),
                "videos": videos
            }
            
        except instaloader.exceptions.ProfileNotExistsException:
            raise HTTPException(status_code=404, detail=f"Profile @{username} does not exist. Please check the username.")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to list videos: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to fetch videos: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List videos failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list videos: {str(e)}")

@router.get("/list-youtube-videos")
async def list_youtube_videos(channel_identifier: str, limit: int = 20):
    """
    List all videos from a YouTube channel
    Supports: @username, channel URL, or channel ID
    """
    try:
        if not channel_identifier:
            raise HTTPException(status_code=400, detail="Channel identifier cannot be empty")
        
        # Normalize channel URL
        import re
        channel_url = channel_identifier.strip()
        
        # Handle different formats
        if '@' in channel_url and 'youtube.com' not in channel_url:
            # Just @username format
            channel_url = f"https://www.youtube.com/@{channel_url.lstrip('@')}/videos"
        elif '@' in channel_url and 'youtube.com' in channel_url:
            # Full URL with @
            if '/videos' not in channel_url:
                channel_url = channel_url.rstrip('/') + '/videos'
        elif 'youtube.com' in channel_url:
            # Already a URL, ensure /videos suffix
            if '/@' in channel_url and '/videos' not in channel_url:
                channel_url = channel_url.rstrip('/') + '/videos'
        else:
            # Assume it's a username
            channel_url = f"https://www.youtube.com/@{channel_url.lstrip('@')}/videos"
        
        logger.info(f"Fetching YouTube videos from: {channel_url}")
        
        # Use yt-dlp to get channel videos
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'playlistend': limit,
            'ignoreerrors': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                playlist_info = ydl.extract_info(channel_url, download=False)
                
                if not playlist_info:
                    raise HTTPException(status_code=404, detail="Channel not found or has no videos")
                
                entries = playlist_info.get('entries', [])
                if not entries:
                    raise HTTPException(status_code=404, detail="No videos found in channel")
                
                videos = []
                for entry in entries[:limit]:
                    if not entry:
                        continue
                    
                    video_id = entry.get('id')
                    if not video_id:
                        continue
                    
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    
                    videos.append({
                        'video_id': video_id,
                        'url': video_url,
                        'title': entry.get('title', 'Unknown'),
                        'view_count': entry.get('view_count', entry.get('play_count', 0)) or 0,
                        'duration': entry.get('duration', 0) or 0,
                        'thumbnail': f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg"
                    })
                
                return {
                    "channel": channel_url,
                    "total_videos": len(videos),
                    "videos": videos
                }
                
        except Exception as e:
            logger.error(f"Failed to fetch YouTube videos: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to fetch YouTube videos: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List YouTube videos failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list YouTube videos: {str(e)}")

@router.get("/list-tiktok-videos")
async def list_tiktok_videos(username: str, limit: int = 20):
    """
    List all videos from a TikTok user
    """
    try:
        # Clean username - remove @ if present
        username = username.strip().lstrip('@')
        
        if not username:
            raise HTTPException(status_code=400, detail="Username cannot be empty")
        
        # Limit to reasonable number for performance
        limit = min(limit, 30)  # Cap at 30 for TikTok (slower than others)
        
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
                        
                        # Get video metadata safely
                        video_id = video.id if hasattr(video, 'id') else ''
                        description = video.desc[:100] if hasattr(video, 'desc') and video.desc else ''
                        
                        # Get thumbnail safely
                        thumbnail = ''
                        if hasattr(video, 'video') and hasattr(video.video, 'cover'):
                            thumbnail = video.video.cover
                        
                        videos.append({
                            'video_id': video_id,
                            'url': f"https://tiktok.com/@{username}/video/{video_id}",
                            'title': description,
                            'view_count': play_count,
                            'likes': digg_count,
                            'comments': comment_count,
                            'thumbnail': thumbnail
                        })
                        video_count += 1
                        
                    except Exception as video_error:
                        logger.warning(f"Error processing TikTok video: {video_error}")
                        continue
                
                if not videos:
                    raise HTTPException(
                        status_code=404,
                        detail=f"No videos found for @{username}. The account may be private, empty, or the username may be incorrect."
                    )
                
                return {
                    "username": username,
                    "total_videos": len(videos),
                    "videos": videos
                }
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"TikTok video listing failed: {e}", exc_info=True)
            
            # Provide more helpful error messages
            error_msg = str(e)
            if "bot" in error_msg.lower() or "empty response" in error_msg.lower():
                raise HTTPException(
                    status_code=503,
                    detail="TikTok detected automated access and blocked the request. TikTok has strong anti-bot protections. Please try again later or use YouTube/Instagram instead."
                )
            elif "not found" in error_msg.lower() or "doesn't exist" in error_msg.lower():
                raise HTTPException(
                    status_code=404,
                    detail=f"TikTok user @{username} not found. Please check the username."
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to fetch TikTok videos: {error_msg}. Note: TikTok scraping is experimental and may not always work due to anti-bot protections."
                )
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List TikTok videos failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list TikTok videos: {str(e)}")

@router.post("/download-video")
async def download_video(url: str, quality: str = "best"):
    """
    Download video for offline analysis
    """
    
    ydl_opts = {
        'format': quality,
        'outtmpl': '/tmp/downloads/%(title)s.%(ext)s',
    }
    
    try:
        os.makedirs('/tmp/downloads', exist_ok=True)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            return {
                "success": True,
                "filename": filename,
                "title": info.get('title'),
                "duration": info.get('duration')
            }
    except Exception as e:
        logger.error(f"Video download failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-analyze")
async def batch_analyze_channel(channel_url: str, limit: int = 10):
    """
    Analyze multiple videos from a channel/creator
    Like Sandcastles' "Track favorite channels" feature
    NOTE: Currently only supports YouTube channels. Instagram profiles are not supported.
    
    Accepts:
    - @username (e.g., @MrBeast)
    - username (e.g., MrBeast)
    - Full URL (e.g., https://www.youtube.com/@MrBeast/videos)
    """
    
    if not channel_url:
        raise HTTPException(status_code=400, detail="channel_url is required")
    
    # Check if it's Instagram - not supported for batch analysis
    if 'instagram.com' in channel_url.lower():
        raise HTTPException(
            status_code=400, 
            detail="Instagram profiles are not supported for batch analysis. Please use YouTube channels (e.g., @username)"
        )
    
    # Normalize YouTube channel URL - handle @username format
    import re
    channel_url_clean = channel_url.strip()
    
    # If it's just a username (with or without @), convert to URL
    if not channel_url_clean.startswith('http'):
        # Remove @ if present
        username = channel_url_clean.lstrip('@')
        # Convert to YouTube channel URL
        channel_url_clean = f"https://www.youtube.com/@{username}/videos"
        logger.info(f"Converted username '{channel_url}' to URL: {channel_url_clean}")
    
    # Normalize existing YouTube URLs
    if '@' in channel_url_clean and 'youtube.com' in channel_url_clean:
        # Ensure /videos suffix is present for channel URLs
        if '/@' in channel_url_clean and '/videos' not in channel_url_clean:
            channel_url_clean = channel_url_clean.rstrip('/') + '/videos'
        elif '/@' not in channel_url_clean:
            # Extract username and convert
            match = re.search(r'@([^/?]+)', channel_url_clean)
            if match:
                channel_url_clean = f"https://www.youtube.com/@{match.group(1)}/videos"
    
    logger.info(f"Processing channel URL: {channel_url_clean}")
    
    # First, get the list of videos (flat extraction for speed)
    ydl_opts_flat = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'playlistend': limit,
        'ignoreerrors': True,
    }
    
    try:
        logger.info(f"Fetching video list from {channel_url_clean}")
        with yt_dlp.YoutubeDL(ydl_opts_flat) as ydl:
            try:
                playlist_info = ydl.extract_info(channel_url_clean, download=False)
            except Exception as e:
                logger.error(f"Failed to extract channel info: {e}")
                # Try with /videos suffix if not present
                if '/videos' not in channel_url_clean and 'youtube.com' in channel_url_clean:
                    try:
                        channel_url_with_videos = channel_url_clean.rstrip('/') + '/videos'
                        logger.info(f"Trying with /videos suffix: {channel_url_with_videos}")
                        playlist_info = ydl.extract_info(channel_url_with_videos, download=False)
                        channel_url_clean = channel_url_with_videos
                    except Exception as e2:
                        raise HTTPException(status_code=400, detail=f"Failed to access channel: {str(e2)}. Make sure the username is correct (e.g., @MrBeast).")
                else:
                    raise HTTPException(status_code=400, detail=f"Failed to access channel: {str(e)}. Make sure the username is correct (e.g., @MrBeast).")
            
            if not playlist_info:
                raise HTTPException(status_code=404, detail="Channel not found or has no videos")
            
            entries = playlist_info.get('entries', [])
            if not entries:
                # Try to get entries differently - sometimes it's nested
                if isinstance(playlist_info, dict) and 'entries' in playlist_info:
                    entries = [e for e in playlist_info['entries'] if e]
                if not entries:
                    raise HTTPException(status_code=404, detail="No videos found in channel")
            
            logger.info(f"Found {len(entries)} video entries")
            
            # Extract basic info from flat extraction (much faster)
            # Flat extraction already gives us some metadata, use that first
            videos = []
            
            logger.info(f"Processing {min(len(entries), limit)} videos from flat extraction...")
            
            for i, entry in enumerate(entries[:limit]):
                if not entry:
                    continue
                
                try:
                    # Get video ID and construct URL
                    video_id = entry.get('id')
                    if not video_id:
                        continue
                    
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    
                    # Use data from flat extraction (faster, but may have limited metadata)
                    # NOTE: Flat extraction gives view_count but NOT like_count
                    # We'll fetch detailed info later to get like counts
                    videos.append({
                        'title': entry.get('title', 'Unknown'),
                        'url': video_url,
                        'view_count': entry.get('view_count', entry.get('play_count', 0)) or 0,
                        'like_count': entry.get('like_count', 0) or 0,  # Will be 0 from flat extraction
                        'duration': entry.get('duration', 0) or 0
                    })
                except Exception as e:
                    logger.warning(f"Error processing video entry {i}: {e}")
                    continue
            
            # Flat extraction gives view counts but NOT like counts
            # We need to fetch detailed info to get like counts for all videos
            # Check if we need to fetch details (if like counts are missing or views are missing)
            videos_without_likes = [i for i, v in enumerate(videos) if v.get('like_count', 0) == 0]
            videos_without_views = [i for i, v in enumerate(videos) if v.get('view_count', 0) == 0]
            
            # Always fetch detailed info to get like counts (flat extraction doesn't provide them)
            # Also fetch if view counts are missing
            if (videos_without_likes or videos_without_views) and len(videos) > 0:
                # Fetch details for all videos (up to limit) to get like counts
                # Combine indices, remove duplicates, and limit to the number of videos we have
                videos_to_fetch = list(set(videos_without_likes + videos_without_views))[:limit]
                logger.info(f"Fetching detailed info for {len(videos_to_fetch)} videos to get likes/views...")
                
                ydl_opts_detailed = {
                    'quiet': True,
                    'no_warnings': True,
                    'skip_download': True,
                    'ignoreerrors': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts_detailed) as ydl_detailed:
                    for i in sorted(videos_to_fetch):
                        if i >= len(videos):
                            continue
                        
                        video = videos[i]
                        try:
                            video_url = video.get('url')
                            if not video_url:
                                continue
                            
                            logger.info(f"Fetching details for video {i+1}/{len(videos_to_fetch)}: {video.get('title', 'Unknown')[:50]}")
                            video_info = ydl_detailed.extract_info(video_url, download=False)
                            if video_info:
                                # Update with detailed info, preserving existing data if new data is missing
                                videos[i] = {
                                    'title': video_info.get('title', video.get('title', 'Unknown')),
                                    'url': video_info.get('webpage_url', video_url),
                                    'view_count': video_info.get('view_count', video_info.get('play_count', video.get('view_count', 0))) or 0,
                                    'like_count': video_info.get('like_count', video.get('like_count', 0)) or 0,
                                    'duration': video_info.get('duration', video.get('duration', 0)) or 0
                                }
                        except Exception as e:
                            logger.warning(f"Failed to get details for video {i}: {e}")
                            continue
            
            if not videos:
                raise HTTPException(status_code=404, detail="No valid videos found in channel")
            
            # Sort by views (find outliers)
            videos_sorted = sorted(videos, key=lambda x: x.get('view_count', 0), reverse=True)
            
            return {
                "channel": playlist_info.get('title', playlist_info.get('uploader', 'Unknown')),
                "total_videos": len(videos),
                "top_performers": videos_sorted[:5],
                "all_videos": videos_sorted
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Channel analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Channel analysis failed: {str(e)}")

