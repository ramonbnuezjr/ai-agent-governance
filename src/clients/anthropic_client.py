"""Thin Anthropic SDK wrapper with retry and explicit error handling."""

import logging
from typing import Any

import anthropic
from anthropic import Anthropic

from src.config import Settings

logger = logging.getLogger(__name__)

# Rate limit and token errors to retry or surface explicitly
ANTHROPIC_RATE_LIMIT_CODES = (429,)
ANTHROPIC_OVERLOADED_CODES = (529, 503)


class AnthropicClientError(Exception):
    """Raised when Anthropic API call fails after retries or with unrecoverable error."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class AnthropicClient:
    """Thin wrapper over Anthropic SDK with retry and error handling. Never log API key."""

    def __init__(self, api_key: str, model: str) -> None:
        self._client: Anthropic = Anthropic(api_key=api_key)
        self._model = model

    @classmethod
    def from_settings(cls, settings: Settings) -> "AnthropicClient":
        """Build client from Settings; raises ValueError if ANTHROPIC_API_KEY not set."""
        key = settings.require_anthropic_key()
        return cls(api_key=key, model=settings.ANTHROPIC_MODEL)

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
            system: Optional system prompt.
            max_retries: Retries on rate limit (429) or overload (503/529).

        Returns:
            The assistant's text content.

        Raises:
            AnthropicClientError: On API failure after retries or unrecoverable error.
        """
        messages = [{"role": "user", "content": user_message}]
        kwargs: dict[str, Any] = {
            "model": self._model,
            "max_tokens": max_tokens,
            "messages": messages,
        }
        if system is not None:
            kwargs["system"] = system

        last_exc: Exception | None = None
        for attempt in range(max_retries + 1):
            try:
                response = self._client.messages.create(**kwargs)
                if not response.content or not response.stop_reason:
                    raise AnthropicClientError("Empty or invalid response from Anthropic")
                text = response.content[0].text if response.content else ""
                return text
            except anthropic.APIStatusError as e:
                last_exc = e
                if e.status_code in ANTHROPIC_RATE_LIMIT_CODES + ANTHROPIC_OVERLOADED_CODES:
                    if attempt < max_retries:
                        logger.warning(
                            "Anthropic rate limit or overload (status=%s), retrying.",
                            e.status_code,
                        )
                        continue
                raise AnthropicClientError(
                    f"Anthropic API error: {e.message}", status_code=e.status_code
                ) from e
            except anthropic.APIConnectionError as e:
                last_exc = e
                if attempt < max_retries:
                    logger.warning("Anthropic connection error, retrying: %s", e)
                    continue
                raise AnthropicClientError("Anthropic connection failed") from e
            except anthropic.APIError as e:
                raise AnthropicClientError(f"Anthropic API error: {e}") from e

        if last_exc is not None:
            raise AnthropicClientError("Anthropic request failed after retries") from last_exc
        raise AnthropicClientError("Anthropic request failed")
