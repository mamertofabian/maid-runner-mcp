"""Behavioral tests for Task 024: Add MCP server instructions.

Tests verify that MAID methodology instructions are properly integrated
into the MCP server to guide AI tools in using the server effectively.

These tests USE the artifacts by:
- Accessing MAID_INSTRUCTIONS constant and verifying its content
- Calling create_server() and verifying the server has instructions
"""

import pytest


class TestMAIDInstructions:
    """Tests for the MAID_INSTRUCTIONS constant."""

    def test_maid_instructions_is_string(self) -> None:
        """MAID_INSTRUCTIONS should be a string constant."""
        from maid_runner_mcp.server import MAID_INSTRUCTIONS

        assert isinstance(MAID_INSTRUCTIONS, str)
        assert len(MAID_INSTRUCTIONS) > 0

    def test_maid_instructions_contains_workflow_phases(self) -> None:
        """Instructions should describe the MAID workflow phases."""
        from maid_runner_mcp.server import MAID_INSTRUCTIONS

        # Should mention the key phases
        assert "Phase 1" in MAID_INSTRUCTIONS or "Goal" in MAID_INSTRUCTIONS
        assert "Phase 2" in MAID_INSTRUCTIONS or "Planning" in MAID_INSTRUCTIONS
        assert "Phase 3" in MAID_INSTRUCTIONS or "Implementation" in MAID_INSTRUCTIONS

    def test_maid_instructions_contains_key_rules(self) -> None:
        """Instructions should include key MAID rules."""
        from maid_runner_mcp.server import MAID_INSTRUCTIONS

        # Should contain guidance about manifests
        assert "manifest" in MAID_INSTRUCTIONS.lower()

    def test_maid_instructions_contains_tool_guidance(self) -> None:
        """Instructions should provide guidance on using tools."""
        from maid_runner_mcp.server import MAID_INSTRUCTIONS

        # Should mention validation
        assert "validat" in MAID_INSTRUCTIONS.lower()

    def test_maid_instructions_mentions_expected_artifacts(self) -> None:
        """Instructions should mention expectedArtifacts structure."""
        from maid_runner_mcp.server import MAID_INSTRUCTIONS

        # Critical: expectedArtifacts is an OBJECT, not array
        assert "expectedArtifacts" in MAID_INSTRUCTIONS


class TestCreateServer:
    """Tests for the create_server function with instructions."""

    def test_create_server_returns_fastmcp(self) -> None:
        """create_server should return a FastMCP instance."""
        from mcp.server.fastmcp import FastMCP

        from maid_runner_mcp.server import create_server

        server = create_server()
        assert isinstance(server, FastMCP)

    def test_create_server_has_instructions(self) -> None:
        """Server created by create_server should have instructions set."""
        from maid_runner_mcp.server import MAID_INSTRUCTIONS, create_server

        server = create_server()
        # FastMCP stores instructions in the instructions attribute
        assert server.instructions is not None
        assert server.instructions == MAID_INSTRUCTIONS

    def test_create_server_instructions_not_empty(self) -> None:
        """Server instructions should not be empty."""
        from maid_runner_mcp.server import create_server

        server = create_server()
        assert server.instructions is not None
        assert len(server.instructions) > 100  # Should be substantial

    def test_server_name_is_maid_runner(self) -> None:
        """Server should be named 'maid-runner'."""
        from maid_runner_mcp.server import create_server

        server = create_server()
        assert server.name == "maid-runner"


class TestServerModuleIntegration:
    """Integration tests for the server module."""

    def test_mcp_instance_has_instructions(self) -> None:
        """The module-level mcp instance should have instructions."""
        from maid_runner_mcp.server import mcp

        assert mcp.instructions is not None
        assert len(mcp.instructions) > 0

    def test_instructions_contain_maid_workflow_summary(self) -> None:
        """Instructions should provide a workflow summary for AI tools."""
        from maid_runner_mcp.server import MAID_INSTRUCTIONS

        # Should be comprehensive enough to guide an AI
        # Minimum reasonable length for useful instructions
        assert len(MAID_INSTRUCTIONS) > 500

        # Should mention key concepts
        lower_instructions = MAID_INSTRUCTIONS.lower()
        assert "maid" in lower_instructions
        assert "tool" in lower_instructions
