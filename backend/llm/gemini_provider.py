"""Gemini LLM provider for the EMC Helpline chatbot.

Provides a clean wrapper around Google's Gemini API via LangChain,
centralizing configuration, error handling, and logging.

Usage:
    provider = GeminiProvider()
    response = provider.generate(messages)
"""
import logging
from functools import lru_cache
from typing import List, Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import (
    GOOGLE_API_KEY,
    GEMINI_MODEL,
    GEMINI_FALLBACK_MODELS,
    GEMINI_MAX_OUTPUT_TOKENS,
    GEMINI_REQUEST_TIMEOUT_SECONDS,
    GEMINI_MAX_RETRIES,
    GEMINI_THINKING_LEVEL,
)

logger = logging.getLogger(__name__)

DEFAULT_TEMPERATURE = None
_llm_runtime_status = "configured" if GOOGLE_API_KEY else "unconfigured"


def get_llm_runtime_status() -> str:
    """Return the latest known LLM state without spending an API request."""
    return _llm_runtime_status


class GeminiProvider:
    """
    Gemini LLM provider for the EMC Helpline chatbot.

    Wraps ChatGoogleGenerativeAI with:
    - Centralized configuration (model, temperature, API key)
    - Configurable automatic fallback between currently supported Gemini models
    - Error handling with graceful fallback messages
    - Logging of requests
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: Optional[float] = DEFAULT_TEMPERATURE,
        api_key: Optional[str] = None,
    ):
        self.model_name = model_name or GEMINI_MODEL
        self.temperature = temperature
        self._api_key = api_key or GOOGLE_API_KEY
        self._llms = {}

        if not self._api_key:
            logger.error("GOOGLE_API_KEY is not set!")
            raise ValueError(
                "GOOGLE_API_KEY is required. Set it in .env or pass it directly."
            )

        self.llm = self._init_llm(self.model_name)

    def _init_llm(self, model: str) -> ChatGoogleGenerativeAI:
        """Initialize ChatGoogleGenerativeAI with a given model name."""
        llm = ChatGoogleGenerativeAI(
            model=model,
            temperature=self.temperature,
            google_api_key=self._api_key,
            max_tokens=GEMINI_MAX_OUTPUT_TOKENS,
            retries=GEMINI_MAX_RETRIES,
            request_timeout=GEMINI_REQUEST_TIMEOUT_SECONDS,
            thinking_level=GEMINI_THINKING_LEVEL,
            convert_system_message_to_human=False,
        )
        self._llms[model] = llm
        logger.info(f"GeminiProvider initialized with model: {model}")
        return llm

    def _get_llm(self, model: str) -> ChatGoogleGenerativeAI:
        """Reuse one initialized client per model."""
        return self._llms.get(model) or self._init_llm(model)

    def generate(self, messages: List[BaseMessage]) -> str:
        """
        Send messages to Gemini and return the response text.
        Automatically falls back to alternative Gemini models if quota is exhausted.
        """
        last_error = None

        global _llm_runtime_status

        # Preserve order while removing duplicate model aliases.
        models_to_try = list(dict.fromkeys([
            self.model_name,
            *GEMINI_FALLBACK_MODELS,
        ]))

        for model in models_to_try:
            try:
                if self.model_name != model:
                    logger.warning(f"Falling back to model: {model}")

                logger.debug(f"Sending {len(messages)} messages to {model}")
                response = self._get_llm(model).invoke(messages)
                content = response.content
                if isinstance(content, list):
                    text_parts = []
                    for part in content:
                        if isinstance(part, dict) and "text" in part:
                            text_parts.append(part["text"])
                        elif isinstance(part, str):
                            text_parts.append(part)
                    answer = "".join(text_parts)
                else:
                    answer = str(content)

                if not answer.strip():
                    raise RuntimeError(f"Model {model} returned an empty response")

                _llm_runtime_status = "healthy"
                return answer.strip()

            except Exception as e:
                last_error = e
                err_str = str(e).lower()
                can_try_another_model = any(marker in err_str for marker in (
                    "429", "quota", "resource_exhausted",
                    "404", "not_found", "no longer available",
                    "model is not found", "unsupported model",
                    "504", "deadline_exceeded", "gateway timeout",
                    "503", "service unavailable",
                ))
                if can_try_another_model:
                    logger.warning(
                        f"Model {model} is unavailable: {e}. Trying fallback model..."
                    )
                    continue
                else:
                    logger.error(f"Gemini API error ({model}): {e}")
                    _llm_runtime_status = "error"
                    raise

        if last_error:
            _llm_runtime_status = "error"
            raise last_error
        return ""

    def is_available(self) -> bool:
        """
        Check if the Gemini API is reachable with a minimal test.

        Returns:
            True if API responds, False otherwise
        """
        try:
            test_messages = [HumanMessage(content="ping")]
            self.llm.invoke(test_messages)
            return True
        except Exception as e:
            logger.warning(f"Gemini availability check failed: {e}")
            return False

    @property
    def info(self) -> dict:
        """Return provider metadata for health checks and logging."""
        return {
            "provider": "google_gemini",
            "model": self.model_name,
            "temperature": self.temperature,
            "has_api_key": bool(self._api_key),
        }


@lru_cache(maxsize=8)
def get_gemini_provider(
    model_name: Optional[str] = None,
    temperature: Optional[float] = DEFAULT_TEMPERATURE,
) -> GeminiProvider:
    """Return a shared stateless provider so sessions reuse HTTP clients."""
    return GeminiProvider(model_name=model_name, temperature=temperature)
