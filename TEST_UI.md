# 🧪 Testing the UI - Step by Step

## Prerequisites Check

Before starting, make sure you have:

- ✅ Python 3.11+ installed
- ✅ Node.js 18+ installed  
- ✅ Ollama installed and running

Check them:
```bash
python3 --version
node --version
ollama --version
```

---

## 🚀 Start Everything (3 Terminals)

### Terminal 1: Ollama
```bash
ollama serve
```
Keep this running. You should see: `Listening on 0.0.0.0:11434`

### Terminal 2: Backend
```bash
cd /Users/summerann/creatorRAG
./start-backend.sh
```
Or manually:
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

### Terminal 3: Frontend
```bash
cd /Users/summerann/creatorRAG
./start-frontend.sh
```
Or manually:
```bash
cd frontend
npm install  # First time only
npm run dev
```

---

## 🌐 Open the UI

**Open your browser to: http://localhost:3000**

You should see:
- Dark sidebar on the left
- Main chat area in the center
- Platform selection buttons
- Input fields

---

## ✅ Test Checklist

### Test 1: UI Loads
- [ ] Page loads without errors
- [ ] Sidebar is visible
- [ ] Platform buttons are clickable
- [ ] No console errors (press F12 to check)

### Test 2: Platform Selection
- [ ] Click "TikTok" - it highlights
- [ ] Click "YouTube Shorts" - it highlights
- [ ] Can select different platforms

### Test 3: Generate Hooks
1. Select "TikTok" platform
2. Enter niche: "travel"
3. Select goal: "Grow Followers"
4. Add reference: "budget travel tips"
5. Click "Generate Hooks"
6. [ ] Content starts streaming in
7. [ ] Can see hooks appearing in real-time
8. [ ] Copy button works
9. [ ] Download button works

### Test 4: Generate Script
1. Keep the same settings
2. Click "Generate Script"
3. [ ] Script starts generating
4. [ ] Script includes timestamps
5. [ ] Script includes visual cues

### Test 5: Generate Shot List
1. Click "Generate Shots"
2. [ ] Shot list appears
3. [ ] Each shot has details

### Test 6: Generate Music
1. Click "Generate Music"
2. [ ] Music recommendations appear
3. [ ] Includes AI prompts and search queries

---

## 🐛 Common Issues

### "Cannot connect to backend"
- Check Terminal 2 (backend) is running
- Check: http://localhost:8000/docs works
- Check browser console for CORS errors

### "Ollama connection failed"
- Check Terminal 1 (Ollama) is running
- Test: `curl http://localhost:11434/api/tags`
- Make sure model is pulled: `ollama pull llama3.1:8b-instruct`

### "Frontend won't start"
- Check Node.js is installed: `node --version`
- Delete `node_modules` and run `npm install` again
- Check port 3000 is free: `lsof -i :3000`

### "No content generating"
- Check backend logs in Terminal 2
- Check Ollama is running
- Check model is downloaded
- Try a simpler request first

---

## 📸 What Success Looks Like

When everything works, you'll see:

1. **Platform selected** → Button highlighted
2. **Click "Generate Hooks"** → Button shows "Generating..."
3. **Content streams in** → Text appears word by word
4. **Content card appears** → With copy/download buttons
5. **Can copy/download** → Buttons work

---

## 🎯 Quick Test Script

Run this to test the API directly:

```bash
curl -X POST http://localhost:8000/api/generate/hooks \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test",
    "platform": "tiktok",
    "niche": "travel",
    "goal": "grow_followers",
    "reference_text": "budget travel tips",
    "content_type": "hooks"
  }'
```

If this works, the backend is fine. If UI doesn't work, it's a frontend issue.

---

## 💡 Pro Tips

1. **Start simple**: Test with "travel" niche first
2. **Check logs**: Always check terminal output for errors
3. **Browser console**: Press F12 to see frontend errors
4. **API docs**: Visit http://localhost:8000/docs to test API directly

---

Happy testing! 🎬

