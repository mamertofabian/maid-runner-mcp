"""Behavioral tests for updating maid_get_schema to use working directory from MCP roots (Task 031).

These tests verify the expected artifacts defined in the manifest:
- SchemaResult: TypedDict class for schema results
- maid_get_schema(): Updated async function that uses get_working_directory()

Tests follow MAID behavioral testing pattern - they USE the artifacts
rather than just checking existence.
"""

import inspect
import pytest


class TestSchemaResultClass:
    """Tests for the SchemaResult TypedDict class."""

    def test_schema_result_class_exists(self):
        """Test that SchemaResult class exists.

        The manifest specifies:
        - type: class
        - name: SchemaResult
        - description: TypedDict for schema results
        """
        from maid_runner_mcp.tools.schema import SchemaResult

        assert SchemaResult is not None, "SchemaResult class should exist"

    def test_schema_result_is_typeddict(self):
        """Test that SchemaResult is a TypedDict."""
        from maid_runner_mcp.tools.schema import SchemaResult

        # TypedDict classes have __annotations__
        assert hasattr(SchemaResult, "__annotations__"), "SchemaResult should have annotations"

        # Check that it has the expected fields
        annotations = SchemaResult.__annotations__
        assert "success" in annotations, "SchemaResult should have success field"
        assert "schema" in annotations, "SchemaResult should have schema field"
        assert "errors" in annotations, "SchemaResult should have errors field"

    def test_schema_result_can_be_used(self):
        """Test that SchemaResult can be instantiated and used."""
        from maid_runner_mcp.tools.schema import SchemaResult

        # Create a SchemaResult instance
        result: SchemaResult = {
            "success": True,
            "schema": {"type": "object"},
            "errors": [],
        }

        # Verify the structure
        assert result["success"] is True
        assert result["schema"] == {"type": "object"}
        assert result["errors"] == []


class TestMaidGetSchemaSignature:
    """Tests for the maid_get_schema function signature."""

    def test_maid_get_schema_has_ctx_parameter(self):
        """Test that maid_get_schema has ctx parameter.

        The manifest specifies:
        - type: function
        - name: maid_get_schema
        - args: includes ctx: Context
        """
        from maid_runner_mcp.tools.schema import maid_get_schema

        sig = inspect.signature(maid_get_schema)
        params = sig.parameters

        assert "ctx" in params, "maid_get_schema should have 'ctx' parameter"

    def test_maid_get_schema_ctx_parameter_type(self):
        """Test that ctx parameter has Context type annotation."""
        from maid_runner_mcp.tools.schema import maid_get_schema

        sig = inspect.signature(maid_get_schema)
        params = sig.parameters

        ctx_param = params.get("ctx")
        assert ctx_param is not None, "ctx parameter should exist"

        # Check the annotation exists
        assert ctx_param.annotation != inspect.Parameter.empty, "ctx should have type annotation"

    def test_maid_get_schema_imports_context(self):
        """Test that schema.py imports Context from mcp.server.fastmcp."""
        from maid_runner_mcp.tools import schema

        # Check that Context is available in the module
        assert hasattr(schema, "Context") or "Context" in dir(
            schema
        ), "schema module should import Context"

    def test_maid_get_schema_imports_get_working_directory(self):
        """Test that schema.py imports get_working_directory from utils.roots."""
        import maid_runner_mcp.tools.schema as schema_module

        # Check module imports - get_working_directory should be used in the code
        import inspect

        source = inspect.getsource(schema_module.maid_get_schema)
        assert (
            "get_working_directory" in source
        ), "maid_get_schema should call get_working_directory"


@pytest.mark.asyncio
class TestMaidGetSchemaUsesWorkingDirectory:
    """Tests for maid_get_schema using working directory."""

    async def test_maid_get_schema_accepts_context_parameter(self):
        """Test that maid_get_schema can be called with ctx parameter."""
        from maid_runner_mcp.tools.schema import maid_get_schema
        from unittest.mock import AsyncMock, MagicMock

        # Create a mock context
        mock_ctx = MagicMock()
        mock_session = MagicMock()
        mock_session.list_roots = AsyncMock(
            return_value=MagicMock(roots=[MagicMock(uri="file:///tmp/test")])
        )
        mock_ctx.session = mock_session

        # Call maid_get_schema with ctx parameter
        result = await maid_get_schema(ctx=mock_ctx)

        # Should return a result (SchemaResult with success, schema, errors)
        assert "success" in result, "Should return SchemaResult"
        assert "schema" in result, "Should have schema field"
        assert "errors" in result, "Should have errors field"

    async def test_maid_get_schema_calls_get_working_directory(self):
        """Test that maid_get_schema calls get_working_directory with ctx."""
        from maid_runner_mcp.tools.schema import maid_get_schema
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
            "maid_runner_mcp.tools.schema.get_working_directory", new_callable=AsyncMock
        ) as mock_get_wd:
            mock_get_wd.return_value = "/tmp/test"

            # Call maid_get_schema
            await maid_get_schema(ctx=mock_ctx)

            # Verify get_working_directory was called with ctx
            mock_get_wd.assert_called_once_with(mock_ctx)
