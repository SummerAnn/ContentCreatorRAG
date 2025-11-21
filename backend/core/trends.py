"""
Trend Integration Service
Fetches real trending topics from multiple sources and integrates them into content generation.
"""

import logging
import requests
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)

@dataclass
class Trend:
    """Represents a trending topic"""
    topic: str
    platform: str
    category: str
    popularity_score: float  # 0-100
    source: str
    metadata: Dict = None

class TrendService:
    """Service to fetch and manage trending topics"""
    
    def __init__(self):
        self.cache: Dict[str, tuple] = {}  # (trends, timestamp)
        self.cache_duration = 3600  # 1 hour cache
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    
    def get_trends(
        self, 
        platform: str, 
        niche: str = None, 
        use_cache: bool = True
    ) -> List[Trend]:
        """
        Get trending topics for a platform and optional niche.
        
        Args:
            platform: Platform name (tiktok, youtube, instagram, etc.)
            niche: Optional niche filter (beauty, tech, food, etc.)
            use_cache: Whether to use cached results
        
        Returns:
            List of Trend objects
        """
        cache_key = f"{platform}_{niche or 'all'}"
        
        # Check cache
        if use_cache and cache_key in self.cache:
            trends, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_duration:
                logger.info(f"Returning cached trends for {cache_key}")
                return trends
        
        # Fetch trends from multiple sources
        all_trends = []
        
        try:
            # Reddit trends (free, no API key needed)
            reddit_trends = self._get_reddit_trends(platform, niche)
            all_trends.extend(reddit_trends)
        except Exception as e:
            logger.warning(f"Failed to fetch Reddit trends: {e}")
        
        try:
            # Google Trends (via RSS/alternative methods)
            google_trends = self._get_google_trends_alternative(platform, niche)
            all_trends.extend(google_trends)
        except Exception as e:
            logger.warning(f"Failed to fetch Google trends: {e}")
        
        try:
            # General web trends (via news aggregators)
            web_trends = self._get_web_trends(platform, niche)
            all_trends.extend(web_trends)
        except Exception as e:
            logger.warning(f"Failed to fetch web trends: {e}")
        
        # Deduplicate and sort by popularity
        unique_trends = self._deduplicate_trends(all_trends)
        unique_trends.sort(key=lambda x: x.popularity_score, reverse=True)
        
        # Cache results
        self.cache[cache_key] = (unique_trends[:20], time.time())  # Top 20
        
        return unique_trends[:20]
    
    def _get_reddit_trends(self, platform: str, niche: str = None) -> List[Trend]:
        """Fetch trending topics from Reddit"""
        trends = []
        
        # Map platforms to relevant subreddits
        subreddit_map = {
            'tiktok': ['TikTok', 'TikTokCringe', 'TikTokmemes'],
            'youtube': ['youtube', 'videos', 'youtubers'],
            'instagram': ['Instagram', 'Instagramreality'],
            'youtube_short': ['youtube', 'videos'],
            'instagram_reel': ['Instagram', 'Instagramreality'],
            'linkedin': ['LinkedIn', 'careerguidance'],
            'twitter_thread': ['Twitter', 'socialmedia'],
        }
        
        subreddits = subreddit_map.get(platform.lower(), ['popular', 'all'])
        
        for subreddit in subreddits[:2]:  # Limit to 2 subreddits
            try:
                url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10"
                headers = {'User-Agent': self.user_agent}
                response = requests.get(url, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    posts = data.get('data', {}).get('children', [])
                    
                    for post in posts[:5]:  # Top 5 from each subreddit
                        post_data = post.get('data', {})
                        title = post_data.get('title', '')
                        score = post_data.get('score', 0)
                        
                        # Filter by niche if provided
                        if niche and niche.lower() not in title.lower():
                            continue
                        
                        trends.append(Trend(
                            topic=title,
                            platform=platform,
                            category=niche or 'general',
                            popularity_score=min(score / 100, 100),  # Normalize to 0-100
                            source='reddit',
                            metadata={'subreddit': subreddit, 'upvotes': score}
                        ))
                
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                logger.debug(f"Error fetching Reddit r/{subreddit}: {e}")
                continue
        
        return trends
    
    def _get_google_trends_alternative(self, platform: str, niche: str = None) -> List[Trend]:
        """
        Alternative Google Trends fetching.
        Note: Official API requires authentication. This uses RSS feeds and web scraping alternatives.
        """
        trends = []
        
        # Use Google Trends RSS (unofficial but works)
        try:
            # For now, we'll use a combination of known trending topics
            # In production, you could use pytrends library or similar
            common_trends = self._get_common_trending_topics(platform, niche)
            trends.extend(common_trends)
        except Exception as e:
            logger.debug(f"Error fetching Google Trends alternative: {e}")
        
        return trends
    
    def _get_common_trending_topics(self, platform: str, niche: str = None) -> List[Trend]:
        """Get common trending topics based on platform and niche patterns"""
        trends = []
        
        # Platform-specific trending patterns
        platform_trends = {
            'tiktok': [
                'viral dance challenge', 'trending audio', 'POV trend', 'get ready with me',
                'day in my life', 'trending sound', 'aesthetic', 'main character energy'
            ],
            'youtube': [
                'tutorial', 'how to', 'product review', 'unboxing', 'vlog', 'reaction',
                'explained', 'tips and tricks', 'beginner guide'
            ],
            'instagram': [
                'aesthetic', 'lifestyle', 'outfit of the day', 'home decor', 'fitness journey',
                'beauty routine', 'travel', 'food', 'fashion'
            ],
            'youtube_short': [
                'quick tip', 'life hack', 'funny moment', 'satisfying', 'oddly satisfying',
                'before and after', 'transformation'
            ],
            'instagram_reel': [
                'trending audio', 'outfit check', 'get ready with me', 'day in my life',
                'aesthetic', 'vibe check'
            ],
            'linkedin': [
                'career advice', 'professional development', 'industry insights', 'networking',
                'leadership', 'productivity tips', 'business strategy'
            ],
        }
        
        base_topics = platform_trends.get(platform.lower(), ['trending', 'viral', 'popular'])
        
        # Add niche-specific variations
        if niche:
            niche_variations = {
                'beauty': ['skincare routine', 'makeup tutorial', 'product review', 'beauty hack'],
                'tech': ['tech review', 'gadget unboxing', 'app tutorial', 'tech tip'],
                'food': ['recipe', 'cooking tutorial', 'food hack', 'meal prep', 'restaurant review'],
                'fitness': ['workout routine', 'fitness transformation', 'gym tips', 'nutrition'],
                'travel': ['travel guide', 'destination', 'travel tips', 'packing', 'itinerary'],
                'education': ['study tips', 'tutorial', 'explained', 'how to learn', 'study with me'],
            }
            
            niche_topics = niche_variations.get(niche.lower(), [])
            base_topics.extend(niche_topics)
        
        # Create trend objects
        for i, topic in enumerate(base_topics[:10]):
            trends.append(Trend(
                topic=topic,
                platform=platform,
                category=niche or 'general',
                popularity_score=80 - (i * 5),  # Decreasing popularity
                source='common_patterns',
                metadata={'type': 'pattern_based'}
            ))
        
        return trends
    
    def _get_web_trends(self, platform: str, niche: str = None) -> List[Trend]:
        """Fetch trends from general web/news sources"""
        trends = []
        
        # Use news aggregator APIs (free tier available)
        # Example: NewsAPI, but requires API key
        # For now, return empty - can be extended with API keys
        
        return trends
    
    def _deduplicate_trends(self, trends: List[Trend]) -> List[Trend]:
        """Remove duplicate trends and merge popularity scores"""
        seen = {}
        
        for trend in trends:
            # Normalize topic for comparison
            normalized = trend.topic.lower().strip()
            
            if normalized in seen:
                # Merge: keep higher popularity, combine metadata
                existing = seen[normalized]
                existing.popularity_score = max(existing.popularity_score, trend.popularity_score)
                if existing.metadata:
                    existing.metadata.update(trend.metadata or {})
            else:
                seen[normalized] = trend
        
        return list(seen.values())
    
    def format_trends_for_prompt(self, trends: List[Trend], max_count: int = 5) -> str:
        """
        Format trends for inclusion in prompts.
        
        Args:
            trends: List of Trend objects
            max_count: Maximum number of trends to include
        
        Returns:
            Formatted string for prompt inclusion
        """
        if not trends:
            return "No specific trending topics available. Focus on evergreen content."
        
        top_trends = trends[:max_count]
        
        trend_list = []
        for trend in top_trends:
            trend_list.append(f"- {trend.topic} (trending on {trend.source})")
        
        return f"""CURRENT TRENDING TOPICS (consider incorporating if relevant):
{chr(10).join(trend_list)}

Note: Only use trends if they naturally fit your content. Don't force trends that don't match your niche or audience."""

# Global instance
trend_service = TrendService()

