"""EMC Helpline API — FastAPI Application.

Main entry point for the multilingual chatbot API.
Assists victims of cyberviolence in French, Arabic, and Darija.

Usage:
    uvicorn backend.main:app --reload
    # or
    python -m backend.main
"""
import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

# Ensure backend is on the Python path
sys.path.insert(0, str(Path(__file__).parent))

from config import API_HOST, API_PORT, API_VERSION
from api.middleware.cors import setup_cors
from api.middleware.rate_limit import setup_rate_limiting
from api.routes import chat, health, admin
from services.session_service import get_session_store, session_cleanup_task

# ============================================================
# Logging
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("emchelpline")


# ============================================================
# Application lifespan (startup / shutdown)
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown events."""
    # --- Startup ---
    logger.info("=" * 50)
    logger.info(f"EMC Helpline API v{API_VERSION} starting...")
    logger.info("=" * 50)

    # Initialize session store
    store = get_session_store()
    logger.info(f"Session store initialized: {store.__class__.__name__}")

    # Start session cleanup background task
    cleanup_task = asyncio.create_task(session_cleanup_task(store))
    logger.info("Session cleanup task started (every 5 minutes)")

    logger.info(f"API ready at http://{API_HOST}:{API_PORT}")
    logger.info(f"Swagger docs at http://{API_HOST}:{API_PORT}/docs")

    yield

    # --- Shutdown ---
    logger.info("Shutting down EMC Helpline API...")
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass
    logger.info("Shutdown complete.")


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="EMC Helpline API",
    description=(
        "API d'assistance aux victimes de cyberviolences — "
        "Espace Maroc Cyberconfiance (EMC) / CMRPI.\n\n"
        "Chatbot IA multilingue supportant le français, l'arabe standard "
        "et le darija marocain.\n\n"
        "**Numéros d'urgence:**\n"
        "- Police : 19\n"
        "- Gendarmerie Royale : 177\n"
        "- ONDE (enfants) : 2511\n"
        "- EMC-Helpline : cyberconfiance.ma"
    ),
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ============================================================
# Middleware
# ============================================================
setup_cors(app)
setup_rate_limiting(app)

# ============================================================
# Routes
# ============================================================
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(admin.router)


# ============================================================
# Root redirect to docs
# ============================================================

@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to API documentation."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")


# ============================================================
# CLI entry point
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
        log_level="info",
    )
