"""Behavioral tests for maid_generate_stubs MCP tool (Task 008).

These tests verify the expected artifacts defined in the manifest:
- GenerateStubsResult: TypedDict for generate-stubs results
- maid_generate_stubs(): Async function that generates test stubs from manifests

Tests follow MAID behavioral testing pattern - they USE the artifacts
rather than just checking existence.
"""

import pytest


class TestGenerateStubsResult:
    """Tests for the GenerateStubsResult TypedDict."""

    def test_generate_stubs_result_is_typed_dict(self):
        """Test that GenerateStubsResult is a TypedDict.

        The manifest specifies:
        - type: class
        - name: GenerateStubsResult
        - description: TypedDict for generate-stubs results
        """
        from maid_runner_mcp.tools.generate_stubs import GenerateStubsResult

        # TypedDict classes have __annotations__
        assert hasattr(
            GenerateStubsResult, "__annotations__"
        ), "GenerateStubsResult should have __annotations__ (TypedDict requirement)"

    def test_generate_stubs_result_has_required_fields(self):
        """Test that GenerateStubsResult has all required fields."""
        from maid_runner_mcp.tools.generate_stubs import GenerateStubsResult

        annotations = GenerateStubsResult.__annotations__

        required_fields = {
            "success": bool,
            "manifest_path": str,
            "generated_files": list,
            "errors": list,
        }

        for field_name in required_fields:
            assert (
                field_name in annotations
            ), f"GenerateStubsResult should have '{field_name}' field"


class TestMaidGenerateStubsFunction:
    """Tests for the maid_generate_stubs async function."""

    def test_maid_generate_stubs_is_callable(self):
        """Test that maid_generate_stubs exists and is callable.

        The manifest specifies:
        - type: function
        - name: maid_generate_stubs
        """
        from maid_runner_mcp.tools.generate_stubs import maid_generate_stubs

        assert callable(maid_generate_stubs), "maid_generate_stubs should be callable"

    def test_maid_generate_stubs_is_async(self):
        """Test that maid_generate_stubs is an async function."""
        import asyncio
        from maid_runner_mcp.tools.generate_stubs import maid_generate_stubs

        assert asyncio.iscoroutinefunction(
            maid_generate_stubs
        ), "maid_generate_stubs should be an async function"

    def test_maid_generate_stubs_has_correct_signature(self):
        """Test that maid_generate_stubs has the expected parameters.

        The manifest specifies:
        - manifest_path: str (required)
        """
        import inspect
        from maid_runner_mcp.tools.generate_stubs import maid_generate_stubs

        sig = inspect.signature(maid_generate_stubs)
        params = sig.parameters

        # Check manifest_path parameter (required, no default)
        assert (
            "manifest_path" in params
        ), "maid_generate_stubs should have 'manifest_path' parameter"
        assert (
            params["manifest_path"].default is inspect.Parameter.empty
        ), "manifest_path should be required (no default)"


@pytest.mark.asyncio
class TestMaidGenerateStubsBehavior:
    """Tests for maid_generate_stubs behavior when called."""

    async def test_maid_generate_stubs_returns_generate_stubs_result(self):
        """Test that maid_generate_stubs returns a GenerateStubsResult-compatible dict."""
        from maid_runner_mcp.tools.generate_stubs import maid_generate_stubs

        # Test with non-existent manifest to check structure without creating files
        manifest_path = "/tmp/nonexistent-test.manifest.json"

        result = await maid_generate_stubs(manifest_path)

        # Result should have the required fields even on failure
        assert "success" in result, "Result should have 'success' field"
        assert "manifest_path" in result, "Result should have 'manifest_path' field"
        assert "generated_files" in result, "Result should have 'generated_files' field"
        assert "errors" in result, "Result should have 'errors' field"

    async def test_maid_generate_stubs_success_case(self):
        """Test that maid_generate_stubs returns correct types for all fields."""
        from maid_runner_mcp.tools.generate_stubs import maid_generate_stubs

        # Test with non-existent manifest - focuses on structure not side effects
        manifest_path = "/tmp/test-missing.manifest.json"

        result = await maid_generate_stubs(manifest_path)

        # Should have correct types regardless of success
        assert isinstance(result["success"], bool), "success should be a bool"
        assert result["manifest_path"] == manifest_path, "manifest_path should match input"
        assert isinstance(result["generated_files"], list), "generated_files should be a list"
        assert isinstance(result["errors"], list), "errors should be a list"

    async def test_maid_generate_stubs_with_nonexistent_manifest(self):
        """Test stub generation with non-existent manifest file."""
        from maid_runner_mcp.tools.generate_stubs import maid_generate_stubs

        manifest_path = "manifests/nonexistent.manifest.json"

        result = await maid_generate_stubs(manifest_path)

        # Should return with errors
        assert isinstance(result["errors"], list), "errors should be a list"
        assert (
            result["manifest_path"] == manifest_path
        ), "manifest_path should be preserved in result"


class TestToolsExport:
    """Tests for tools module exports."""

    def test_generate_stubs_result_exported_from_tools(self):
        """Test that GenerateStubsResult is exported from tools package."""
        from maid_runner_mcp.tools import GenerateStubsResult

        assert hasattr(GenerateStubsResult, "__annotations__")

    def test_maid_generate_stubs_exported_from_tools(self):
        """Test that maid_generate_stubs is exported from tools package."""
        from maid_runner_mcp.tools import maid_generate_stubs

        assert callable(maid_generate_stubs)
