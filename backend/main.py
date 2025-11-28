from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import logging

from routers import generate, upload, agents, chat, trends, templates, swipefile, calendar, ab_testing, viral_score, thumbnail_ab, engagement_predictor, multi_platform, competitor_analysis, humanize, precheck, insights, profile, viral_analyzer, content_sorter, transcription, viral_title_generator, trend_detector, ideas_feed, workflows, autopilot
from core.embeddings import EmbeddingEngine
from core.vector_store import VectorStore
from core.llm_backend import get_llm_backend
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
embedding_engine = None
vector_store = None
llm_backend = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup, cleanup on shutdown"""
    global embedding_engine, vector_store, llm_backend
    
    logger.info("🚀 Starting CreatorFlow AI Backend...")
    
    try:
        # Initialize core components
        logger.info("📥 Loading embedding models...")
        embedding_engine = EmbeddingEngine()
        
        logger.info("💾 Initializing vector store...")
        vector_store = VectorStore()
        
        logger.info("🤖 Connecting to LLM backend...")
        llm_backend = get_llm_backend(
            backend_type=settings.LLM_BACKEND,
            model=settings.DEFAULT_MODEL,
            base_url=settings.OLLAMA_URL
        )
        
        # Test LLM connection (non-blocking, don't fail startup if it hangs)
        try:
            # Quick check: verify Ollama is responding
            import requests
            try:
                health_check = requests.get(f"{settings.OLLAMA_URL}/api/tags", timeout=2)
                if health_check.status_code == 200:
                    logger.info(f"✅ Ollama is responding at {settings.OLLAMA_URL}")
                else:
                    logger.warning(f"⚠️ Ollama responded with status {health_check.status_code}")
            except requests.exceptions.RequestException as e:
                logger.warning(f"⚠️ Cannot reach Ollama at {settings.OLLAMA_URL}: {e}")
                logger.warning("⚠️ Backend will start, but generation will fail until Ollama is running")
        except Exception as e:
            logger.warning(f"⚠️ LLM health check failed: {e}")
        
        # Inject globals into routers after initialization
        generate.set_globals(embedding_engine, vector_store, llm_backend)
        upload.set_globals(embedding_engine, vector_store, llm_backend)
        agents.set_globals(embedding_engine, vector_store, llm_backend)
        chat.set_globals(embedding_engine, vector_store, llm_backend)
        calendar.set_globals(embedding_engine, vector_store, llm_backend)
        ab_testing.set_globals(embedding_engine, vector_store, llm_backend)
        viral_score.set_globals(embedding_engine, vector_store, llm_backend)
        thumbnail_ab.set_globals(embedding_engine, vector_store, llm_backend)
        engagement_predictor.set_globals(embedding_engine, vector_store, llm_backend)
        multi_platform.set_globals(embedding_engine, vector_store, llm_backend)
        competitor_analysis.set_globals(embedding_engine, vector_store, llm_backend)
        humanize.set_globals(embedding_engine, vector_store, llm_backend)
        precheck.set_globals(embedding_engine, vector_store, llm_backend)
        insights.set_globals(embedding_engine, vector_store, llm_backend)
        profile.set_llm_backend(llm_backend)
        viral_analyzer.set_globals(embedding_engine, vector_store, llm_backend)
        content_sorter.set_globals(embedding_engine, vector_store, llm_backend)
        transcription.set_globals(embedding_engine, vector_store, llm_backend)
        viral_title_generator.set_globals(embedding_engine, vector_store, llm_backend)
        trend_detector.set_globals(embedding_engine, vector_store, llm_backend)
        ideas_feed.set_globals(embedding_engine, vector_store, llm_backend)
        workflows.set_globals(embedding_engine, vector_store, llm_backend)
        autopilot.set_globals(embedding_engine, vector_store, llm_backend)
        
        # Start autopilot background task
        import asyncio
        asyncio.create_task(autopilot.autopilot_daily_task())
        
        logger.info("✅ All systems ready!")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down...")
    if vector_store:
        vector_store.save_index()

# Create FastAPI app
app = FastAPI(
    title="CreatorFlow AI API",
    description="AI-powered content generation for creators",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(generate.router)
app.include_router(upload.router)
app.include_router(agents.router)
app.include_router(chat.router)
app.include_router(trends.router)
app.include_router(templates.router)
app.include_router(swipefile.router)
app.include_router(calendar.router)
app.include_router(ab_testing.router)
app.include_router(viral_score.router)
app.include_router(thumbnail_ab.router)
app.include_router(engagement_predictor.router)
app.include_router(multi_platform.router)
app.include_router(competitor_analysis.router)
app.include_router(humanize.router)
app.include_router(precheck.router)
app.include_router(insights.router)
app.include_router(profile.router)
app.include_router(viral_analyzer.router)
app.include_router(content_sorter.router)
app.include_router(transcription.router)
app.include_router(viral_title_generator.router)
app.include_router(trend_detector.router)
app.include_router(ideas_feed.router)
app.include_router(workflows.router)
app.include_router(autopilot.router)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "CreatorFlow AI Backend",
        "version": "1.0.0",
        "llm_backend": settings.LLM_BACKEND,
        "model": settings.DEFAULT_MODEL
    }

@app.get("/health")
async def health_check():
    """Detailed health check - non-blocking"""
    import requests

    health = {
        "status": "ok",
        "components": {
            "embeddings": "ok" if embedding_engine else "not_loaded",
            "vector_store": "ok" if vector_store else "not_loaded",
            "llm": "checking"
        }
    }

    # Quick LLM check - just verify Ollama is responding, don't actually generate
    try:
        if llm_backend:
            # Fast check: just ping Ollama API (< 1 second)
            resp = requests.get(f"{settings.OLLAMA_URL}/api/tags", timeout=2)
            if resp.status_code == 200:
                health["components"]["llm"] = "ok"
            else:
                health["components"]["llm"] = f"ollama returned {resp.status_code}"
                health["status"] = "degraded"
        else:
            health["components"]["llm"] = "not_initialized"
    except requests.exceptions.Timeout:
        health["components"]["llm"] = "timeout"
        health["status"] = "degraded"
    except Exception as e:
        health["components"]["llm"] = f"error: {str(e)}"
        health["status"] = "degraded"

    return health

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

