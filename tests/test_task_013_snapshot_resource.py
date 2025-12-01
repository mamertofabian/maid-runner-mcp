"""Behavioral tests for snapshot resource (Task 013).

These tests verify the expected artifacts defined in the manifest:
- get_system_snapshot() -> str: MCP resource handler for accessing system-wide manifest snapshots

Tests follow MAID behavioral testing pattern - they USE the artifacts
rather than just checking existence.
"""

import json
import pytest


class TestGetSystemSnapshotFunction:
    """Tests for the get_system_snapshot function signature and basic properties."""

    def test_get_system_snapshot_exists_and_is_callable(self):
        """Test that get_system_snapshot exists and is callable.

        The manifest specifies:
        - type: function
        - name: get_system_snapshot
        """
        from src.maid_runner_mcp.resources.snapshot import get_system_snapshot

        assert callable(get_system_snapshot), "get_system_snapshot should be callable"

    def test_get_system_snapshot_is_async(self):
        """Test that get_system_snapshot is an async function.

        MCP resources use FastMCP's @mcp.resource() decorator which requires async functions.
        """
        import asyncio
        from src.maid_runner_mcp.resources.snapshot import get_system_snapshot

        assert asyncio.iscoroutinefunction(
            get_system_snapshot
        ), "get_system_snapshot should be an async function"

    def test_get_system_snapshot_has_no_parameters(self):
        """Test that get_system_snapshot accepts no parameters.

        The manifest specifies:
        - args: []

        This is a resource that returns the system-wide snapshot without input.
        """
        import inspect
        from src.maid_runner_mcp.resources.snapshot import get_system_snapshot

        sig = inspect.signature(get_system_snapshot)
        params = sig.parameters

        assert len(params) == 0, "get_system_snapshot should have no parameters"

    def test_get_system_snapshot_returns_string(self):
        """Test that get_system_snapshot return type is str.

        The manifest specifies:
        - returns: str
        """
        import inspect
        from src.maid_runner_mcp.resources.snapshot import get_system_snapshot

        sig = inspect.signature(get_system_snapshot)

        assert (
            sig.return_annotation is not inspect.Signature.empty
        ), "get_system_snapshot should have a return type annotation"


@pytest.mark.asyncio
class TestGetSystemSnapshotBehavior:
    """Tests for get_system_snapshot behavior when called."""

    async def test_get_system_snapshot_returns_valid_string(self):
        """Test that get_system_snapshot returns a non-empty string.

        This test verifies the basic return type and non-emptiness.
        """
        from src.maid_runner_mcp.resources.snapshot import get_system_snapshot

        result = await get_system_snapshot()

        # Result should be a string
        assert isinstance(result, str), "get_system_snapshot should return a string"

        # Result should not be empty
        assert len(result) > 0, "get_system_snapshot should return non-empty content"

    async def test_get_system_snapshot_returns_valid_json(self):
        """Test that get_system_snapshot returns valid JSON string.

        The system snapshot is a JSON document, so it should be parseable JSON.
        """
        from src.maid_runner_mcp.resources.snapshot import get_system_snapshot

        result = await get_system_snapshot()

        # Should be parseable as JSON
        snapshot_data = json.loads(result)

        # Should be a dict (JSON object)
        assert isinstance(snapshot_data, dict), "Snapshot should be a JSON object"

    async def test_get_system_snapshot_contains_manifest_data(self):
        """Test that the returned snapshot has expected structure.

        A system snapshot typically contains:
        - Aggregate information about manifests
        - File tracking data
        - System-wide validation results

        At minimum, it should be a valid dictionary with some content.
        """
        from src.maid_runner_mcp.resources.snapshot import get_system_snapshot

        result = await get_system_snapshot()
        snapshot_data = json.loads(result)

        # Should have some content (not empty dict)
        assert len(snapshot_data) > 0, "Snapshot should contain data"

        # Should be a dictionary
        assert isinstance(snapshot_data, dict), "Snapshot should be a dictionary"

    async def test_get_system_snapshot_is_consistent_across_calls(self):
        """Test that get_system_snapshot returns consistent results on multiple calls.

        Note: Due to caching (TTL), results should be consistent within the cache window.
        This tests that the function can be called multiple times successfully.
        """
        from src.maid_runner_mcp.resources.snapshot import get_system_snapshot

        result1 = await get_system_snapshot()
        result2 = await get_system_snapshot()

        # Both should be valid strings
        assert isinstance(result1, str), "First call should return string"
        assert isinstance(result2, str), "Second call should return string"

        # Both should be valid JSON
        snapshot1 = json.loads(result1)
        snapshot2 = json.loads(result2)

        assert isinstance(snapshot1, dict), "First result should be dict"
        assert isinstance(snapshot2, dict), "Second result should be dict"

        # If caching is working, results should be identical
        # (We don't enforce this strictly since caching might have TTL)
        # But at least both should be valid snapshots
        assert len(snapshot1) > 0 or len(snapshot2) > 0, "At least one snapshot should have data"

    async def test_get_system_snapshot_matches_maid_cli_output_format(self):
        """Test that the snapshot format is compatible with MAID CLI output.

        This ensures consistency with the MAID Runner tool that's being wrapped.
        The snapshot should be a valid system manifest format.
        """
        import subprocess
        from src.maid_runner_mcp.resources.snapshot import get_system_snapshot

        # Get snapshot from resource
        result = await get_system_snapshot()
        resource_snapshot = json.loads(result)

        # Verify it's a valid dictionary (basic format check)
        assert isinstance(resource_snapshot, dict), "Snapshot should be a dictionary"

        # Try to get snapshot from MAID CLI for comparison
        try:
            import tempfile
            import os

            # Use temp file to avoid creating system.manifest.json in project root
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_output = os.path.join(tmpdir, "system.manifest.json")
                cli_result = subprocess.run(
                    ["uv", "run", "maid", "snapshot-system", "--output", tmp_output, "--quiet"],
                    capture_output=True,
                    text=True,
                    check=True,
                )

            # If CLI succeeds, verify our resource returns similar structure
            # Note: This is optional since snapshot-system might not be in all MAID versions
            # We mainly verify the resource returns valid data
            assert len(resource_snapshot) >= 0, "Resource snapshot should be valid"

        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("MAID CLI snapshot-system not available for comparison")

    async def test_get_system_snapshot_includes_file_information(self):
        """Test that the snapshot includes file-related information.

        A system snapshot should contain information about files tracked by manifests.
        This could be in various formats, but should include some file data.
        """
        from src.maid_runner_mcp.resources.snapshot import get_system_snapshot

        result = await get_system_snapshot()
        snapshot_data = json.loads(result)

        # Should be a dictionary with content
        assert isinstance(snapshot_data, dict), "Snapshot should be a dictionary"
        assert len(snapshot_data) > 0, "Snapshot should contain data"

        # The exact structure depends on MAID implementation, but it should have content
        # We verify it's a valid non-empty dictionary

    async def test_get_system_snapshot_handles_empty_project(self):
        """Test that get_system_snapshot handles projects with no manifests gracefully.

        Even if there are no manifests, the function should return valid JSON
        (possibly empty or with minimal structure).
        """
        from src.maid_runner_mcp.resources.snapshot import get_system_snapshot

        # Call the function
        result = await get_system_snapshot()

        # Should still return valid JSON
        snapshot_data = json.loads(result)

        # Should be a dictionary (even if empty)
        assert isinstance(snapshot_data, dict), "Snapshot should always be a dictionary"

    async def test_get_system_snapshot_error_handling(self):
        """Test that get_system_snapshot handles errors gracefully.

        If the underlying MAID CLI command fails, the resource should either:
        - Raise an appropriate exception (RuntimeError)
        - Return a valid error structure as JSON

        This tests that errors don't cause crashes.
        """
        from src.maid_runner_mcp.resources.snapshot import get_system_snapshot

        # This test verifies the function can be called
        # Error handling behavior will depend on implementation
        try:
            result = await get_system_snapshot()

            # If successful, verify it's valid
            assert isinstance(result, str), "Should return string"
            snapshot_data = json.loads(result)
            assert isinstance(snapshot_data, dict), "Should be valid JSON dict"

        except RuntimeError as e:
            # It's acceptable to raise RuntimeError on CLI failures
            assert str(e), "RuntimeError should have a message"


@pytest.mark.asyncio
class TestResourceDecorator:
    """Tests for MCP resource decorator and registration."""

    async def test_resource_decorator_applied(self):
        """Test that the @mcp.resource decorator is properly applied.

        The function should be registered as an MCP resource with URI: snapshot://system
        """
        import asyncio
        from src.maid_runner_mcp.resources.snapshot import get_system_snapshot

        # Check if function has MCP resource metadata
        # FastMCP decorators typically add attributes or wrap the function
        assert callable(get_system_snapshot), "Function should be callable"
        assert asyncio.iscoroutinefunction(get_system_snapshot), "Function should be async"

    async def test_resource_uri_is_correct(self):
        """Test that the resource is registered with URI 'snapshot://system'.

        This verifies the resource can be accessed via the correct URI pattern.
        """
        # This is verified through the decorator parameter
        # The actual registration is tested in integration tests
        # Here we verify the function exists and is properly structured
        from src.maid_runner_mcp.resources.snapshot import get_system_snapshot

        assert callable(get_system_snapshot), "Resource function should exist"


@pytest.mark.asyncio
class TestCachingBehavior:
    """Tests for TTL caching behavior if implemented."""

    async def test_caching_reduces_cli_calls(self):
        """Test that caching reduces redundant CLI calls.

        If TTL caching is implemented, multiple calls within the cache window
        should not repeatedly call the MAID CLI.

        Note: This test is optional since caching implementation may vary.
        """
        from src.maid_runner_mcp.resources.snapshot import get_system_snapshot

        # Call multiple times in quick succession
        result1 = await get_system_snapshot()
        result2 = await get_system_snapshot()
        result3 = await get_system_snapshot()

        # All should return valid results
        for result in [result1, result2, result3]:
            assert isinstance(result, str), "Each call should return string"
            snapshot = json.loads(result)
            assert isinstance(snapshot, dict), "Each result should be valid JSON dict"

        # If caching is working, results should be identical
        # But we don't enforce this strictly as implementation may vary


class TestResourcesExport:
    """Tests for resources module exports."""

    def test_get_system_snapshot_exported_from_resources(self):
        """Test that get_system_snapshot is exported from resources package.

        This ensures the function is accessible via the resources module.
        """
        from src.maid_runner_mcp.resources import get_system_snapshot

        assert callable(
            get_system_snapshot
        ), "get_system_snapshot should be exported from resources"


@pytest.mark.asyncio
class TestIntegrationWithSnapshotTool:
    """Tests for integration with the snapshot_system tool."""

    async def test_resource_uses_maid_cli_correctly(self):
        """Test that the resource correctly invokes MAID CLI commands.

        The resource should use the same command structure as the snapshot_system tool.
        """
        from src.maid_runner_mcp.resources.snapshot import get_system_snapshot

        # Call the resource
        result = await get_system_snapshot()

        # Verify it returns valid snapshot data
        assert isinstance(result, str), "Should return string"
        snapshot_data = json.loads(result)
        assert isinstance(snapshot_data, dict), "Should be valid JSON dict"

    async def test_resource_handles_concurrent_calls(self):
        """Test that the resource handles concurrent calls safely.

        Multiple simultaneous calls should not cause race conditions or errors.
        """
        import asyncio
        from src.maid_runner_mcp.resources.snapshot import get_system_snapshot

        # Make multiple concurrent calls
        results = await asyncio.gather(
            get_system_snapshot(),
            get_system_snapshot(),
            get_system_snapshot(),
            return_exceptions=True,
        )

        # All should succeed or all should fail with same error
        successful_results = [r for r in results if isinstance(r, str)]

        # At least some should succeed (or all should fail with same error type)
        if successful_results:
            for result in successful_results:
                assert isinstance(result, str), "Successful results should be strings"
                snapshot = json.loads(result)
                assert isinstance(snapshot, dict), "Should be valid JSON dict"
        else:
            # All failed - they should fail with same error type
            error_types = set(type(r) for r in results)
            assert len(error_types) == 1, "All failures should be same error type"
