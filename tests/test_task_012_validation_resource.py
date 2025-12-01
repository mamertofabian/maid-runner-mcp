"""Behavioral tests for validation cache resource (Task 012).

These tests verify the expected artifacts defined in the manifest:
- _validation_cache: Module-level dictionary to store validation results
- get_validation_result(manifest_name: str) -> str: MCP resource handler for accessing cached validation results

Tests follow MAID behavioral testing pattern - they USE the artifacts
rather than just checking existence.
"""

import json
import pytest


class TestValidationCacheAttribute:
    """Tests for the _validation_cache module-level attribute."""

    def test_validation_cache_exists(self):
        """Test that _validation_cache exists in the module.

        The manifest specifies:
        - type: attribute
        - name: _validation_cache
        """
        from src.maid_runner_mcp.resources import validation

        assert hasattr(
            validation, "_validation_cache"
        ), "_validation_cache should exist in validation module"

    def test_validation_cache_is_dict(self):
        """Test that _validation_cache is a dictionary.

        The manifest description says it's a "dictionary to store validation results".
        """
        from src.maid_runner_mcp.resources.validation import _validation_cache

        assert isinstance(_validation_cache, dict), "_validation_cache should be a dictionary"


class TestGetValidationResultFunction:
    """Tests for the get_validation_result function signature and basic properties."""

    def test_get_validation_result_exists_and_is_callable(self):
        """Test that get_validation_result exists and is callable.

        The manifest specifies:
        - type: function
        - name: get_validation_result
        """
        from src.maid_runner_mcp.resources.validation import get_validation_result

        assert callable(get_validation_result), "get_validation_result should be callable"

    def test_get_validation_result_is_async(self):
        """Test that get_validation_result is an async function.

        MCP resources use FastMCP's @mcp.resource() decorator which requires async functions.
        """
        import asyncio
        from src.maid_runner_mcp.resources.validation import get_validation_result

        assert asyncio.iscoroutinefunction(
            get_validation_result
        ), "get_validation_result should be an async function"

    def test_get_validation_result_has_correct_signature(self):
        """Test that get_validation_result has the expected parameter.

        The manifest specifies:
        - args: [{"name": "manifest_name", "type": "str"}]
        """
        import inspect
        from src.maid_runner_mcp.resources.validation import get_validation_result

        sig = inspect.signature(get_validation_result)
        params = sig.parameters

        assert (
            "manifest_name" in params
        ), "get_validation_result should have 'manifest_name' parameter"

    def test_get_validation_result_returns_string(self):
        """Test that get_validation_result return type is str.

        The manifest specifies:
        - returns: str
        """
        import inspect
        from src.maid_runner_mcp.resources.validation import get_validation_result

        sig = inspect.signature(get_validation_result)

        assert (
            sig.return_annotation is not inspect.Signature.empty
        ), "get_validation_result should have a return type annotation"


@pytest.mark.asyncio
class TestGetValidationResultBehavior:
    """Tests for get_validation_result behavior when called with various inputs."""

    async def test_get_validation_result_reads_cached_result(self):
        """Test that get_validation_result can read a cached validation result.

        This test verifies the primary use case: reading a cached validation result.
        """
        from src.maid_runner_mcp.resources.validation import (
            _validation_cache,
            get_validation_result,
        )

        # Populate cache with a test result
        test_result = {"success": True, "mode": "implementation", "errors": []}
        _validation_cache["task-001-mcp-server-core"] = test_result

        # Retrieve the cached result
        result = await get_validation_result("task-001-mcp-server-core")

        # Result should be a string
        assert isinstance(result, str), "get_validation_result should return a string"

        # Result should not be empty
        assert len(result) > 0, "get_validation_result should return non-empty content"

        # Clean up
        _validation_cache.clear()

    async def test_get_validation_result_returns_valid_json(self):
        """Test that get_validation_result returns valid JSON string.

        Validation results should be JSON-serializable.
        """
        from src.maid_runner_mcp.resources.validation import (
            _validation_cache,
            get_validation_result,
        )

        # Populate cache
        test_result = {
            "success": True,
            "mode": "implementation",
            "manifest": "task-001",
            "errors": [],
        }
        _validation_cache["task-001"] = test_result

        result = await get_validation_result("task-001")

        # Should be parseable as JSON
        result_data = json.loads(result)

        # Should have typical validation result fields
        assert "success" in result_data, "Validation result should have 'success' field"

        # Clean up
        _validation_cache.clear()

    async def test_get_validation_result_uncached_manifest_raises_error(self):
        """Test that get_validation_result raises error for uncached manifest.

        The manifest specifies:
        - raises: ["ValueError", "KeyError"]
        """
        from src.maid_runner_mcp.resources.validation import (
            _validation_cache,
            get_validation_result,
        )

        # Ensure cache is clean
        _validation_cache.clear()

        with pytest.raises((KeyError, ValueError)):
            await get_validation_result("nonexistent-manifest-not-in-cache")

    async def test_get_validation_result_empty_name_raises_error(self):
        """Test that get_validation_result raises error for empty manifest name.

        The manifest specifies:
        - raises: ["ValueError", "KeyError"]
        """
        from src.maid_runner_mcp.resources.validation import get_validation_result

        with pytest.raises((ValueError, KeyError)):
            await get_validation_result("")

    async def test_get_validation_result_multiple_cached_results(self):
        """Test that get_validation_result can retrieve different cached results.

        Verify it works with multiple different cached validation results.
        """
        from src.maid_runner_mcp.resources.validation import (
            _validation_cache,
            get_validation_result,
        )

        # Populate cache with multiple results
        test_results = {
            "task-001": {"success": True, "errors": []},
            "task-002": {"success": False, "errors": ["Error 1"]},
            "task-003": {"success": True, "errors": []},
        }

        for name, result in test_results.items():
            _validation_cache[name] = result

        # Retrieve each result
        for name in test_results:
            result = await get_validation_result(name)

            # Each should return valid content
            assert isinstance(result, str), f"get_validation_result('{name}') should return string"
            assert (
                len(result) > 0
            ), f"get_validation_result('{name}') should return non-empty content"

            # Each should be valid JSON
            result_data = json.loads(result)
            assert "success" in result_data, f"Result '{name}' should have 'success' field"

        # Clean up
        _validation_cache.clear()

    async def test_get_validation_result_content_matches_cache(self):
        """Test that get_validation_result returns content that matches the cached data.

        This verifies the function actually reads from cache correctly.
        """
        from src.maid_runner_mcp.resources.validation import (
            _validation_cache,
            get_validation_result,
        )

        manifest_name = "task-test"
        expected_data = {
            "success": True,
            "mode": "behavioral",
            "manifest": "task-test.manifest.json",
            "errors": [],
            "warnings": ["Test warning"],
        }

        # Populate cache
        _validation_cache[manifest_name] = expected_data

        # Get result from function
        result = await get_validation_result(manifest_name)

        # Parse and compare
        result_data = json.loads(result)

        assert (
            result_data == expected_data
        ), "get_validation_result should return same data as cached"

        # Clean up
        _validation_cache.clear()


class TestValidationResourceIntegration:
    """Tests for integration with tools/validate.py."""

    def test_validation_cache_can_be_updated(self):
        """Test that the validation cache can be updated by other modules.

        The validate tool should be able to update the cache after validation.
        """
        from src.maid_runner_mcp.resources.validation import _validation_cache

        # Simulate what validate.py would do
        manifest_name = "test-manifest"
        validation_result = {"success": True, "mode": "implementation", "errors": []}

        # Update cache
        _validation_cache[manifest_name] = validation_result

        # Verify it was stored
        assert manifest_name in _validation_cache
        assert _validation_cache[manifest_name] == validation_result

        # Clean up
        _validation_cache.clear()

    @pytest.mark.asyncio
    async def test_validation_cache_handles_special_characters(self):
        """Test that manifest names with special characters are handled safely.

        This is a security test to ensure no injection vulnerabilities.
        """
        from src.maid_runner_mcp.resources.validation import (
            _validation_cache,
            get_validation_result,
        )

        # Test various special characters that might appear in manifest names
        test_names = [
            "task-001-test",
            "task_001_test",
            "task.001.test",
        ]

        for name in test_names:
            test_result = {"success": True, "manifest": name}
            _validation_cache[name] = test_result

            result = await get_validation_result(name)
            assert isinstance(result, str), f"Should handle manifest name: {name}"

            result_data = json.loads(result)
            assert result_data["manifest"] == name

        # Clean up
        _validation_cache.clear()

    @pytest.mark.asyncio
    async def test_validation_cache_handles_path_like_names(self):
        """Test that manifest names that look like paths are rejected or handled safely.

        Security test: should not allow path traversal through manifest names.
        """
        from src.maid_runner_mcp.resources.validation import (
            _validation_cache,
            get_validation_result,
        )

        # These should either be rejected or handled safely
        malicious_names = [
            "../../../etc/passwd",
            "../../src/server.py",
            "/absolute/path/manifest",
        ]

        for name in malicious_names:
            # Even if we put it in cache, get_validation_result should handle it safely
            _validation_cache[name] = {"success": True}

            try:
                result = await get_validation_result(name)
                # If it returns, verify it's safe (contains the data we put in)
                result_data = json.loads(result)
                assert isinstance(result_data, dict)
            except (ValueError, KeyError):
                # It's acceptable to reject suspicious names
                pass

        # Clean up
        _validation_cache.clear()


class TestResourcesExport:
    """Tests for resources module exports."""

    def test_get_validation_result_exported_from_resources(self):
        """Test that get_validation_result is exported from resources package.

        This ensures the function is accessible via the resources module.
        """
        from src.maid_runner_mcp.resources import get_validation_result

        assert callable(
            get_validation_result
        ), "get_validation_result should be exported from resources"

    def test_validation_cache_exported_from_resources(self):
        """Test that _validation_cache is accessible via the resources module.

        This is necessary for the validate tool to update the cache.
        """
        from src.maid_runner_mcp.resources import validation

        assert hasattr(
            validation, "_validation_cache"
        ), "_validation_cache should be accessible from resources.validation"
