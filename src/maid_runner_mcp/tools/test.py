"""Test tool for MAID Runner MCP.

This module implements the maid_test MCP tool which wraps the MAID Runner
test command. It provides async execution, structured output, and comprehensive
error handling for running validation commands from manifests.
"""

import asyncio
import re
from typing import Any


async def maid_test(
    manifest_dir: str = "manifests",
    manifest: str | None = None,
    fail_fast: bool = False,
    timeout: int = 300,
) -> dict[str, Any]:
    """MCP tool that runs validation commands from all non-superseded manifests.

    This function wraps the MAID Runner `test` CLI command and returns structured
    test results. It executes the command asynchronously and parses both stdout
    and stderr to extract total manifests, passed/failed counts, and failed manifest names.

    Args:
        manifest_dir: Directory containing manifests (default: "manifests")
        manifest: Run validation for a single manifest (filename or path, optional)
        fail_fast: Stop execution on first failure (default: False)
        timeout: Command timeout in seconds (default: 300)

    Returns:
        Dictionary containing test results with the following structure:
        {
            "success": bool,                    # True if all tests passed
            "total_manifests": int,             # Total number of manifests tested
            "passed": int,                      # Number of passed manifests
            "failed": int,                      # Number of failed manifests
            "failed_manifests": list[str],      # List of failed manifest filenames
            "manifest_dir": str,                # Manifest directory used
            "timeout": int,                     # Timeout value used
            "errors": list[str],                # List of error messages (if any)
        }

    Examples:
        >>> result = await maid_test()
        >>> result["success"]
        True
        >>> result["total_manifests"]
        5

        >>> result = await maid_test(
        ...     manifest="task-001.manifest.json",
        ...     fail_fast=True,
        ...     timeout=600
        ... )
    """
    # Build command arguments
    cmd = ["maid", "test"]

    # Add manifest directory
    cmd.extend(["--manifest-dir", manifest_dir])

    # Add single manifest flag if specified
    if manifest:
        cmd.extend(["--manifest", manifest])

    # Add fail-fast flag
    if fail_fast:
        cmd.append("--fail-fast")

    # Add timeout
    cmd.extend(["--timeout", str(timeout)])

    # Add quiet mode to get cleaner output
    cmd.append("--quiet")

    # Initialize result structure
    result: dict[str, Any] = {
        "success": False,
        "total_manifests": 0,
        "passed": 0,
        "failed": 0,
        "failed_manifests": [],
        "manifest_dir": manifest_dir,
        "timeout": timeout,
    }

    try:
        # Execute the test command asynchronously
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

        # Parse test results
        if process.returncode == 0:
            result["success"] = True

            # Parse summary from stdout
            summary = _parse_summary(stdout)
            result["total_manifests"] = summary["total"]
            result["passed"] = summary["passed"]
            result["failed"] = summary["failed"]

            # Extract failed manifests (should be empty on success)
            failed_manifests = _extract_failed_manifests(stdout)
            result["failed_manifests"] = failed_manifests

        else:
            # Parse errors and summary from output
            summary = _parse_summary(stdout)
            result["total_manifests"] = summary["total"]
            result["passed"] = summary["passed"]
            result["failed"] = summary["failed"]

            # Extract failed manifests
            failed_manifests = _extract_failed_manifests(stdout)
            result["failed_manifests"] = failed_manifests

            # Parse errors from stderr if available
            if stderr.strip():
                errors = _parse_errors(stderr, stdout)
                result["errors"] = errors
            else:
                # Use failed manifests as errors if no stderr
                result["errors"] = [f"Validation failed for: {m}" for m in failed_manifests] or [
                    "Test command failed"
                ]

    except asyncio.TimeoutError:
        # Handle timeout
        result["errors"] = ["Test command timed out"]

    except TimeoutError:
        # Handle timeout (Python 3.11+ compatibility)
        result["errors"] = ["Test command timed out"]

    except OSError as e:
        # Handle subprocess errors (e.g., command not found)
        result["errors"] = [f"Failed to execute test command: {str(e)}"]

    except Exception as e:
        # Handle unexpected errors
        result["errors"] = [f"Unexpected error during test: {str(e)}"]

    return result


def _parse_summary(output: str) -> dict[str, int]:
    """Parse test summary from output.

    Looks for patterns like:
    - "Summary: 3 manifests, 2 passed, 1 failed"
    - "Summary: 1 manifest, 1 passed, 0 failed"
    - "No manifests found to test."

    Args:
        output: stdout from test command

    Returns:
        Dictionary with total, passed, and failed counts
    """
    summary = {"total": 0, "passed": 0, "failed": 0}

    # Look for "No manifests found" message
    if "no manifests found" in output.lower():
        return summary

    # Look for summary line with pattern: "Summary: N manifest(s), M passed, K failed"
    summary_pattern = (
        r"Summary:\s*(\d+)\s*manifests?\s*(?:tested)?,\s*(\d+)\s*passed,\s*(\d+)\s*failed"
    )
    match = re.search(summary_pattern, output, re.IGNORECASE)

    if match:
        summary["total"] = int(match.group(1))
        summary["passed"] = int(match.group(2))
        summary["failed"] = int(match.group(3))

    return summary


def _extract_failed_manifests(output: str) -> list[str]:
    """Extract failed manifest filenames from output.

    Looks for patterns like:
    - "Failed manifests:"
    - "- task-001.manifest.json"
    - "- task-002.manifest.json"

    Args:
        output: stdout from test command

    Returns:
        List of failed manifest filenames
    """
    failed_manifests: list[str] = []

    # Look for "Failed manifests:" section
    lines = output.splitlines()
    in_failed_section = False

    for line in lines:
        line = line.strip()

        # Check if we're entering the failed manifests section
        if "failed manifests:" in line.lower():
            in_failed_section = True
            continue

        # If we're in the section, extract manifest names
        if in_failed_section:
            # Stop at empty line or next section
            if not line or line.startswith("Summary:") or line.startswith("Running"):
                in_failed_section = False
                continue

            # Extract manifest name (remove leading "- ")
            if line.startswith("- "):
                manifest_name = line[2:].strip()
                if manifest_name:
                    failed_manifests.append(manifest_name)

    return failed_manifests


def _parse_errors(stderr: str, stdout: str) -> list[str]:
    """Parse error messages from test output.

    Extracts error messages from stderr and stdout, filtering out empty lines
    and providing structured error information.

    Args:
        stderr: stderr output from test command
        stdout: stdout output from test command (may contain errors)

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
        errors.append("Test failed (no specific error message available)")

    return errors
