from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import logging

from routers import generate, upload, agents, chat, trends, templates, swipefile, calendar, ab_testing, viral_score, thumbnail_ab, engagement_predictor, multi_platform, competitor_analysis
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
        
        # Test LLM connection
        try:
            test_response = llm_backend.generate([
                {"role": "user", "content": "Say 'ready' if you're working"}
            ])
            logger.info(f"✅ LLM test: {test_response[:50]}")
        except Exception as e:
            logger.warning(f"⚠️ LLM test failed (may need to start Ollama): {e}")
        
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
    """Detailed health check"""
    health = {
        "status": "ok",
        "components": {
            "embeddings": "ok" if embedding_engine else "not_loaded",
            "vector_store": "ok" if vector_store else "not_loaded",
            "llm": "checking"
        }
    }
    
    # Test LLM
    try:
        if llm_backend:
            llm_backend.generate([{"role": "user", "content": "test"}])
            health["components"]["llm"] = "ok"
    except Exception as e:
        health["components"]["llm"] = f"error: {str(e)}"
        health["status"] = "degraded"
    
    return health

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

