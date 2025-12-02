"""Behavioral tests for updating maid_validate to use working directory from MCP roots (Task 027).

These tests verify the expected artifacts defined in the manifest:
- maid_validate(): Updated async function that uses get_working_directory()

Tests follow MAID behavioral testing pattern - they USE the artifacts
rather than just checking existence.
"""

import inspect
import pytest


class TestMaidValidateSignature:
    """Tests for the maid_validate function signature."""

    def test_maid_validate_has_ctx_parameter(self):
        """Test that maid_validate has ctx parameter.

        The manifest specifies:
        - type: function
        - name: maid_validate
        - args: includes ctx: Context
        """
        from maid_runner_mcp.tools.validate import maid_validate

        sig = inspect.signature(maid_validate)
        params = sig.parameters

        assert "ctx" in params, "maid_validate should have 'ctx' parameter"

    def test_maid_validate_ctx_parameter_type(self):
        """Test that ctx parameter has Context type annotation."""
        from maid_runner_mcp.tools.validate import maid_validate

        sig = inspect.signature(maid_validate)
        params = sig.parameters

        ctx_param = params.get("ctx")
        assert ctx_param is not None, "ctx parameter should exist"

        # Check the annotation exists
        assert ctx_param.annotation != inspect.Parameter.empty, "ctx should have type annotation"

    def test_maid_validate_imports_context(self):
        """Test that validate.py imports Context from mcp.server.fastmcp."""
        from maid_runner_mcp.tools import validate

        # Check that Context is available in the module
        assert hasattr(validate, "Context") or "Context" in dir(
            validate
        ), "validate module should import Context"

    def test_maid_validate_imports_get_working_directory(self):
        """Test that validate.py imports get_working_directory from utils.roots."""
        import maid_runner_mcp.tools.validate as validate_module

        # Check module imports - get_working_directory should be used in the code
        import inspect

        source = inspect.getsource(validate_module.maid_validate)
        assert (
            "get_working_directory" in source
        ), "maid_validate should call get_working_directory"


@pytest.mark.asyncio
class TestMaidValidateUsesWorkingDirectory:
    """Tests for maid_validate using working directory."""

    async def test_maid_validate_accepts_context_parameter(self):
        """Test that maid_validate can be called with ctx parameter."""
        from maid_runner_mcp.tools.validate import maid_validate
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
        result = await maid_validate(
            manifest_path="nonexistent.json",
            ctx=mock_ctx,
        )

        # Should return a result (even if it's an error)
        assert "success" in result, "Should return ValidateResult"

    async def test_maid_validate_calls_get_working_directory(self):
        """Test that maid_validate calls get_working_directory with ctx."""
        from maid_runner_mcp.tools.validate import maid_validate
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
            "maid_runner_mcp.tools.validate.get_working_directory", new_callable=AsyncMock
        ) as mock_get_wd:
            mock_get_wd.return_value = "/tmp/test"

            # Call maid_validate
            result = await maid_validate(
                manifest_path="nonexistent.json",
                ctx=mock_ctx,
            )

            # Verify get_working_directory was called with ctx
            mock_get_wd.assert_called_once_with(mock_ctx)
