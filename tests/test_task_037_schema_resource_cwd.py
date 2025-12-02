"""Behavioral tests for updating get_manifest_schema to use working directory from MCP roots (Task 037).

These tests verify the expected artifacts defined in the manifest:
- get_manifest_schema(): Updated async function that uses get_working_directory()

Tests follow MAID behavioral testing pattern - they USE the artifacts
rather than just checking existence.
"""

import inspect
import pytest


class TestGetManifestSchemaSignature:
    """Tests for the get_manifest_schema function signature."""

    def test_get_manifest_schema_has_ctx_parameter(self):
        """Test that get_manifest_schema has ctx parameter.

        The manifest specifies:
        - type: function
        - name: get_manifest_schema
        - args: includes ctx: Context
        """
        from maid_runner_mcp.resources.schema import get_manifest_schema

        sig = inspect.signature(get_manifest_schema)
        params = sig.parameters

        assert "ctx" in params, "get_manifest_schema should have 'ctx' parameter"

    def test_get_manifest_schema_ctx_parameter_type(self):
        """Test that ctx parameter has Context type annotation."""
        from maid_runner_mcp.resources.schema import get_manifest_schema

        sig = inspect.signature(get_manifest_schema)
        params = sig.parameters

        ctx_param = params.get("ctx")
        assert ctx_param is not None, "ctx parameter should exist"

        # Check the annotation exists
        assert ctx_param.annotation != inspect.Parameter.empty, "ctx should have type annotation"

    def test_get_manifest_schema_imports_context(self):
        """Test that schema.py imports Context from mcp.server.fastmcp."""
        from maid_runner_mcp.resources import schema

        # Check that Context is available in the module
        assert hasattr(schema, "Context") or "Context" in dir(
            schema
        ), "schema module should import Context"

    def test_get_manifest_schema_imports_get_working_directory(self):
        """Test that schema.py imports get_working_directory from utils.roots."""
        import maid_runner_mcp.resources.schema as schema_module

        # Check module imports - get_working_directory should be used in the code
        import inspect

        source = inspect.getsource(schema_module.get_manifest_schema)
        assert (
            "get_working_directory" in source
        ), "get_manifest_schema should call get_working_directory"


@pytest.mark.asyncio
class TestGetManifestSchemaUsesWorkingDirectory:
    """Tests for get_manifest_schema using working directory."""

    async def test_get_manifest_schema_accepts_context_parameter(self):
        """Test that get_manifest_schema can be called with ctx parameter."""
        from maid_runner_mcp.resources.schema import get_manifest_schema
        from unittest.mock import AsyncMock, MagicMock, patch

        # Create a mock context
        mock_ctx = MagicMock()
        mock_session = MagicMock()
        mock_session.list_roots = AsyncMock(
            return_value=MagicMock(roots=[MagicMock(uri="file:///tmp/test")])
        )
        mock_ctx.session = mock_session

        # Mock subprocess to avoid actual command execution
        with patch("maid_runner_mcp.resources.schema.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout='{"type": "object"}', stderr="")

            # Call with ctx parameter
            result = await get_manifest_schema(ctx=mock_ctx)

            # Should return a result
            assert isinstance(result, str), "Should return schema as string"
            assert len(result) > 0, "Schema should not be empty"

    async def test_get_manifest_schema_calls_get_working_directory(self):
        """Test that get_manifest_schema calls get_working_directory with ctx."""
        from maid_runner_mcp.resources.schema import get_manifest_schema
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
            "maid_runner_mcp.resources.schema.get_working_directory", new_callable=AsyncMock
        ) as mock_get_wd:
            mock_get_wd.return_value = "/tmp/test"

            # Mock subprocess to avoid actual command execution
            with patch("maid_runner_mcp.resources.schema.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0, stdout='{"type": "object"}', stderr=""
                )

                # Call get_manifest_schema
                result = await get_manifest_schema(ctx=mock_ctx)

                # Verify get_working_directory was called with ctx
                mock_get_wd.assert_called_once_with(mock_ctx)

                # Verify result is valid
                assert isinstance(result, str), "Should return schema as string"
