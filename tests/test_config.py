"""Tests for application configuration."""

import pytest

from src.config import Settings


def test_settings_loads_with_minimal_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Settings loads with only required defaults when no API keys are set."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    monkeypatch.setenv("ENVIRONMENT", "local")
    monkeypatch.setenv("LOG_LEVEL", "INFO")
    s = Settings()
    assert s.ANTHROPIC_API_KEY == "sk-ant-test"
    assert s.ENVIRONMENT == "local"
    assert s.LOG_LEVEL == "INFO"
    assert s.HARDWARE_ENABLED is False


def test_settings_coerces_bool(monkeypatch: pytest.MonkeyPatch) -> None:
    """HARDWARE_ENABLED and other bools are coerced from env strings."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    monkeypatch.setenv("HARDWARE_ENABLED", "true")
    s = Settings()
    assert s.HARDWARE_ENABLED is True


def test_settings_optional_openai(monkeypatch: pytest.MonkeyPatch) -> None:
    """OpenAI key and model are optional and default correctly."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    s = Settings()
    assert s.OPENAI_API_KEY is None or s.OPENAI_API_KEY == ""
    assert s.OPENAI_MODEL == "gpt-4o"


def test_settings_loads_without_anthropic_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Settings can load without ANTHROPIC_API_KEY; client will validate at use time."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    s = Settings()
    assert s.ANTHROPIC_API_KEY is None or s.ANTHROPIC_API_KEY == ""


def test_require_anthropic_key_raises_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """require_anthropic_key raises ValueError when key is not set."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    s = Settings()
    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY is required"):
        s.require_anthropic_key()


def test_require_anthropic_key_returns_stripped_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """require_anthropic_key returns stripped key when set."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "  sk-ant-test  ")
    s = Settings()
    assert s.require_anthropic_key() == "sk-ant-test"


def test_settings_default_model(monkeypatch: pytest.MonkeyPatch) -> None:
    """Default Anthropic model is set."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    s = Settings()
    assert "claude" in s.ANTHROPIC_MODEL.lower() or s.ANTHROPIC_MODEL


def test_require_gemini_key_raises_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """require_gemini_key raises ValueError when key is not set."""
    monkeypatch.setenv("GEMINI_API_KEY", "")
    s = Settings()
    with pytest.raises(ValueError, match="GEMINI_API_KEY is required"):
        s.require_gemini_key()


def test_require_gemini_key_returns_stripped_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """require_gemini_key returns stripped key when set."""
    monkeypatch.setenv("GEMINI_API_KEY", "  my-gemini-key  ")
    s = Settings()
    assert s.require_gemini_key() == "my-gemini-key"
