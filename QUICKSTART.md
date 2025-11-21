# 🚀 Quick Start Guide

## Prerequisites

Before you begin, make sure you have:

- **Docker** installed ([Get Docker](https://docs.docker.com/get-docker/))
- **Docker Compose** installed (usually comes with Docker Desktop)
- **8GB+ RAM** available
- **20GB+ free disk space** (for models)

## Installation Steps

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/creatorflow
cd creatorflow

# Make setup script executable
chmod +x setup.sh

# Run setup (this will take 5-10 minutes)
./setup.sh
```

The setup script will:
- ✅ Create necessary directories
- ✅ Build Docker containers
- ✅ Download the AI model (llama3.1:8b-instruct, ~4.7GB)
- ✅ Start all services

### 2. Access the Application

Once setup completes, open your browser:

- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs
- **Ollama**: http://localhost:11434

### 3. First Use

1. **Select Platform**: Choose YouTube Shorts, TikTok, Instagram Reels, etc.
2. **Enter Niche**: Type your niche (e.g., "travel", "food", "tech")
3. **Set Goal**: Choose your content goal
4. **Add Reference** (optional): Describe your content idea
5. **Generate**: Click "Generate Hooks" to start!

## Troubleshooting

### Model Not Downloading

If the model doesn't download automatically:

```bash
docker exec creatorflow-ollama ollama pull llama3.1:8b-instruct
```

### Services Not Starting

Check logs:

```bash
docker-compose logs -f
```

### Port Already in Use

If ports 3000, 8000, or 11434 are already in use, edit `docker-compose.yml` to change them.

### Out of Memory

If you get memory errors:
- Close other applications
- Use a smaller model: `ollama pull llama3.1:8b-instruct` (already default)
- Or use `mistral:7b-instruct` which is smaller

## Next Steps

- **Index Your Content**: Upload your best-performing content to improve RAG results
- **Experiment**: Try different platforms and niches
- **Customize**: Edit prompts in `backend/prompts/` to match your style

## Stopping the Application

```bash
docker-compose down
```

To remove all data:

```bash
docker-compose down -v
```

## Getting Help

- Check the [README.md](README.md) for detailed documentation
- Open an issue on GitHub
- Check logs: `docker-compose logs -f`

---

Happy creating! 🎬✨

