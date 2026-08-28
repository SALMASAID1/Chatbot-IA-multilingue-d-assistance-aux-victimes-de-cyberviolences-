"""Integration tests for the chat API routes.

Uses FastAPI TestClient (via httpx) to test the full request/response cycle.
Note: These tests mock the RAG pipeline to avoid requiring ChromaDB/Gemini.
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset global singletons between tests."""
    import services.session_service as ss
    import services.chat_service as cs
    ss._session_store = None
    cs._chat_service = None
    yield
    ss._session_store = None
    cs._chat_service = None


@pytest.fixture
def client():
    """Create a test client with mocked RAG chain."""
    # Mock the RAG chain to avoid loading ChromaDB/embeddings/Gemini
    mock_rag = MagicMock()
    mock_rag.ask.return_value = {
        "answer": "Voici les étapes à suivre pour signaler...",
        "sources": [
            {"path": "fiches_pratiques/sextorsion.md", "categorie": "fiches_pratiques", "score": 0.85}
        ],
        "langue": "fr",
        "context_used": "test context",
        "is_urgent": False,
        "user_profile": "victim",
    }

    with patch("services.session_service.Session.rag_chain", new_callable=lambda: property(lambda self: mock_rag)):
        from main import app
        with TestClient(app) as c:
            yield c


@pytest.fixture
def client_with_urgent_response():
    """Create a test client that simulates an urgent response."""
    mock_rag = MagicMock()
    mock_rag.ask.return_value = {
        "answer": "Si vous êtes en danger immédiat, appelez le 19...",
        "sources": [],
        "langue": "fr",
        "context_used": "",
        "is_urgent": True,
        "user_profile": "detresse_emotionnelle",
    }

    with patch("services.session_service.Session.rag_chain", new_callable=lambda: property(lambda self: mock_rag)):
        from main import app
        with TestClient(app) as c:
            yield c


# ============================================================
# Health endpoint tests
# ============================================================

class TestHealthEndpoint:
    """Test the /api/health endpoint."""

    def test_health_check(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in {"healthy", "degraded"}
        assert "version" in data
        assert "rag_status" in data
        assert "llm_status" in data
        assert "uptime_seconds" in data

    def test_health_has_session_count(self, client):
        response = client.get("/api/health")
        data = response.json()
        assert "active_sessions" in data
        assert isinstance(data["active_sessions"], int)


# ============================================================
# Chat endpoint tests
# ============================================================

class TestChatEndpoint:
    """Test the POST /api/chat endpoint."""

    def test_send_french_message(self, client):
        response = client.post("/api/chat", json={
            "message": "Je suis victime de cyberharcèlement"
        })
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "session_id" in data
        assert "message_id" in data
        assert data["langue"] in ("fr", "ar")

    def test_send_arabic_message(self, client):
        response = client.post("/api/chat", json={
            "message": "أنا ضحية ابتزاز جنسي، ماذا أفعل؟",
            "langue": "ar",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] is not None

    def test_send_with_existing_session(self, client):
        # Create a session first
        r1 = client.post("/api/chat", json={
            "message": "Bonjour, j'ai besoin d'aide"
        })
        session_id = r1.json()["session_id"]

        # Send a follow-up
        r2 = client.post("/api/chat", json={
            "message": "Quels sont mes droits ?",
            "session_id": session_id,
        })
        assert r2.status_code == 200
        assert r2.json()["session_id"] == session_id

    def test_empty_message_rejected(self, client):
        response = client.post("/api/chat", json={
            "message": ""
        })
        assert response.status_code == 422  # Validation error

    def test_whitespace_message_rejected(self, client):
        response = client.post("/api/chat", json={
            "message": "   "
        })
        assert response.status_code == 422

    def test_response_has_sources(self, client):
        response = client.post("/api/chat", json={
            "message": "Que faire en cas de sextorsion ?"
        })
        data = response.json()
        assert "sources" in data
        assert isinstance(data["sources"], list)

    def test_urgent_detection(self, client_with_urgent_response):
        response = client_with_urgent_response.post("/api/chat", json={
            "message": "Je suis en danger, il est chez moi"
        })
        data = response.json()
        assert data["is_urgent"] is True


# ============================================================
# Session endpoint tests
# ============================================================

class TestSessionEndpoint:
    """Test the POST /api/chat/session endpoint."""

    def test_create_session(self, client):
        response = client.post("/api/chat/session", json={})
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "created_at" in data

    def test_create_session_with_language(self, client):
        response = client.post("/api/chat/session", json={
            "langue": "ar"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["langue"] == "ar"


# ============================================================
# History endpoint tests
# ============================================================

class TestHistoryEndpoint:
    """Test the GET /api/chat/history/{session_id} endpoint."""

    def test_get_history(self, client):
        # Send a message to create history
        r1 = client.post("/api/chat", json={
            "message": "Bonjour"
        })
        session_id = r1.json()["session_id"]

        # Get history
        r2 = client.get(f"/api/chat/history/{session_id}")
        assert r2.status_code == 200
        data = r2.json()
        assert data["session_id"] == session_id
        assert data["total_messages"] >= 2  # user + assistant

    def test_history_not_found(self, client):
        response = client.get("/api/chat/history/nonexistent-session")
        assert response.status_code == 404


# ============================================================
# Feedback endpoint tests
# ============================================================

class TestFeedbackEndpoint:
    """Test the POST /api/chat/feedback endpoint."""

    def test_submit_feedback(self, client):
        # Create a session with a message
        r1 = client.post("/api/chat", json={
            "message": "Aide"
        })
        session_id = r1.json()["session_id"]
        message_id = r1.json()["message_id"]

        # Submit feedback
        r2 = client.post("/api/chat/feedback", json={
            "session_id": session_id,
            "message_id": message_id,
            "rating": 5,
            "comment": "Très utile",
        })
        assert r2.status_code == 200

    def test_feedback_session_not_found(self, client):
        response = client.post("/api/chat/feedback", json={
            "session_id": "nonexistent",
            "message_id": "msg-123",
            "rating": 3,
        })
        assert response.status_code == 404


# ============================================================
# Admin endpoint security tests
# ============================================================

class TestAdminEndpointsDisabled:
    """Ensure unauthenticated admin endpoints are not publicly exposed."""

    def test_admin_routes_are_not_registered(self, client):
        assert client.get("/api/admin/sessions").status_code == 404
        assert client.delete("/api/admin/sessions/any-session-id").status_code == 404


# ============================================================
# Root redirect test
# ============================================================

class TestRootRedirect:
    """Test that root URL redirects to docs."""

    def test_root_redirects(self, client):
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/docs" in response.headers.get("location", "")
