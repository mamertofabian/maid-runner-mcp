"""MAID Runner MCP Server.

Minimal MCP server that provides the foundation for MAID Runner tool integration.
Uses stdio transport for communication with MCP clients like Claude Code.
"""

import asyncio
import io

from mcp.server import Server
from mcp.server.stdio import stdio_server

from maid_runner_mcp.__version__ import __version__


def create_server() -> Server:
    """Factory function to create and configure MCP server instance.

    Returns:
        Server: Configured MCP server instance with metadata.
    """
    server = Server(name="maid-runner-mcp", version=__version__)
    return server


def main() -> None:
    """Entry point that runs the MCP server with stdio transport.

    Starts the MCP server using stdio transport (stdin/stdout) for communication
    with MCP clients. Handles KeyboardInterrupt gracefully for clean shutdown.
    """

    async def _run_server() -> None:
        """Async helper to run the server."""
        server = create_server()

        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())

    try:
        asyncio.run(_run_server())
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        pass
    except io.UnsupportedOperation:
        # Handle stdio transport errors gracefully (e.g., in test environments)
        # where stdin/stdout may not be available or readable
        pass
