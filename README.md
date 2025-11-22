# CreatorFlow AI

**100% Free & Open Source AI Platform for Content Creators**

Generate viral hooks, scripts, shot lists, and music prompts for YouTube Shorts, TikTok, Instagram Reels, and more—powered by local AI models with no API costs.

---

## Features

- **Platform-Specific Generation**: Optimized for YouTube, TikTok, Instagram, LinkedIn, Twitter/X, Pinterest, Podcasts
- **RAG-Powered**: Learns from YOUR best-performing content
- **Complete Content Packages**: Hooks, scripts, shot lists, music prompts, titles, descriptions, tags, thumbnails, beatmaps, CTAs
- **100% Free**: Runs locally with open-source models (no API costs)
- **Privacy-First**: Your content never leaves your machine
- **ChatGPT-like UI**: Intuitive conversational interface with collapsible sidebar
- **Idea Notes**: Brainstorm and save ideas, then develop them with AI
- **Continue Conversations**: Chat with AI to refine, revise, or expand on generated content
- **Random Idea Roaster**: Get instant inspiration with random content ideas
- **Conversation History**: Save and revisit past conversations
- **Luxury UI**: Beautiful black & cream design with Manrope font
- **Tool Recommendations**: Get AI-suggested tools based on your content type
- **Template Library**: 10+ ready-to-use templates for instant content creation (Storytime, Product Review, Educational, etc.)
- **Personal Swipe File**: Save and organize inspiration videos with tags and notes
- **Trend Integration**: Real-time trending topics from Reddit and pattern-based sources
- **Talk or No Talking**: Choose voiceover scripts or silent text-overlay content
- **Content Calendar AI**: Generate strategic monthly/weekly content calendars with themed weeks and optimal posting times
- **A/B Testing Simulator**: Compare content variants and predict which performs better based on your history
- **Viral Score Analyzer**: Real-time viral potential scoring as you type (hook strength, pattern match, emotional impact)
- **Strategic Hashtag Engine**: 30/50/20 mix of viral/community/niche tags optimized for your goals
- **Thumbnail A/B Tester**: Analyze and compare thumbnail variants for click-worthiness
- **Engagement Predictor**: Predict views and engagement before posting based on content quality and historical data
- **Multi-Platform Optimizer**: Adapt one piece of content for multiple platforms automatically
- **Competitor Analysis Tool**: Analyze competitor strategies and find content gaps
- **AI Humanizer**: Rewrite AI content to sound natural and prevent AI detection (CRITICAL for 2025)
- **Content Pre-Check**: Check content against platform guidelines before posting (like TikTok's pre-check)
- **Search Insights Integration**: Show trending searches and content opportunities based on real-time trends
- **User Profile System**: Save your preferences once - platform, niche, personality, audience defaults auto-load

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- 8GB RAM minimum (16GB recommended)
- 20GB free disk space

### Installation

```bash
# Clone the repository
git clone https://github.com/SummerAnn/ContentCreatorRAG.git
cd ContentCreatorRAG

# Run setup script
chmod +x setup.sh
./setup.sh

# Open browser
open http://localhost:3000
```

That's it! The setup script will:
1. Build all containers
2. Download the AI model (~4.7GB)
3. Start all services

---

## Usage

### 1. First Time Setup

- Upload 5-10 of your best-performing content (for RAG learning)
- Set your brand voice preferences

### 2. Generate Content

1. Select platform (YouTube Short, TikTok, Instagram Reel, etc.)
2. Choose niche (travel, food, tech, beauty, etc.)
3. Set personality (friendly, educational, motivational, etc.)
4. Select target audience (Gen Z, Millennials, Professionals, etc.)
5. Set goal (grow followers, drive clicks, educate, UGC, brand deals, etc.)
6. Provide reference (image, link, or description)
7. Generate hooks, scripts, shots, music, titles, descriptions, tags, thumbnails, beatmaps, CTAs, and tool recommendations!

### 3. Workflow Features

- **Idea Notes**: Click "Idea Notes" in the sidebar to brainstorm and save ideas. Click "Develop with AI" to send your idea to the chat.
- **Random Idea Roaster**: Get instant random content ideas with platform, niche, personality, and audience suggestions.
- **Continue Chatting**: After generating content, continue the conversation to refine, revise, or get more ideas.
- **Conversation History**: Access your past conversations from the sidebar.
- **Collapsible Sidebar**: Minimize the sidebar to icons-only for more screen space (like ChatGPT).

### 4. Export & Use

- Copy generated content to clipboard
- Edit generated content inline
- Select hooks to generate scripts from them
- Continue chatting to refine content
- Save conversations for later

---

## Architecture

```
Frontend (Next.js) ← → Backend (FastAPI) ← → Ollama (Local LLM)
                              ↓
                    RAG Engine + Vector Store
                         (FAISS + SQLite)
```

**Tech Stack:**

- Frontend: Next.js 14, TypeScript, Tailwind CSS
- Backend: FastAPI, Python 3.11
- LLM: Ollama (Llama 3.1 8B)
- Embeddings: Sentence Transformers
- Vector Store: FAISS + SQLite

---

## Development

### Manual Setup (without Docker)

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Install and start Ollama separately
ollama pull llama3.1:8b-instruct

# Run backend
uvicorn main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

---

## Troubleshooting

### React Hydration Warning (Development Only)

If you see a console warning like "Warning: Extra attributes from the server: data-has-listeners", **this is expected and harmless**. Here's why:

- **Cause**: Browser extensions (password managers, form fillers, etc.) add attributes like `data-has-listeners` to input fields, which React detects during hydration
- **Impact**: **None** - This is a development-only warning that doesn't affect functionality
- **Solution**: The warning is automatically suppressed in production builds. In development, you can safely ignore it

This is a known interaction between React's hydration system and browser extensions, and we've implemented multiple layers of suppression to minimize it. Your app will work perfectly regardless of this warning.

---

## Project Structure

```
creatorflow/
├── backend/          # FastAPI server
│   ├── core/        # RAG engine, LLM, embeddings
│   ├── prompts/     # Platform-specific prompt templates
│   └── routers/     # API endpoints
├── frontend/         # Next.js app
│   ├── app/         # Pages and layouts
│   └── components/  # React components
└── data/            # User data (gitignored)
```

---

## Supported Platforms

- YouTube Shorts
- YouTube Long-form
- TikTok
- Instagram Reels
- Instagram Carousels
- LinkedIn Posts
- Twitter/X Threads
- Pinterest Pins
- Podcast Clips

## Image Reference Support

Upload reference images and our CLIP-powered vision model will understand the visual context to generate better, more relevant content suggestions.

---

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Roadmap

### Phase 1 (Current)
- [x] Basic RAG implementation
- [x] Hook generator
- [x] Script generator
- [x] Shot list generator
- [x] Music prompt generator
- [x] Titles, descriptions, tags, thumbnails generator
- [x] Beatmap/retention map generator
- [x] CTA generator
- [x] Tool recommendations
- [x] Image reference support (CLIP)
- [x] Link extraction
- [x] Conversation history
- [x] Continue chatting feature
- [x] Idea Notes / Brainstorming
- [x] Random Idea Roaster
- [x] Collapsible sidebar
- [x] Content editing
- [x] Hook selection workflow
- [x] Template Library (10+ templates)
- [x] Personal Swipe File
- [x] Content Calendar AI
- [x] A/B Testing Simulator
- [x] Viral Score Analyzer
- [x] Strategic Hashtag Engine (30/50/20 mix)
- [x] Thumbnail A/B Tester
- [x] Engagement Predictor
- [x] Multi-Platform Optimizer
- [x] Competitor Analysis Tool
- [x] AI Humanizer (rewrite AI content to sound natural)
- [x] Content Pre-Check (check against platform guidelines)
- [x] Search Insights Integration (trending searches and opportunities)
- [x] User Profile System (save preferences, auto-load defaults)

### Phase 2
- [ ] Performance tracking
- [ ] Analytics-aware feedback
- [ ] Script-to-Storyboard (requires image generation)

### Phase 3
- [ ] Multi-user support
- [ ] Cloud deployment option
- [ ] Mobile app
- [ ] Plugin system

---

## Support

- Email: support@creatorflow.ai
- Discord: [Join our community](https://discord.gg/creatorflow)
- Issues: [GitHub Issues](https://github.com/SummerAnn/ContentCreatorRAG/issues)

---

## Acknowledgments

- Ollama for local LLM infrastructure
- Sentence Transformers for embeddings
- The open-source AI community

---

Made for content creators

