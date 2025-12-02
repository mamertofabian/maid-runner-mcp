"""Behavioral tests for updating maid_test to use working directory from MCP roots (Task 028).

These tests verify the expected artifacts defined in the manifest:
- maid_test(): Updated async function that uses get_working_directory()

Tests follow MAID behavioral testing pattern - they USE the artifacts
rather than just checking existence.
"""

import inspect
import pytest


class TestMaidTestSignature:
    """Tests for the maid_test function signature."""

    def test_maid_test_has_ctx_parameter(self):
        """Test that maid_test has ctx parameter.

        The manifest specifies:
        - type: function
        - name: maid_test
        - args: includes ctx: Context
        """
        from maid_runner_mcp.tools.test import maid_test

        sig = inspect.signature(maid_test)
        params = sig.parameters

        assert "ctx" in params, "maid_test should have 'ctx' parameter"

    def test_maid_test_ctx_parameter_type(self):
        """Test that ctx parameter has Context type annotation."""
        from maid_runner_mcp.tools.test import maid_test

        sig = inspect.signature(maid_test)
        params = sig.parameters

        ctx_param = params.get("ctx")
        assert ctx_param is not None, "ctx parameter should exist"

        # Check the annotation exists
        assert ctx_param.annotation != inspect.Parameter.empty, "ctx should have type annotation"

    def test_maid_test_imports_context(self):
        """Test that test.py imports Context from mcp.server.fastmcp."""
        from maid_runner_mcp.tools import test

        # Check that Context is available in the module
        assert hasattr(test, "Context") or "Context" in dir(
            test
        ), "test module should import Context"

    def test_maid_test_imports_get_working_directory(self):
        """Test that test.py imports get_working_directory from utils.roots."""
        import maid_runner_mcp.tools.test as test_module

        # Check module imports - get_working_directory should be used in the code
        import inspect

        source = inspect.getsource(test_module.maid_test)
        assert "get_working_directory" in source, "maid_test should call get_working_directory"


@pytest.mark.asyncio
class TestMaidTestUsesWorkingDirectory:
    """Tests for maid_test using working directory."""

    async def test_maid_test_accepts_context_parameter(self):
        """Test that maid_test can be called with ctx parameter."""
        from maid_runner_mcp.tools.test import maid_test
        from unittest.mock import AsyncMock, MagicMock

        # Create a mock context
        mock_ctx = MagicMock()
        mock_session = MagicMock()
        mock_session.list_roots = AsyncMock(
            return_value=MagicMock(roots=[MagicMock(uri="file:///tmp/test")])
        )
        mock_ctx.session = mock_session

        # Call with manifest_dir parameter to trigger quick execution
        # The important part is that it accepts ctx parameter
        result = await maid_test(
            manifest_dir="nonexistent-dir",
            ctx=mock_ctx,
        )

        # Should return a result (even if it's an error)
        assert "success" in result, "Should return TestResult"

    async def test_maid_test_calls_get_working_directory(self):
        """Test that maid_test calls get_working_directory with ctx."""
        from maid_runner_mcp.tools.test import maid_test
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
            "maid_runner_mcp.tools.test.get_working_directory", new_callable=AsyncMock
        ) as mock_get_wd:
            mock_get_wd.return_value = "/tmp/test"

            # Call maid_test
            result = await maid_test(
                manifest_dir="nonexistent-dir",
                ctx=mock_ctx,
            )

            # Verify get_working_directory was called with ctx
            mock_get_wd.assert_called_once_with(mock_ctx)
