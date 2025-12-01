"""MCP tool for MAID manifest snapshot generation."""

import asyncio
import subprocess
from typing import TypedDict

from maid_runner_mcp.server import mcp


class SnapshotResult(TypedDict, total=False):
    """Result of manifest snapshot generation.

    Fields:
        success: Whether snapshot generation succeeded
        manifest_path: Path to the generated manifest file
        test_stub_path: Path to the generated test stub file (optional)
        superseded_manifests: List of manifests that are superseded
        errors: List of error messages if generation failed
    """

    success: bool
    manifest_path: str
    test_stub_path: str | None
    superseded_manifests: list[str]
    errors: list[str]


@mcp.tool()
async def maid_snapshot(
    file_path: str,
    output_dir: str = "manifests",
    force: bool = False,
    skip_test_stub: bool = False,
) -> SnapshotResult:
    """Generate a manifest snapshot from existing code using MAID Runner.

    Args:
        file_path: Path to the source file to generate a snapshot for
        output_dir: Directory to output the manifest (default: "manifests")
        force: Whether to overwrite existing manifest files
        skip_test_stub: Whether to skip generating test stub file

    Returns:
        SnapshotResult with generation outcome
    """
    # Build command
    cmd = ["uv", "run", "maid", "snapshot", file_path]

    cmd.extend(["--output-dir", output_dir])

    if force:
        cmd.append("--force")

    if skip_test_stub:
        cmd.append("--skip-test-stub")

    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(
            None, lambda: subprocess.run(cmd, capture_output=True, text=True)
        )

        success = result.returncode == 0
        errors: list[str] = []
        manifest_path = ""
        test_stub_path: str | None = None
        superseded_manifests: list[str] = []

        if not success:
            # Parse error output
            error_output = result.stderr or result.stdout
            if error_output:
                errors = [line.strip() for line in error_output.strip().split("\n") if line.strip()]
        else:
            # Parse successful output for manifest path
            output = result.stdout or ""
            for line in output.split("\n"):
                if "manifest" in line.lower() and ".json" in line:
                    # Extract path from output
                    parts = line.split()
                    for part in parts:
                        if part.endswith(".json"):
                            manifest_path = part
                            break
                if "test" in line.lower() and ".py" in line:
                    # Extract test stub path
                    parts = line.split()
                    for part in parts:
                        if part.endswith(".py"):
                            test_stub_path = part
                            break

        return SnapshotResult(
            success=success,
            manifest_path=manifest_path,
            test_stub_path=test_stub_path,
            superseded_manifests=superseded_manifests,
            errors=errors,
        )

    except FileNotFoundError:
        return SnapshotResult(
            success=False,
            manifest_path="",
            test_stub_path=None,
            superseded_manifests=[],
            errors=[f"Source file not found: {file_path}"],
        )
    except Exception as e:
        return SnapshotResult(
            success=False,
            manifest_path="",
            test_stub_path=None,
            superseded_manifests=[],
            errors=[str(e)],
        )
