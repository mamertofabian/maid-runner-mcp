"""Validation tool for MAID Runner MCP.

This module implements the maid_validate MCP tool which wraps the MAID Runner
validate command. It provides async execution, structured output, and comprehensive
error handling for manifest validation.
"""

import asyncio
import json
from typing import Any


async def maid_validate(
    manifest_path: str,
    validation_mode: str = "implementation",
    use_manifest_chain: bool = False,
    manifest_dir: str | None = None,
    quiet: bool = True,
) -> dict[str, Any]:
    """MCP tool that validates a MAID manifest against implementation or behavioral tests.

    This function wraps the MAID Runner `validate` CLI command and returns structured
    validation results. It executes the validation asynchronously and parses both
    stdout and stderr to provide comprehensive feedback.

    Args:
        manifest_path: Path to the manifest JSON file to validate
        validation_mode: Validation mode - 'implementation' (default) or 'behavioral'
        use_manifest_chain: Whether to use manifest chain for validation (default: False)
        manifest_dir: Optional custom manifest directory path
        quiet: Enable quiet mode - suppress success messages (default: True)

    Returns:
        Dictionary containing validation results with the following structure:
        {
            "success": bool,           # True if validation passed
            "manifest": str,           # Path to the validated manifest
            "mode": str,               # Validation mode used
            "use_manifest_chain": bool, # Whether chain was used
            "manifest_dir": str,       # Manifest directory (if specified)
            "quiet": bool,             # Quiet mode setting
            "target_file": str,        # Target file from manifest (if available)
            "errors": list[str],       # List of error messages (if any)
            "file_tracking": dict,     # File tracking info (if available)
        }

    Examples:
        >>> result = await maid_validate("manifests/task-001.manifest.json")
        >>> result["success"]
        True

        >>> result = await maid_validate(
        ...     "manifests/task-002.manifest.json",
        ...     validation_mode="behavioral",
        ...     use_manifest_chain=True
        ... )
    """
    # Build command arguments
    cmd = ["maid", "validate", manifest_path]

    # Add validation mode
    cmd.extend(["--validation-mode", validation_mode])

    # Add manifest chain flag
    if use_manifest_chain:
        cmd.append("--use-manifest-chain")

    # Add manifest directory
    if manifest_dir:
        cmd.extend(["--manifest-dir", manifest_dir])

    # Add quiet flag
    if quiet:
        cmd.append("--quiet")

    # Initialize result structure
    result: dict[str, Any] = {
        "success": False,
        "manifest": manifest_path,
        "mode": validation_mode,
        "use_manifest_chain": use_manifest_chain,
        "quiet": quiet,
    }

    # Add optional fields
    if manifest_dir:
        result["manifest_dir"] = manifest_dir

    try:
        # Execute the validation command asynchronously
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        # Wait for command to complete and capture output
        stdout_bytes, stderr_bytes = await process.communicate()

        # Decode output
        stdout = stdout_bytes.decode("utf-8", errors="replace")
        stderr = stderr_bytes.decode("utf-8", errors="replace")

        # Parse validation results
        if process.returncode == 0:
            result["success"] = True

            # Try to extract target file from stdout
            target_file = _extract_target_file(stdout)
            if target_file:
                result["target_file"] = target_file

            # Try to extract file tracking info
            file_tracking = _extract_file_tracking(stdout)
            if file_tracking:
                result["file_tracking"] = file_tracking
        else:
            # Parse errors from stderr
            errors = _parse_errors(stderr, stdout)
            result["errors"] = errors

    except asyncio.TimeoutError:
        # Handle timeout
        result["errors"] = ["Validation command timed out"]

    except OSError as e:
        # Handle subprocess errors (e.g., command not found)
        result["errors"] = [f"Failed to execute validation command: {str(e)}"]

    except Exception as e:
        # Handle unexpected errors
        result["errors"] = [f"Unexpected error during validation: {str(e)}"]

    return result


def _extract_target_file(output: str) -> str | None:
    """Extract target file path from validation output.

    Args:
        output: stdout from validation command

    Returns:
        Target file path if found, None otherwise
    """
    # Look for patterns like "Target: file.py" or "Validating: file.py"
    for line in output.splitlines():
        if "Target:" in line:
            parts = line.split("Target:", 1)
            if len(parts) == 2:
                return parts[1].strip()
        if "Validating:" in line:
            parts = line.split("Validating:", 1)
            if len(parts) == 2:
                return parts[1].strip()

    return None


def _extract_file_tracking(output: str) -> dict[str, Any] | None:
    """Extract file tracking information from validation output.

    Args:
        output: stdout from validation command

    Returns:
        File tracking dictionary if found, None otherwise
    """
    # Try to find JSON blocks in output that might contain file tracking
    try:
        # Look for JSON-like structures in the output
        for line in output.splitlines():
            line = line.strip()
            if line.startswith("{") and line.endswith("}"):
                try:
                    data = json.loads(line)
                    if isinstance(data, dict) and ("file_tracking" in data or "files" in data):
                        return data
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass

    return None


def _parse_errors(stderr: str, stdout: str) -> list[str]:
    """Parse error messages from validation output.

    Extracts error messages from stderr and stdout, filtering out empty lines
    and providing structured error information.

    Args:
        stderr: stderr output from validation command
        stdout: stdout output from validation command (may contain errors)

    Returns:
        List of error message strings
    """
    errors: list[str] = []

    # Parse stderr for errors
    for line in stderr.splitlines():
        line = line.strip()
        if line:
            errors.append(line)

    # If no errors in stderr, check stdout for error indicators
    if not errors:
        for line in stdout.splitlines():
            line = line.strip()
            if line and (
                line.startswith("Error:")
                or line.startswith("ERROR:")
                or "failed" in line.lower()
                or "error" in line.lower()
            ):
                errors.append(line)

    # If still no errors, provide a generic message
    if not errors:
        errors.append("Validation failed (no specific error message available)")

    return errors
