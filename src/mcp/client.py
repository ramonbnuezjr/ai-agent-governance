"""MCP client stub with Pydantic-validated responses. Server type TBD."""

from pydantic import BaseModel, Field


class MCPToolSchema(BaseModel):
    """Validated schema for a single MCP tool (stub shape)."""

    name: str = Field(..., description="Tool name.")
    description: str | None = Field(default=None, description="Tool description.")
    input_schema: dict[str, object] | None = Field(default=None, description="JSON schema for inputs.")


class MCPListToolsResponse(BaseModel):
    """Validated response for list_tools (stub)."""

    tools: list[MCPToolSchema] = Field(default_factory=list, description="List of available tools.")


class MCPClientStub:
    """
    Stub MCP client that returns Pydantic-validated structures.
    Does not connect to a real server; server type (stdio vs SSE) TBD.
    """

    def __init__(self, server_url: str | None = None, auth_token: str | None = None) -> None:
        self._server_url = server_url
        self._auth_token = auth_token

    def list_tools(self) -> MCPListToolsResponse:
        """
        Return a validated list of tools. Stub implementation returns empty list.
        Real implementation will call MCP server and validate response via MCPListToolsResponse.
        """
        return MCPListToolsResponse(tools=[])
