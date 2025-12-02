"""Behavioral tests for roots utility module (Task 026).

These tests verify the expected artifacts defined in the manifest:
- get_working_directory(ctx: Context) -> str | None

The function should:
1. Accept a Context object from FastMCP
2. Call ctx.session.list_roots() to get roots
3. Find the first root with a file:// URI
4. Extract and return the path from the URI
5. Return None if no file roots are found or on error

Tests follow MAID behavioral testing pattern - they USE the artifacts
rather than just checking existence. We use mocking to test specific scenarios.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock


class TestGetWorkingDirectorySignature:
    """Tests for get_working_directory function signature and properties."""

    def test_get_working_directory_is_callable(self):
        """Test that get_working_directory exists and is callable.

        The manifest specifies:
        - type: function
        - name: get_working_directory
        """
        from maid_runner_mcp.utils.roots import get_working_directory

        assert callable(get_working_directory), "get_working_directory should be callable"

    def test_get_working_directory_is_async(self):
        """Test that get_working_directory is an async function."""
        import asyncio
        from maid_runner_mcp.utils.roots import get_working_directory

        assert asyncio.iscoroutinefunction(
            get_working_directory
        ), "get_working_directory should be an async function"

    def test_get_working_directory_has_correct_signature(self):
        """Test that get_working_directory has the expected parameter.

        The manifest specifies:
        - args: [{"name": "ctx", "type": "Context"}]
        - returns: str | None
        """
        import inspect
        from maid_runner_mcp.utils.roots import get_working_directory

        sig = inspect.signature(get_working_directory)
        params = sig.parameters

        # Check ctx parameter
        assert "ctx" in params, "get_working_directory should have 'ctx' parameter"


@pytest.mark.asyncio
class TestGetWorkingDirectoryBehavior:
    """Tests for get_working_directory behavior when called.

    Note: We use mocking here to avoid needing a real MCP session
    and to test specific scenarios in isolation.
    """

    async def test_get_working_directory_returns_path_from_file_uri(self):
        """Test that get_working_directory returns path from file:// URI.

        When roots contain a file:// URI, the function should extract
        and return the path component.
        """
        from maid_runner_mcp.utils.roots import get_working_directory
        from mcp.types import ListRootsResult, Root
        from pydantic import FileUrl

        # Create mock context with file:// root
        mock_ctx = MagicMock()
        mock_ctx.session = MagicMock()

        # Create a root with file:// URI
        mock_root = Root(uri=FileUrl("file:///home/user/project"), name="project")
        mock_roots_result = ListRootsResult(roots=[mock_root])

        mock_ctx.session.list_roots = AsyncMock(return_value=mock_roots_result)

        result = await get_working_directory(mock_ctx)

        assert result == "/home/user/project", "Should return extracted path from file:// URI"

    async def test_get_working_directory_returns_none_when_no_roots(self):
        """Test that get_working_directory returns None when no roots available.

        When the session has no roots, the function should return None.
        """
        from maid_runner_mcp.utils.roots import get_working_directory
        from mcp.types import ListRootsResult

        # Create mock context with empty roots
        mock_ctx = MagicMock()
        mock_ctx.session = MagicMock()

        mock_roots_result = ListRootsResult(roots=[])
        mock_ctx.session.list_roots = AsyncMock(return_value=mock_roots_result)

        result = await get_working_directory(mock_ctx)

        assert result is None, "Should return None when no roots available"

    async def test_get_working_directory_returns_none_when_no_file_roots(self):
        """Test that get_working_directory returns None when no file:// roots.

        When roots exist but none have file:// URIs, should return None.
        """
        from maid_runner_mcp.utils.roots import get_working_directory

        # Create mock context with non-file roots
        mock_ctx = MagicMock()
        mock_ctx.session = MagicMock()

        # Create mock root with non-file URI (MCP Root type only accepts file://)
        # We use MagicMock to simulate a root with https:// URI
        mock_root = MagicMock()
        mock_root.uri = "https://example.com/project"

        mock_roots_result = MagicMock()
        mock_roots_result.roots = [mock_root]

        mock_ctx.session.list_roots = AsyncMock(return_value=mock_roots_result)

        result = await get_working_directory(mock_ctx)

        assert result is None, "Should return None when no file:// roots exist"

    async def test_get_working_directory_returns_first_file_root(self):
        """Test that get_working_directory returns the first file:// root.

        When multiple file:// roots exist, should return the first one.
        """
        from maid_runner_mcp.utils.roots import get_working_directory
        from mcp.types import ListRootsResult, Root
        from pydantic import FileUrl

        # Create mock context with multiple file roots
        mock_ctx = MagicMock()
        mock_ctx.session = MagicMock()

        # Create multiple roots with file:// URIs
        mock_root1 = Root(uri=FileUrl("file:///first/path"), name="first")
        mock_root2 = Root(uri=FileUrl("file:///second/path"), name="second")
        mock_roots_result = ListRootsResult(roots=[mock_root1, mock_root2])

        mock_ctx.session.list_roots = AsyncMock(return_value=mock_roots_result)

        result = await get_working_directory(mock_ctx)

        assert result == "/first/path", "Should return path from first file:// root"

    async def test_get_working_directory_handles_exception(self):
        """Test that get_working_directory handles exceptions gracefully.

        When list_roots raises an exception, should return None.
        """
        from maid_runner_mcp.utils.roots import get_working_directory

        # Create mock context that raises exception
        mock_ctx = MagicMock()
        mock_ctx.session = MagicMock()
        mock_ctx.session.list_roots = AsyncMock(side_effect=Exception("Connection failed"))

        result = await get_working_directory(mock_ctx)

        assert result is None, "Should return None when exception occurs"

    async def test_get_working_directory_handles_none_session(self):
        """Test that get_working_directory handles None session gracefully.

        When ctx.session is None, should return None without raising.
        """
        from maid_runner_mcp.utils.roots import get_working_directory

        # Create mock context with None session
        mock_ctx = MagicMock()
        mock_ctx.session = None

        result = await get_working_directory(mock_ctx)

        assert result is None, "Should return None when session is None"

    async def test_get_working_directory_skips_non_file_roots_and_finds_file_root(self):
        """Test that get_working_directory skips non-file roots to find file:// root.

        When roots contain mixed URI types, should find and return the first file:// one.
        """
        from maid_runner_mcp.utils.roots import get_working_directory

        # Create mock context with mixed roots
        mock_ctx = MagicMock()
        mock_ctx.session = MagicMock()

        # Create mock roots with mixed URIs - non-file first, then file
        # MCP Root type only accepts file://, so we use MagicMock for mixed URIs
        mock_root_http = MagicMock()
        mock_root_http.uri = "https://example.com/repo"

        mock_root_file = MagicMock()
        mock_root_file.uri = "file:///local/workspace"

        mock_roots_result = MagicMock()
        mock_roots_result.roots = [mock_root_http, mock_root_file]

        mock_ctx.session.list_roots = AsyncMock(return_value=mock_roots_result)

        result = await get_working_directory(mock_ctx)

        assert result == "/local/workspace", "Should find and return path from file:// root"

    async def test_get_working_directory_handles_windows_file_uri(self):
        """Test that get_working_directory handles Windows-style file URIs.

        Windows file URIs look like: file:///C:/Users/name/project
        """
        from maid_runner_mcp.utils.roots import get_working_directory
        from mcp.types import ListRootsResult, Root
        from pydantic import FileUrl

        # Create mock context with Windows-style file root
        mock_ctx = MagicMock()
        mock_ctx.session = MagicMock()

        # Windows file URI format
        mock_root = Root(uri=FileUrl("file:///C:/Users/name/project"), name="project")
        mock_roots_result = ListRootsResult(roots=[mock_root])

        mock_ctx.session.list_roots = AsyncMock(return_value=mock_roots_result)

        result = await get_working_directory(mock_ctx)

        # Should extract the path correctly for Windows
        assert result is not None, "Should return path from Windows file:// URI"
        assert "project" in result, "Path should contain project directory"
