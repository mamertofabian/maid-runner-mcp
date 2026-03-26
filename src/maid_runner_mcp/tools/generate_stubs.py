"""MCP tool for MAID test stub generation."""

import asyncio
from pathlib import Path
from typing import TypedDict

from mcp.server.fastmcp import Context

from maid_runner import load_manifest
from maid_runner.core.snapshot import generate_test_stub
from maid_runner_mcp.server import mcp
from maid_runner_mcp.utils.roots import get_working_directory


class GenerateStubsResult(TypedDict):
    """Result of test stub generation.

    Fields:
        success: Whether stub generation succeeded
        manifest_path: Path to the manifest file
        generated_files: List of generated test stub file paths
        errors: List of error messages if generation failed
    """

    success: bool
    manifest_path: str
    generated_files: list[str]
    errors: list[str]


@mcp.tool()
async def maid_generate_stubs(ctx: Context, manifest_path: str) -> GenerateStubsResult:
    """Generate test stubs from a manifest using MAID Runner.

    **When to use:**
    - Phase 2 (Planning): After creating manifest, generate test file skeleton
    - Jumpstarting tests: Create boilerplate test structure from manifest
    - Consistency: Ensure test file naming matches manifest conventions

    **What it generates:**
    - Test file with naming pattern: `tests/test_task_XXX_*.py`
    - Test class structure based on expectedArtifacts
    - Import statements for artifacts being tested
    - Placeholder test methods for each artifact

    **Tips:**
    - Run after creating/updating a manifest
    - Generated stubs are starting points - add assertions
    - Test file is added to manifest's `readonlyFiles` automatically

    Args:
        ctx: MCP context containing session and roots information
        manifest_path: Path to the manifest JSON file

    Returns:
        GenerateStubsResult with generation outcome
    """
    cwd = await get_working_directory(ctx)

    loop = asyncio.get_event_loop()
    try:
        # Resolve manifest path relative to project root
        resolved_path = Path(cwd or ".") / manifest_path
        if not resolved_path.exists():
            resolved_path = Path(manifest_path)

        manifest = await loop.run_in_executor(
            None,
            lambda: load_manifest(resolved_path),
        )

        stub_files = await loop.run_in_executor(
            None,
            lambda: generate_test_stub(manifest),
        )

        generated_files = list(stub_files.keys()) if stub_files else []

        return GenerateStubsResult(
            success=True,
            manifest_path=manifest_path,
            generated_files=generated_files,
            errors=[],
        )

    except FileNotFoundError:
        return GenerateStubsResult(
            success=False,
            manifest_path=manifest_path,
            generated_files=[],
            errors=[f"Manifest file not found: {manifest_path}"],
        )
    except Exception as e:
        return GenerateStubsResult(
            success=False,
            manifest_path=manifest_path,
            generated_files=[],
            errors=[str(e)],
        )
