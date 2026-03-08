"""Tests for Gemini client wrapper."""

from unittest.mock import MagicMock, patch

import pytest

from src.clients.gemini_client import GeminiClient, GeminiClientError
from src.config import Settings


def test_gemini_client_raises_when_key_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """GeminiClient.from_settings raises when GEMINI_API_KEY is not set."""
    monkeypatch.setenv("GEMINI_API_KEY", "")
    settings = Settings()
    with pytest.raises(ValueError, match="GEMINI_API_KEY is required"):
        GeminiClient.from_settings(settings)


def test_gemini_client_from_settings_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    """GeminiClient.from_settings returns client when key is set."""
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    settings = Settings()
    with patch("src.clients.gemini_client.genai") as mock_genai:
        client = GeminiClient.from_settings(settings)
        assert client is not None
        mock_genai.configure.assert_called_once_with(api_key="test-key")


def test_gemini_client_complete_returns_text(monkeypatch: pytest.MonkeyPatch) -> None:
    """complete() returns response text from mocked generate_content."""
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    settings = Settings()
    mock_response = MagicMock()
    mock_response.text = "Hello from Gemini"
    with patch("src.clients.gemini_client.genai") as mock_genai:
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.types.GenerationConfig.return_value = MagicMock()
        client = GeminiClient.from_settings(settings)
        out = client.complete("Hi")
        assert out == "Hello from Gemini"
        mock_model.generate_content.assert_called_once()
