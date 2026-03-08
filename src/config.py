"""Application configuration via pydantic-settings. All env vars documented in .env.example."""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Load and validate configuration from environment. Never log secret values."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Anthropic
    ANTHROPIC_API_KEY: str | None = Field(default=None, description="Required when using Anthropic client.")
    ANTHROPIC_MODEL: str = Field(default="claude-sonnet-4-20250514", description="Default model.")

    # OpenAI
    OPENAI_API_KEY: str | None = Field(default=None, description="Required when using OpenAI client.")
    OPENAI_MODEL: str = Field(default="gpt-4o", description="Default model.")

    # Google Gemini
    GEMINI_API_KEY: str | None = Field(default=None, description="Required when using Gemini client.")
    GEMINI_MODEL: str = Field(default="gemini-1.5-flash", description="Default model.")

    # MCP (server type TBD)
    MCP_SERVER_URL: str | None = Field(default=None, description="MCP server endpoint if remote.")
    MCP_AUTH_TOKEN: str | None = Field(default=None, description="MCP auth token.")

    # Hardware
    GPIO_MODE: Literal["BCM", "BOARD"] = Field(default="BCM", description="Raspberry Pi pin numbering.")
    HARDWARE_ENABLED: bool = Field(default=False, description="Set true on Pi hardware.")

    # Runtime
    ENVIRONMENT: Literal["local", "staging", "production"] = Field(
        default="local", description="Deployment environment."
    )
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO", description="Logging level."
    )

    # API / Governance
    DATABASE_URL: str = Field(
        default="sqlite:///agent_ops.db",
        description="Database URL (sqlite:///path or postgres://...).",
    )
    API_HOST: str = Field(default="0.0.0.0", description="API bind host.")
    API_PORT: int = Field(default=8000, description="API bind port.")
    CORS_ORIGINS: str = Field(
        default="",
        description="Comma-separated origins for CORS (e.g. https://your-app.vercel.app). Local dev origins are always allowed.",
    )

    def require_anthropic_key(self) -> str:
        """Return Anthropic API key; raise if not set. Use before creating Anthropic client."""
        if not self.ANTHROPIC_API_KEY or not self.ANTHROPIC_API_KEY.strip():
            raise ValueError("ANTHROPIC_API_KEY is required for Anthropic client. Set it in .env.")
        return self.ANTHROPIC_API_KEY.strip()

    def require_gemini_key(self) -> str:
        """Return Gemini API key; raise if not set. Use before creating Gemini client."""
        if not self.GEMINI_API_KEY or not self.GEMINI_API_KEY.strip():
            raise ValueError("GEMINI_API_KEY is required for Gemini client. Set it in .env.")
        return self.GEMINI_API_KEY.strip()
