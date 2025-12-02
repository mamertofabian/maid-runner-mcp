"""Behavioral tests for updating get_system_snapshot to use working directory from MCP roots (Task 036).

These tests verify the expected artifacts defined in the manifest:
- get_system_snapshot(): Updated async function that uses get_working_directory()

Tests follow MAID behavioral testing pattern - they USE the artifacts
rather than just checking existence.
"""

import inspect
import pytest


class TestGetSystemSnapshotSignature:
    """Tests for the get_system_snapshot function signature."""

    def test_get_system_snapshot_has_ctx_parameter(self):
        """Test that get_system_snapshot has ctx parameter.

        The manifest specifies:
        - type: function
        - name: get_system_snapshot
        - args: includes ctx: Context
        """
        from maid_runner_mcp.resources.snapshot import get_system_snapshot

        sig = inspect.signature(get_system_snapshot)
        params = sig.parameters

        assert "ctx" in params, "get_system_snapshot should have 'ctx' parameter"

    def test_get_system_snapshot_ctx_parameter_type(self):
        """Test that ctx parameter has Context type annotation."""
        from maid_runner_mcp.resources.snapshot import get_system_snapshot

        sig = inspect.signature(get_system_snapshot)
        params = sig.parameters

        ctx_param = params.get("ctx")
        assert ctx_param is not None, "ctx parameter should exist"

        # Check the annotation exists
        assert ctx_param.annotation != inspect.Parameter.empty, "ctx should have type annotation"

    def test_get_system_snapshot_imports_context(self):
        """Test that snapshot.py imports Context from mcp.server.fastmcp."""
        from maid_runner_mcp.resources import snapshot

        # Check that Context is available in the module
        assert hasattr(snapshot, "Context") or "Context" in dir(
            snapshot
        ), "snapshot module should import Context"

    def test_get_system_snapshot_imports_get_working_directory(self):
        """Test that snapshot.py imports get_working_directory from utils.roots."""
        import maid_runner_mcp.resources.snapshot as snapshot_module

        # Check module imports - get_working_directory should be used in the code
        import inspect

        source = inspect.getsource(snapshot_module.get_system_snapshot)
        assert (
            "get_working_directory" in source
        ), "get_system_snapshot should call get_working_directory"


@pytest.mark.asyncio
class TestGetSystemSnapshotUsesWorkingDirectory:
    """Tests for get_system_snapshot using working directory."""

    async def test_get_system_snapshot_accepts_context_parameter(self):
        """Test that get_system_snapshot can be called with ctx parameter."""
        from maid_runner_mcp.resources.snapshot import get_system_snapshot
        from unittest.mock import AsyncMock, MagicMock, patch

        # Create a mock context
        mock_ctx = MagicMock()
        mock_session = MagicMock()
        mock_session.list_roots = AsyncMock(
            return_value=MagicMock(roots=[MagicMock(uri="file:///tmp/test")])
        )
        mock_ctx.session = mock_session

        # Patch subprocess to avoid actual command execution
        with patch("maid_runner_mcp.resources.snapshot.asyncio.get_event_loop") as mock_loop:
            mock_executor = AsyncMock()
            mock_executor.return_value = MagicMock(returncode=1, stderr="test error", stdout="")
            mock_loop.return_value.run_in_executor = mock_executor

            # Call with ctx parameter - should accept it without error
            try:
                result = await get_system_snapshot(ctx=mock_ctx)
            except RuntimeError as e:
                # Expected to fail since we're mocking, but it should have accepted ctx
                assert (
                    "ctx" not in str(e).lower() or "parameter" not in str(e).lower()
                ), "Should not fail due to ctx parameter issue"

    async def test_get_system_snapshot_calls_get_working_directory(self):
        """Test that get_system_snapshot calls get_working_directory with ctx."""
        from maid_runner_mcp.resources.snapshot import get_system_snapshot
        from unittest.mock import AsyncMock, MagicMock, patch

        # Create a mock context
        mock_ctx = MagicMock()
        mock_session = MagicMock()
        mock_session.list_roots = AsyncMock(
            return_value=MagicMock(roots=[MagicMock(uri="file:///tmp/test")])
        )
        mock_ctx.session = mock_session

        # Patch get_working_directory to track if it was called
        with patch(
            "maid_runner_mcp.resources.snapshot.get_working_directory", new_callable=AsyncMock
        ) as mock_get_wd:
            mock_get_wd.return_value = "/tmp/test"

            # Patch subprocess to avoid actual command execution
            with patch("maid_runner_mcp.resources.snapshot.asyncio.get_event_loop") as mock_loop:
                mock_executor = AsyncMock()
                mock_executor.return_value = MagicMock(returncode=1, stderr="test error", stdout="")
                mock_loop.return_value.run_in_executor = mock_executor

                # Call get_system_snapshot
                try:
                    result = await get_system_snapshot(ctx=mock_ctx)
                except RuntimeError:
                    pass  # Expected to fail with mocked subprocess

                # Verify get_working_directory was called with ctx
                mock_get_wd.assert_called_once_with(mock_ctx)
