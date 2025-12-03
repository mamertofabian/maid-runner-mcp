"""Behavioral tests for schema resource (Task 011).

These tests verify the expected artifacts defined in the manifest:
- get_manifest_schema() -> str: MCP resource handler for accessing the MAID manifest JSON schema

Tests follow MAID behavioral testing pattern - they USE the artifacts
rather than just checking existence.
"""

import json
import os
import pytest
from unittest.mock import AsyncMock, MagicMock
from mcp.types import ListRootsResult, Root
from pydantic import FileUrl


class TestGetManifestSchemaFunction:
    """Tests for the get_manifest_schema function signature and basic properties."""

    def test_get_manifest_schema_exists_and_is_callable(self):
        """Test that get_manifest_schema exists and is callable.

        The manifest specifies:
        - type: function
        - name: get_manifest_schema
        """
        from src.maid_runner_mcp.resources.schema import get_manifest_schema

        assert callable(get_manifest_schema), "get_manifest_schema should be callable"

    def test_get_manifest_schema_is_async(self):
        """Test that get_manifest_schema is an async function.

        MCP resources use FastMCP's @mcp.resource() decorator which requires async functions.
        """
        import asyncio
        from src.maid_runner_mcp.resources.schema import get_manifest_schema

        assert asyncio.iscoroutinefunction(
            get_manifest_schema
        ), "get_manifest_schema should be an async function"

    def test_get_manifest_schema_has_ctx_parameter(self):
        """Test that get_manifest_schema has ctx parameter.

        The manifest specifies:
        - args: [{"name": "ctx", "type": "Context"}]

        Updated to use working directory from MCP roots.
        """
        import inspect
        from src.maid_runner_mcp.resources.schema import get_manifest_schema

        sig = inspect.signature(get_manifest_schema)
        params = sig.parameters

        assert "ctx" in params, "get_manifest_schema should have 'ctx' parameter"

    def test_get_manifest_schema_returns_string(self):
        """Test that get_manifest_schema return type is str.

        The manifest specifies:
        - returns: str
        """
        import inspect
        from src.maid_runner_mcp.resources.schema import get_manifest_schema

        sig = inspect.signature(get_manifest_schema)

        assert (
            sig.return_annotation is not inspect.Signature.empty
        ), "get_manifest_schema should have a return type annotation"


@pytest.mark.asyncio
class TestGetManifestSchemaBehavior:
    """Tests for get_manifest_schema behavior when called."""

    async def test_get_manifest_schema_returns_valid_string(self):
        """Test that get_manifest_schema returns a non-empty string.

        This test verifies the basic return type and non-emptiness.
        """
        from src.maid_runner_mcp.resources.schema import get_manifest_schema

        # Create mock context
        mock_ctx = MagicMock()
        mock_ctx.session = AsyncMock()
        cwd = os.getcwd()
        mock_ctx.session.list_roots = AsyncMock(
            return_value=ListRootsResult(roots=[Root(uri=FileUrl(f"file://{cwd}"))])
        )

        result = await get_manifest_schema(ctx=mock_ctx)

        # Result should be a string
        assert isinstance(result, str), "get_manifest_schema should return a string"

        # Result should not be empty
        assert len(result) > 0, "get_manifest_schema should return non-empty content"

    async def test_get_manifest_schema_returns_valid_json(self):
        """Test that get_manifest_schema returns valid JSON string.

        The schema is a JSON Schema document, so it should be parseable JSON.
        """
        from src.maid_runner_mcp.resources.schema import get_manifest_schema

        # Create mock context
        mock_ctx = MagicMock()
        mock_ctx.session = AsyncMock()
        cwd = os.getcwd()
        mock_ctx.session.list_roots = AsyncMock(
            return_value=ListRootsResult(roots=[Root(uri=FileUrl(f"file://{cwd}"))])
        )

        result = await get_manifest_schema(ctx=mock_ctx)

        # Should be parseable as JSON
        schema_data = json.loads(result)

        # Should be a dict (JSON object)
        assert isinstance(schema_data, dict), "Schema should be a JSON object"

    async def test_get_manifest_schema_contains_schema_properties(self):
        """Test that the returned schema has expected JSON Schema properties.

        A valid JSON Schema typically contains:
        - $schema: URI to the JSON Schema spec version
        - type: The root type (usually "object" for manifest)
        - properties: Object properties definition

        At minimum, it should have 'properties' or 'type' to be a valid schema.
        """
        from src.maid_runner_mcp.resources.schema import get_manifest_schema

        # Create mock context
        mock_ctx = MagicMock()
        mock_ctx.session = AsyncMock()
        cwd = os.getcwd()
        mock_ctx.session.list_roots = AsyncMock(
            return_value=ListRootsResult(roots=[Root(uri=FileUrl(f"file://{cwd}"))])
        )

        result = await get_manifest_schema(ctx=mock_ctx)
        schema_data = json.loads(result)

        # Check for common JSON Schema fields
        # At least one of these should be present for a valid schema
        has_properties = "properties" in schema_data
        has_type = "type" in schema_data
        has_schema_uri = "$schema" in schema_data

        assert (
            has_properties or has_type or has_schema_uri
        ), "Schema should have typical JSON Schema fields (properties, type, or $schema)"

    async def test_get_manifest_schema_matches_maid_manifest_structure(self):
        """Test that the schema defines MAID manifest structure.

        The schema should define fields that are part of a MAID manifest:
        - goal
        - taskType
        - expectedArtifacts
        - creatableFiles / editableFiles
        - validationCommand
        """
        from src.maid_runner_mcp.resources.schema import get_manifest_schema

        # Create mock context
        mock_ctx = MagicMock()
        mock_ctx.session = AsyncMock()
        cwd = os.getcwd()
        mock_ctx.session.list_roots = AsyncMock(
            return_value=ListRootsResult(roots=[Root(uri=FileUrl(f"file://{cwd}"))])
        )

        result = await get_manifest_schema(ctx=mock_ctx)
        schema_data = json.loads(result)

        # Get properties from schema
        # Handle both direct properties and nested definitions
        properties = schema_data.get("properties", {})

        # Check for key MAID manifest fields
        expected_fields = ["goal", "taskType", "expectedArtifacts", "validationCommand"]

        found_fields = [field for field in expected_fields if field in properties]

        assert (
            len(found_fields) >= 2
        ), f"Schema should define at least 2 core MAID fields, found: {found_fields}"

    async def test_get_manifest_schema_is_consistent_across_calls(self):
        """Test that get_manifest_schema returns the same schema on multiple calls.

        The schema is static, so multiple calls should return identical content.
        """
        from src.maid_runner_mcp.resources.schema import get_manifest_schema

        # Create mock context
        mock_ctx = MagicMock()
        mock_ctx.session = AsyncMock()
        cwd = os.getcwd()
        mock_ctx.session.list_roots = AsyncMock(
            return_value=ListRootsResult(roots=[Root(uri=FileUrl(f"file://{cwd}"))])
        )

        result1 = await get_manifest_schema(ctx=mock_ctx)
        result2 = await get_manifest_schema(ctx=mock_ctx)

        # Parse both as JSON and compare
        schema1 = json.loads(result1)
        schema2 = json.loads(result2)

        assert schema1 == schema2, "get_manifest_schema should return consistent results"

    async def test_get_manifest_schema_matches_maid_cli_output(self):
        """Test that the schema matches what MAID CLI 'maid schema' command returns.

        This ensures consistency with the MAID Runner tool that's being wrapped.
        """
        import subprocess
        from src.maid_runner_mcp.resources.schema import get_manifest_schema

        # Create mock context
        mock_ctx = MagicMock()
        mock_ctx.session = AsyncMock()
        cwd = os.getcwd()
        mock_ctx.session.list_roots = AsyncMock(
            return_value=ListRootsResult(roots=[Root(uri=FileUrl(f"file://{cwd}"))])
        )

        # Get schema from resource
        result = await get_manifest_schema(ctx=mock_ctx)
        resource_schema = json.loads(result)

        # Get schema from MAID CLI
        try:
            cli_result = subprocess.run(
                ["uv", "run", "maid", "schema"],
                capture_output=True,
                text=True,
                check=True,
            )
            cli_schema = json.loads(cli_result.stdout)

            # Compare schemas (should be identical)
            assert (
                resource_schema == cli_schema
            ), "Resource schema should match MAID CLI schema output"
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("MAID CLI not available for comparison")

    async def test_get_manifest_schema_can_validate_real_manifest(self):
        """Test that the returned schema can validate an actual manifest.

        Use jsonschema library to validate a real manifest against the schema.
        This is the ultimate behavioral test - the schema should be usable.
        """
        from src.maid_runner_mcp.resources.schema import get_manifest_schema

        # Create mock context
        mock_ctx = MagicMock()
        mock_ctx.session = AsyncMock()
        cwd = os.getcwd()
        mock_ctx.session.list_roots = AsyncMock(
            return_value=ListRootsResult(roots=[Root(uri=FileUrl(f"file://{cwd}"))])
        )

        # Get schema
        schema_str = await get_manifest_schema(ctx=mock_ctx)
        schema_data = json.loads(schema_str)

        # Try to import jsonschema (skip if not available)
        try:
            import jsonschema
        except ImportError:
            pytest.skip("jsonschema library not available")

        # Load a real manifest
        manifest_path = "manifests/task-001-mcp-server-core.manifest.json"
        try:
            with open(manifest_path, "r") as f:
                manifest_data = json.load(f)

            # Validate manifest against schema
            # This should not raise an exception
            jsonschema.validate(instance=manifest_data, schema=schema_data)

        except FileNotFoundError:
            pytest.skip(f"Test manifest not found: {manifest_path}")


class TestResourcesExport:
    """Tests for resources module exports."""

    def test_get_manifest_schema_exported_from_resources(self):
        """Test that get_manifest_schema is exported from resources package.

        This ensures the function is accessible via the resources module.
        """
        from src.maid_runner_mcp.resources import get_manifest_schema

        assert callable(
            get_manifest_schema
        ), "get_manifest_schema should be exported from resources"
