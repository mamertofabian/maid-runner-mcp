"""MCP resource for accessing MAID manifest schema."""

import asyncio
import subprocess

from mcp.server.fastmcp import Context

from maid_runner_mcp.server import mcp
from maid_runner_mcp.utils.roots import get_working_directory


@mcp.resource("schema://manifest")
async def get_manifest_schema(ctx: Context) -> str:
    """MCP resource handler for accessing the MAID manifest JSON schema.

    Provides read-only access to the manifest schema by calling the MAID CLI.

    Args:
        ctx: MCP context containing session information (roots)

    Returns:
        str: The manifest schema as a JSON string

    Raises:
        RuntimeError: If schema retrieval fails
    """
    # Get working directory from MCP roots
    cwd = await get_working_directory(ctx)

    # Build command
    cmd = ["uv", "run", "maid", "schema"]

    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(
            None, lambda: subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
        )

        if result.returncode == 0:
            # Return schema as string
            return result.stdout
        else:
            # Parse error output
            error_output = result.stderr or result.stdout
            raise RuntimeError(f"Failed to retrieve schema: {error_output}")

    except FileNotFoundError:
        raise RuntimeError("MAID Runner command not found")
    except subprocess.SubprocessError as e:
        raise RuntimeError(f"Failed to retrieve schema: {e}")
