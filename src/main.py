"""Entrypoint for agent_ops. Loads config and runs governed workflow."""

import logging
import sys

from src.config import Settings
from src.hardware.gpio import GPIOAdapter
from src.mcp.client import MCPClientStub

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(name)s %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Load settings, optionally wire MCP/GPIO, and run. No AI call by default."""
    settings = Settings()
    logger.info("Config loaded; environment=%s log_level=%s", settings.ENVIRONMENT, settings.LOG_LEVEL)

    # Stub MCP client (server type TBD)
    mcp = MCPClientStub(server_url=settings.MCP_SERVER_URL, auth_token=settings.MCP_AUTH_TOKEN)
    tools_response = mcp.list_tools()
    logger.info("MCP stub list_tools: %s tools", len(tools_response.tools))

    # GPIO degrades gracefully when disabled
    gpio = GPIOAdapter(enabled=settings.HARDWARE_ENABLED, mode=settings.GPIO_MODE)
    gpio.setup(17, "out")
    gpio.cleanup()

    logger.info("agent_ops run complete.")


if __name__ == "__main__":
    main()
