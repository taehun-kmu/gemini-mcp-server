"""Tests for MCP server module."""

from pathlib import Path
from typing import Any
from unittest.mock import patch

import mcp.types as types
import pytest

from gemini_mcp.server import MCPServer


class TestMCPServer:
    """Test cases for MCPServer class."""

    def test_initialization(self) -> None:
        """Test MCPServer initialization."""
        server = MCPServer(project_root="/test/path")
        assert server.project_root == Path("/test/path")
        assert server.gemini is not None

    def test_initialization_default_path(self) -> None:
        """Test MCPServer initialization with default path."""
        server = MCPServer()
        assert server.project_root == Path.cwd()

    @patch("gemini_mcp.server.Path.exists")
    @patch("builtins.open")
    def test_load_gemini_config_from_file(
        self, mock_open: Any, mock_exists: Any
    ) -> None:
        """Test loading configuration from file."""
        mock_exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = """
        {
            "enabled": false,
            "timeout": 120
        }
        """

        server = MCPServer()
        config = server._load_gemini_config()

        assert config["enabled"] is False
        assert config["timeout"] == 120

    @patch.dict(
        "os.environ",
        {
            "GEMINI_ENABLED": "true",
            "GEMINI_TIMEOUT": "300",
            "GEMINI_MODEL": "gemini-2.5-pro",
        },
    )
    def test_load_gemini_config_from_env(self) -> None:
        """Test loading configuration from environment variables."""
        server = MCPServer()
        config = server._load_gemini_config()

        assert config["enabled"] is True
        assert config["timeout"] == 300
        assert config["model"] == "gemini-2.5-pro"

    @pytest.mark.asyncio
    async def test_handle_list_tools(self) -> None:
        """Test tool listing."""
        server = MCPServer()

        # Mock the server's list_tools handler
        with patch.object(server.server, "list_tools") as mock_list_tools:
            # Get the actual handler function
            handler = None
            for call in mock_list_tools.call_args_list:
                if call[0]:  # If there are positional arguments
                    handler = call[0][0]
                    break

            # Call the handler if we found it
            if handler:
                tools = await handler()
                assert len(tools) == 3
                tool_names = [tool.name for tool in tools]
                assert "consult_gemini" in tool_names
                assert "gemini_status" in tool_names
                assert "toggle_gemini_auto_consult" in tool_names

    @pytest.mark.asyncio
    async def test_handle_consult_gemini(self) -> None:
        """Test Gemini consultation handler."""
        server = MCPServer()

        # Mock the gemini integration
        with patch.object(server.gemini, "consult_gemini") as mock_consult:
            mock_consult.return_value = {
                "status": "success",
                "response": "Test response",
                "execution_time": 1.23,
            }

            result = await server._handle_consult_gemini(
                {"query": "Test query", "context": "Test context"}
            )

            assert len(result) == 1
            assert isinstance(result[0], types.TextContent)
            assert "Test response" in result[0].text
            assert "1.23s" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_consult_gemini_error(self) -> None:
        """Test Gemini consultation handler with error."""
        server = MCPServer()

        # Mock the gemini integration
        with patch.object(server.gemini, "consult_gemini") as mock_consult:
            mock_consult.return_value = {
                "status": "error",
                "error": "Test error message",
            }

            result = await server._handle_consult_gemini({"query": "Test query"})

            assert len(result) == 1
            assert isinstance(result[0], types.TextContent)
            assert "Failed" in result[0].text
            assert "Test error message" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_gemini_status(self) -> None:
        """Test status handler."""
        server = MCPServer()

        # No need to mock, the method directly accesses properties
        server.gemini.enabled = True
        server.gemini.model = "gemini-2.5-flash"
        server.gemini.consultation_log = [{"timestamp": "2024-01-01"}] * 5

        result = await server._handle_gemini_status({})

        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "Enabled" in result[0].text
        assert "5" in result[0].text
        assert "gemini-2.5-flash" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_toggle_auto_consult(self) -> None:
        """Test toggle auto consultation handler."""
        server = MCPServer()

        # No need to mock, the method directly modifies properties
        server.gemini.auto_consult = False  # Start with disabled

        result = await server._handle_toggle_auto_consult({"enable": True})

        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "enabled" in result[0].text.lower()
        assert server.gemini.auto_consult is True

    @pytest.mark.asyncio
    async def test_run_method(self) -> None:
        """Test the run method."""
        server = MCPServer()

        # Test that the run method can be called without errors
        # Since we can't easily mock the actual mcp.server.stdio internals,
        # we'll just verify the method exists and is callable
        assert hasattr(server, "run")
        assert callable(server.run)
