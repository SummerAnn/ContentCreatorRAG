# 🎬 START HERE - CreatorFlow AI

## Yes! There IS a UI - Here's How to Get It Running

### Quick Answer: How to Test the UI

**Option 1: With Docker (Easiest)**
```bash
# Install Docker first: https://docs.docker.com/get-docker/
./setup.sh
# Then open: http://localhost:3000
```

**Option 2: Without Docker (Manual)**
```bash
# See instructions below
```

---

## 🚀 Quick Start (Without Docker)

Since Docker isn't installed, here's how to run it manually:

### Step 1: Install Ollama

**macOS:**
```bash
brew install ollama
# OR download from: https://ollama.com/download
```

**Start Ollama:**
```bash
ollama serve
```

**In a NEW terminal, pull the model:**
```bash
ollama pull llama3.1:8b-instruct
```

### Step 2: Start Backend

Open a **new terminal**:

```bash
cd /Users/summerann/creatorRAG/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see: `Uvicorn running on http://0.0.0.0:8000`

### Step 3: Start Frontend

Open **another new terminal**:

```bash
cd /Users/summerann/creatorRAG/frontend

# Install dependencies (first time only)
npm install

# Start the dev server
npm run dev
```

You should see: `Ready on http://localhost:3000`

### Step 4: Open the UI! 🎉

Open your browser and go to:
**http://localhost:3000**

---

## 🎨 What You'll See

A beautiful ChatGPT-like interface with:

1. **Left Sidebar**: Navigation (New Project, History, Settings)
2. **Main Area**: 
   - Platform selector (YouTube, TikTok, Instagram, etc.)
   - Niche input field
   - Goal dropdown
   - Reference input
   - Generate buttons

3. **Chat Interface**: Where generated content appears

---

## 🧪 Quick Test

1. **Select Platform**: Click "TikTok" or "YouTube Shorts"
2. **Enter Niche**: Type "travel" or "food" or "tech"
3. **Choose Goal**: Select "Grow Followers"
4. **Add Reference**: Type "budget travel tips"
5. **Click "Generate Hooks"**

Watch as 15 viral hooks stream in real-time! 🚀

---

## 📊 Check Everything is Working

**Backend API**: http://localhost:8000/docs
- Should show FastAPI documentation
- Try the `/health` endpoint

**Frontend UI**: http://localhost:3000
- Should show the chat interface
- If you see errors, check the browser console (F12)

**Ollama**: Check if it's running
```bash
curl http://localhost:11434/api/tags
```

---

## 🐛 Troubleshooting

**"Cannot connect to Ollama"**
- Make sure `ollama serve` is running
- Check: `curl http://localhost:11434/api/tags`

**"Frontend won't load"**
- Check if port 3000 is free: `lsof -i :3000`
- Kill any process using it if needed

**"Backend errors"**
- Make sure you activated the virtual environment
- Check: `pip list` should show fastapi, uvicorn, etc.

**"Model not found"**
- Run: `ollama pull llama3.1:8b-instruct`
- Wait for download to complete (~4.7GB)

---

## 🎯 What You Can Do

✅ Generate viral hooks for any platform
✅ Create full video scripts
✅ Get shot-by-shot breakdowns
✅ Get music recommendations
✅ All powered by local AI (no API costs!)

---

## 📝 Next Steps

1. **Index Your Content**: Upload your best-performing posts to improve results
2. **Experiment**: Try different platforms and niches
3. **Customize**: Edit prompts in `backend/prompts/` to match your style

---

**Need help?** Check the logs:
- Backend: Look at the terminal where you ran `uvicorn`
- Frontend: Look at the terminal where you ran `npm run dev`
- Browser: Press F12 to see console errors

Happy creating! 🎬✨

