"""Chat endpoints — core conversation functionality.

Endpoints:
- POST /api/chat           — Send a message, receive RAG-augmented response
- POST /api/chat/session   — Create a new conversation session
- GET  /api/chat/history   — Retrieve conversation history
- POST /api/chat/feedback  — Submit feedback on a response
"""
import logging

from fastapi import APIRouter, HTTPException, Request

from api.middleware.rate_limit import limiter

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from config import RATE_LIMIT_CHAT
from api.models.schemas import (
    ChatRequest,
    ChatResponse,
    SessionCreateRequest,
    SessionResponse,
    ChatHistory,
    ChatMessage,
    FeedbackRequest,
    FeedbackResponse,
    SourceInfo,
    ErrorResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post(
    "",
    response_model=ChatResponse,
    responses={
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Send a chat message",
    description=(
        "Send a message to the chatbot and receive a RAG-augmented response. "
        "Language is auto-detected (FR/AR/Darija) unless overridden. "
        "A new session is created automatically if no session_id is provided."
    ),
)
@limiter.limit(RATE_LIMIT_CHAT)
async def send_message(request: Request, body: ChatRequest):
    """Process a user message through the full RAG pipeline."""
    from services.chat_service import get_chat_service

    try:
        chat_service = get_chat_service()
        result = chat_service.process_message(
            message=body.message,
            session_id=body.session_id,
            langue_override=body.langue.value if body.langue else None,
        )

        return ChatResponse(
            answer=result["answer"],
            sources=[SourceInfo(**s) for s in result.get("sources", [])],
            langue=result["langue"],
            is_darija=result.get("is_darija", False),
            is_urgent=result.get("is_urgent", False),
            user_profile=result.get("user_profile", "victim"),
            session_id=result["session_id"],
            message_id=result["message_id"],
            timestamp=result["timestamp"],
        )

    except Exception as e:
        logger.error(f"Chat processing error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Une erreur interne s'est produite. Veuillez réessayer.",
        )


@router.post(
    "/session",
    response_model=SessionResponse,
    summary="Create a new session",
    description="Create a new conversation session. Optionally specify a preferred language.",
)
async def create_session(body: SessionCreateRequest = SessionCreateRequest()):
    """Create a new conversation session."""
    from services.session_service import get_session_store

    store = get_session_store()
    langue = body.langue.value if body.langue else None
    session = store.create_session(langue=langue)

    return SessionResponse(
        session_id=session.session_id,
        created_at=session.created_at,
        langue=session.langue,
    )


@router.get(
    "/history/{session_id}",
    response_model=ChatHistory,
    responses={
        404: {"model": ErrorResponse, "description": "Session not found"},
    },
    summary="Get conversation history",
    description="Retrieve the full conversation history for a session.",
)
async def get_history(session_id: str):
    """Retrieve conversation history for a session."""
    from services.chat_service import get_chat_service

    chat_service = get_chat_service()
    history = chat_service.get_history(session_id)

    if history is None:
        raise HTTPException(
            status_code=404,
            detail=f"Session '{session_id}' introuvable ou expirée.",
        )

    return ChatHistory(
        session_id=history["session_id"],
        messages=[ChatMessage(**msg) for msg in history["messages"]],
        total_messages=history["total_messages"],
    )


@router.post(
    "/feedback",
    response_model=FeedbackResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Session not found"},
    },
    summary="Submit feedback",
    description="Submit a rating (1-5) and optional comment for a specific chatbot response.",
)
async def submit_feedback(body: FeedbackRequest):
    """Submit user feedback on a chatbot response."""
    from services.chat_service import get_chat_service

    chat_service = get_chat_service()
    success = chat_service.submit_feedback(
        session_id=body.session_id,
        message_id=body.message_id,
        rating=body.rating,
        comment=body.comment,
    )

    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Session '{body.session_id}' introuvable ou expirée.",
        )

    return FeedbackResponse(
        status="received",
        message="Merci pour votre retour. / شكرا على ملاحظاتك.",
    )
