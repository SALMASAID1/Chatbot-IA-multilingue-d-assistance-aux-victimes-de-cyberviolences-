"""Tests for the administration API key guard.

The admin endpoints expose session metadata and can destroy sessions, so they
must be unreachable unless an operator has explicitly configured a key.
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient

import config

ADMIN_KEY = "test-admin-key-0123456789"


@pytest.fixture(autouse=True)
def reset_singletons():
    import services.session_service as ss
    import services.chat_service as cs

    ss._session_store = None
    cs._chat_service = None
    yield
    ss._session_store = None
    cs._chat_service = None


@pytest.fixture
def client():
    """Test client with the RAG pipeline mocked out."""
    mock_rag = MagicMock()
    mock_rag.ask.return_value = {
        "answer": "Réponse de test.",
        "sources": [],
        "langue": "fr",
        "context_used": "",
        "is_urgent": False,
        "user_profile": "victim",
    }
    with patch(
        "services.session_service.Session.rag_chain",
        new_callable=lambda: property(lambda self: mock_rag),
    ):
        from main import app

        with TestClient(app) as test_client:
            yield test_client


@pytest.fixture
def admin_enabled(monkeypatch):
    monkeypatch.setattr(config, "ADMIN_API_KEY", ADMIN_KEY)
    return ADMIN_KEY


@pytest.fixture
def admin_disabled(monkeypatch):
    monkeypatch.setattr(config, "ADMIN_API_KEY", None)


class TestAdminDisabledByDefault:
    """With no key configured the admin surface must not exist at all."""

    def test_list_sessions_is_hidden(self, client, admin_disabled):
        response = client.get("/api/admin/sessions")
        assert response.status_code == 404

    def test_delete_session_is_hidden(self, client, admin_disabled):
        response = client.delete("/api/admin/sessions/whatever")
        assert response.status_code == 404

    def test_a_supplied_key_does_not_help(self, client, admin_disabled):
        response = client.get("/api/admin/sessions", headers={"X-Admin-Key": ADMIN_KEY})
        assert response.status_code == 404

    def test_response_does_not_leak_that_an_admin_api_exists(self, client, admin_disabled):
        body = client.get("/api/admin/sessions").text.lower()
        assert "admin" not in body
        assert "clé" not in body


class TestAdminRequiresKey:
    """With a key configured, only requests carrying it are served."""

    def test_missing_header_is_rejected(self, client, admin_enabled):
        response = client.get("/api/admin/sessions")
        assert response.status_code == 401

    def test_wrong_key_is_rejected(self, client, admin_enabled):
        response = client.get("/api/admin/sessions", headers={"X-Admin-Key": "wrong"})
        assert response.status_code == 401

    def test_empty_key_is_rejected(self, client, admin_enabled):
        response = client.get("/api/admin/sessions", headers={"X-Admin-Key": ""})
        assert response.status_code == 401

    def test_correct_key_is_accepted(self, client, admin_enabled):
        response = client.get("/api/admin/sessions", headers={"X-Admin-Key": admin_enabled})
        assert response.status_code == 200
        assert "total_sessions" in response.json()

    def test_delete_requires_the_key(self, client, admin_enabled):
        created = client.post("/api/chat", json={"message": "Bonjour"})
        session_id = created.json()["session_id"]

        assert client.delete(f"/api/admin/sessions/{session_id}").status_code == 401

        deleted = client.delete(
            f"/api/admin/sessions/{session_id}",
            headers={"X-Admin-Key": admin_enabled},
        )
        assert deleted.status_code == 200

    def test_chat_endpoints_stay_public(self, client, admin_enabled):
        """Guarding admin must not require a key for ordinary users."""
        assert client.post("/api/chat", json={"message": "Bonjour"}).status_code == 200
        assert client.get("/api/health").status_code == 200
