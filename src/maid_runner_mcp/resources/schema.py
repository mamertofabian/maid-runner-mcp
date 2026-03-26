"""MCP resource for accessing MAID manifest schema."""

import asyncio
from pathlib import Path

from mcp.server.fastmcp import Context

from maid_runner_mcp.server import mcp
from maid_runner_mcp.utils.roots import get_working_directory


def _get_schema_path() -> Path:
    """Get the path to the maid_runner manifest JSON schema file."""
    import maid_runner.core.manifest as manifest_mod

    schema_dir = Path(manifest_mod.__file__).parent.parent / "schemas"
    return schema_dir / "manifest.v2.schema.json"


@mcp.resource("schema://manifest")
async def get_manifest_schema(ctx: Context) -> str:
    """MCP resource handler for accessing the MAID manifest JSON schema.

    Provides read-only access to the manifest schema by reading the JSON schema
    file from the installed maid_runner package.

    Args:
        ctx: MCP context containing session information (roots)

    Returns:
        str: The manifest schema as a JSON string

    Raises:
        RuntimeError: If schema retrieval fails
    """
    await get_working_directory(ctx)

    loop = asyncio.get_event_loop()
    try:
        schema_text = await loop.run_in_executor(None, lambda: _get_schema_path().read_text())
        return schema_text

    except FileNotFoundError:
        raise RuntimeError("MAID Runner schema file not found")
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve schema: {e}")
