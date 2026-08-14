"""Health check endpoint.

Returns API status, RAG pipeline health, active sessions, and uptime.
"""
import time

from fastapi import APIRouter, Request

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from config import API_VERSION
from api.models.schemas import HealthResponse

router = APIRouter(prefix="/api", tags=["Health"])

# Track API start time
_start_time = time.time()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="API Health Check",
    description="Returns the current status of the API, RAG pipeline, and session count.",
)
async def health_check():
    """Check API health and return status information."""
    from services.session_service import get_session_store

    store = get_session_store()

    # Check RAG pipeline status
    rag_status = "healthy"
    try:
        from config import CHROMA_PERSIST_DIR
        if not CHROMA_PERSIST_DIR.exists():
            rag_status = "not_initialized"
    except Exception:
        rag_status = "error"

    return HealthResponse(
        status="healthy",
        version=API_VERSION,
        rag_status=rag_status,
        active_sessions=store.active_count if hasattr(store, "active_count") else 0,
        uptime_seconds=round(time.time() - _start_time, 2),
    )
