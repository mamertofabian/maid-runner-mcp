"""Manifests listing tool for MAID Runner MCP.

This module implements the maid_list_manifests MCP tool which wraps the MAID Runner
manifests command. It provides async execution, structured output, and comprehensive
error handling for listing manifests that reference a given file.
"""

import asyncio
import re
from typing import Any


async def maid_list_manifests(
    file_path: str,
    manifest_dir: str = "manifests",
) -> dict[str, Any]:
    """MCP tool that lists all manifests referencing a given file, categorized by reference type.

    This function wraps the MAID Runner `manifests` CLI command and returns structured
    manifest listing results. It executes the command asynchronously and parses both stdout
    and stderr to extract manifests categorized by how they reference the file (created,
    edited, or read).

    Args:
        file_path: Path to the file to search for in manifests
        manifest_dir: Directory containing manifests (default: "manifests")

    Returns:
        Dictionary containing manifest listing results with the following structure:
        {
            "success": bool,                # True if listing succeeded
            "file_path": str,               # Path to the queried file
            "total_manifests": int,         # Total number of manifests referencing the file
            "created_by": list[str],        # List of manifests that create the file
            "edited_by": list[str],         # List of manifests that edit the file
            "read_by": list[str],           # List of manifests that read the file
            "errors": list[str],            # List of error messages (if any)
        }

    Examples:
        >>> result = await maid_list_manifests("src/module.py")
        >>> result["success"]
        True
        >>> result["total_manifests"]
        3
        >>> result["created_by"]
        ["task-001-create-module.manifest.json"]

        >>> result = await maid_list_manifests(
        ...     "src/file.py",
        ...     manifest_dir="custom_manifests"
        ... )
    """
    # Build command arguments
    cmd = ["maid", "manifests", file_path]

    # Add manifest directory
    cmd.extend(["--manifest-dir", manifest_dir])

    # Initialize result structure
    result: dict[str, Any] = {
        "success": False,
        "file_path": file_path,
        "total_manifests": 0,
        "created_by": [],
        "edited_by": [],
        "read_by": [],
    }

    try:
        # Execute the manifests command asynchronously
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

        # Parse manifest listing results
        if process.returncode == 0:
            result["success"] = True

            # Extract total manifests count
            total = _extract_total_manifests(stdout)
            result["total_manifests"] = total

            # Extract categorized manifest lists
            created_by = _extract_created_by(stdout)
            result["created_by"] = created_by

            edited_by = _extract_edited_by(stdout)
            result["edited_by"] = edited_by

            read_by = _extract_read_by(stdout)
            result["read_by"] = read_by

        else:
            # Parse errors from stderr
            errors = _parse_errors(stderr, stdout)
            result["errors"] = errors

    except asyncio.TimeoutError:
        # Handle timeout
        result["errors"] = ["Manifests listing command timed out"]

    except TimeoutError:
        # Handle timeout (Python 3.11+ compatibility)
        result["errors"] = ["Manifests listing command timed out"]

    except OSError as e:
        # Handle subprocess errors (e.g., command not found)
        result["errors"] = [f"Failed to execute manifests command: {str(e)}"]

    except Exception as e:
        # Handle unexpected errors
        result["errors"] = [f"Unexpected error during manifest listing: {str(e)}"]

    return result


def _extract_total_manifests(output: str) -> int:
    """Extract total manifest count from output.

    Args:
        output: stdout from manifests command

    Returns:
        Total number of manifests, or 0 if not found
    """
    # Look for pattern: "Total: N manifest(s)"
    for line in output.splitlines():
        if "total:" in line.lower():
            # Extract number before "manifest(s)"
            match = re.search(r"total:\s*(\d+)\s+manifest", line, re.IGNORECASE)
            if match:
                return int(match.group(1))

    return 0


def _extract_created_by(output: str) -> list[str]:
    """Extract list of manifests that create the file.

    Args:
        output: stdout from manifests command

    Returns:
        List of manifest filenames that create the file
    """
    return _extract_manifest_category(output, "CREATED BY")


def _extract_edited_by(output: str) -> list[str]:
    """Extract list of manifests that edit the file.

    Args:
        output: stdout from manifests command

    Returns:
        List of manifest filenames that edit the file
    """
    return _extract_manifest_category(output, "EDITED BY")


def _extract_read_by(output: str) -> list[str]:
    """Extract list of manifests that read the file.

    Args:
        output: stdout from manifests command

    Returns:
        List of manifest filenames that read the file
    """
    return _extract_manifest_category(output, "READ BY")


def _extract_manifest_category(output: str, category: str) -> list[str]:
    """Extract manifests for a specific category from output.

    Args:
        output: stdout from manifests command
        category: Category name (e.g., "CREATED BY", "EDITED BY", "READ BY")

    Returns:
        List of manifest filenames in the category
    """
    manifests: list[str] = []
    lines = output.splitlines()

    # Find the category header line
    in_category = False
    for i, line in enumerate(lines):
        # Check if this line contains the category header
        if category.upper() in line.upper():
            in_category = True
            continue

        # If we're in the category, collect manifest names
        if in_category:
            # Stop if we hit another category header or separator line
            if (
                "CREATED BY" in line.upper()
                or "EDITED BY" in line.upper()
                or "READ BY" in line.upper()
            ) and category.upper() not in line.upper():
                break
            if "=" * 10 in line:
                break

            # Extract manifest filename from lines like "  - task-001-example.manifest.json"
            line = line.strip()
            if line.startswith("-"):
                # Remove leading "- " and whitespace
                manifest_name = line[1:].strip()
                if manifest_name and manifest_name.endswith(".manifest.json"):
                    manifests.append(manifest_name)

    return manifests


def _parse_errors(stderr: str, stdout: str) -> list[str]:
    """Parse error messages from manifests output.

    Extracts error messages from stderr and stdout, filtering out empty lines
    and providing structured error information.

    Args:
        stderr: stderr output from manifests command
        stdout: stdout output from manifests command (may contain errors)

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
                line.startswith("Error:") or line.startswith("ERROR:") or "failed" in line.lower()
            ):
                errors.append(line)

    # If still no errors, provide a generic message
    if not errors:
        errors.append("Manifests listing failed (no specific error message available)")

    return errors
