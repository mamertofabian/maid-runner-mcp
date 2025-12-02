"""MCP tool for MAID test stub generation."""

import asyncio
import subprocess
from typing import TypedDict

from maid_runner_mcp.server import mcp


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
async def maid_generate_stubs(manifest_path: str) -> GenerateStubsResult:
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
        manifest_path: Path to the manifest JSON file

    Returns:
        GenerateStubsResult with generation outcome
    """
    # Build command
    cmd = ["uv", "run", "maid", "generate-stubs", manifest_path]

    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(
            None, lambda: subprocess.run(cmd, capture_output=True, text=True)
        )

        success = result.returncode == 0
        errors: list[str] = []
        generated_files: list[str] = []

        if not success:
            # Parse error output
            error_output = result.stderr or result.stdout
            if error_output:
                errors = [line.strip() for line in error_output.strip().split("\n") if line.strip()]
        else:
            # Parse successful output for generated file paths
            output = result.stdout or ""
            for line in output.split("\n"):
                # Look for lines like "Test stub generated: tests/test_task_XXX_*.py"
                if "generated:" in line.lower() and ".py" in line:
                    # Extract path from output
                    parts = line.split(":")
                    if len(parts) >= 2:
                        file_path = parts[1].strip()
                        if file_path:
                            generated_files.append(file_path)

        return GenerateStubsResult(
            success=success,
            manifest_path=manifest_path,
            generated_files=generated_files,
            errors=errors,
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
