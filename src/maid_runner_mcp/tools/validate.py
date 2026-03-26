"""MCP tool for MAID manifest validation."""

import asyncio
import json
from pathlib import Path
from typing import Any, TypedDict, cast

from mcp.server.fastmcp import Context

from maid_runner import validate as maid_runner_validate, ValidationMode
from maid_runner.core.manifest import validate_manifest_schema
from maid_runner_mcp.server import mcp
from maid_runner_mcp.resources.validation import _validation_cache
from maid_runner_mcp.utils.roots import get_working_directory


class ValidateResult(TypedDict, total=False):
    """Result of manifest validation.

    Fields:
        success: Whether validation passed
        mode: Validation mode used (implementation, behavioral, or schema)
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


_MODE_MAP: dict[str, ValidationMode] = {
    "implementation": ValidationMode.IMPLEMENTATION,
    "behavioral": ValidationMode.BEHAVIORAL,
}


def _validate_schema(manifest_path: str, project_root: str | None) -> dict[str, Any]:
    """Run schema-only validation on a manifest file."""
    resolved = Path(project_root or ".") / manifest_path
    if not resolved.exists():
        resolved = Path(manifest_path)
    data = json.loads(resolved.read_text())
    errors = validate_manifest_schema(data)
    return {
        "success": len(errors) == 0,
        "errors": errors,
        "target_file": "",
    }


@mcp.tool()
async def maid_validate(
    manifest_path: str,
    ctx: Context,
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
    - `schema`: Checks that the manifest structure conforms to the JSON schema

    **Use manifest chain when:**
    - Editing existing files (taskType: "edit")
    - The file has previous manifests that define its history
    - You need to verify the full history of changes is valid

    Args:
        manifest_path: Path to the manifest JSON file
        validation_mode: Validation mode (implementation, behavioral, or schema)
        use_manifest_chain: Whether to use manifest chain for validation
        manifest_dir: Directory containing manifests (optional)
        quiet: Whether to suppress verbose output
        ctx: MCP context for accessing working directory

    Returns:
        ValidateResult with validation outcome
    """
    try:
        cwd = await get_working_directory(ctx)
        loop = asyncio.get_event_loop()

        if validation_mode == "schema":
            result_dict = await loop.run_in_executor(
                None,
                lambda: _validate_schema(manifest_path, cwd),
            )
        else:
            mode = _MODE_MAP.get(validation_mode, ValidationMode.IMPLEMENTATION)

            kwargs: dict[str, Any] = {
                "mode": mode,
                "use_chain": use_manifest_chain,
            }
            if cwd:
                kwargs["project_root"] = cwd
            if manifest_dir:
                kwargs["manifest_dir"] = manifest_dir

            result = await loop.run_in_executor(
                None,
                lambda: maid_runner_validate(manifest_path, **kwargs),
            )
            result_dict = result.to_dict()

        validate_result = ValidateResult(
            success=result_dict.get("success", False),
            mode=validation_mode,
            manifest=manifest_path,
            target_file=result_dict.get("target_file", ""),
            used_chain=use_manifest_chain,
            errors=result_dict.get("errors", []),
            file_tracking=result_dict.get("file_tracking"),
        )

        # Cache the validation result by manifest name
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
