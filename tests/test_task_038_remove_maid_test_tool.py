"""
Behavioral tests for task-038: Remove maid_test MCP tool

Goal: Remove maid_test MCP tool and update documentation to reflect that
      validation commands should be executed via Bash tool in project context

These tests verify that:
1. maid_test function is not exported from tools module
2. TestResult type is not exported from tools module
3. server.py does not import the test module
4. Documentation reflects the removal
"""

import importlib
import sys
from pathlib import Path


class TestRemoveMaidTestTool:
    """Test that maid_test tool has been removed from the codebase"""

    def test_maid_test_not_in_tools_all(self):
        """Verify maid_test is not in tools.__all__"""
        import maid_runner_mcp.tools as tools

        assert hasattr(tools, "__all__"), "tools module should have __all__ attribute"
        assert "maid_test" not in tools.__all__, "maid_test should not be in tools.__all__"

    def test_test_result_not_in_tools_all(self):
        """Verify TestResult is not in tools.__all__"""
        import maid_runner_mcp.tools as tools

        assert hasattr(tools, "__all__"), "tools module should have __all__ attribute"
        assert "TestResult" not in tools.__all__, "TestResult should not be in tools.__all__"

    def test_maid_test_not_importable(self):
        """Verify maid_test cannot be imported from tools"""
        import maid_runner_mcp.tools as tools

        assert not hasattr(
            tools, "maid_test"
        ), "maid_test should not be accessible from tools module"

    def test_test_result_not_importable(self):
        """Verify TestResult cannot be imported from tools"""
        import maid_runner_mcp.tools as tools

        assert not hasattr(
            tools, "TestResult"
        ), "TestResult should not be accessible from tools module"

    def test_test_module_not_imported_in_server(self):
        """Verify server.py does not import the test module"""
        # Reload server module to get fresh imports
        if "maid_runner_mcp.server" in sys.modules:
            importlib.reload(sys.modules["maid_runner_mcp.server"])

        server_file = Path(__file__).parent.parent / "src" / "maid_runner_mcp" / "server.py"
        content = server_file.read_text()

        # Check that test module is not imported
        assert (
            "from maid_runner_mcp.tools import test" not in content
        ), "server.py should not import test module"
        assert (
            "from .tools import test" not in content
        ), "server.py should not import test module (relative)"

    def test_maid_test_not_in_server_instructions(self):
        """Verify maid_test is documented as removed in server instructions"""
        server_file = Path(__file__).parent.parent / "src" / "maid_runner_mcp" / "server.py"
        content = server_file.read_text()

        # Verify MAID_INSTRUCTIONS is defined
        assert "MAID_INSTRUCTIONS = " in content, "MAID_INSTRUCTIONS should be defined in server.py"

        # Extract the instructions string (simplified approach)
        # Find the start of MAID_INSTRUCTIONS assignment
        start_marker = 'MAID_INSTRUCTIONS = """'
        end_marker = '""".strip()'

        start_idx = content.find(start_marker)
        assert start_idx != -1, "MAID_INSTRUCTIONS assignment not found"

        start_idx += len(start_marker)
        end_idx = content.find(end_marker, start_idx)
        assert end_idx != -1, "MAID_INSTRUCTIONS end not found"

        maid_instructions = content[start_idx:end_idx]

        # Verify maid_test is documented as NOT available
        # Should NOT list it as an available tool
        assert (
            "- `maid_test`" not in maid_instructions and "- maid_test" not in maid_instructions
        ), "maid_test should not be listed as an available tool"

        # Verify there's an explanation about why maid_test is not available
        assert (
            "validation commands" in maid_instructions.lower()
            and "bash tool" in maid_instructions.lower()
        ), "Should explain to use Bash tool for validation commands"

    def test_readme_updated(self):
        """Verify README.md does not list maid_test as an available tool"""
        readme_file = Path(__file__).parent.parent / "README.md"
        content = readme_file.read_text()

        # Should not list maid_test as an available tool
        assert (
            "- `maid_test`" not in content and "- maid_test" not in content
        ), "README.md should not list maid_test as an available tool"

    def test_claude_md_updated(self):
        """Verify CLAUDE.md does not list maid_test as an available tool"""
        claude_md_file = Path(__file__).parent.parent / "CLAUDE.md"
        content = claude_md_file.read_text()

        # Should not list maid_test in Available Tools section
        assert (
            "- `maid_test`" not in content and "- maid_test" not in content
        ), "CLAUDE.md should not list maid_test as an available tool"

    def test_other_tools_still_available(self):
        """Verify other tools are still exported and functional"""
        import maid_runner_mcp.tools as tools

        # Check that other essential tools are still available
        essential_tools = [
            "maid_validate",
            "maid_snapshot",
            "maid_list_manifests",
            "maid_init",
            "maid_get_schema",
            "maid_generate_stubs",
            "maid_files",
        ]

        for tool_name in essential_tools:
            assert tool_name in tools.__all__, f"{tool_name} should still be in __all__"
            assert hasattr(tools, tool_name), f"{tool_name} should still be importable"
