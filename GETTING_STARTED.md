# 🚀 Getting Started - CreatorFlow AI

## Yes, there's a UI! Here's how to use it:

### Step 1: Start the Services

You have two options:

#### Option A: Using Docker (Recommended - Easiest)

```bash
# Make sure you're in the project directory
cd /Users/summerann/creatorRAG

# Run the setup script (first time only)
./setup.sh

# Or manually start with Docker Compose
docker-compose up
```

This will start:
- **Ollama** (AI model server) on port 11434
- **Backend API** (FastAPI) on port 8000
- **Frontend UI** (Next.js) on port 3000

#### Option B: Manual Setup (Without Docker)

**Terminal 1 - Start Ollama:**
```bash
# Install Ollama if not installed
# macOS: brew install ollama
# Or download from: https://ollama.com

# Start Ollama
ollama serve

# In another terminal, pull the model
ollama pull llama3.1:8b-instruct
```

**Terminal 2 - Start Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**Terminal 3 - Start Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Step 2: Access the UI

Once everything is running, open your browser:

🌐 **Frontend UI**: http://localhost:3000

You'll see a ChatGPT-like interface with:
- Sidebar on the left (navigation)
- Main chat area in the center
- Platform selector
- Input fields for niche and reference

### Step 3: Test the UI

1. **Select a Platform**: Click on YouTube Shorts, TikTok, Instagram Reels, etc.

2. **Enter Your Niche**: Type something like "travel", "food", "tech", "beauty"

3. **Choose a Goal**: Select from dropdown (grow followers, drive traffic, etc.)

4. **Add Reference** (optional): Describe your content idea

5. **Generate Content**: Click one of the buttons:
   - "Generate Hooks" - Creates viral video hooks
   - "Generate Script" - Creates full video scripts
   - "Generate Shots" - Creates shot lists
   - "Generate Music" - Creates music recommendations

6. **Watch it Generate**: Content will stream in real-time!

### New Features Available in Sidebar

- **Viral Video Analyzer**: Analyze any viral video from YouTube, TikTok, or Instagram. Get hook analysis, story structure, key moments, and remix suggestions
- **Content Sorter**: Sort your Instagram or TikTok content by performance metrics (views, likes, engagement rate, etc.) and export to CSV/JSON/Excel
- **Transcription**: Transcribe audio/video files or URLs. Generate SRT/VTT caption files automatically

7. **Copy or Download**: Use the buttons to copy or download generated content

### Step 4: Check API Health

Visit the API docs to see all available endpoints:
📚 **API Documentation**: http://localhost:8000/docs

### Troubleshooting

**Frontend not loading?**
- Check if port 3000 is available: `lsof -i :3000`
- Check frontend logs: `docker-compose logs frontend`

**Backend errors?**
- Check if Ollama is running: `curl http://localhost:11434/api/tags`
- Check backend logs: `docker-compose logs backend`

**Model not found?**
```bash
docker exec creatorflow-ollama ollama pull llama3.1:8b-instruct
```

**Port conflicts?**
Edit `docker-compose.yml` to change ports if needed.

### Quick Test

Once running, try this in the UI:
1. Platform: **TikTok**
2. Niche: **travel**
3. Goal: **grow followers**
4. Reference: **"budget travel tips for Europe"**
5. Click **"Generate Hooks"**

You should see 15 viral hooks streaming in!

---

## What the UI Looks Like

```
┌─────────────────────────────────────────────────────┐
│  [CreatorFlow AI]          [Profile] [Settings]    │
├──────────────┬──────────────────────────────────────┤
│              │                                      │
│  Sidebar     │         Main Chat Area              │
│              │                                      │
│  New Project │  ┌────────────────────────────┐    │
│  History     │  │ Select Platform:            │    │
│  Templates   │  │ [YT Shorts] [TikTok] [IG]   │    │
│  My RAG Data │  │                              │    │
│              │  │ Niche: [travel_______]      │    │
│              │  │                              │    │
│              │  │ [Generate Hooks] [Script]   │    │
│              │  └────────────────────────────┘    │
│              │                                      │
│              │  ┌─────────────────────────┐       │
│              │  │  Generated Content      │       │
│              │  │  [Copy] [Download]      │       │
│              │  └─────────────────────────┘       │
└──────────────┴──────────────────────────────────────┘
```

---

## Next Steps

- **Index Your Content**: Upload your best-performing content to improve results
- **Experiment**: Try different platforms and niches
- **Customize Prompts**: Edit `backend/prompts/` to match your style

Happy creating! 🎬✨

