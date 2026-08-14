"""Tests for the session management service.

Covers:
- Session creation
- Session retrieval
- Session expiration
- History management
- Feedback storage
- Cleanup of expired sessions
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))
from services.session_service import Session, InMemorySessionStore


# ============================================================
# Session model tests
# ============================================================

class TestSession:
    """Test the Session data model."""

    def test_create_session(self):
        session = Session(session_id="test-123", langue="fr")
        assert session.session_id == "test-123"
        assert session.langue == "fr"
        assert session.message_count == 0
        assert isinstance(session.created_at, datetime)

    def test_add_message(self):
        session = Session(session_id="test-123")
        session.add_message("user", "Hello")
        session.add_message("assistant", "Hi there!")
        assert session.message_count == 2
        assert session.history[0]["role"] == "user"
        assert session.history[1]["role"] == "assistant"

    def test_history_trimming(self):
        session = Session(session_id="test-123")
        # Add more than MAX_HISTORY_SIZE messages
        for i in range(60):
            session.add_message("user", f"Message {i}")
        # Should be trimmed to MAX_HISTORY_SIZE (default 50)
        assert session.message_count <= 50

    def test_add_feedback(self):
        session = Session(session_id="test-123")
        session.add_feedback("msg-1", 5, "Très utile")
        assert len(session.feedback) == 1
        assert session.feedback[0]["rating"] == 5
        assert session.feedback[0]["comment"] == "Très utile"

    def test_session_expiry(self):
        session = Session(session_id="test-123")
        # Should not be expired immediately
        assert session.is_expired(ttl_minutes=30) is False

        # Manually set last_activity to the past
        session.last_activity = datetime.utcnow() - timedelta(minutes=31)
        assert session.is_expired(ttl_minutes=30) is True

    def test_to_summary(self):
        session = Session(session_id="test-123", langue="ar")
        session.add_message("user", "مرحبا")
        summary = session.to_summary()
        assert summary["session_id"] == "test-123"
        assert summary["langue"] == "ar"
        assert summary["message_count"] == 1


# ============================================================
# InMemorySessionStore tests
# ============================================================

class TestInMemorySessionStore:
    """Test the in-memory session store."""

    def setup_method(self):
        """Create a fresh store for each test."""
        self.store = InMemorySessionStore()

    def test_create_session(self):
        session = self.store.create_session(langue="fr")
        assert session.session_id is not None
        assert session.langue == "fr"

    def test_get_session(self):
        session = self.store.create_session()
        retrieved = self.store.get_session(session.session_id)
        assert retrieved is not None
        assert retrieved.session_id == session.session_id

    def test_get_nonexistent_session(self):
        result = self.store.get_session("nonexistent-id")
        assert result is None

    def test_get_expired_session(self):
        session = self.store.create_session()
        # Manually expire it
        session.last_activity = datetime.utcnow() - timedelta(minutes=60)
        result = self.store.get_session(session.session_id)
        assert result is None

    def test_delete_session(self):
        session = self.store.create_session()
        assert self.store.delete_session(session.session_id) is True
        assert self.store.get_session(session.session_id) is None

    def test_delete_nonexistent(self):
        assert self.store.delete_session("nonexistent") is False

    def test_get_all_sessions(self):
        self.store.create_session(langue="fr")
        self.store.create_session(langue="ar")
        self.store.create_session(langue="fr")
        sessions = self.store.get_all_sessions()
        assert len(sessions) == 3

    def test_cleanup_expired(self):
        s1 = self.store.create_session()
        s2 = self.store.create_session()
        s3 = self.store.create_session()

        # Expire s1 and s2
        s1.last_activity = datetime.utcnow() - timedelta(minutes=60)
        s2.last_activity = datetime.utcnow() - timedelta(minutes=60)

        removed = self.store.cleanup_expired()
        assert removed == 2
        assert self.store.active_count == 1

    def test_active_count(self):
        self.store.create_session()
        self.store.create_session()
        assert self.store.active_count == 2
