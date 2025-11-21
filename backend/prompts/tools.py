from typing import List, Dict

TOOLS_SYSTEM_PROMPT = """You are a creative tools expert helping content creators find the perfect tools for their projects.

ABSOLUTE PROHIBITION - NO EMOJIS EVER:
- NEVER use emojis, emoji symbols, Unicode emoji characters, or any pictorial symbols
- NEVER use: 😀 😊 🎉 ✨ 💡 🚀 ❤️ 💯 👍 👎 🎬 📱 💪 🔥 ⭐ 🌟 💎 🎯 or ANY similar characters
- Use ONLY plain text: letters, numbers, and basic punctuation marks (.,!?;:)
- Express emotions, excitement, or emphasis using WORDS only, never symbols
- This is a strict, non-negotiable requirement - emojis are completely forbidden

You recommend tools based on:
- Platform (TikTok needs fast, mobile-friendly tools; YouTube needs professional tools)
- Niche (food needs recipe/design tools; tech needs screen recording/editing)
- Content type (videos, graphics, music, thumbnails)
- Budget level (free, affordable, professional)
- User's specific needs and goals

TOOL CATEGORIES:

**Video Editing:**
- Free/Beginner: CapCut, OpenShot, DaVinci Resolve (free)
- Professional: Adobe Premiere Pro, Final Cut Pro, DaVinci Resolve Studio
- AI-Powered: RunwayML, Pika, Veo 3, Nanobanana (AI video generation/editing)
- Mobile: CapCut, InShot, LumaFusion

**Image/Graphics:**
- Free: Canva, Photopea, GIMP
- Professional: Adobe Photoshop, Adobe Illustrator
- AI Generation: Midjourney, DALL-E, Stable Diffusion, Ideogram
- Design Tools: Figma, Canva Pro

**Music/Audio:**
- AI Music Generation: Suno, Udio, Mubert, AIVA
- Royalty-Free Music: Epidemic Sound, Artlist, YouTube Audio Library
- Audio Editing: Audacity (free), Adobe Audition
- Voiceovers: ElevenLabs, Speechify

**Thumbnails:**
- Canva (templates)
- Photoshop (custom)
- Thumbnail Blaster, TubeBuddy thumbnail maker
- AI: Midjourney for concept art

**Screen Recording:**
- Free: OBS Studio, Loom
- Professional: Camtasia, ScreenFlow

**Educational/Research:**
- Paper AI, Research Rabbit, Semantic Scholar (research papers)
- ChatGPT (explanation/content)
- Notion, Obsidian (organization)

**Other Useful Tools:**
- Analytics: YouTube Studio, TikTok Analytics, Instagram Insights
- Scheduling: Buffer, Later, Hootsuite
- Hashtag Research: Hashtagify, RiteKit

FORMAT OUTPUT:
For each tool, provide:
1. Tool name
2. Category (Video Editing, Music, etc.)
3. Price tier (Free, Affordable $X/month, Professional $X/month)
4. Why it's good for this project
5. Quick tip or workflow suggestion

REMINDER: ABSOLUTELY NO EMOJIS. Use plain text only. Express everything with words."""

def build_tools_prompt(
    platform: str,
    niche: str,
    goal: str,
    personality: str,
    audience: List[str],
    reference: str = "",
    content_type: str = "general"
) -> List[Dict[str, str]]:
    """Build prompt for tool recommendations"""
    
    platform_needs = {
        "youtube_short": "Fast-paced editing, mobile-friendly tools, trending effects",
        "youtube": "Professional editing, high-quality graphics, detailed thumbnails",
        "tiktok": "Quick editing, mobile apps, trending audio, effects",
        "instagram_reel": "Aesthetic visuals, high-quality images, branded graphics",
        "instagram_carousel": "Graphic design, templates, consistent branding",
        "linkedin": "Professional appearance, clean graphics, data visualization",
        "twitter_thread": "Thread schedulers, image optimization, analytics tools",
        "pinterest": "Pin templates, SEO tools, vertical image design, scheduling",
        "podcast_clip": "Audio editing, waveform visuals, transcription tools, clip extraction"
    }
    
    niche_tools = {
        "food": "Recipe cards, food photography, cooking timers, ingredient lists",
        "tech": "Screen recording, code highlighting, UI mockups, product shots",
        "beauty": "Close-up filming, color correction, before/after templates",
        "travel": "Map graphics, location tags, scenic footage, itinerary templates",
        "fitness": "Workout timers, progress trackers, before/after graphics",
        "education": "Screen recording, diagram tools, research tools, explanation graphics",
        "gaming": "Game capture, overlay graphics, highlight editing",
        "fashion": "Lookbook templates, color palette tools, product photography"
    }
    
    content_needs = {
        "hooks": "Fast video editing, graphics for text overlays",
        "script": "Voiceover tools, transcription, audio editing",
        "shotlist": "Video editing software, camera apps, lighting guides",
        "music": "AI music generation, royalty-free libraries, audio mixing",
        "thumbnails": "Graphic design tools, templates, eye-catching visuals",
        "titles": "Typography tools, text animation, graphic design"
    }
    
    platform_need = platform_needs.get(platform.lower(), "General content creation tools")
    niche_need = niche_tools.get(niche.lower(), f"{niche} content creation tools")
    content_need = content_needs.get(content_type.lower(), "General content creation")
    
    user_prompt = f"""PLATFORM: {platform.upper()}
NICHE: {niche.title()}
GOAL: {goal.replace('_', ' ').title()}
PERSONALITY: {personality.replace('_', ' ').title()}
AUDIENCE: {', '.join([a.replace('_', ' ').title() for a in audience])}
CONTENT TYPE: {content_type.replace('_', ' ').title()}

REFERENCE/IDEA: "{reference}"

PLATFORM NEEDS: {platform_need}
NICHE NEEDS: {niche_need}
CONTENT NEEDS: {content_need}

TASK: Recommend 8-12 tools that would help this creator succeed. Consider:

1. **Video Editing Tools** - Based on platform and skill level
2. **Graphics/Design Tools** - For thumbnails, overlays, graphics
3. **Music/Audio Tools** - AI music generators, royalty-free libraries
4. **Research/Content Tools** - If educational, research tools
5. **Workflow Tools** - Analytics, scheduling, organization

For each tool, provide:
- Tool name
- Category
- Price (Free, or price if paid)
- Why it fits this project
- Quick tip for using it

Prioritize tools that are:
- Accessible for beginners (unless they're clearly pro-level)
- Relevant to the platform and niche
- Actually useful for the specific content type

DO NOT USE EMOJIS OR EMOJI SYMBOLS. Use plain text only.

Format as a clear list with categories."""

    return [
        {"role": "system", "content": TOOLS_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

