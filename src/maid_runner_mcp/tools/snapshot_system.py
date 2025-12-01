"""MCP tool for MAID system-wide manifest snapshot generation."""

import asyncio
import subprocess
from typing import TypedDict

from maid_runner_mcp.server import mcp


class SystemSnapshotResult(TypedDict):
    """Result of system-wide manifest snapshot generation.

    Fields:
        success: Whether snapshot generation succeeded
        output_path: Path to the generated system manifest file
        errors: List of error messages if generation failed
    """

    success: bool
    output_path: str
    errors: list[str]


@mcp.tool()
async def maid_snapshot_system(
    output: str = "system.manifest.json",
    manifest_dir: str = "manifests",
    quiet: bool = True,
) -> SystemSnapshotResult:
    """Generate a system-wide manifest snapshot using MAID Runner.

    Args:
        output: Path to the output system manifest file (default: "system.manifest.json")
        manifest_dir: Directory containing individual manifests (default: "manifests")
        quiet: Whether to suppress progress output (default: True)

    Returns:
        SystemSnapshotResult with generation outcome
    """
    # Build command
    cmd = ["uv", "run", "maid", "snapshot-system"]

    cmd.extend(["--output", output])
    cmd.extend(["--manifest-dir", manifest_dir])

    if quiet:
        cmd.append("--quiet")

    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(
            None, lambda: subprocess.run(cmd, capture_output=True, text=True)
        )

        success = result.returncode == 0
        errors: list[str] = []
        output_path = output

        if not success:
            # Parse error output
            error_output = result.stderr or result.stdout
            if error_output:
                errors = [line.strip() for line in error_output.strip().split("\n") if line.strip()]
        else:
            # Parse successful output for output path confirmation
            stdout = result.stdout or ""
            # If output mentions a different path, use it
            for line in stdout.split("\n"):
                if "system" in line.lower() and ".json" in line:
                    # Extract path from output
                    parts = line.split()
                    for part in parts:
                        if part.endswith(".json"):
                            output_path = part
                            break

        return SystemSnapshotResult(
            success=success,
            output_path=output_path,
            errors=errors,
        )

    except FileNotFoundError:
        return SystemSnapshotResult(
            success=False,
            output_path=output,
            errors=[f"Manifest directory not found: {manifest_dir}"],
        )
    except Exception as e:
        return SystemSnapshotResult(
            success=False,
            output_path=output,
            errors=[str(e)],
        )
