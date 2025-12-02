"""Behavioral tests for updating maid_files to use working directory from MCP roots (Task 032).

These tests verify the expected artifacts defined in the manifest:
- maid_files(): Updated async function that uses get_working_directory()

Tests follow MAID behavioral testing pattern - they USE the artifacts
rather than just checking existence.
"""

import inspect
import pytest


class TestMaidFilesSignature:
    """Tests for the maid_files function signature."""

    def test_maid_files_has_ctx_parameter(self):
        """Test that maid_files has ctx parameter.

        The manifest specifies:
        - type: function
        - name: maid_files
        - args: includes ctx: Context
        """
        from maid_runner_mcp.tools.files import maid_files

        sig = inspect.signature(maid_files)
        params = sig.parameters

        assert "ctx" in params, "maid_files should have 'ctx' parameter"

    def test_maid_files_ctx_parameter_type(self):
        """Test that ctx parameter has Context type annotation."""
        from maid_runner_mcp.tools.files import maid_files

        sig = inspect.signature(maid_files)
        params = sig.parameters

        ctx_param = params.get("ctx")
        assert ctx_param is not None, "ctx parameter should exist"

        # Check the annotation exists
        assert ctx_param.annotation != inspect.Parameter.empty, "ctx should have type annotation"

    def test_maid_files_imports_context(self):
        """Test that files.py imports Context from mcp.server.fastmcp."""
        from maid_runner_mcp.tools import files

        # Check that Context is available in the module
        assert hasattr(files, "Context") or "Context" in dir(
            files
        ), "files module should import Context"

    def test_maid_files_imports_get_working_directory(self):
        """Test that files.py imports get_working_directory from utils.roots."""
        import maid_runner_mcp.tools.files as files_module

        # Check module imports - get_working_directory should be used in the code
        import inspect

        source = inspect.getsource(files_module.maid_files)
        assert "get_working_directory" in source, "maid_files should call get_working_directory"


@pytest.mark.asyncio
class TestMaidFilesUsesWorkingDirectory:
    """Tests for maid_files using working directory."""

    async def test_maid_files_accepts_context_parameter(self):
        """Test that maid_files can be called with ctx parameter."""
        from maid_runner_mcp.tools.files import maid_files
        from unittest.mock import AsyncMock, MagicMock

        # Create a mock context
        mock_ctx = MagicMock()
        mock_session = MagicMock()
        mock_session.list_roots = AsyncMock(
            return_value=MagicMock(roots=[MagicMock(uri="file:///tmp/test")])
        )
        mock_ctx.session = mock_session

        # Call maid_files with ctx parameter
        # Use a specific manifest_dir to trigger quick error path if dir doesn't exist
        result = await maid_files(
            manifest_dir="nonexistent-manifests",
            ctx=mock_ctx,
        )

        # Should return a FileTrackingResult (even if empty due to error)
        assert "undeclared" in result, "Should return FileTrackingResult"
        assert "registered" in result, "Should return FileTrackingResult"
        assert "tracked" in result, "Should return FileTrackingResult"

    async def test_maid_files_calls_get_working_directory(self):
        """Test that maid_files calls get_working_directory with ctx."""
        from maid_runner_mcp.tools.files import maid_files
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
            "maid_runner_mcp.tools.files.get_working_directory", new_callable=AsyncMock
        ) as mock_get_wd:
            mock_get_wd.return_value = "/tmp/test"

            # Call maid_files
            result = await maid_files(
                manifest_dir="nonexistent-manifests",
                ctx=mock_ctx,
            )

            # Verify get_working_directory was called with ctx
            mock_get_wd.assert_called_once_with(mock_ctx)
