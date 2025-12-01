"""MCP Server for MAID Runner.

Exposes MAID Runner validation tools via Model Context Protocol (MCP).
"""

from mcp.server.fastmcp import FastMCP


def create_server() -> FastMCP:
    """Create and configure a FastMCP server instance.

    Returns:
        FastMCP: A configured MCP server ready to register tools.
    """
    return FastMCP("maid-runner")


# Module-level server instance
mcp = create_server()


def main() -> None:
    """Entry point for the MCP server.

    Runs the server using stdio transport (default).
    """
    mcp.run()
