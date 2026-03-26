"""MCP tool for file tracking status using MAID Runner."""

import asyncio
from typing import TypedDict

from mcp.server.fastmcp import Context

from maid_runner import ManifestChain, ValidationEngine
from maid_runner_mcp.server import mcp
from maid_runner_mcp.utils.roots import get_working_directory


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


def _entry_to_file_info(entry: object) -> FileInfo:
    """Convert a FileTrackingEntry to a FileInfo dict."""
    return FileInfo(
        file=getattr(entry, "path", ""),
        status=str(getattr(entry, "status", "")).split(".")[-1].lower(),
        issues=list(getattr(entry, "issues", ())),
        manifests=list(getattr(entry, "manifests", ())),
    )


@mcp.tool()
async def maid_files(
    ctx: Context,
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
    cwd = await get_working_directory(ctx)

    loop = asyncio.get_event_loop()
    try:
        project_root = cwd or "."

        chain = await loop.run_in_executor(
            None,
            lambda: ManifestChain(manifest_dir, project_root=project_root),
        )

        engine = await loop.run_in_executor(
            None,
            lambda: ValidationEngine(project_root=project_root),
        )

        report = await loop.run_in_executor(
            None,
            lambda: engine.run_file_tracking(chain),
        )

        undeclared = [_entry_to_file_info(e) for e in report.undeclared]
        registered = [_entry_to_file_info(e) for e in report.registered]
        tracked = [e.path for e in report.tracked]

        # Apply filters
        if issues_only:
            undeclared = [f for f in undeclared if f["issues"]]
            registered = [f for f in registered if f["issues"]]

        if status is not None:
            if status != "undeclared":
                undeclared = []
            if status != "registered":
                registered = []
            if status != "tracked":
                tracked = []

        return FileTrackingResult(
            undeclared=undeclared,
            registered=registered,
            tracked=tracked,
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
