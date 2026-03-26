"""MCP tool for MAID manifest snapshot generation."""

import asyncio
from typing import TypedDict

from mcp.server.fastmcp import Context

from maid_runner import generate_snapshot
from maid_runner.core.snapshot import save_snapshot, generate_test_stub
from maid_runner_mcp.server import mcp
from maid_runner_mcp.utils.roots import get_working_directory


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
    ctx: Context,
    file_path: str,
    output_dir: str = "manifests",
    force: bool = False,
    skip_test_stub: bool = False,
) -> SnapshotResult:
    """Generate a manifest snapshot from existing code using MAID Runner.

    **When to use:**
    - Onboarding existing code: Create manifests for pre-existing files
    - Before refactoring: Capture current state as a baseline
    - Documentation: Generate manifest to document existing APIs

    **Key behavior:**
    - Analyzes source file to extract public artifacts (functions, classes)
    - Creates a manifest with expectedArtifacts matching current code
    - Optionally generates test stub file for the manifest

    **Tips:**
    - Use before making changes to existing code without manifests
    - The generated manifest serves as a "snapshot" of current state
    - Review and adjust the generated manifest as needed

    Args:
        file_path: Path to the source file to generate a snapshot for
        output_dir: Directory to output the manifest (default: "manifests")
        force: Whether to overwrite existing manifest files
        skip_test_stub: Whether to skip generating test stub file

    Returns:
        SnapshotResult with generation outcome
    """
    cwd = await get_working_directory(ctx)

    loop = asyncio.get_event_loop()
    try:
        project_root = cwd or "."

        manifest = await loop.run_in_executor(
            None,
            lambda: generate_snapshot(file_path, project_root=project_root),
        )

        manifest_path = await loop.run_in_executor(
            None,
            lambda: save_snapshot(manifest, output_dir=output_dir),
        )

        test_stub_path: str | None = None
        if not skip_test_stub:
            stub_result = await loop.run_in_executor(
                None,
                lambda: generate_test_stub(manifest),
            )
            if stub_result:
                test_stub_path = next(iter(stub_result.values()), None)

        superseded = list(manifest.supersedes) if manifest.supersedes else []

        return SnapshotResult(
            success=True,
            manifest_path=str(manifest_path),
            test_stub_path=test_stub_path,
            superseded_manifests=superseded,
            errors=[],
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
