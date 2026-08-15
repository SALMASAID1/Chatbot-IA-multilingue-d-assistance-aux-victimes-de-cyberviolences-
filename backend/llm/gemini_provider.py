"""Gemini LLM provider for the EMC Helpline chatbot.

Provides a clean wrapper around Google's Gemini API via LangChain,
centralizing configuration, error handling, and logging.

Usage:
    provider = GeminiProvider()
    response = provider.generate(messages)
"""
import logging
from typing import List, Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import GOOGLE_API_KEY

logger = logging.getLogger(__name__)

# Fallback model chain with verified active models
MODELS_FALLBACK_CHAIN = ["gemini-flash-latest", "gemini-2.5-flash", "gemini-pro-latest"]
DEFAULT_TEMPERATURE = 0.3


class GeminiProvider:
    """
    Gemini LLM provider for the EMC Helpline chatbot.

    Wraps ChatGoogleGenerativeAI with:
    - Centralized configuration (model, temperature, API key)
    - Automatic fallback between Gemini models (gemini-flash-latest -> gemini-2.5-flash -> gemini-pro-latest)
    - Error handling with graceful fallback messages
    - Logging of requests
    """

    def __init__(
        self,
        model_name: str = "gemini-flash-latest",
        temperature: float = DEFAULT_TEMPERATURE,
        api_key: Optional[str] = None,
    ):
        self.model_name = model_name
        self.temperature = temperature
        self._api_key = api_key or GOOGLE_API_KEY

        if not self._api_key:
            logger.error("GOOGLE_API_KEY is not set!")
            raise ValueError(
                "GOOGLE_API_KEY is required. Set it in .env or pass it directly."
            )

        self._init_llm(self.model_name)

    def _init_llm(self, model: str):
        """Initialize ChatGoogleGenerativeAI with a given model name."""
        self.model_name = model
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            temperature=self.temperature,
            google_api_key=self._api_key,
            convert_system_message_to_human=True,
        )
        logger.info(f"GeminiProvider initialized with model: {model}")

    def generate(self, messages: List[BaseMessage]) -> str:
        """
        Send messages to Gemini and return the response text.
        Automatically falls back to alternative Gemini models if quota is exhausted.
        """
        last_error = None

        # Build fallback list starting from current requested model
        models_to_try = [self.model_name] + [m for m in MODELS_FALLBACK_CHAIN if m != self.model_name]

        for model in models_to_try:
            try:
                if self.model_name != model:
                    logger.warning(f"Falling back to model: {model}")
                    self._init_llm(model)

                logger.debug(f"Sending {len(messages)} messages to {self.model_name}")
                response = self.llm.invoke(messages)
                content = response.content
                if isinstance(content, list):
                    text_parts = []
                    for part in content:
                        if isinstance(part, dict) and "text" in part:
                            text_parts.append(part["text"])
                        elif isinstance(part, str):
                            text_parts.append(part)
                    return "".join(text_parts)
                return str(content)

            except Exception as e:
                last_error = e
                err_str = str(e).lower()
                if "429" in err_str or "quota" in err_str or "resource_exhausted" in err_str:
                    logger.warning(f"Model {model} hit quota/rate limit: {e}. Trying fallback model...")
                    continue
                else:
                    logger.error(f"Gemini API error ({model}): {e}")
                    raise

        if last_error:
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
