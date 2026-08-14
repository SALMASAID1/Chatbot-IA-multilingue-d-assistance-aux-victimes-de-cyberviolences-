"""Pydantic schemas for the EMC Helpline API.

Defines all request/response models with validation rules.
Includes trilingual examples (FR, AR, Darija) for Swagger documentation.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


# ============================================================
# Enums
# ============================================================

class SupportedLanguage(str, Enum):
    """Languages supported by the chatbot."""
    FR = "fr"
    AR = "ar"


# ============================================================
# Chat schemas
# ============================================================

class ChatRequest(BaseModel):
    """Incoming chat message from the user."""
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User message (FR, AR, or Darija)",
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Session ID (UUID). Omit to auto-create a new session.",
    )
    langue: Optional[SupportedLanguage] = Field(
        default=None,
        description="Language override. If omitted, language is auto-detected.",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "Je suis victime de cyberharcèlement, que dois-je faire ?",
                    "session_id": None,
                    "langue": None,
                },
                {
                    "message": "أنا ضحية ابتزاز جنسي، ماذا أفعل؟",
                    "session_id": None,
                    "langue": "ar",
                },
                {
                    "message": "واش نقدر نقدم شكاية؟",
                    "session_id": None,
                    "langue": None,
                },
            ]
        }
    }

    @field_validator("message")
    @classmethod
    def message_not_blank(cls, v: str) -> str:
        """Reject messages that are whitespace-only."""
        if not v.strip():
            raise ValueError("Message cannot be empty or whitespace-only.")
        return v.strip()


class SourceInfo(BaseModel):
    """A source document used in the RAG response."""
    path: Optional[str] = Field(default=None, description="Relative path to source document")
    categorie: Optional[str] = Field(default=None, description="Document category")
    score: Optional[float] = Field(default=None, description="Relevance score (0-1)")


class ChatResponse(BaseModel):
    """Response from the chatbot."""
    answer: str = Field(..., description="Chatbot response text")
    sources: List[SourceInfo] = Field(
        default_factory=list,
        description="Source documents used for the response",
    )
    langue: str = Field(..., description="Language of the response (fr/ar)")
    is_darija: bool = Field(default=False, description="Whether input was detected as Darija")
    is_urgent: bool = Field(default=False, description="Whether urgency was detected")
    user_profile: str = Field(
        default="victim",
        description="Detected user profile (victim, parent, enseignant, temoin, jeune, detresse_emotionnelle)",
    )
    session_id: str = Field(..., description="Session ID for this conversation")
    message_id: str = Field(..., description="Unique ID for this message exchange")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp (UTC)",
    )


# ============================================================
# Session schemas
# ============================================================

class SessionCreateRequest(BaseModel):
    """Request to create a new conversation session."""
    langue: Optional[SupportedLanguage] = Field(
        default=None,
        description="Preferred language for the session",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"langue": "fr"},
                {"langue": "ar"},
                {"langue": None},
            ]
        }
    }


class SessionResponse(BaseModel):
    """Response when a session is created."""
    session_id: str = Field(..., description="Unique session ID (UUID)")
    created_at: datetime = Field(..., description="Session creation time (UTC)")
    langue: Optional[str] = Field(default=None, description="Session language preference")


# ============================================================
# Chat history schemas
# ============================================================

class ChatMessage(BaseModel):
    """A single message in the conversation history."""
    role: str = Field(..., description="Message sender: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="Message timestamp (UTC)")
    message_id: Optional[str] = Field(default=None, description="Unique message ID")


class ChatHistory(BaseModel):
    """Conversation history for a session."""
    session_id: str = Field(..., description="Session ID")
    messages: List[ChatMessage] = Field(default_factory=list, description="List of messages")
    total_messages: int = Field(default=0, description="Total number of messages")


# ============================================================
# Feedback schemas
# ============================================================

class FeedbackRequest(BaseModel):
    """User feedback on a chatbot response."""
    session_id: str = Field(..., description="Session ID")
    message_id: str = Field(..., description="ID of the message being rated")
    rating: int = Field(
        ...,
        ge=1,
        le=5,
        description="Rating from 1 (bad) to 5 (excellent)",
    )
    comment: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional feedback comment",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "550e8400-e29b-41d4-a716-446655440000",
                    "message_id": "msg-123",
                    "rating": 5,
                    "comment": "Très utile, merci !",
                },
            ]
        }
    }


class FeedbackResponse(BaseModel):
    """Response after submitting feedback."""
    status: str = Field(default="received", description="Feedback status")
    message: str = Field(default="Merci pour votre retour.", description="Confirmation message")


# ============================================================
# Health schemas
# ============================================================

class HealthResponse(BaseModel):
    """API health check response."""
    status: str = Field(..., description="API status: 'healthy' or 'degraded'")
    version: str = Field(..., description="API version")
    rag_status: str = Field(..., description="RAG pipeline status")
    active_sessions: int = Field(default=0, description="Number of active sessions")
    uptime_seconds: float = Field(default=0.0, description="API uptime in seconds")


# ============================================================
# Admin schemas
# ============================================================

class SessionSummary(BaseModel):
    """Summary of an active session (for admin)."""
    session_id: str
    created_at: datetime
    last_activity: datetime
    langue: Optional[str] = None
    message_count: int = 0


class ActiveSessionsResponse(BaseModel):
    """List of active sessions (admin endpoint)."""
    total_sessions: int = Field(default=0, description="Total active sessions")
    sessions: List[SessionSummary] = Field(default_factory=list)
    by_language: dict = Field(default_factory=dict, description="Session count by language")


class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str = Field(..., description="Error description")
    error_code: Optional[str] = Field(default=None, description="Machine-readable error code")
