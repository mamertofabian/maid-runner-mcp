"""Schema tool for MAID Runner MCP.

This module implements the maid_get_schema MCP tool which wraps the MAID Runner
schema command. It provides async execution, structured output, and comprehensive
error handling for retrieving the MAID manifest JSON schema.
"""

import asyncio
import json
from typing import Any


async def maid_get_schema() -> dict[str, Any]:
    """MCP tool that retrieves the MAID manifest JSON schema.

    This function wraps the MAID Runner `schema` CLI command and returns the
    complete JSON schema for MAID manifests. It executes the command asynchronously
    and parses the JSON output to provide structured feedback.

    Returns:
        Dictionary containing the schema retrieval results with the following structure:
        {
            "success": bool,     # True if schema retrieval succeeded
            "schema": dict,      # The complete JSON schema (if successful)
            "errors": list[str], # List of error messages (if any)
        }

    Examples:
        >>> result = await maid_get_schema()
        >>> result["success"]
        True
        >>> result["schema"]["title"]
        'MAID Task Manifest'
    """
    # Build command arguments
    cmd = ["maid", "schema"]

    # Initialize result structure
    result: dict[str, Any] = {
        "success": False,
    }

    try:
        # Execute the schema command asynchronously
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

        # Parse schema results
        if process.returncode == 0:
            # Try to parse JSON schema from stdout
            try:
                schema = json.loads(stdout)
                result["success"] = True
                result["schema"] = schema
            except json.JSONDecodeError as e:
                # Handle JSON parse errors
                result["errors"] = [f"Failed to parse schema JSON: {str(e)}"]
        else:
            # Parse errors from stderr
            errors = _parse_errors(stderr, stdout)
            result["errors"] = errors

    except asyncio.TimeoutError:
        # Handle timeout
        result["errors"] = ["Schema command timed out"]

    except OSError as e:
        # Handle subprocess errors (e.g., command not found)
        result["errors"] = [f"Failed to execute schema command: {str(e)}"]

    except Exception as e:
        # Handle unexpected errors
        result["errors"] = [f"Unexpected error during schema retrieval: {str(e)}"]

    # Validate result has required fields
    if not result.get("success", False):
        # Ensure errors field exists for failures
        if "errors" not in result or not result["errors"]:
            result["errors"] = ["Schema retrieval failed (no specific error message available)"]

    return result


def _parse_errors(stderr: str, stdout: str) -> list[str]:
    """Parse error messages from schema command output.

    Extracts error messages from stderr and stdout, filtering out empty lines
    and providing structured error information.

    Args:
        stderr: stderr output from schema command
        stdout: stdout output from schema command (may contain errors)

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

    # If still no errors but stdout is empty, report that
    if not errors and not stdout.strip():
        errors.append("Schema command returned empty output")

    # If still no errors, provide a generic message
    if not errors:
        errors.append("Schema retrieval failed (no specific error message available)")

    return errors
