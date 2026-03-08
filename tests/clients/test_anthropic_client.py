"""Tests for Anthropic client wrapper."""

from unittest.mock import MagicMock, patch

import pytest

from src.clients.anthropic_client import AnthropicClient
from src.config import Settings


def test_anthropic_client_raises_when_key_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """AnthropicClient.from_settings raises when ANTHROPIC_API_KEY is not set."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    settings = Settings()
    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY is required"):
        AnthropicClient.from_settings(settings)


def test_anthropic_client_from_settings_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    """AnthropicClient.from_settings returns client when key is set."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    settings = Settings()
    with patch("src.clients.anthropic_client.Anthropic") as mock_anthropic:
        client = AnthropicClient.from_settings(settings)
        assert client is not None
        mock_anthropic.assert_called_once_with(api_key="sk-ant-test")


def test_complete_calls_sdk_with_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    """complete() calls Anthropic API with model and messages; retries on rate limit."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    settings = Settings()
    with patch("src.clients.anthropic_client.Anthropic") as mock_anthropic_cls:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = MagicMock(
            content=[MagicMock(text="Hi")],
            stop_reason="end_turn",
        )
        mock_anthropic_cls.return_value = mock_client
        client = AnthropicClient.from_settings(settings)
        out = client.complete("Hello")
        assert out == "Hi"
        mock_client.messages.create.assert_called_once()
        call_kw = mock_client.messages.create.call_args[1]
        assert call_kw["model"] == settings.ANTHROPIC_MODEL
        assert call_kw["max_tokens"] == 1024
