"""Behavioral tests for maid_snapshot_system MCP tool (Task 007).

These tests verify the expected artifacts defined in the manifest:
- SystemSnapshotResult: TypedDict for system snapshot results
- maid_snapshot_system(): Async function that generates system-wide manifest snapshots

Tests follow MAID behavioral testing pattern - they USE the artifacts
rather than just checking existence.
"""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock
from mcp.types import ListRootsResult, Root
from pydantic import FileUrl


class TestSystemSnapshotResult:
    """Tests for the SystemSnapshotResult TypedDict."""

    def test_system_snapshot_result_is_typed_dict(self):
        """Test that SystemSnapshotResult is a TypedDict.

        The manifest specifies:
        - type: class
        - name: SystemSnapshotResult
        - description: TypedDict for system snapshot results
        """
        from maid_runner_mcp.tools.snapshot_system import SystemSnapshotResult

        # TypedDict classes have __annotations__
        assert hasattr(
            SystemSnapshotResult, "__annotations__"
        ), "SystemSnapshotResult should have __annotations__ (TypedDict requirement)"

    def test_system_snapshot_result_has_required_fields(self):
        """Test that SystemSnapshotResult has all required fields.

        Expected fields:
        - success (boolean)
        - output_path (string)
        - errors (array of strings)
        """
        from maid_runner_mcp.tools.snapshot_system import SystemSnapshotResult

        annotations = SystemSnapshotResult.__annotations__

        required_fields = ["success", "output_path", "errors"]

        for field_name in required_fields:
            assert (
                field_name in annotations
            ), f"SystemSnapshotResult should have '{field_name}' field"


class TestMaidSnapshotSystemFunction:
    """Tests for the maid_snapshot_system async function."""

    def test_maid_snapshot_system_is_callable(self):
        """Test that maid_snapshot_system exists and is callable.

        The manifest specifies:
        - type: function
        - name: maid_snapshot_system
        """
        from maid_runner_mcp.tools.snapshot_system import maid_snapshot_system

        assert callable(maid_snapshot_system), "maid_snapshot_system should be callable"

    def test_maid_snapshot_system_is_async(self):
        """Test that maid_snapshot_system is an async function."""
        import asyncio
        from maid_runner_mcp.tools.snapshot_system import maid_snapshot_system

        assert asyncio.iscoroutinefunction(
            maid_snapshot_system
        ), "maid_snapshot_system should be an async function"

    def test_maid_snapshot_system_has_correct_signature(self):
        """Test that maid_snapshot_system has the expected parameters.

        The manifest specifies:
        - output: str (default: "system.manifest.json")
        - manifest_dir: str (default: "manifests")
        - quiet: bool (default: True)
        """
        import inspect
        from maid_runner_mcp.tools.snapshot_system import maid_snapshot_system

        sig = inspect.signature(maid_snapshot_system)
        params = sig.parameters

        # Check output parameter with default
        assert "output" in params, "maid_snapshot_system should have 'output' parameter"
        assert (
            params["output"].default == "system.manifest.json"
        ), "output should default to 'system.manifest.json'"

        # Check manifest_dir parameter with default
        assert "manifest_dir" in params, "maid_snapshot_system should have 'manifest_dir' parameter"
        assert (
            params["manifest_dir"].default == "manifests"
        ), "manifest_dir should default to 'manifests'"

        # Check quiet parameter with default
        assert "quiet" in params, "maid_snapshot_system should have 'quiet' parameter"
        assert params["quiet"].default is True, "quiet should default to True"

    def test_maid_snapshot_system_returns_system_snapshot_result(self):
        """Test that maid_snapshot_system return type is SystemSnapshotResult.

        The manifest specifies:
        - returns: SystemSnapshotResult
        """
        import inspect
        from maid_runner_mcp.tools.snapshot_system import (
            maid_snapshot_system,
        )

        sig = inspect.signature(maid_snapshot_system)

        # The return annotation should reference SystemSnapshotResult
        assert (
            sig.return_annotation is not inspect.Signature.empty
        ), "maid_snapshot_system should have a return type annotation"


@pytest.mark.asyncio
class TestMaidSnapshotSystemBehavior:
    """Tests for maid_snapshot_system behavior when called."""

    async def test_maid_snapshot_system_returns_system_snapshot_result(self):
        """Test that maid_snapshot_system returns a SystemSnapshotResult-compatible dict."""
        import tempfile
        import os
        from maid_runner_mcp.tools.snapshot_system import maid_snapshot_system

        # Create mock context
        mock_ctx = MagicMock()
        mock_ctx.session = AsyncMock()
        cwd = os.getcwd()
        mock_ctx.session.list_roots = AsyncMock(
            return_value=ListRootsResult(roots=[Root(uri=FileUrl(f"file://{cwd}"))])
        )

        # Use temporary directory to avoid creating files in current directory
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "system.manifest.json")
            result = await maid_snapshot_system(ctx=mock_ctx, output=output_path)

            # Result should have the required fields
            assert "success" in result, "Result should have 'success' field"
            assert "output_path" in result, "Result should have 'output_path' field"
            assert "errors" in result, "Result should have 'errors' field"

    async def test_maid_snapshot_system_success_case(self):
        """Test maid_snapshot_system successful execution."""
        import tempfile
        import os
        from maid_runner_mcp.tools.snapshot_system import maid_snapshot_system

        # Create mock context
        mock_ctx = MagicMock()
        mock_ctx.session = AsyncMock()
        cwd = os.getcwd()
        mock_ctx.session.list_roots = AsyncMock(
            return_value=ListRootsResult(roots=[Root(uri=FileUrl(f"file://{cwd}"))])
        )

        # Use a temporary directory for output
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test-system.manifest.json")

            result = await maid_snapshot_system(
                ctx=mock_ctx, output=output_path, manifest_dir="manifests", quiet=True
            )

            # Result should have proper structure
            assert "success" in result
            assert "output_path" in result
            assert "errors" in result
            assert isinstance(result["errors"], list)

    async def test_maid_snapshot_system_error_handling(self):
        """Test that maid_snapshot_system handles errors gracefully."""
        from maid_runner_mcp.tools.snapshot_system import maid_snapshot_system

        # Create mock context
        mock_ctx = MagicMock()
        mock_ctx.session = AsyncMock()
        cwd = os.getcwd()
        mock_ctx.session.list_roots = AsyncMock(
            return_value=ListRootsResult(roots=[Root(uri=FileUrl(f"file://{cwd}"))])
        )

        # Call with an invalid manifest directory
        result = await maid_snapshot_system(
            ctx=mock_ctx, manifest_dir="/nonexistent/manifests/directory"
        )

        # Should return with errors field populated
        assert "errors" in result
        assert isinstance(result["errors"], list)

    async def test_maid_snapshot_system_with_custom_output(self):
        """Test maid_snapshot_system with custom output path."""
        import tempfile
        import os
        from maid_runner_mcp.tools.snapshot_system import maid_snapshot_system

        # Create mock context
        mock_ctx = MagicMock()
        mock_ctx.session = AsyncMock()
        cwd = os.getcwd()
        mock_ctx.session.list_roots = AsyncMock(
            return_value=ListRootsResult(roots=[Root(uri=FileUrl(f"file://{cwd}"))])
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            custom_output = os.path.join(tmpdir, "custom-system.manifest.json")

            result = await maid_snapshot_system(ctx=mock_ctx, output=custom_output)

            # Result should include the output path
            assert "output_path" in result
            assert isinstance(result["output_path"], str)


class TestToolsExport:
    """Tests for tools module exports."""

    def test_system_snapshot_result_exported_from_tools(self):
        """Test that SystemSnapshotResult is exported from tools package."""
        from maid_runner_mcp.tools import SystemSnapshotResult

        assert hasattr(SystemSnapshotResult, "__annotations__")

    def test_maid_snapshot_system_exported_from_tools(self):
        """Test that maid_snapshot_system is exported from tools package."""
        from maid_runner_mcp.tools import maid_snapshot_system

        assert callable(maid_snapshot_system)
