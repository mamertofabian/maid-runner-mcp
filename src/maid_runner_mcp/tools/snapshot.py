"""Snapshot tool for MAID Runner MCP.

This module implements the maid_snapshot MCP tool which wraps the MAID Runner
snapshot command. It provides async execution, structured output, and comprehensive
error handling for manifest snapshot generation.
"""

import asyncio
import re
from typing import Any


async def maid_snapshot(
    file_path: str,
    output_dir: str = "manifests",
    force: bool = False,
    skip_test_stub: bool = False,
) -> dict[str, Any]:
    """MCP tool that generates a snapshot manifest from an existing Python file.

    This function wraps the MAID Runner `snapshot` CLI command and returns structured
    snapshot results. It executes the command asynchronously and parses both stdout
    and stderr to extract manifest paths, test stub paths, and superseded manifests.

    Args:
        file_path: Path to the Python file to snapshot
        output_dir: Directory for output manifest (default: "manifests")
        force: Overwrite existing manifest if it exists (default: False)
        skip_test_stub: Skip test stub generation (default: False)

    Returns:
        Dictionary containing snapshot results with the following structure:
        {
            "success": bool,                    # True if snapshot succeeded
            "manifest_path": str,               # Path to generated manifest
            "test_stub_path": str | None,       # Path to test stub (if generated)
            "superseded_manifests": list[str],  # List of superseded manifest filenames
            "errors": list[str],                # List of error messages (if any)
        }

    Examples:
        >>> result = await maid_snapshot("src/module.py")
        >>> result["success"]
        True
        >>> result["manifest_path"]
        "manifests/task-001-snapshot-module.manifest.json"

        >>> result = await maid_snapshot(
        ...     "src/file.py",
        ...     output_dir="custom",
        ...     force=True,
        ...     skip_test_stub=True
        ... )
    """
    # Build command arguments
    cmd = ["maid", "snapshot", file_path]

    # Add output directory
    cmd.extend(["--output-dir", output_dir])

    # Add force flag
    if force:
        cmd.append("--force")

    # Add skip test stub flag
    if skip_test_stub:
        cmd.append("--skip-test-stub")

    # Initialize result structure
    result: dict[str, Any] = {
        "success": False,
        "manifest_path": "",
        "test_stub_path": None,
        "superseded_manifests": [],
        "errors": [],
    }

    try:
        # Execute the snapshot command asynchronously
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

        # Parse snapshot results
        if process.returncode == 0:
            result["success"] = True

            # Extract manifest path from stdout
            manifest_path = _extract_manifest_path(stdout)
            if manifest_path:
                result["manifest_path"] = manifest_path

            # Extract test stub path from stdout (if generated)
            test_stub_path = _extract_test_stub_path(stdout)
            if test_stub_path:
                result["test_stub_path"] = test_stub_path

            # Extract superseded manifests from stdout
            superseded = _extract_superseded_manifests(stdout)
            result["superseded_manifests"] = superseded

        else:
            # Parse errors from stderr
            errors = _parse_errors(stderr, stdout)
            result["errors"] = errors

    except asyncio.TimeoutError:
        # Handle timeout
        result["errors"] = ["Snapshot command timeout"]

    except TimeoutError:
        # Handle timeout (Python 3.11+ compatibility)
        result["errors"] = ["Snapshot command timeout"]

    except OSError as e:
        # Handle subprocess errors (e.g., command not found)
        result["errors"] = [f"Failed to execute snapshot command: {str(e)}"]

    except Exception as e:
        # Handle unexpected errors
        result["errors"] = [f"Unexpected error during snapshot: {str(e)}"]

    return result


def _extract_manifest_path(output: str) -> str:
    """Extract manifest path from snapshot output.

    Args:
        output: stdout from snapshot command

    Returns:
        Manifest path if found, empty string otherwise
    """
    # Look for pattern: "Snapshot manifest generated successfully: <path>"
    for line in output.splitlines():
        if "generated successfully:" in line.lower() or "snapshot manifest" in line.lower():
            # Extract path after the colon
            match = re.search(r":\s*(.+\.manifest\.json)", line)
            if match:
                return match.group(1).strip()

    return ""


def _extract_test_stub_path(output: str) -> str | None:
    """Extract test stub path from snapshot output.

    Args:
        output: stdout from snapshot command

    Returns:
        Test stub path if found, None otherwise
    """
    # Look for pattern: "Test stub generated: <path>"
    for line in output.splitlines():
        if "test stub generated:" in line.lower():
            # Extract path after the colon
            match = re.search(r":\s*(.+\.py)", line)
            if match:
                return match.group(1).strip()

    return None


def _extract_superseded_manifests(output: str) -> list[str]:
    """Extract superseded manifest filenames from snapshot output.

    Args:
        output: stdout from snapshot command

    Returns:
        List of superseded manifest filenames
    """
    superseded: list[str] = []

    # Look for pattern: "Superseding previous manifests: file1.json, file2.json"
    for line in output.splitlines():
        if "superseding previous manifests:" in line.lower():
            # Extract the part after the colon
            match = re.search(r":\s*(.+)", line, re.IGNORECASE)
            if match:
                manifests_str = match.group(1).strip()
                # Split by comma and clean up whitespace
                manifests = [m.strip() for m in manifests_str.split(",")]
                superseded.extend(manifests)

    return superseded


def _parse_errors(stderr: str, stdout: str) -> list[str]:
    """Parse error messages from snapshot output.

    Extracts error messages from stderr and stdout, filtering out empty lines
    and providing structured error information.

    Args:
        stderr: stderr output from snapshot command
        stdout: stdout output from snapshot command (may contain errors)

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
        errors.append("Snapshot failed (no specific error message available)")

    return errors
