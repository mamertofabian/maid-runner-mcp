"""MCP resource for accessing MAID manifest schema."""

import asyncio
import subprocess

from maid_runner_mcp.server import mcp


@mcp.resource("schema://manifest")
async def get_manifest_schema() -> str:
    """MCP resource handler for accessing the MAID manifest JSON schema.

    Provides read-only access to the manifest schema by calling the MAID CLI.

    Returns:
        str: The manifest schema as a JSON string

    Raises:
        RuntimeError: If schema retrieval fails
    """
    # Build command
    cmd = ["uv", "run", "maid", "schema"]

    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(
            None, lambda: subprocess.run(cmd, capture_output=True, text=True)
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
