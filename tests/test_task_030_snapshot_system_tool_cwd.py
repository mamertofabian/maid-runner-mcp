"""Behavioral tests for updating maid_snapshot_system to use working directory from MCP roots (Task 030).

These tests verify the expected artifacts defined in the manifest:
- maid_snapshot_system(): Updated async function that uses get_working_directory()

Tests follow MAID behavioral testing pattern - they USE the artifacts
rather than just checking existence.
"""

import inspect
import pytest


class TestMaidSnapshotSystemSignature:
    """Tests for the maid_snapshot_system function signature."""

    def test_maid_snapshot_system_has_ctx_parameter(self):
        """Test that maid_snapshot_system has ctx parameter.

        The manifest specifies:
        - type: function
        - name: maid_snapshot_system
        - args: includes ctx: Context
        """
        from maid_runner_mcp.tools.snapshot_system import maid_snapshot_system

        sig = inspect.signature(maid_snapshot_system)
        params = sig.parameters

        assert "ctx" in params, "maid_snapshot_system should have 'ctx' parameter"

    def test_maid_snapshot_system_ctx_parameter_type(self):
        """Test that ctx parameter has Context type annotation."""
        from maid_runner_mcp.tools.snapshot_system import maid_snapshot_system

        sig = inspect.signature(maid_snapshot_system)
        params = sig.parameters

        ctx_param = params.get("ctx")
        assert ctx_param is not None, "ctx parameter should exist"

        # Check the annotation exists
        assert ctx_param.annotation != inspect.Parameter.empty, "ctx should have type annotation"

    def test_maid_snapshot_system_imports_context(self):
        """Test that snapshot_system.py imports Context from mcp.server.fastmcp."""
        from maid_runner_mcp.tools import snapshot_system

        # Check that Context is available in the module
        assert hasattr(snapshot_system, "Context") or "Context" in dir(
            snapshot_system
        ), "snapshot_system module should import Context"

    def test_maid_snapshot_system_imports_get_working_directory(self):
        """Test that snapshot_system.py imports get_working_directory from utils.roots."""
        import maid_runner_mcp.tools.snapshot_system as snapshot_system_module

        # Check module imports - get_working_directory should be used in the code
        import inspect

        source = inspect.getsource(snapshot_system_module.maid_snapshot_system)
        assert (
            "get_working_directory" in source
        ), "maid_snapshot_system should call get_working_directory"


@pytest.mark.asyncio
class TestMaidSnapshotSystemUsesWorkingDirectory:
    """Tests for maid_snapshot_system using working directory."""

    async def test_maid_snapshot_system_accepts_context_parameter(self):
        """Test that maid_snapshot_system can be called with ctx parameter."""
        from maid_runner_mcp.tools.snapshot_system import maid_snapshot_system
        from unittest.mock import AsyncMock, MagicMock, patch

        # Create a mock context
        mock_ctx = MagicMock()
        mock_session = MagicMock()
        mock_session.list_roots = AsyncMock(
            return_value=MagicMock(roots=[MagicMock(uri="file:///tmp/test")])
        )
        mock_ctx.session = mock_session

        # Mock subprocess to avoid actual execution
        with patch("maid_runner_mcp.tools.snapshot_system.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1,  # Fail to avoid actual work
                stderr="Test error",
                stdout="",
            )

            # Call with ctx parameter
            result = await maid_snapshot_system(
                output="test.json",
                ctx=mock_ctx,
            )

            # Should return a result (even if it's an error)
            assert "success" in result, "Should return SystemSnapshotResult"

    async def test_maid_snapshot_system_calls_get_working_directory(self):
        """Test that maid_snapshot_system calls get_working_directory with ctx."""
        from maid_runner_mcp.tools.snapshot_system import maid_snapshot_system
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
            "maid_runner_mcp.tools.snapshot_system.get_working_directory", new_callable=AsyncMock
        ) as mock_get_wd:
            mock_get_wd.return_value = "/tmp/test"

            # Mock subprocess to avoid actual execution
            with patch("maid_runner_mcp.tools.snapshot_system.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=1,
                    stderr="Test error",
                    stdout="",
                )

                # Call maid_snapshot_system
                result = await maid_snapshot_system(
                    output="test.json",
                    ctx=mock_ctx,
                )

                # Verify get_working_directory was called with ctx
                mock_get_wd.assert_called_once_with(mock_ctx)
