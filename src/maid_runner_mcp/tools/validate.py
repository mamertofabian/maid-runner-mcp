"""MCP tool for MAID manifest validation."""

import asyncio
import subprocess
from typing import TypedDict

from maid_runner_mcp.server import mcp


class ValidateResult(TypedDict, total=False):
    """Result of manifest validation.

    Fields:
        success: Whether validation passed
        mode: Validation mode used (implementation or behavioral)
        manifest: Path to the manifest file
        target_file: Target file being validated
        used_chain: Whether manifest chain was used
        errors: List of error messages if validation failed
        file_tracking: Optional file tracking information
    """

    success: bool
    mode: str
    manifest: str
    target_file: str
    used_chain: bool
    errors: list[str]
    file_tracking: dict | None


@mcp.tool()
async def maid_validate(
    manifest_path: str,
    validation_mode: str = "implementation",
    use_manifest_chain: bool = False,
    manifest_dir: str | None = None,
    quiet: bool = True,
) -> ValidateResult:
    """Validate a MAID manifest using MAID Runner.

    Args:
        manifest_path: Path to the manifest JSON file
        validation_mode: Validation mode (implementation or behavioral)
        use_manifest_chain: Whether to use manifest chain for validation
        manifest_dir: Directory containing manifests (optional)
        quiet: Whether to suppress verbose output

    Returns:
        ValidateResult with validation outcome
    """
    # Build command
    cmd = ["uv", "run", "maid", "validate", manifest_path]

    if validation_mode:
        cmd.extend(["--validation-mode", validation_mode])

    if use_manifest_chain:
        cmd.append("--use-manifest-chain")

    if manifest_dir:
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

        if not success:
            # Parse error output
            error_output = result.stderr or result.stdout
            if error_output:
                errors = [line.strip() for line in error_output.strip().split("\n") if line.strip()]

        return ValidateResult(
            success=success,
            mode=validation_mode,
            manifest=manifest_path,
            target_file="",  # Would need to parse from output
            used_chain=use_manifest_chain,
            errors=errors,
            file_tracking=None,
        )

    except FileNotFoundError:
        return ValidateResult(
            success=False,
            mode=validation_mode,
            manifest=manifest_path,
            target_file="",
            used_chain=use_manifest_chain,
            errors=[f"Manifest file not found: {manifest_path}"],
            file_tracking=None,
        )
    except Exception as e:
        return ValidateResult(
            success=False,
            mode=validation_mode,
            manifest=manifest_path,
            target_file="",
            used_chain=use_manifest_chain,
            errors=[str(e)],
            file_tracking=None,
        )
