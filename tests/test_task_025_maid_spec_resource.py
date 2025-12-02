"""Behavioral tests for Task 025: MAID spec resource.

Tests verify that the maid://spec resource correctly exposes
the full MAID methodology specification document.

These tests USE the artifacts by:
- Calling get_maid_spec() and verifying it returns the spec content
- Checking the content contains key MAID methodology concepts
"""

import pytest


class TestGetMaidSpec:
    """Tests for the get_maid_spec resource function."""

    @pytest.mark.asyncio
    async def test_get_maid_spec_returns_string(self) -> None:
        """get_maid_spec should return a string."""
        from maid_runner_mcp.resources.spec import get_maid_spec

        result = await get_maid_spec()
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_maid_spec_contains_maid_title(self) -> None:
        """Spec should contain the MAID methodology title."""
        from maid_runner_mcp.resources.spec import get_maid_spec

        result = await get_maid_spec()
        assert "MAID" in result
        assert "Manifest-driven AI Development" in result

    @pytest.mark.asyncio
    async def test_get_maid_spec_contains_core_principles(self) -> None:
        """Spec should contain the core principles section."""
        from maid_runner_mcp.resources.spec import get_maid_spec

        result = await get_maid_spec()
        assert "Core Principles" in result
        # Key principles
        assert "Explicitness" in result or "explicit" in result.lower()

    @pytest.mark.asyncio
    async def test_get_maid_spec_contains_workflow(self) -> None:
        """Spec should contain the workflow section."""
        from maid_runner_mcp.resources.spec import get_maid_spec

        result = await get_maid_spec()
        assert "Workflow" in result
        # Should mention phases
        assert "Phase" in result

    @pytest.mark.asyncio
    async def test_get_maid_spec_contains_manifest_info(self) -> None:
        """Spec should contain manifest structure information."""
        from maid_runner_mcp.resources.spec import get_maid_spec

        result = await get_maid_spec()
        # Should mention task manifest
        assert "Task Manifest" in result or "manifest" in result.lower()
        # Should have JSON examples
        assert "expectedArtifacts" in result

    @pytest.mark.asyncio
    async def test_get_maid_spec_is_substantial(self) -> None:
        """Spec should be substantial (full document, not summary)."""
        from maid_runner_mcp.resources.spec import get_maid_spec

        result = await get_maid_spec()
        # Full spec should be at least several thousand characters
        assert len(result) > 5000


class TestMaidSpecResourceRegistration:
    """Tests for resource registration with MCP server."""

    def test_spec_resource_is_registered(self) -> None:
        """The maid://spec resource should be registered with the server."""
        from maid_runner_mcp.server import mcp

        # Check that the resource is available
        # FastMCP stores resources internally
        resources = mcp._resource_manager._resources
        resource_uris = [str(r.uri) for r in resources.values()]

        assert any("maid://spec" in uri for uri in resource_uris)


class TestMaidSpecResourceIntegration:
    """Integration tests for the spec resource."""

    @pytest.mark.asyncio
    async def test_spec_matches_file_content(self) -> None:
        """Resource content should match the actual spec file."""
        from pathlib import Path

        from maid_runner_mcp.resources.spec import get_maid_spec

        result = await get_maid_spec()

        # Read the actual file
        spec_path = Path(".maid/docs/maid_specs.md")
        if spec_path.exists():
            expected = spec_path.read_text()
            assert result == expected
        else:
            # If file doesn't exist at expected path, just verify we got content
            assert len(result) > 0
