"""Behavioral tests for updating maid_generate_stubs to use working directory from MCP roots (Task 033).

These tests verify the expected artifacts defined in the manifest:
- maid_generate_stubs(): Updated async function that uses get_working_directory()

Tests follow MAID behavioral testing pattern - they USE the artifacts
rather than just checking existence.
"""

import inspect
import pytest


class TestMaidGenerateStubsSignature:
    """Tests for the maid_generate_stubs function signature."""

    def test_maid_generate_stubs_has_ctx_parameter(self):
        """Test that maid_generate_stubs has ctx parameter.

        The manifest specifies:
        - type: function
        - name: maid_generate_stubs
        - args: includes ctx: Context
        """
        from maid_runner_mcp.tools.generate_stubs import maid_generate_stubs

        sig = inspect.signature(maid_generate_stubs)
        params = sig.parameters

        assert "ctx" in params, "maid_generate_stubs should have 'ctx' parameter"

    def test_maid_generate_stubs_ctx_parameter_type(self):
        """Test that ctx parameter has Context type annotation."""
        from maid_runner_mcp.tools.generate_stubs import maid_generate_stubs

        sig = inspect.signature(maid_generate_stubs)
        params = sig.parameters

        ctx_param = params.get("ctx")
        assert ctx_param is not None, "ctx parameter should exist"

        # Check the annotation exists
        assert ctx_param.annotation != inspect.Parameter.empty, "ctx should have type annotation"

    def test_maid_generate_stubs_imports_context(self):
        """Test that generate_stubs.py imports Context from mcp.server.fastmcp."""
        from maid_runner_mcp.tools import generate_stubs

        # Check that Context is available in the module
        assert hasattr(generate_stubs, "Context") or "Context" in dir(
            generate_stubs
        ), "generate_stubs module should import Context"

    def test_maid_generate_stubs_imports_get_working_directory(self):
        """Test that generate_stubs.py imports get_working_directory from utils.roots."""
        import maid_runner_mcp.tools.generate_stubs as generate_stubs_module

        # Check module imports - get_working_directory should be used in the code
        import inspect

        source = inspect.getsource(generate_stubs_module.maid_generate_stubs)
        assert (
            "get_working_directory" in source
        ), "maid_generate_stubs should call get_working_directory"


@pytest.mark.asyncio
class TestMaidGenerateStubsUsesWorkingDirectory:
    """Tests for maid_generate_stubs using working directory."""

    async def test_maid_generate_stubs_accepts_context_parameter(self):
        """Test that maid_generate_stubs can be called with ctx parameter."""
        from maid_runner_mcp.tools.generate_stubs import maid_generate_stubs
        from unittest.mock import AsyncMock, MagicMock

        # Create a mock context
        mock_ctx = MagicMock()
        mock_session = MagicMock()
        mock_session.list_roots = AsyncMock(
            return_value=MagicMock(roots=[MagicMock(uri="file:///tmp/test")])
        )
        mock_ctx.session = mock_session

        # Call with a nonexistent manifest to trigger quick error path
        # The important part is that it accepts ctx parameter
        result = await maid_generate_stubs(
            manifest_path="nonexistent.json",
            ctx=mock_ctx,
        )

        # Should return a result (even if it's an error)
        assert "success" in result, "Should return GenerateStubsResult"

    async def test_maid_generate_stubs_calls_get_working_directory(self):
        """Test that maid_generate_stubs calls get_working_directory with ctx."""
        from maid_runner_mcp.tools.generate_stubs import maid_generate_stubs
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
            "maid_runner_mcp.tools.generate_stubs.get_working_directory", new_callable=AsyncMock
        ) as mock_get_wd:
            mock_get_wd.return_value = "/tmp/test"

            # Call maid_generate_stubs
            await maid_generate_stubs(
                manifest_path="nonexistent.json",
                ctx=mock_ctx,
            )

            # Verify get_working_directory was called with ctx
            mock_get_wd.assert_called_once_with(mock_ctx)
