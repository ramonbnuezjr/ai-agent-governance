"""Thin Google Gemini SDK wrapper with retry and explicit error handling."""

import logging
from typing import Any

import google.generativeai as genai

from src.config import Settings

logger = logging.getLogger(__name__)


class GeminiClientError(Exception):
    """Raised when Gemini API call fails after retries or with unrecoverable error."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class GeminiClient:
    """Thin wrapper over Google Generative AI (Gemini) with retry and error handling. Never log API key."""

    def __init__(self, api_key: str, model: str) -> None:
        genai.configure(api_key=api_key)
        self._model_name = model
        self._model = genai.GenerativeModel(model_name=model)

    @classmethod
    def from_settings(cls, settings: Settings) -> "GeminiClient":
        """Build client from Settings; raises ValueError if GEMINI_API_KEY not set."""
        key = settings.require_gemini_key()
        return cls(api_key=key, model=settings.GEMINI_MODEL)

    def complete(
        self,
        user_message: str,
        *,
        max_tokens: int = 1024,
        system: str | None = None,
        max_retries: int = 2,
    ) -> str:
        """
        Send a single user message and return the assistant text.

        Args:
            user_message: The user prompt.
            max_tokens: Maximum tokens in the response.
            system: Optional system instruction.
            max_retries: Retries on rate limit or transient errors.

        Returns:
            The assistant's text content.

        Raises:
            GeminiClientError: On API failure after retries or unrecoverable error.
        """
        model = self._model
        if system is not None:
            model = genai.GenerativeModel(
                model_name=self._model_name,
                system_instruction=system,
            )
        generation_config = genai.types.GenerationConfig(max_output_tokens=max_tokens)
        last_exc: Exception | None = None
        for attempt in range(max_retries + 1):
            try:
                response = model.generate_content(
                    user_message,
                    generation_config=generation_config,
                )
                if not response or not response.text:
                    raise GeminiClientError("Empty or invalid response from Gemini")
                return response.text
            except Exception as e:
                last_exc = e
                err_str = str(e).lower()
                if "429" in err_str or "resource_exhausted" in err_str or "quota" in err_str:
                    if attempt < max_retries:
                        logger.warning("Gemini rate limit or quota, retrying: %s", e)
                        continue
                raise GeminiClientError(f"Gemini API error: {e}") from e
        if last_exc is not None:
            raise GeminiClientError("Gemini request failed after retries") from last_exc
        raise GeminiClientError("Gemini request failed")
