"""MCP Server for MAID Runner.

Exposes MAID Runner validation tools via Model Context Protocol (MCP).
"""

from mcp.server.fastmcp import FastMCP


# Module-level server instance (singleton)
# Tools are registered via @mcp.tool() decorators in tools modules
_server: FastMCP | None = None


def create_server() -> FastMCP:
    """Get the configured FastMCP server instance.

    Returns the singleton server instance with all registered tools.
    This ensures tools decorated with @mcp.tool() are available.

    Returns:
        FastMCP: The configured MCP server with registered tools.
    """
    global _server
    if _server is None:
        _server = FastMCP("maid-runner")
    return _server


# Initialize the server instance
mcp = create_server()

# Import tools to register them with the server
# Tools use @mcp.tool() decorator from this module
from maid_runner_mcp.tools import generate_stubs  # noqa: E402, F401
from maid_runner_mcp.tools import init  # noqa: E402, F401
from maid_runner_mcp.tools import manifests  # noqa: E402, F401
from maid_runner_mcp.tools import schema  # noqa: E402, F401
from maid_runner_mcp.tools import snapshot  # noqa: E402, F401
from maid_runner_mcp.tools import snapshot_system  # noqa: E402, F401
from maid_runner_mcp.tools import test  # noqa: E402, F401
from maid_runner_mcp.tools import validate  # noqa: E402, F401

# Import resources module to make it available for future resource implementations
import maid_runner_mcp.resources  # noqa: E402, F401


def main() -> None:
    """Entry point for the MCP server.

    Runs the server using stdio transport (default).
    """
    mcp.run()
