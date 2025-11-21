# 📁 CreatorFlow AI - Project Structure

## Complete File Tree

```
creatorflow/
├── backend/                          # FastAPI Backend
│   ├── main.py                      # FastAPI app entry point
│   ├── config.py                    # Configuration settings
│   ├── requirements.txt             # Python dependencies
│   ├── Dockerfile                   # Backend Docker image
│   ├── core/                        # Core RAG engine
│   │   ├── __init__.py
│   │   ├── llm_backend.py          # LLM interface (Ollama)
│   │   ├── embeddings.py           # Text/image embeddings
│   │   ├── vector_store.py         # FAISS + SQLite vector store
│   │   └── rag_engine.py           # RAG orchestration
│   ├── prompts/                     # Prompt templates
│   │   ├── __init__.py
│   │   ├── hooks.py                # Hook generation prompts
│   │   ├── scripts.py              # Script generation prompts
│   │   ├── shots.py                # Shot list prompts
│   │   └── music.py                # Music recommendation prompts
│   ├── routers/                     # API endpoints
│   │   ├── __init__.py
│   │   ├── generate.py             # Content generation endpoints
│   │   └── upload.py               # Content indexing endpoints
│   ├── models/                      # Data models (future)
│   │   └── __init__.py
│   └── scripts/                     # Utility scripts
│       ├── __init__.py
│       └── download_models.py      # Model downloader
│
├── frontend/                        # Next.js Frontend
│   ├── package.json                # Node dependencies
│   ├── next.config.js              # Next.js config
│   ├── tsconfig.json               # TypeScript config
│   ├── tailwind.config.ts          # Tailwind CSS config
│   ├── postcss.config.js           # PostCSS config
│   ├── Dockerfile                  # Frontend Docker image
│   ├── app/                        # Next.js app directory
│   │   ├── layout.tsx              # Root layout
│   │   ├── page.tsx               # Main page
│   │   └── globals.css             # Global styles
│   ├── components/                 # React components
│   │   ├── __init__.ts
│   │   ├── Chat.tsx               # Main chat interface
│   │   ├── ChatMessage.tsx         # Message component
│   │   ├── PlatformSelector.tsx    # Platform selection
│   │   ├── ReferenceInput.tsx      # Reference input
│   │   ├── GeneratedContent.tsx    # Generated content display
│   │   └── Sidebar.tsx             # Sidebar navigation
│   └── lib/                        # Utilities
│       └── api.ts                 # API client functions
│
├── data/                           # User data (gitignored)
│   ├── uploads/                    # User uploads
│   └── projects/                   # Generated projects
│
├── docker-compose.yml              # Docker orchestration
├── setup.sh                        # One-command setup script
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
├── README.md                       # Main documentation
├── QUICKSTART.md                   # Quick start guide
└── PROJECT_STRUCTURE.md            # This file
```

## Key Components

### Backend (FastAPI)

- **main.py**: Application entry, lifespan management, CORS setup
- **core/**: RAG engine, LLM backend, embeddings, vector store
- **prompts/**: Platform-specific prompt engineering
- **routers/**: REST API endpoints for generation and upload

### Frontend (Next.js)

- **app/**: Next.js 14 app router structure
- **components/**: React components for chat UI
- **lib/**: API client utilities

### Infrastructure

- **docker-compose.yml**: Orchestrates Ollama, backend, frontend
- **setup.sh**: Automated setup script
- **data/**: Persistent storage (gitignored)

## API Endpoints

### Generation
- `POST /api/generate/hooks` - Generate viral hooks
- `POST /api/generate/script` - Generate video scripts
- `POST /api/generate/shotlist` - Generate shot lists
- `POST /api/generate/music` - Generate music recommendations

### Upload
- `POST /api/upload/index` - Index user content for RAG
- `GET /api/upload/stats/{user_id}` - Get user stats

### Health
- `GET /` - Basic health check
- `GET /health` - Detailed health check

## Technology Stack

### Backend
- FastAPI 0.104+
- Python 3.11
- Ollama (local LLM)
- Sentence Transformers (embeddings)
- FAISS (vector search)
- SQLite (metadata)

### Frontend
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Lucide Icons

### Infrastructure
- Docker & Docker Compose
- Ollama container
- Multi-stage builds

## Getting Started

1. Run `./setup.sh` to initialize everything
2. Access frontend at http://localhost:3000
3. Start generating content!

See [QUICKSTART.md](QUICKSTART.md) for detailed instructions.

