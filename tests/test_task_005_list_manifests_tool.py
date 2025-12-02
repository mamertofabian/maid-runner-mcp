"""Behavioral tests for maid_list_manifests MCP tool (Task 005).

These tests verify the expected artifacts defined in the manifest:
- ListManifestsResult: TypedDict for list manifests results
- maid_list_manifests(): Async function that lists manifests referencing a file

Tests follow MAID behavioral testing pattern - they USE the artifacts
rather than just checking existence.
"""

import pytest


class TestListManifestsResult:
    """Tests for the ListManifestsResult TypedDict."""

    def test_list_manifests_result_is_typed_dict(self):
        """Test that ListManifestsResult is a TypedDict.

        The manifest specifies:
        - type: class
        - name: ListManifestsResult
        - description: TypedDict for list manifests results
        """
        from maid_runner_mcp.tools.manifests import ListManifestsResult

        # TypedDict classes have __annotations__
        assert hasattr(
            ListManifestsResult, "__annotations__"
        ), "ListManifestsResult should have __annotations__ (TypedDict requirement)"

    def test_list_manifests_result_has_required_fields(self):
        """Test that ListManifestsResult has all required fields.

        Per Issue #89, the output schema requires:
        - file_path (string)
        - total_manifests (integer)
        - created_by (array of strings)
        - edited_by (array of strings)
        - read_by (array of strings)
        """
        from maid_runner_mcp.tools.manifests import ListManifestsResult

        annotations = ListManifestsResult.__annotations__

        required_fields = [
            "file_path",
            "total_manifests",
            "created_by",
            "edited_by",
            "read_by",
        ]

        for field_name in required_fields:
            assert (
                field_name in annotations
            ), f"ListManifestsResult should have '{field_name}' field"


class TestMaidListManifestsFunction:
    """Tests for the maid_list_manifests async function."""

    def test_maid_list_manifests_is_callable(self):
        """Test that maid_list_manifests exists and is callable.

        The manifest specifies:
        - type: function
        - name: maid_list_manifests
        """
        from maid_runner_mcp.tools.manifests import maid_list_manifests

        assert callable(maid_list_manifests), "maid_list_manifests should be callable"

    def test_maid_list_manifests_is_async(self):
        """Test that maid_list_manifests is an async function."""
        import asyncio
        from maid_runner_mcp.tools.manifests import maid_list_manifests

        assert asyncio.iscoroutinefunction(
            maid_list_manifests
        ), "maid_list_manifests should be an async function"

    def test_maid_list_manifests_has_correct_signature(self):
        """Test that maid_list_manifests has the expected parameters.

        The manifest specifies:
        - file_path: str (required)
        - manifest_dir: str (default: "manifests")
        """
        import inspect
        from maid_runner_mcp.tools.manifests import maid_list_manifests

        sig = inspect.signature(maid_list_manifests)
        params = sig.parameters

        # Check required parameter
        assert "file_path" in params, "maid_list_manifests should have 'file_path' parameter"
        assert (
            params["file_path"].default is inspect.Parameter.empty
        ), "file_path should be a required parameter (no default)"

        # Check optional parameter with default
        assert "manifest_dir" in params, "maid_list_manifests should have 'manifest_dir' parameter"
        assert (
            params["manifest_dir"].default == "manifests"
        ), "manifest_dir should default to 'manifests'"


@pytest.mark.asyncio
class TestMaidListManifestsBehavior:
    """Tests for maid_list_manifests behavior when called."""

    async def test_maid_list_manifests_returns_list_manifests_result(self):
        """Test that maid_list_manifests returns a ListManifestsResult-compatible dict."""
        from unittest.mock import AsyncMock, MagicMock
        from mcp.types import ListRootsResult, Root
        from pydantic import FileUrl
        from maid_runner_mcp.tools.manifests import maid_list_manifests

        # Create mock context
        mock_ctx = MagicMock()
        mock_ctx.session = AsyncMock()
        mock_ctx.session.list_roots = AsyncMock(
            return_value=ListRootsResult(roots=[Root(uri=FileUrl("file:///home/user/project"))])
        )

        # Call with an existing file that is referenced by manifests
        result = await maid_list_manifests(file_path="src/maid_runner_mcp/server.py", ctx=mock_ctx)

        # Result should have all required fields
        assert "file_path" in result, "Result should have 'file_path' field"
        assert "total_manifests" in result, "Result should have 'total_manifests' field"
        assert "created_by" in result, "Result should have 'created_by' field"
        assert "edited_by" in result, "Result should have 'edited_by' field"
        assert "read_by" in result, "Result should have 'read_by' field"

    async def test_maid_list_manifests_returns_correct_types(self):
        """Test that maid_list_manifests returns correct field types."""
        from unittest.mock import AsyncMock, MagicMock
        from mcp.types import ListRootsResult, Root
        from pydantic import FileUrl
        from maid_runner_mcp.tools.manifests import maid_list_manifests

        # Create mock context
        mock_ctx = MagicMock()
        mock_ctx.session = AsyncMock()
        mock_ctx.session.list_roots = AsyncMock(
            return_value=ListRootsResult(roots=[Root(uri=FileUrl("file:///home/user/project"))])
        )

        result = await maid_list_manifests(file_path="src/maid_runner_mcp/server.py", ctx=mock_ctx)

        # Verify types match the output schema from Issue #89
        assert isinstance(result["file_path"], str), "file_path should be a string"
        assert isinstance(result["total_manifests"], int), "total_manifests should be an integer"
        assert isinstance(result["created_by"], list), "created_by should be a list"
        assert isinstance(result["edited_by"], list), "edited_by should be a list"
        assert isinstance(result["read_by"], list), "read_by should be a list"

    async def test_maid_list_manifests_finds_manifests_for_server(self):
        """Test that maid_list_manifests finds manifests for server.py."""
        import os
        from unittest.mock import AsyncMock, MagicMock
        from mcp.types import ListRootsResult, Root
        from pydantic import FileUrl
        from maid_runner_mcp.tools.manifests import maid_list_manifests

        # Create mock context with current directory
        mock_ctx = MagicMock()
        mock_ctx.session = AsyncMock()
        cwd = os.getcwd()
        mock_ctx.session.list_roots = AsyncMock(
            return_value=ListRootsResult(roots=[Root(uri=FileUrl(f"file://{cwd}"))])
        )

        result = await maid_list_manifests(file_path="src/maid_runner_mcp/server.py", ctx=mock_ctx)

        # server.py should be referenced by at least one manifest
        assert (
            result["total_manifests"] > 0
        ), "server.py should be referenced by at least one manifest"

        # server.py was created by task-001
        assert (
            len(result["created_by"]) > 0
        ), "server.py should have at least one created_by manifest"

    async def test_maid_list_manifests_with_unreferenced_file(self):
        """Test that maid_list_manifests handles files not in any manifest."""
        from unittest.mock import AsyncMock, MagicMock
        from mcp.types import ListRootsResult, Root
        from pydantic import FileUrl
        from maid_runner_mcp.tools.manifests import maid_list_manifests

        # Create mock context
        mock_ctx = MagicMock()
        mock_ctx.session = AsyncMock()
        mock_ctx.session.list_roots = AsyncMock(
            return_value=ListRootsResult(roots=[Root(uri=FileUrl("file:///home/user/project"))])
        )

        # Use a file that is not in any manifest (LICENSE is not tracked)
        result = await maid_list_manifests(file_path="LICENSE", ctx=mock_ctx)

        # Should return a valid result with empty lists
        assert result["total_manifests"] == 0, "LICENSE should not be in any manifest"
        assert result["created_by"] == [], "created_by should be empty"
        assert result["edited_by"] == [], "edited_by should be empty"
        assert result["read_by"] == [], "read_by should be empty"

    async def test_maid_list_manifests_custom_manifest_dir(self):
        """Test that maid_list_manifests accepts custom manifest_dir."""
        from unittest.mock import AsyncMock, MagicMock
        from mcp.types import ListRootsResult, Root
        from pydantic import FileUrl
        from maid_runner_mcp.tools.manifests import maid_list_manifests

        # Create mock context
        mock_ctx = MagicMock()
        mock_ctx.session = AsyncMock()
        mock_ctx.session.list_roots = AsyncMock(
            return_value=ListRootsResult(roots=[Root(uri=FileUrl("file:///home/user/project"))])
        )

        # Use default manifest dir
        result = await maid_list_manifests(
            file_path="src/maid_runner_mcp/server.py", ctx=mock_ctx, manifest_dir="manifests"
        )

        # Should work with explicit manifest_dir
        assert "file_path" in result
        assert result["file_path"] == "src/maid_runner_mcp/server.py"
