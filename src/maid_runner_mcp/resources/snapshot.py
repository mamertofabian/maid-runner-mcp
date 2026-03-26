"""MCP resource for accessing system-wide manifest snapshots."""

import asyncio
import json

from mcp.server.fastmcp import Context

from maid_runner.core.manifest import _manifest_to_dict
from maid_runner.core.snapshot import generate_system_snapshot
from maid_runner_mcp.server import mcp
from maid_runner_mcp.utils.cache import TTLCache
from maid_runner_mcp.utils.roots import get_working_directory


# TTL cache for system snapshot (5 minutes)
_snapshot_cache: TTLCache[str] = TTLCache(ttl_seconds=300)


@mcp.resource("snapshot://system")
async def get_system_snapshot(ctx: Context) -> str:
    """MCP resource handler for accessing the system-wide manifest snapshot.

    Provides read-only access to the system-wide snapshot by calling the
    maid_runner library directly. Results are cached for 5 minutes to reduce overhead.

    Args:
        ctx: MCP context for accessing session roots

    Returns:
        str: The system snapshot as a JSON string

    Raises:
        RuntimeError: If snapshot generation fails
    """
    # Check cache first
    cache_key = "system"
    cached = _snapshot_cache.get(cache_key)
    if cached is not None:
        return cached

    cwd = await get_working_directory(ctx)
    project_root = cwd or "."

    loop = asyncio.get_event_loop()
    try:
        manifest = await loop.run_in_executor(
            None,
            lambda: generate_system_snapshot(
                manifest_dir="manifests/",
                project_root=project_root,
            ),
        )

        snapshot_json = await loop.run_in_executor(
            None,
            lambda: json.dumps(_manifest_to_dict(manifest), indent=2),
        )

        _snapshot_cache.set(cache_key, snapshot_json)
        return snapshot_json

    except FileNotFoundError:
        raise RuntimeError("Manifest directory not found")
    except Exception as e:
        raise RuntimeError(f"Failed to generate system snapshot: {e}")
