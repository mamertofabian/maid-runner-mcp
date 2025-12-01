"""Behavioral tests for maid_init and maid_get_schema MCP tools (Task 006).

These tests verify the expected artifacts defined in the manifest:
- InitResult: TypedDict for init results
- maid_init(): Async function that initializes MAID projects
- SchemaResult: TypedDict for schema results
- maid_get_schema(): Async function that retrieves the manifest schema

Tests follow MAID behavioral testing pattern - they USE the artifacts
rather than just checking existence.
"""

import pytest


class TestInitResult:
    """Tests for the InitResult TypedDict."""

    def test_init_result_is_typed_dict(self):
        """Test that InitResult is a TypedDict.

        The manifest specifies:
        - type: class
        - name: InitResult
        - description: TypedDict for init results
        """
        from maid_runner_mcp.tools.init import InitResult

        # TypedDict classes have __annotations__
        assert hasattr(
            InitResult, "__annotations__"
        ), "InitResult should have __annotations__ (TypedDict requirement)"

    def test_init_result_has_required_fields(self):
        """Test that InitResult has all required fields."""
        from maid_runner_mcp.tools.init import InitResult

        annotations = InitResult.__annotations__

        required_fields = {
            "success": bool,
            "target_dir": str,
            "errors": list,
        }

        for field_name in required_fields:
            assert field_name in annotations, f"InitResult should have '{field_name}' field"


class TestMaidInitFunction:
    """Tests for the maid_init async function."""

    def test_maid_init_is_callable(self):
        """Test that maid_init exists and is callable.

        The manifest specifies:
        - type: function
        - name: maid_init
        """
        from maid_runner_mcp.tools.init import maid_init

        assert callable(maid_init), "maid_init should be callable"

    def test_maid_init_is_async(self):
        """Test that maid_init is an async function."""
        import asyncio
        from maid_runner_mcp.tools.init import maid_init

        assert asyncio.iscoroutinefunction(maid_init), "maid_init should be an async function"

    def test_maid_init_has_correct_signature(self):
        """Test that maid_init has the expected parameters.

        The manifest specifies:
        - target_dir: str (default: ".")
        - force: bool (default: False)
        """
        import inspect
        from maid_runner_mcp.tools.init import maid_init

        sig = inspect.signature(maid_init)
        params = sig.parameters

        # Check target_dir parameter with default
        assert "target_dir" in params, "maid_init should have 'target_dir' parameter"
        assert params["target_dir"].default == ".", "target_dir should default to '.'"

        # Check force parameter with default
        assert "force" in params, "maid_init should have 'force' parameter"
        assert params["force"].default is False, "force should default to False"


class TestSchemaResult:
    """Tests for the SchemaResult TypedDict."""

    def test_schema_result_is_typed_dict(self):
        """Test that SchemaResult is a TypedDict.

        The schema tool should return a TypedDict containing:
        - schema: the JSON schema object
        """
        from maid_runner_mcp.tools.schema import SchemaResult

        # TypedDict classes have __annotations__
        assert hasattr(
            SchemaResult, "__annotations__"
        ), "SchemaResult should have __annotations__ (TypedDict requirement)"

    def test_schema_result_has_schema_field(self):
        """Test that SchemaResult has the schema field."""
        from maid_runner_mcp.tools.schema import SchemaResult

        annotations = SchemaResult.__annotations__

        assert "schema" in annotations, "SchemaResult should have 'schema' field"


class TestMaidGetSchemaFunction:
    """Tests for the maid_get_schema async function."""

    def test_maid_get_schema_is_callable(self):
        """Test that maid_get_schema exists and is callable."""
        from maid_runner_mcp.tools.schema import maid_get_schema

        assert callable(maid_get_schema), "maid_get_schema should be callable"

    def test_maid_get_schema_is_async(self):
        """Test that maid_get_schema is an async function."""
        import asyncio
        from maid_runner_mcp.tools.schema import maid_get_schema

        assert asyncio.iscoroutinefunction(
            maid_get_schema
        ), "maid_get_schema should be an async function"

    def test_maid_get_schema_has_no_required_parameters(self):
        """Test that maid_get_schema has no required parameters."""
        import inspect
        from maid_runner_mcp.tools.schema import maid_get_schema

        sig = inspect.signature(maid_get_schema)
        params = sig.parameters

        # All parameters (if any) should have defaults
        for param_name, param in params.items():
            assert (
                param.default is not inspect.Parameter.empty
            ), f"Parameter '{param_name}' should have a default value"


@pytest.mark.asyncio
class TestMaidInitBehavior:
    """Tests for maid_init behavior when called."""

    async def test_maid_init_returns_init_result(self):
        """Test that maid_init returns an InitResult-compatible dict."""
        import tempfile
        from maid_runner_mcp.tools.init import maid_init

        # Use a temporary directory to avoid overwriting project files
        with tempfile.TemporaryDirectory() as tmpdir:
            result = await maid_init(target_dir=tmpdir)

            # Result should have the required fields
            assert "success" in result, "Result should have 'success' field"
            assert "target_dir" in result, "Result should have 'target_dir' field"
            assert "errors" in result, "Result should have 'errors' field"

    async def test_maid_init_with_nonexistent_directory(self):
        """Test that maid_init handles nonexistent directories."""
        from maid_runner_mcp.tools.init import maid_init

        # Call with a nonexistent directory
        result = await maid_init(target_dir="/nonexistent/path/that/does/not/exist")

        # Should return with errors
        assert isinstance(result["errors"], list), "errors should be a list"


@pytest.mark.asyncio
class TestMaidGetSchemaBehavior:
    """Tests for maid_get_schema behavior when called."""

    async def test_maid_get_schema_returns_schema_result(self):
        """Test that maid_get_schema returns a SchemaResult-compatible dict."""
        from maid_runner_mcp.tools.schema import maid_get_schema

        # Call with no parameters
        result = await maid_get_schema()

        # Result should have the schema field
        assert "schema" in result, "Result should have 'schema' field"

    async def test_maid_get_schema_returns_valid_json_schema(self):
        """Test that maid_get_schema returns a valid JSON schema object."""
        from maid_runner_mcp.tools.schema import maid_get_schema

        result = await maid_get_schema()

        # Schema should be a dict with standard JSON schema fields
        schema = result["schema"]
        assert isinstance(schema, dict), "schema should be a dictionary"

        # A valid JSON schema typically has these fields
        assert (
            "$schema" in schema or "type" in schema or "properties" in schema
        ), "Schema should have standard JSON schema fields"


class TestToolsExport:
    """Tests for tools module exports."""

    def test_init_result_exported_from_tools(self):
        """Test that InitResult is exported from tools package."""
        from maid_runner_mcp.tools import InitResult

        assert hasattr(InitResult, "__annotations__")

    def test_maid_init_exported_from_tools(self):
        """Test that maid_init is exported from tools package."""
        from maid_runner_mcp.tools import maid_init

        assert callable(maid_init)

    def test_schema_result_exported_from_tools(self):
        """Test that SchemaResult is exported from tools package."""
        from maid_runner_mcp.tools import SchemaResult

        assert hasattr(SchemaResult, "__annotations__")

    def test_maid_get_schema_exported_from_tools(self):
        """Test that maid_get_schema is exported from tools package."""
        from maid_runner_mcp.tools import maid_get_schema

        assert callable(maid_get_schema)
