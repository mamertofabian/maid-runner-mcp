"""MCP resource for accessing system-wide manifest snapshots."""

import asyncio
import subprocess
import tempfile
from pathlib import Path

from maid_runner_mcp.server import mcp
from maid_runner_mcp.utils.cache import TTLCache


# TTL cache for system snapshot (5 minutes)
_snapshot_cache: TTLCache[str] = TTLCache(ttl_seconds=300)


@mcp.resource("snapshot://system")
async def get_system_snapshot() -> str:
    """MCP resource handler for accessing the system-wide manifest snapshot.

    Provides read-only access to the system-wide snapshot by calling MAID CLI.
    Results are cached for 5 minutes to reduce CLI overhead.

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

    # Create temporary file for snapshot output
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        # Build command - generate to temp file with quiet flag
        cmd = [
            "uv",
            "run",
            "maid",
            "snapshot-system",
            "--output",
            tmp_path,
            "--quiet",
        ]

        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, lambda: subprocess.run(cmd, capture_output=True, text=True)
        )

        if result.returncode == 0:
            # Read the generated JSON file
            snapshot = Path(tmp_path).read_text(encoding="utf-8")

            # Cache and return snapshot as string
            _snapshot_cache.set(cache_key, snapshot)
            return snapshot
        else:
            # Parse error output
            error_output = result.stderr or result.stdout
            raise RuntimeError(f"Failed to generate system snapshot: {error_output}")

    except FileNotFoundError:
        raise RuntimeError("MAID Runner command not found")
    except subprocess.SubprocessError as e:
        raise RuntimeError(f"Failed to generate system snapshot: {e}")
    finally:
        # Clean up temporary file
        try:
            Path(tmp_path).unlink()
        except Exception:
            pass  # Ignore cleanup errors
