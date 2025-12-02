"""Utility functions for working with MCP session roots.

This module provides helpers for extracting information from
MCP session roots, such as the working directory.
"""

from urllib.parse import unquote, urlparse

from mcp.server.fastmcp import Context


async def get_working_directory(ctx: Context) -> str | None:
    """Get working directory from MCP roots.

    Finds first file:// root URI and extracts the path.
    Returns None if no file roots available.

    Args:
        ctx: The FastMCP Context object containing the session.

    Returns:
        The path from the first file:// root URI, or None if no
        file roots are found or on error.
    """
    try:
        # Handle None session
        if ctx.session is None:
            return None

        # Get roots from session
        roots_result = await ctx.session.list_roots()

        # Check if we have any roots
        if not roots_result.roots:
            return None

        # Find first file:// root
        for root in roots_result.roots:
            uri_str = str(root.uri)
            if uri_str.startswith("file://"):
                # Parse the URI and extract the path
                parsed = urlparse(uri_str)
                # unquote handles percent-encoded characters
                path = unquote(parsed.path)

                # Handle Windows-style URIs (file:///C:/path)
                # The path will be /C:/path, need to remove leading /
                if len(path) >= 3 and path[0] == "/" and path[2] == ":":
                    path = path[1:]

                return path

        # No file:// roots found
        return None

    except Exception:
        # Return None on any error
        return None
