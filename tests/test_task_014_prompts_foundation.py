"""Tests for Task 014: Prompts Foundation.

Tests verify that the prompts module is properly initialized
and registered with the MCP server.
"""


class TestPromptsModuleStructure:
    """Test prompts module initialization."""

    def test_prompts_module_importable(self):
        """Test that prompts module can be imported."""
        from maid_runner_mcp import prompts

        assert prompts is not None

    def test_prompts_module_has_all_attribute(self):
        """Test that prompts module has __all__ attribute."""
        from maid_runner_mcp import prompts

        assert hasattr(prompts, "__all__")
        assert isinstance(prompts.__all__, list)


class TestServerIntegration:
    """Test prompts module integration with MCP server."""

    def test_server_imports_prompts_module(self):
        """Test that server imports prompts module without error."""
        # This test verifies that the server.py imports the prompts module
        # If the import fails, this will raise an ImportError
        from maid_runner_mcp import server

        assert server.mcp is not None

    def test_prompts_module_accessible_from_package(self):
        """Test prompts module is accessible from main package."""
        import maid_runner_mcp

        # Verify prompts module exists in package
        assert hasattr(maid_runner_mcp, "prompts") or "prompts" in dir(maid_runner_mcp)
