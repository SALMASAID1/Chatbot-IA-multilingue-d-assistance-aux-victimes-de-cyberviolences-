"""Session management service.

Provides in-memory session storage for development with an abstract
base class to support Redis or other backends in production.

Each session owns its own RAGChain instance to maintain independent
conversation history.
"""
import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import uuid4

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import SESSION_TTL_MINUTES, MAX_HISTORY_SIZE

logger = logging.getLogger(__name__)


# ============================================================
# Session data model
# ============================================================

class Session:
    """Represents a conversation session."""

    def __init__(self, session_id: str, langue: Optional[str] = None):
        self.session_id = session_id
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.langue = langue
        self.history: List[Dict[str, str]] = []
        self.feedback: List[Dict] = []
        self._rag_chain = None  # Lazily initialized

    @property
    def rag_chain(self):
        """Lazily initialize the RAG chain (heavy import)."""
        if self._rag_chain is None:
            from rag.chain import RAGChain
            self._rag_chain = RAGChain()
        return self._rag_chain

    def add_message(self, role: str, content: str, message_id: Optional[str] = None):
        """Add a message to the session history."""
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "message_id": message_id or str(uuid4()),
        })
        self.last_activity = datetime.utcnow()

        # Trim history if it exceeds max size
        if len(self.history) > MAX_HISTORY_SIZE:
            self.history = self.history[-MAX_HISTORY_SIZE:]

    def add_feedback(self, message_id: str, rating: int, comment: Optional[str] = None):
        """Store user feedback for a specific message."""
        self.feedback.append({
            "message_id": message_id,
            "rating": rating,
            "comment": comment,
            "timestamp": datetime.utcnow().isoformat(),
        })
        self.last_activity = datetime.utcnow()

    def is_expired(self, ttl_minutes: int = SESSION_TTL_MINUTES) -> bool:
        """Check if the session has expired due to inactivity."""
        return datetime.utcnow() - self.last_activity > timedelta(minutes=ttl_minutes)

    @property
    def message_count(self) -> int:
        """Number of messages in the session."""
        return len(self.history)

    def to_summary(self) -> dict:
        """Return a summary dict for admin endpoints."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "last_activity": self.last_activity,
            "langue": self.langue,
            "message_count": self.message_count,
        }


# ============================================================
# Abstract session store
# ============================================================

class SessionStore(ABC):
    """Abstract base class for session storage backends."""

    @abstractmethod
    def create_session(self, langue: Optional[str] = None) -> Session:
        """Create a new session."""
        ...

    @abstractmethod
    def get_session(self, session_id: str) -> Optional[Session]:
        """Retrieve a session by ID."""
        ...

    @abstractmethod
    def delete_session(self, session_id: str) -> bool:
        """Delete a session. Returns True if it existed."""
        ...

    @abstractmethod
    def get_all_sessions(self) -> List[Session]:
        """List all active sessions."""
        ...

    @abstractmethod
    def cleanup_expired(self) -> int:
        """Remove expired sessions. Returns count removed."""
        ...


# ============================================================
# In-memory session store (development)
# ============================================================

class InMemorySessionStore(SessionStore):
    """Thread-safe in-memory session store for development."""

    def __init__(self):
        self._sessions: Dict[str, Session] = {}

    def create_session(self, langue: Optional[str] = None) -> Session:
        """Create a new session with a unique UUID."""
        session_id = str(uuid4())
        session = Session(session_id=session_id, langue=langue)
        self._sessions[session_id] = session
        logger.info(f"Session created: {session_id} (langue={langue})")
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Retrieve a session, returning None if expired or not found."""
        session = self._sessions.get(session_id)
        if session is None:
            return None
        if session.is_expired():
            logger.info(f"Session expired: {session_id}")
            self.delete_session(session_id)
            return None
        return session

    def delete_session(self, session_id: str) -> bool:
        """Delete a session by ID."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"Session deleted: {session_id}")
            return True
        return False

    def get_all_sessions(self) -> List[Session]:
        """List all non-expired sessions."""
        # Clean up expired first
        self.cleanup_expired()
        return list(self._sessions.values())

    def cleanup_expired(self) -> int:
        """Remove expired sessions. Returns count removed."""
        expired = [
            sid for sid, session in self._sessions.items()
            if session.is_expired()
        ]
        for sid in expired:
            del self._sessions[sid]
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired session(s)")
        return len(expired)

    @property
    def active_count(self) -> int:
        """Number of active (non-expired) sessions."""
        return len([s for s in self._sessions.values() if not s.is_expired()])


# ============================================================
# Session cleanup background task
# ============================================================

async def session_cleanup_task(store: SessionStore, interval_seconds: int = 300):
    """Background task that periodically cleans up expired sessions.

    Args:
        store: The session store to clean
        interval_seconds: Cleanup interval (default: 5 minutes)
    """
    while True:
        try:
            await asyncio.sleep(interval_seconds)
            removed = store.cleanup_expired()
            if removed:
                logger.info(f"Session cleanup: removed {removed} expired session(s)")
        except asyncio.CancelledError:
            logger.info("Session cleanup task cancelled")
            break
        except Exception as e:
            logger.error(f"Session cleanup error: {e}")


# ============================================================
# Global session store singleton
# ============================================================

_session_store: Optional[SessionStore] = None


def get_session_store() -> SessionStore:
    """Get or create the global session store singleton."""
    global _session_store
    if _session_store is None:
        _session_store = InMemorySessionStore()
        logger.info("Initialized InMemorySessionStore")
    return _session_store
