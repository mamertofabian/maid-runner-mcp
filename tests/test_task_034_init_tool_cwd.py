"""Behavioral tests for updating maid_init to use working directory from MCP roots (Task 034).

These tests verify the expected artifacts defined in the manifest:
- maid_init(): Updated async function that uses get_working_directory()

Tests follow MAID behavioral testing pattern - they USE the artifacts
rather than just checking existence.
"""

import inspect
import pytest


class TestMaidInitSignature:
    """Tests for the maid_init function signature."""

    def test_maid_init_has_ctx_parameter(self):
        """Test that maid_init has ctx parameter.

        The manifest specifies:
        - type: function
        - name: maid_init
        - args: includes ctx: Context
        """
        from maid_runner_mcp.tools.init import maid_init

        sig = inspect.signature(maid_init)
        params = sig.parameters

        assert "ctx" in params, "maid_init should have 'ctx' parameter"

    def test_maid_init_ctx_parameter_type(self):
        """Test that ctx parameter has Context type annotation."""
        from maid_runner_mcp.tools.init import maid_init

        sig = inspect.signature(maid_init)
        params = sig.parameters

        ctx_param = params.get("ctx")
        assert ctx_param is not None, "ctx parameter should exist"

        # Check the annotation exists
        assert ctx_param.annotation != inspect.Parameter.empty, "ctx should have type annotation"

    def test_maid_init_imports_context(self):
        """Test that init.py imports Context from mcp.server.fastmcp."""
        from maid_runner_mcp.tools import init

        # Check that Context is available in the module
        assert hasattr(init, "Context") or "Context" in dir(
            init
        ), "init module should import Context"

    def test_maid_init_imports_get_working_directory(self):
        """Test that init.py imports get_working_directory from utils.roots."""
        import maid_runner_mcp.tools.init as init_module

        # Check module imports - get_working_directory should be used in the code
        import inspect

        source = inspect.getsource(init_module.maid_init)
        assert "get_working_directory" in source, "maid_init should call get_working_directory"


@pytest.mark.asyncio
class TestMaidInitUsesWorkingDirectory:
    """Tests for maid_init using working directory."""

    async def test_maid_init_accepts_context_parameter(self):
        """Test that maid_init can be called with ctx parameter."""
        from maid_runner_mcp.tools.init import maid_init
        from unittest.mock import AsyncMock, MagicMock, patch

        # Create a mock context
        mock_ctx = MagicMock()
        mock_session = MagicMock()
        mock_session.list_roots = AsyncMock(
            return_value=MagicMock(roots=[MagicMock(uri="file:///tmp/test")])
        )
        mock_ctx.session = mock_session

        # Mock subprocess to avoid actually running maid init
        with patch("maid_runner_mcp.tools.init.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1,  # Fail intentionally
                stderr="Error: test",
                stdout="",
            )

            # Call with ctx parameter
            result = await maid_init(
                target_dir="/tmp/test",
                force=False,
                ctx=mock_ctx,
            )

            # Should return a result (even if it's an error)
            assert "success" in result, "Should return InitResult"

    async def test_maid_init_calls_get_working_directory(self):
        """Test that maid_init calls get_working_directory with ctx."""
        from maid_runner_mcp.tools.init import maid_init
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
            "maid_runner_mcp.tools.init.get_working_directory", new_callable=AsyncMock
        ) as mock_get_wd:
            mock_get_wd.return_value = "/tmp/test"

            # Mock subprocess to avoid actually running maid init
            with patch("maid_runner_mcp.tools.init.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=1,  # Fail intentionally
                    stderr="Error: test",
                    stdout="",
                )

                # Call maid_init
                await maid_init(
                    target_dir=".",
                    force=False,
                    ctx=mock_ctx,
                )

                # Verify get_working_directory was called with ctx
                mock_get_wd.assert_called_once_with(mock_ctx)
