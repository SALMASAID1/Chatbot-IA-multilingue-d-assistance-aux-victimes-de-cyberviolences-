"""Chat orchestration service.

Main business logic layer that ties together:
- Language detection (language_service)
- Session management (session_service)
- RAG pipeline (rag.chain.RAGChain)

Flow:
    User message → detect language → get/create session
    → RAGChain.ask(message, langue) → build response with metadata
"""
import logging
from typing import Optional
from uuid import uuid4

from services.language_service import detect_language, LanguageResult
from services.session_service import get_session_store, Session

logger = logging.getLogger(__name__)


class ChatServiceUnavailableError(RuntimeError):
    """Raised when the RAG/LLM dependency cannot produce an answer."""

    def __init__(self, langue: str):
        self.langue = langue
        super().__init__(_get_error_response(langue))


class ChatService:
    """Orchestrates the chat flow between the API layer and the RAG pipeline."""

    def __init__(self):
        self.session_store = get_session_store()

    def process_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        langue_override: Optional[str] = None,
    ) -> dict:
        """
        Process a user message through the full pipeline.

        Args:
            message: User's input message
            session_id: Existing session ID (or None to create new)
            langue_override: Language override from the user (e.g., from frontend selector)

        Returns:
            dict with: answer, sources, langue, is_darija, is_urgent,
                       user_profile, session_id, message_id, timestamp
        """
        # 1. Detect language (unless overridden)
        if langue_override:
            lang_result = LanguageResult(
                detected_lang=langue_override,
                is_darija=False,
                confidence=1.0,
                raw_detection=f"override:{langue_override}",
            )
        else:
            lang_result = detect_language(message)

        logger.info(
            f"Language detected: {lang_result.detected_lang} "
            f"(darija={lang_result.is_darija}, confidence={lang_result.confidence})"
        )

        # 2. Get or create session
        session = None
        if session_id:
            session = self.session_store.get_session(session_id)

        if session is None:
            session = self.session_store.create_session(langue=lang_result.detected_lang)
            logger.info(f"New session created: {session.session_id}")

        # Update session language if it changed
        if session.langue != lang_result.detected_lang:
            session.langue = lang_result.detected_lang

        # 3. Generate a message ID for this exchange
        message_id = f"msg-{uuid4().hex[:12]}"

        # 4. Call the RAG pipeline
        try:
            rag_result = session.rag_chain.ask(
                question=message,
                langue=lang_result.detected_lang,
                include_history=True,
            )
        except Exception as e:
            logger.error(f"RAG pipeline error: {e}", exc_info=True)
            raise ChatServiceUnavailableError(lang_result.detected_lang) from e

        # 5. Store messages in session history
        session.add_message("user", message, message_id=f"{message_id}-q")
        session.add_message("assistant", rag_result["answer"], message_id=f"{message_id}-a")

        # 6. Build response
        from datetime import datetime

        sources = []
        for src in rag_result.get("sources", []):
            sources.append({
                "path": src.get("path"),
                "categorie": src.get("categorie"),
                "score": src.get("score"),
            })

        response = {
            "answer": rag_result["answer"],
            "sources": sources,
            "langue": rag_result["langue"],
            "is_darija": lang_result.is_darija,
            "is_urgent": rag_result.get("is_urgent", False),
            "user_profile": rag_result.get("user_profile", "victim"),
            "session_id": session.session_id,
            "message_id": message_id,
            "timestamp": datetime.utcnow(),
        }

        logger.info(
            f"Chat processed: session={session.session_id}, "
            f"lang={response['langue']}, urgent={response['is_urgent']}, "
            f"profile={response['user_profile']}"
        )

        return response

    def get_history(self, session_id: str) -> Optional[dict]:
        """
        Retrieve conversation history for a session.

        Returns None if session not found.
        """
        session = self.session_store.get_session(session_id)
        if session is None:
            return None

        from datetime import datetime

        messages = []
        for msg in session.history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"],
                "timestamp": msg["timestamp"],
                "message_id": msg.get("message_id"),
            })

        return {
            "session_id": session.session_id,
            "messages": messages,
            "total_messages": len(messages),
        }

    def submit_feedback(
        self,
        session_id: str,
        message_id: str,
        rating: int,
        comment: Optional[str] = None,
    ) -> bool:
        """
        Submit feedback for a specific message.

        Returns False if session not found.
        """
        session = self.session_store.get_session(session_id)
        if session is None:
            return False

        session.add_feedback(message_id, rating, comment)
        logger.info(
            f"Feedback received: session={session_id}, "
            f"message={message_id}, rating={rating}"
        )
        return True


def _get_error_response(langue: str) -> str:
    """Return a user-friendly error message in the detected language."""
    if langue == "ar":
        return (
            "عذرًا، حدث خطأ تقني. يرجى المحاولة مرة أخرى.\n\n"
            "إذا كنت في خطر فوري، اتصل بالشرطة: 19 أو الدرك الملكي: 177"
        )
    return (
        "Désolé, une erreur technique s'est produite. Veuillez réessayer.\n\n"
        "Si vous êtes en danger immédiat, appelez la Police : 19 ou la Gendarmerie : 177"
    )


# ============================================================
# Global chat service singleton
# ============================================================

_chat_service: Optional[ChatService] = None


def get_chat_service() -> ChatService:
    """Get or create the global chat service singleton."""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
