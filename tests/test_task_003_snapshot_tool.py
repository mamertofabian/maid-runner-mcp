"""Behavioral tests for maid_snapshot MCP tool (Task 003).

These tests verify the expected artifacts defined in the manifest:
- SnapshotResult: TypedDict for snapshot results
- maid_snapshot(): Async function that generates manifest snapshots using MAID Runner

Tests follow MAID behavioral testing pattern - they USE the artifacts
rather than just checking existence.
"""

import os
import tempfile

import pytest


class TestSnapshotResult:
    """Tests for the SnapshotResult TypedDict."""

    def test_snapshot_result_is_typed_dict(self):
        """Test that SnapshotResult is a TypedDict.

        The manifest specifies:
        - type: class
        - name: SnapshotResult
        - description: TypedDict for snapshot results
        """
        from maid_runner_mcp.tools.snapshot import SnapshotResult

        # TypedDict classes have __annotations__
        assert hasattr(
            SnapshotResult, "__annotations__"
        ), "SnapshotResult should have __annotations__ (TypedDict requirement)"

    def test_snapshot_result_has_required_fields(self):
        """Test that SnapshotResult has all required fields.

        From Issue #89 spec:
        - success (boolean)
        - manifest_path (string)
        - test_stub_path (string, optional)
        - superseded_manifests (array of strings)
        - errors (array of strings)
        """
        from maid_runner_mcp.tools.snapshot import SnapshotResult

        annotations = SnapshotResult.__annotations__

        required_fields = ["success", "manifest_path", "superseded_manifests", "errors"]

        for field_name in required_fields:
            assert field_name in annotations, f"SnapshotResult should have '{field_name}' field"

    def test_snapshot_result_has_optional_test_stub_path(self):
        """Test that SnapshotResult has optional test_stub_path field."""
        from maid_runner_mcp.tools.snapshot import SnapshotResult

        annotations = SnapshotResult.__annotations__

        assert "test_stub_path" in annotations, "SnapshotResult should have 'test_stub_path' field"


class TestMaidSnapshotFunction:
    """Tests for the maid_snapshot async function."""

    def test_maid_snapshot_is_callable(self):
        """Test that maid_snapshot exists and is callable.

        The manifest specifies:
        - type: function
        - name: maid_snapshot
        """
        from maid_runner_mcp.tools.snapshot import maid_snapshot

        assert callable(maid_snapshot), "maid_snapshot should be callable"

    def test_maid_snapshot_is_async(self):
        """Test that maid_snapshot is an async function."""
        import asyncio
        from maid_runner_mcp.tools.snapshot import maid_snapshot

        assert asyncio.iscoroutinefunction(
            maid_snapshot
        ), "maid_snapshot should be an async function"

    def test_maid_snapshot_has_correct_signature(self):
        """Test that maid_snapshot has the expected parameters.

        The manifest specifies:
        - file_path: str (required)
        - output_dir: str (default: "manifests")
        - force: bool (default: False)
        - skip_test_stub: bool (default: False)
        """
        import inspect
        from maid_runner_mcp.tools.snapshot import maid_snapshot

        sig = inspect.signature(maid_snapshot)
        params = sig.parameters

        # Check required parameter
        assert "file_path" in params, "maid_snapshot should have 'file_path' parameter"
        assert (
            params["file_path"].default is inspect.Parameter.empty
        ), "file_path should be a required parameter (no default)"

        # Check optional parameters with defaults
        assert "output_dir" in params, "maid_snapshot should have 'output_dir' parameter"
        assert (
            params["output_dir"].default == "manifests"
        ), "output_dir should default to 'manifests'"

        assert "force" in params, "maid_snapshot should have 'force' parameter"
        assert params["force"].default is False, "force should default to False"

        assert "skip_test_stub" in params, "maid_snapshot should have 'skip_test_stub' parameter"
        assert params["skip_test_stub"].default is False, "skip_test_stub should default to False"


@pytest.mark.asyncio
class TestMaidSnapshotBehavior:
    """Tests for maid_snapshot behavior when called."""

    async def test_maid_snapshot_returns_snapshot_result(self):
        """Test that maid_snapshot returns a SnapshotResult-compatible dict."""
        from maid_runner_mcp.tools.snapshot import maid_snapshot

        # Call with an invalid path to trigger error handling
        result = await maid_snapshot(file_path="nonexistent.py")

        # Result should have the required fields
        assert "success" in result, "Result should have 'success' field"
        assert "manifest_path" in result, "Result should have 'manifest_path' field"
        assert "test_stub_path" in result, "Result should have 'test_stub_path' field"
        assert "superseded_manifests" in result, "Result should have 'superseded_manifests' field"
        assert "errors" in result, "Result should have 'errors' field"

    async def test_maid_snapshot_error_handling(self):
        """Test that maid_snapshot handles errors gracefully."""
        from maid_runner_mcp.tools.snapshot import maid_snapshot

        # Call with a nonexistent file
        result = await maid_snapshot(file_path="nonexistent.py")

        # Should return success=False with errors
        assert result["success"] is False, "Should return success=False for invalid file"
        assert isinstance(result["errors"], list), "errors should be a list"
        assert len(result["errors"]) > 0, "Should have at least one error message"

    async def test_maid_snapshot_with_valid_file(self):
        """Test maid_snapshot with a valid source file."""
        from maid_runner_mcp.tools.snapshot import maid_snapshot

        # Use a temporary directory to avoid polluting the manifests folder
        with tempfile.TemporaryDirectory() as tmpdir:
            # Use the existing server.py which should be valid
            result = await maid_snapshot(
                file_path="src/maid_runner_mcp/server.py",
                output_dir=tmpdir,
                skip_test_stub=True,  # Don't create test stub for this test
            )

            # Result should have proper structure regardless of success
            assert "success" in result
            assert "manifest_path" in result
            assert "superseded_manifests" in result
            assert isinstance(result["superseded_manifests"], list)
