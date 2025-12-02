"""MCP tool for MAID manifest validation."""

import asyncio
import subprocess
from pathlib import Path
from typing import Any, TypedDict, cast

from maid_runner_mcp.server import mcp
from maid_runner_mcp.resources.validation import _validation_cache


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

    **When to use:**
    - Phase 2 (Planning): After creating/updating a manifest, validate it passes
    - Phase 3 (Implementation): After writing code, verify it matches the manifest
    - Before committing: Ensure all manifests are valid

    **Validation modes:**
    - `implementation`: Checks that code artifacts match manifest expectedArtifacts
    - `behavioral`: Checks that tests exist and reference the expected artifacts

    **Use manifest chain when:**
    - Editing existing files (taskType: "edit")
    - The file has previous manifests that define its history
    - You need to verify the full history of changes is valid

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

        validate_result = ValidateResult(
            success=success,
            mode=validation_mode,
            manifest=manifest_path,
            target_file="",  # Would need to parse from output
            used_chain=use_manifest_chain,
            errors=errors,
            file_tracking=None,
        )

        # Cache the validation result by manifest name
        # Extract manifest name from path (remove directory and extension)
        manifest_name = Path(manifest_path).stem
        if manifest_name.endswith(".manifest"):
            manifest_name = manifest_name[: -len(".manifest")]
        _validation_cache[manifest_name] = cast(dict[str, Any], validate_result)

        return validate_result

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
