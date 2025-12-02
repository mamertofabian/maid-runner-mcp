"""MCP tool for file tracking status using MAID Runner."""

import asyncio
import json
import subprocess
from typing import TypedDict


from maid_runner_mcp.server import mcp


class FileInfo(TypedDict):
    """Individual file tracking information.

    Fields:
        file: The file path
        status: The tracking status (e.g., "undeclared", "registered")
        issues: List of issues with the file
        manifests: List of manifests referencing the file
    """

    file: str
    status: str
    issues: list[str]
    manifests: list[str]


class FileTrackingResult(TypedDict):
    """Result of file tracking analysis.

    Fields:
        undeclared: List of files not declared in any manifest
        registered: List of files registered but with potential issues
        tracked: List of fully tracked file paths
    """

    undeclared: list[FileInfo]
    registered: list[FileInfo]
    tracked: list[str]


@mcp.tool()
async def maid_files(
    manifest_dir: str = "manifests",
    issues_only: bool = False,
    status: str | None = None,
) -> FileTrackingResult:
    """Get file-level tracking status using MAID Runner.

    **When to use:**
    - Project health check: See which files lack manifests
    - Onboarding: Identify files that need to be brought under MAID
    - Compliance audit: Ensure all source files are tracked

    **Status categories:**
    - `undeclared`: Files not referenced in any manifest (needs attention)
    - `registered`: Files in manifests but with potential issues
    - `tracked`: Files fully compliant with MAID methodology

    **Tips:**
    - Use `issues_only=True` to focus on problem files
    - Filter by `status="undeclared"` to find files needing manifests
    - Run periodically to maintain MAID compliance

    Args:
        manifest_dir: Directory containing manifests (default: "manifests")
        issues_only: If True, only show files with issues
        status: Filter by status (e.g., "undeclared", "registered", "tracked")

    Returns:
        FileTrackingResult with categorized files
    """
    # Build command
    cmd = ["uv", "run", "maid", "files", "--manifest-dir", manifest_dir, "--json"]

    if issues_only:
        cmd.append("--issues-only")

    if status is not None:
        cmd.extend(["--status", status])

    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(
            None, lambda: subprocess.run(cmd, capture_output=True, text=True)
        )

        # Check for errors
        if result.returncode != 0:
            return FileTrackingResult(
                undeclared=[],
                registered=[],
                tracked=[],
            )

        # Parse JSON output
        try:
            data = json.loads(result.stdout)
            return FileTrackingResult(
                undeclared=data.get("undeclared", []),
                registered=data.get("registered", []),
                tracked=data.get("tracked", []),
            )
        except json.JSONDecodeError:
            return FileTrackingResult(
                undeclared=[],
                registered=[],
                tracked=[],
            )

    except FileNotFoundError:
        return FileTrackingResult(
            undeclared=[],
            registered=[],
            tracked=[],
        )
    except Exception:
        return FileTrackingResult(
            undeclared=[],
            registered=[],
            tracked=[],
        )
