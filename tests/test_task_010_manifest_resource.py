"""Behavioral tests for manifest resource (Task 010).

These tests verify the expected artifacts defined in the manifest:
- get_manifest(manifest_name: str) -> str: MCP resource handler for accessing manifest files

Tests follow MAID behavioral testing pattern - they USE the artifacts
rather than just checking existence.
"""

import json
import pytest


class TestGetManifestFunction:
    """Tests for the get_manifest function signature and basic properties."""

    def test_get_manifest_exists_and_is_callable(self):
        """Test that get_manifest exists and is callable.

        The manifest specifies:
        - type: function
        - name: get_manifest
        """
        from src.maid_runner_mcp.resources.manifest import get_manifest

        assert callable(get_manifest), "get_manifest should be callable"

    def test_get_manifest_is_async(self):
        """Test that get_manifest is an async function.

        MCP resources use FastMCP's @mcp.resource() decorator which requires async functions.
        """
        import asyncio
        from src.maid_runner_mcp.resources.manifest import get_manifest

        assert asyncio.iscoroutinefunction(get_manifest), "get_manifest should be an async function"

    def test_get_manifest_has_correct_signature(self):
        """Test that get_manifest has the expected parameter.

        The manifest specifies:
        - args: [{"name": "manifest_name", "type": "str"}]
        """
        import inspect
        from src.maid_runner_mcp.resources.manifest import get_manifest

        sig = inspect.signature(get_manifest)
        params = sig.parameters

        assert "manifest_name" in params, "get_manifest should have 'manifest_name' parameter"

    def test_get_manifest_returns_string(self):
        """Test that get_manifest return type is str.

        The manifest specifies:
        - returns: str
        """
        import inspect
        from src.maid_runner_mcp.resources.manifest import get_manifest

        sig = inspect.signature(get_manifest)

        assert (
            sig.return_annotation is not inspect.Signature.empty
        ), "get_manifest should have a return type annotation"


@pytest.mark.asyncio
class TestGetManifestBehavior:
    """Tests for get_manifest behavior when called with various inputs."""

    async def test_get_manifest_reads_existing_manifest(self):
        """Test that get_manifest can read an existing manifest file.

        This test verifies the primary use case: reading a manifest by name.
        """
        from src.maid_runner_mcp.resources.manifest import get_manifest

        # Use an existing manifest file (Task 001)
        result = await get_manifest("task-001-mcp-server-core")

        # Result should be a string
        assert isinstance(result, str), "get_manifest should return a string"

        # Result should not be empty
        assert len(result) > 0, "get_manifest should return non-empty content"

    async def test_get_manifest_returns_valid_json(self):
        """Test that get_manifest returns valid JSON string.

        Manifests are JSON files, so the returned string should be parseable JSON.
        """
        from src.maid_runner_mcp.resources.manifest import get_manifest

        result = await get_manifest("task-001-mcp-server-core")

        # Should be parseable as JSON
        manifest_data = json.loads(result)

        # Should have typical manifest fields
        assert "goal" in manifest_data, "Manifest should have 'goal' field"
        assert "taskType" in manifest_data, "Manifest should have 'taskType' field"

    async def test_get_manifest_with_multiple_manifests(self):
        """Test that get_manifest can read different manifest files.

        Verify it works with multiple different manifests.
        """
        from src.maid_runner_mcp.resources.manifest import get_manifest

        manifest_names = [
            "task-001-mcp-server-core",
            "task-002-maid-validate-tool",
            "task-003-maid-snapshot-tool",
        ]

        for name in manifest_names:
            result = await get_manifest(name)

            # Each should return valid content
            assert isinstance(result, str), f"get_manifest('{name}') should return string"
            assert len(result) > 0, f"get_manifest('{name}') should return non-empty content"

            # Each should be valid JSON
            manifest_data = json.loads(result)
            assert "goal" in manifest_data, f"Manifest '{name}' should have 'goal' field"

    async def test_get_manifest_nonexistent_file_raises_error(self):
        """Test that get_manifest raises FileNotFoundError for non-existent manifest.

        The manifest specifies:
        - raises: ["FileNotFoundError", "ValueError"]
        """
        from src.maid_runner_mcp.resources.manifest import get_manifest

        with pytest.raises(FileNotFoundError):
            await get_manifest("nonexistent-manifest-that-does-not-exist")

    async def test_get_manifest_empty_name_raises_error(self):
        """Test that get_manifest raises ValueError for empty manifest name.

        The manifest specifies:
        - raises: ["FileNotFoundError", "ValueError"]
        """
        from src.maid_runner_mcp.resources.manifest import get_manifest

        with pytest.raises(ValueError):
            await get_manifest("")

    async def test_get_manifest_handles_name_with_extension(self):
        """Test that get_manifest can handle manifest names with or without .json extension.

        This is a common use case - users might provide either form.
        """
        from src.maid_runner_mcp.resources.manifest import get_manifest

        # Try without extension (preferred)
        result1 = await get_manifest("task-001-mcp-server-core")
        assert isinstance(result1, str)
        assert len(result1) > 0

        # Try with extension (should also work or raise clear error)
        try:
            result2 = await get_manifest("task-001-mcp-server-core.manifest.json")
            # If it works, verify it returns valid content
            assert isinstance(result2, str)
        except (FileNotFoundError, ValueError):
            # It's acceptable to reject names with extensions
            pass

    async def test_get_manifest_content_matches_file_system(self):
        """Test that get_manifest returns content that matches the actual file.

        This verifies the function actually reads the file correctly.
        """
        import os
        from src.maid_runner_mcp.resources.manifest import get_manifest

        manifest_name = "task-001-mcp-server-core"

        # Get result from function
        result = await get_manifest(manifest_name)

        # Read the actual file directly
        manifest_path = os.path.join("manifests", f"{manifest_name}.manifest.json")
        with open(manifest_path, "r") as f:
            expected_content = f.read()

        # Parse both as JSON and compare (to ignore whitespace differences)
        result_json = json.loads(result)
        expected_json = json.loads(expected_content)

        assert result_json == expected_json, "get_manifest should return same content as file"

    async def test_get_manifest_handles_path_traversal_attempt(self):
        """Test that get_manifest safely handles path traversal attempts.

        Security test: should not allow reading files outside manifests directory.
        """
        from src.maid_runner_mcp.resources.manifest import get_manifest

        # Try various path traversal patterns
        malicious_names = [
            "../etc/passwd",
            "../../etc/passwd",
            "../src/maid_runner_mcp/server.py",
        ]

        for name in malicious_names:
            with pytest.raises((FileNotFoundError, ValueError)):
                await get_manifest(name)


class TestResourcesExport:
    """Tests for resources module exports."""

    def test_get_manifest_exported_from_resources(self):
        """Test that get_manifest is exported from resources package.

        This ensures the function is accessible via the resources module.
        """
        from src.maid_runner_mcp.resources import get_manifest

        assert callable(get_manifest), "get_manifest should be exported from resources"
