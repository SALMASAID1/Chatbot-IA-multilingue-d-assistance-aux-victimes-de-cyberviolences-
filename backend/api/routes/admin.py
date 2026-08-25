"""Admin endpoints for session management.

Endpoints:
- GET    /api/admin/sessions              — List active sessions
- DELETE /api/admin/sessions/{session_id} — Force-expire a session
"""
import logging
from collections import Counter

from fastapi import APIRouter, Depends, HTTPException, Request

from api.middleware.rate_limit import limiter
from api.security import require_admin_key

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from config import RATE_LIMIT_ADMIN
from api.models.schemas import (
    ActiveSessionsResponse,
    SessionSummary,
    ErrorResponse,
)

logger = logging.getLogger(__name__)

# Every route in this router requires a valid X-Admin-Key header. When
# ADMIN_API_KEY is not configured the dependency answers 404, so an
# unconfigured deployment exposes no admin surface at all.
router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"],
    dependencies=[Depends(require_admin_key)],
    responses={
        401: {"description": "Missing or invalid admin key"},
        404: {"description": "Admin API disabled (ADMIN_API_KEY not configured)"},
    },
)


@router.get(
    "/sessions",
    response_model=ActiveSessionsResponse,
    summary="List active sessions",
    description="List all active (non-expired) sessions with language distribution.",
)
@limiter.limit(RATE_LIMIT_ADMIN)
async def list_sessions(request: Request):
    """List all active sessions with summary statistics."""
    from services.session_service import get_session_store

    store = get_session_store()
    sessions = store.get_all_sessions()

    summaries = [
        SessionSummary(**s.to_summary())
        for s in sessions
    ]

    # Count sessions by language
    lang_counter = Counter(s.langue or "unknown" for s in sessions)

    return ActiveSessionsResponse(
        total_sessions=len(summaries),
        sessions=summaries,
        by_language=dict(lang_counter),
    )


@router.delete(
    "/sessions/{session_id}",
    responses={
        404: {"model": ErrorResponse, "description": "Session not found"},
    },
    summary="Delete a session",
    description="Force-expire and delete a specific session.",
)
@limiter.limit(RATE_LIMIT_ADMIN)
async def delete_session(request: Request, session_id: str):
    """Force-expire a specific session."""
    from services.session_service import get_session_store

    store = get_session_store()
    deleted = store.delete_session(session_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Session '{session_id}' introuvable.",
        )

    logger.info(f"Admin: session {session_id} force-deleted")
    return {"status": "deleted", "session_id": session_id}
