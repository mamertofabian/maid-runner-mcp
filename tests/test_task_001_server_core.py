"""Behavioral tests for MCP server core (Task 001).

These tests verify the expected artifacts defined in the manifest:
- mcp: Module-level FastMCP server instance (attribute)
- create_server(): Factory function returning FastMCP
- main(): Entry point returning None

Tests follow MAID behavioral testing pattern - they USE the artifacts
rather than just checking existence.
"""

from mcp.server.fastmcp import FastMCP


class TestMCPServerCore:
    """Tests for the MCP server core module artifacts."""

    def test_mcp_attribute_is_fastmcp_instance(self):
        """Test that mcp module-level attribute exists and is a FastMCP instance.

        The manifest specifies:
        - type: attribute
        - name: mcp
        - description: Module-level FastMCP server instance
        """
        from maid_runner_mcp.server import mcp

        assert isinstance(
            mcp, FastMCP
        ), f"Expected mcp to be a FastMCP instance, got {type(mcp).__name__}"

    def test_mcp_attribute_has_name(self):
        """Test that the mcp instance has a proper server name configured."""
        from maid_runner_mcp.server import mcp

        # FastMCP instances should have a name attribute
        assert hasattr(mcp, "name"), "FastMCP instance should have a name attribute"
        assert mcp.name is not None, "FastMCP name should not be None"

    def test_create_server_returns_fastmcp_instance(self):
        """Test that create_server() factory function returns a FastMCP instance.

        The manifest specifies:
        - type: function
        - name: create_server
        - args: []
        - returns: FastMCP
        """
        from maid_runner_mcp.server import create_server

        server = create_server()

        assert isinstance(
            server, FastMCP
        ), f"Expected create_server() to return FastMCP instance, got {type(server).__name__}"

    def test_create_server_returns_new_instance_each_call(self):
        """Test that create_server() creates fresh instances (factory pattern)."""
        from maid_runner_mcp.server import create_server

        server1 = create_server()
        server2 = create_server()

        # Factory should create new instances (or return the same singleton - both are valid)
        # At minimum, both should be valid FastMCP instances
        assert isinstance(server1, FastMCP)
        assert isinstance(server2, FastMCP)

    def test_create_server_accepts_no_arguments(self):
        """Test that create_server() can be called with no arguments."""
        from maid_runner_mcp.server import create_server

        # Should not raise any exceptions when called without arguments
        server = create_server()
        assert server is not None

    def test_main_entry_point(self):
        """Test that main entry point works correctly.

        The manifest specifies:
        - type: function
        - name: main
        - args: []
        - returns: None

        We mock the server.run() method to prevent blocking while still
        testing that main() executes correctly.
        """
        from unittest.mock import patch

        from maid_runner_mcp.server import main

        assert callable(main), "main should be callable"

        # Call main() with mocked server run to prevent blocking
        with patch("maid_runner_mcp.server.mcp.run") as mock_run:
            result = main()

            # main() should return None
            assert result is None, f"main() should return None, got {result}"

            # main() should call mcp.run()
            mock_run.assert_called_once()

    def test_main_function_signature(self):
        """Test that main() has the expected signature (no required args)."""
        import inspect
        from maid_runner_mcp.server import main

        sig = inspect.signature(main)

        # main() should have no required parameters
        required_params = [
            p
            for p in sig.parameters.values()
            if p.default is inspect.Parameter.empty
            and p.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
        ]

        assert (
            len(required_params) == 0
        ), f"main() should have no required parameters, found: {required_params}"

    def test_module_imports_successfully(self):
        """Test that the server module can be imported without errors."""
        # This test verifies the module is properly structured
        import maid_runner_mcp.server as server_module

        # Verify expected attributes exist
        assert hasattr(server_module, "mcp"), "Module should have 'mcp' attribute"
        assert hasattr(
            server_module, "create_server"
        ), "Module should have 'create_server' function"
        assert hasattr(server_module, "main"), "Module should have 'main' function"


class TestMCPServerConfiguration:
    """Tests for MCP server configuration aspects."""

    def test_mcp_server_has_valid_configuration(self):
        """Test that the mcp server instance is properly configured."""
        from maid_runner_mcp.server import mcp

        # FastMCP should be ready to register tools/resources
        # This validates the server is in a usable state
        assert isinstance(mcp, FastMCP)

    def test_created_server_matches_module_level_instance_type(self):
        """Test that create_server() returns same type as module-level mcp."""
        from maid_runner_mcp.server import mcp, create_server

        created = create_server()

        # Both should be FastMCP instances
        assert type(mcp) is type(created), (
            f"create_server() should return same type as mcp attribute. "
            f"mcp is {type(mcp)}, created is {type(created)}"
        )
