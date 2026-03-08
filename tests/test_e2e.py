"""End-to-end test: load config, run main flow (no live API calls)."""

import os

import pytest


def test_e2e_load_config_and_run_main(monkeypatch: pytest.MonkeyPatch) -> None:
    """Load settings and run main() without requiring real API keys or hardware."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-e2e-test")
    monkeypatch.setenv("ENVIRONMENT", "local")
    monkeypatch.setenv("LOG_LEVEL", "INFO")
    monkeypatch.setenv("HARDWARE_ENABLED", "false")

    from src.main import main

    main()
    # If we get here without exception, config loaded and stub/GPIO paths ran
    assert True
