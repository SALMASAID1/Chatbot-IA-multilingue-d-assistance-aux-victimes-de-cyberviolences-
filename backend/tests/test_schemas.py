"""Tests for Pydantic schemas validation.

Covers:
- ChatRequest validation (length, blank, language enum)
- FeedbackRequest validation (rating range)
- HealthResponse structure
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from pydantic import ValidationError
from api.models.schemas import (
    ChatRequest,
    ChatResponse,
    FeedbackRequest,
    HealthResponse,
    SessionCreateRequest,
    SupportedLanguage,
)


class TestChatRequest:
    """Test ChatRequest schema validation."""

    def test_valid_french_message(self):
        req = ChatRequest(message="Je suis victime de cyberharcèlement")
        assert req.message == "Je suis victime de cyberharcèlement"
        assert req.session_id is None
        assert req.langue is None

    def test_valid_arabic_message(self):
        req = ChatRequest(
            message="أنا ضحية ابتزاز جنسي",
            langue=SupportedLanguage.AR,
        )
        assert req.langue == SupportedLanguage.AR

    def test_valid_with_session(self):
        req = ChatRequest(
            message="Aide",
            session_id="550e8400-e29b-41d4-a716-446655440000",
        )
        assert req.session_id == "550e8400-e29b-41d4-a716-446655440000"

    def test_empty_message_rejected(self):
        with pytest.raises(ValidationError):
            ChatRequest(message="")

    def test_whitespace_message_rejected(self):
        with pytest.raises(ValidationError):
            ChatRequest(message="   ")

    def test_message_too_long(self):
        with pytest.raises(ValidationError):
            ChatRequest(message="x" * 2001)

    def test_message_stripped(self):
        req = ChatRequest(message="  Aide  ")
        assert req.message == "Aide"

    def test_invalid_language(self):
        with pytest.raises(ValidationError):
            ChatRequest(message="Hello", langue="en")


class TestFeedbackRequest:
    """Test FeedbackRequest schema validation."""

    def test_valid_feedback(self):
        req = FeedbackRequest(
            session_id="test-123",
            message_id="msg-456",
            rating=5,
            comment="Très utile",
        )
        assert req.rating == 5

    def test_rating_too_low(self):
        with pytest.raises(ValidationError):
            FeedbackRequest(
                session_id="test-123",
                message_id="msg-456",
                rating=0,
            )

    def test_rating_too_high(self):
        with pytest.raises(ValidationError):
            FeedbackRequest(
                session_id="test-123",
                message_id="msg-456",
                rating=6,
            )

    def test_feedback_without_comment(self):
        req = FeedbackRequest(
            session_id="test-123",
            message_id="msg-456",
            rating=3,
        )
        assert req.comment is None


class TestSessionCreateRequest:
    """Test SessionCreateRequest schema validation."""

    def test_no_language(self):
        req = SessionCreateRequest()
        assert req.langue is None

    def test_with_language(self):
        req = SessionCreateRequest(langue=SupportedLanguage.FR)
        assert req.langue == SupportedLanguage.FR


class TestHealthResponse:
    """Test HealthResponse schema."""

    def test_healthy_response(self):
        resp = HealthResponse(
            status="healthy",
            version="1.0.0",
            rag_status="healthy",
            active_sessions=5,
            uptime_seconds=120.5,
        )
        assert resp.status == "healthy"
        assert resp.active_sessions == 5
