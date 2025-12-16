"""Init tool for MAID Runner MCP.

This module implements the maid_init MCP tool which wraps the MAID Runner
init command. It provides async execution, structured output, and comprehensive
error handling for MAID project initialization.
"""

import asyncio
import re
from typing import Any


async def maid_init(
    target_dir: str = ".",
    force: bool = False,
) -> dict[str, Any]:
    """MCP tool that initializes a MAID project structure in the target directory.

    This function wraps the MAID Runner `init` CLI command and returns structured
    initialization results. It executes the command asynchronously and parses both
    stdout and stderr to extract created files and handle errors.

    Args:
        target_dir: Target directory to initialize (default: ".")
        force: Overwrite existing MAID files if they exist (default: False)

    Returns:
        Dictionary containing initialization results with the following structure:
        {
            "success": bool,              # True if initialization succeeded
            "initialized_dir": str,       # Directory that was initialized
            "created_files": list[str],   # List of created file paths
            "errors": list[str],          # List of error messages (if any)
        }

    Examples:
        >>> result = await maid_init()
        >>> result["success"]
        True
        >>> result["initialized_dir"]
        "."

        >>> result = await maid_init(
        ...     target_dir="/path/to/project",
        ...     force=True
        ... )
        >>> result["created_files"]
        [".maid/docs/maid_specs.md", "manifests/", "tests/"]
    """
    # Build command arguments
    cmd = ["maid", "init", target_dir]

    # Add force flag
    if force:
        cmd.append("--force")

    # Initialize result structure
    result: dict[str, Any] = {
        "success": False,
        "initialized_dir": target_dir,
        "created_files": [],
        "errors": [],
    }

    try:
        # Execute the init command asynchronously
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

        # Parse init results
        if process.returncode == 0:
            result["success"] = True

            # Extract created files from stdout
            created_files = _extract_created_files(stdout)
            result["created_files"] = created_files

        else:
            # Parse errors from stderr
            errors = _parse_errors(stderr, stdout)
            result["errors"] = errors

    except asyncio.TimeoutError:
        # Handle timeout
        result["errors"] = ["Init command timed out"]

    except TimeoutError:
        # Handle timeout (Python 3.11+ compatibility)
        result["errors"] = ["Init command timed out"]

    except OSError as e:
        # Handle subprocess errors (e.g., command not found)
        result["errors"] = [f"Failed to execute init command: {str(e)}"]

    except Exception as e:
        # Handle unexpected errors
        result["errors"] = [f"Unexpected error during init: {str(e)}"]

    return result


def _extract_created_files(output: str) -> list[str]:
    """Extract created file paths from init output.

    Args:
        output: stdout from init command

    Returns:
        List of created file paths
    """
    created_files: list[str] = []

    # Look for patterns like "Created: <path>" or "Overwritten: <path>"
    for line in output.splitlines():
        line = line.strip()

        # Match "Created: <path>" pattern
        created_match = re.search(r"^Created:\s*(.+)", line)
        if created_match:
            created_files.append(created_match.group(1).strip())
            continue

        # Match "Overwritten: <path>" pattern
        overwritten_match = re.search(r"^Overwritten:\s*(.+)", line)
        if overwritten_match:
            created_files.append(overwritten_match.group(1).strip())
            continue

    return created_files


def _parse_errors(stderr: str, stdout: str) -> list[str]:
    """Parse error messages from init output.

    Extracts error messages from stderr and stdout, filtering out empty lines
    and providing structured error information.

    Args:
        stderr: stderr output from init command
        stdout: stdout output from init command (may contain errors)

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
        errors.append("Init failed (no specific error message available)")

    return errors
