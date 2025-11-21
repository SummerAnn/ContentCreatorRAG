# 🔥 Trend Integration Guide

## What's Actually Trending?

The trend system fetches **real trending topics** from multiple sources and integrates them into your content generation.

### Current Data Sources

1. **Reddit Trending Posts** (Free, No API Key Required)
   - Fetches hot posts from relevant subreddits
   - Platform-specific subreddits (r/TikTok, r/youtube, r/Instagram, etc.)
   - Real-time upvotes and engagement scores
   - Filtered by niche when provided

2. **Platform-Specific Trend Patterns**
   - Common trending formats per platform
   - Niche-specific variations
   - Pattern-based trending topics

3. **Common Trending Topics** (Fallback)
   - Platform-native trending formats
   - Niche-specific trending topics
   - Evergreen trending patterns

## How It Works

### Automatic Integration

When you generate hooks, the system:
1. Fetches trending topics for your platform + niche
2. Formats them for AI prompt inclusion
3. Automatically includes them in the generation prompt
4. AI considers trends when creating hooks (only if relevant)

### Example Trend Data

For **TikTok + Beauty** niche, you might get:
```
CURRENT TRENDING TOPICS (consider incorporating if relevant):
- viral dance challenge (trending on reddit)
- trending audio (trending on reddit)
- skincare routine (trending on common_patterns)
- makeup tutorial (trending on common_patterns)
- beauty hack (trending on common_patterns)
```

### API Endpoints

#### Get Trends
```bash
GET /api/trends/?platform=tiktok&niche=beauty
```

Response:
```json
{
  "status": "success",
  "platform": "tiktok",
  "niche": "beauty",
  "trends": [
    {
      "topic": "viral dance challenge",
      "platform": "tiktok",
      "category": "beauty",
      "popularity_score": 85.5,
      "source": "reddit",
      "metadata": {
        "subreddit": "TikTok",
        "upvotes": 8550
      }
    }
  ],
  "count": 20
}
```

#### Get Formatted Trends (for prompts)
```bash
GET /api/trends/formatted?platform=tiktok&niche=beauty&max_count=5
```

## Caching

- Trends are cached for **1 hour** to avoid rate limits
- Cache key: `{platform}_{niche}`
- Can force refresh with `use_cache=false`

## Platform-Specific Trends

### TikTok
- Viral dance challenges
- Trending audio/sounds
- POV trends
- Get ready with me
- Day in my life
- Aesthetic content
- Main character energy

### YouTube
- Tutorials
- Product reviews
- Unboxing
- Vlogs
- Reactions
- Explained videos
- Tips and tricks

### Instagram
- Aesthetic content
- Lifestyle
- Outfit of the day
- Home decor
- Fitness journey
- Beauty routine
- Travel

### LinkedIn
- Career advice
- Professional development
- Industry insights
- Networking
- Leadership
- Productivity tips

## Niche-Specific Trends

### Beauty
- Skincare routine
- Makeup tutorial
- Product review
- Beauty hack

### Tech
- Tech review
- Gadget unboxing
- App tutorial
- Tech tip

### Food
- Recipe
- Cooking tutorial
- Food hack
- Meal prep
- Restaurant review

### Fitness
- Workout routine
- Fitness transformation
- Gym tips
- Nutrition

### Travel
- Travel guide
- Destination
- Travel tips
- Packing
- Itinerary

## Future Enhancements

### Planned Integrations

1. **Google Trends API**
   - Requires API key
   - Real search trend data
   - Geographic trends
   - Time-based trends

2. **Twitter/X Trends API**
   - Real-time trending topics
   - Hashtag trends
   - Requires API key

3. **TikTok Creative Center API**
   - Official TikTok trends
   - Audio trends
   - Format trends
   - Requires API access

4. **YouTube Trends API**
   - YouTube trending videos
   - Category trends
   - Regional trends

5. **News Aggregator APIs**
   - NewsAPI
   - Current events
   - Breaking news

## How to Use

### In Content Generation

Trends are **automatically included** when generating hooks. The AI will:
- Consider trending topics if they fit naturally
- Not force trends that don't match your niche
- Use trends to inspire fresh angles
- Maintain your personality and style

### Manual Trend Fetching

You can also fetch trends manually via the API:

```python
import requests

# Get trends for TikTok beauty content
response = requests.get(
    "http://localhost:8000/api/trends/",
    params={"platform": "tiktok", "niche": "beauty"}
)

trends = response.json()["trends"]
```

### Frontend Integration (Coming Soon)

A UI component to display trending topics in the sidebar or as suggestions.

## Best Practices

1. **Don't Force Trends**: Only use trends that naturally fit your content
2. **Stay Authentic**: Trends should enhance, not replace, your unique voice
3. **Check Relevance**: Ensure trends match your niche and audience
4. **Timing Matters**: Some trends are time-sensitive
5. **Combine with RAG**: Use trends + your past successful content for best results

## Technical Details

### Trend Service Architecture

```
TrendService
├── get_trends() - Main entry point
├── _get_reddit_trends() - Reddit API
├── _get_google_trends_alternative() - Pattern-based
├── _get_web_trends() - News aggregators
└── format_trends_for_prompt() - Format for AI
```

### Caching Strategy

- In-memory cache (1 hour TTL)
- Cache key: `{platform}_{niche}`
- Automatic refresh after expiry
- Manual refresh available

### Rate Limiting

- Reddit: 0.5s delay between requests
- Respects Reddit's rate limits
- Graceful fallback on errors

## Troubleshooting

### No Trends Returned

- Check if Reddit is accessible
- Verify platform/niche spelling
- Check logs for API errors
- Fallback to pattern-based trends

### Trends Not Relevant

- Trends are filtered by niche
- Some platforms have limited subreddits
- Pattern-based trends are more generic
- Consider adding more specific sources

### API Errors

- Reddit API may be rate-limited
- Network connectivity issues
- Check backend logs
- System falls back gracefully

## Contributing

Want to add more trend sources? See `backend/core/trends.py` and add new methods following the existing pattern.

