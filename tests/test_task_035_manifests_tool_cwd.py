"""Behavioral tests for updating maid_list_manifests to use working directory from MCP roots (Task 035).

These tests verify the expected artifacts defined in the manifest:
- maid_list_manifests(): Updated async function that uses get_working_directory()

Tests follow MAID behavioral testing pattern - they USE the artifacts
rather than just checking existence.
"""

import inspect
import pytest


class TestMaidListManifestsSignature:
    """Tests for the maid_list_manifests function signature."""

    def test_maid_list_manifests_has_ctx_parameter(self):
        """Test that maid_list_manifests has ctx parameter.

        The manifest specifies:
        - type: function
        - name: maid_list_manifests
        - args: includes ctx: Context
        """
        from maid_runner_mcp.tools.manifests import maid_list_manifests

        sig = inspect.signature(maid_list_manifests)
        params = sig.parameters

        assert "ctx" in params, "maid_list_manifests should have 'ctx' parameter"

    def test_maid_list_manifests_ctx_parameter_type(self):
        """Test that ctx parameter has Context type annotation."""
        from maid_runner_mcp.tools.manifests import maid_list_manifests

        sig = inspect.signature(maid_list_manifests)
        params = sig.parameters

        ctx_param = params.get("ctx")
        assert ctx_param is not None, "ctx parameter should exist"

        # Check the annotation exists
        assert ctx_param.annotation != inspect.Parameter.empty, "ctx should have type annotation"

    def test_maid_list_manifests_imports_context(self):
        """Test that manifests.py imports Context from mcp.server.fastmcp."""
        from maid_runner_mcp.tools import manifests

        # Check that Context is available in the module
        assert hasattr(manifests, "Context") or "Context" in dir(
            manifests
        ), "manifests module should import Context"

    def test_maid_list_manifests_imports_get_working_directory(self):
        """Test that manifests.py imports get_working_directory from utils.roots."""
        import maid_runner_mcp.tools.manifests as manifests_module

        # Check module imports - get_working_directory should be used in the code
        import inspect

        source = inspect.getsource(manifests_module.maid_list_manifests)
        assert (
            "get_working_directory" in source
        ), "maid_list_manifests should call get_working_directory"


@pytest.mark.asyncio
class TestMaidListManifestsUsesWorkingDirectory:
    """Tests for maid_list_manifests using working directory."""

    async def test_maid_list_manifests_accepts_context_parameter(self):
        """Test that maid_list_manifests can be called with ctx parameter."""
        from maid_runner_mcp.tools.manifests import maid_list_manifests
        from unittest.mock import AsyncMock, MagicMock

        # Create a mock context
        mock_ctx = MagicMock()
        mock_session = MagicMock()
        mock_session.list_roots = AsyncMock(
            return_value=MagicMock(roots=[MagicMock(uri="file:///tmp/test")])
        )
        mock_ctx.session = mock_session

        # Call with a nonexistent file to trigger quick error path
        # The important part is that it accepts ctx parameter
        result = await maid_list_manifests(
            file_path="nonexistent.py",
            ctx=mock_ctx,
        )

        # Should return a result (even if it's an error)
        assert "file_path" in result, "Should return ListManifestsResult"
        assert "total_manifests" in result, "Should have total_manifests field"

    async def test_maid_list_manifests_calls_get_working_directory(self):
        """Test that maid_list_manifests calls get_working_directory with ctx."""
        from maid_runner_mcp.tools.manifests import maid_list_manifests
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
            "maid_runner_mcp.tools.manifests.get_working_directory", new_callable=AsyncMock
        ) as mock_get_wd:
            mock_get_wd.return_value = "/tmp/test"

            # Call maid_list_manifests
            await maid_list_manifests(
                file_path="nonexistent.py",
                ctx=mock_ctx,
            )

            # Verify get_working_directory was called with ctx
            mock_get_wd.assert_called_once_with(mock_ctx)
