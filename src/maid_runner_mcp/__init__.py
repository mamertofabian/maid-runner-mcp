"""MAID Runner MCP - Model Context Protocol server for MAID Runner.

Exposes MAID Runner validation tools to AI agents via MCP protocol.
"""

from maid_runner_mcp.__version__ import __version__
from maid_runner_mcp import prompts

__all__ = ["__version__", "prompts"]
