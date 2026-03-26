"""MCP tool for MAID system-wide manifest snapshot generation."""

import asyncio
from typing import TypedDict

from mcp.server.fastmcp import Context

from maid_runner.core.snapshot import generate_system_snapshot, save_snapshot
from maid_runner_mcp.server import mcp
from maid_runner_mcp.utils.roots import get_working_directory


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
    ctx: Context,
    output: str = "system.manifest.json",
    manifest_dir: str = "manifests",
    quiet: bool = True,
) -> SystemSnapshotResult:
    """Generate a system-wide manifest snapshot using MAID Runner.

    **When to use:**
    - Documentation: Create a comprehensive view of all project artifacts
    - Architecture review: See all public APIs across the codebase
    - Dependency analysis: Understand cross-file relationships

    **What it creates:**
    - Aggregated manifest combining all individual manifests
    - System-wide view of all tracked artifacts
    - Uses `systemArtifacts` (array) instead of `expectedArtifacts` (object)

    **Tips:**
    - Run periodically to update system documentation
    - Useful for onboarding new team members
    - Compare snapshots over time to track API evolution

    Args:
        output: Path to the output system manifest file (default: "system.manifest.json")
        manifest_dir: Directory containing individual manifests (default: "manifests")
        quiet: Whether to suppress progress output (default: True)

    Returns:
        SystemSnapshotResult with generation outcome
    """
    cwd = await get_working_directory(ctx)

    loop = asyncio.get_event_loop()
    try:
        project_root = cwd or "."

        manifest = await loop.run_in_executor(
            None,
            lambda: generate_system_snapshot(
                manifest_dir=manifest_dir,
                project_root=project_root,
            ),
        )

        output_path = await loop.run_in_executor(
            None,
            lambda: save_snapshot(manifest, output=output),
        )

        return SystemSnapshotResult(
            success=True,
            output_path=str(output_path),
            errors=[],
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
