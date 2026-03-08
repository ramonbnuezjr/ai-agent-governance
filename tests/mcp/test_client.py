"""Tests for MCP client stub."""

import pytest

from src.mcp.client import MCPClientStub, MCPListToolsResponse, MCPToolSchema


def test_mcp_client_stub_list_tools_returns_validated_response() -> None:
    """list_tools() returns a Pydantic-validated MCPListToolsResponse."""
    stub = MCPClientStub(server_url=None, auth_token=None)
    response = stub.list_tools()
    assert isinstance(response, MCPListToolsResponse)
    assert response.tools == []


def test_mcp_tool_schema_validates() -> None:
    """MCPToolSchema accepts valid tool shape."""
    tool = MCPToolSchema(name="run_shell", description="Run a command", input_schema={"type": "object"})
    assert tool.name == "run_shell"
    assert tool.description == "Run a command"
    assert tool.input_schema == {"type": "object"}


def test_mcp_list_tools_response_validates_list() -> None:
    """MCPListToolsResponse validates list of tools."""
    response = MCPListToolsResponse(
        tools=[
            MCPToolSchema(name="a", description="A"),
            MCPToolSchema(name="b"),
        ]
    )
    assert len(response.tools) == 2
    assert response.tools[0].name == "a"
    assert response.tools[1].name == "b"
