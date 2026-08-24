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

    # Validate the actual persisted collection and cached embedding readiness.
    try:
        from rag.embeddings import get_vector_store_status
        rag_status = get_vector_store_status()
    except Exception:
        rag_status = "error"

    try:
        from llm.gemini_provider import get_llm_runtime_status
        llm_status = get_llm_runtime_status()
    except Exception:
        llm_status = "error"

    overall_status = (
        "healthy"
        if rag_status == "healthy" and llm_status in {"configured", "healthy"}
        else "degraded"
    )

    return HealthResponse(
        status=overall_status,
        version=API_VERSION,
        rag_status=rag_status,
        llm_status=llm_status,
        active_sessions=store.active_count if hasattr(store, "active_count") else 0,
        uptime_seconds=round(time.time() - _start_time, 2),
    )
