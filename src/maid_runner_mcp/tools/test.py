"""MCP tool for running MAID validation commands."""

import asyncio
import re
import subprocess
from typing import TypedDict

from mcp.server.fastmcp import Context

from maid_runner_mcp.server import mcp
from maid_runner_mcp.utils.roots import get_working_directory


class TestResult(TypedDict):
    """Result of running validation commands from manifests.

    Fields:
        success: Whether all validation commands passed
        total_manifests: Total number of manifests processed
        passed: Number of manifests that passed validation
        failed: Number of manifests that failed validation
        failed_manifests: List of manifest paths that failed
    """

    success: bool
    total_manifests: int
    passed: int
    failed: int
    failed_manifests: list[str]


@mcp.tool()
async def maid_test(
    ctx: Context,
    manifest_dir: str = "manifests",
    manifest: str | None = None,
    fail_fast: bool = False,
    timeout: int = 300,
) -> TestResult:
    """Run validation commands from MAID manifests.

    **When to use:**
    - Phase 3 (Implementation): Execute tests to verify code passes
    - Phase 4 (Integration): Run all tests to ensure nothing is broken
    - CI/CD: Automated verification of all manifests

    **Key behavior:**
    - Executes the `validationCommand` from each manifest
    - Reports pass/fail status for each manifest
    - Can run single manifest or all manifests in directory

    **Tips:**
    - Use `manifest` parameter to test a specific task during development
    - Use `fail_fast=True` during iterative development to stop early
    - Increase `timeout` for slow-running test suites

    Args:
        ctx: MCP context for accessing working directory
        manifest_dir: Directory containing manifests (default: "manifests")
        manifest: Specific manifest file to test (optional, tests all if None)
        fail_fast: Stop on first failure (default: False)
        timeout: Timeout in seconds for the test command (default: 300)

    Returns:
        TestResult with test outcome details
    """
    # Build command
    cmd = ["uv", "run", "maid", "test"]

    if manifest:
        # Test a specific manifest
        cmd.append(manifest)
    else:
        # Use manifest directory
        cmd.extend(["--manifest-dir", manifest_dir])

    if fail_fast:
        cmd.append("--fail-fast")

    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    try:
        cwd = await get_working_directory(ctx)
        result = await loop.run_in_executor(
            None,
            lambda: subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd),
        )

        # Parse output to extract results
        output = result.stdout + result.stderr
        success = result.returncode == 0

        # Parse manifest counts from output
        total_manifests = 0
        passed = 0
        failed = 0
        failed_manifests: list[str] = []

        # Try to extract counts from output
        # Look for patterns like "X passed" or "X failed" or summary lines
        total_match = re.search(r"(\d+)\s+manifest", output, re.IGNORECASE)
        if total_match:
            total_manifests = int(total_match.group(1))

        passed_match = re.search(r"(\d+)\s+passed", output, re.IGNORECASE)
        if passed_match:
            passed = int(passed_match.group(1))

        failed_match = re.search(r"(\d+)\s+failed", output, re.IGNORECASE)
        if failed_match:
            failed = int(failed_match.group(1))

        # Extract failed manifest names
        # Look for patterns like "FAILED: manifest-name" or similar
        failed_pattern = re.findall(
            r"(?:FAILED|FAIL|Error).*?([^\s]+\.manifest\.json)", output, re.IGNORECASE
        )
        if failed_pattern:
            failed_manifests = list(set(failed_pattern))

        # If we couldn't parse counts, infer from success/failure
        if total_manifests == 0 and passed == 0 and failed == 0:
            if success:
                # Successful run with no specific counts - assume at least one passed
                # Check if directory/manifest exists
                if "No manifests found" in output or "not found" in output.lower():
                    total_manifests = 0
                    passed = 0
                    failed = 0
                else:
                    # Assume success means at least something worked
                    total_manifests = 1 if manifest else 0
                    passed = total_manifests
                    failed = 0
            else:
                # Failed run - count as one failure if specific manifest
                if manifest:
                    total_manifests = 1
                    passed = 0
                    failed = 1
                    if manifest not in failed_manifests:
                        failed_manifests.append(manifest)

        # Ensure consistency: passed + failed = total
        if passed + failed != total_manifests:
            # Recalculate based on what we know
            if total_manifests > 0:
                if success:
                    passed = total_manifests
                    failed = 0
                else:
                    # If failed, assume at least one failure
                    failed = max(1, failed)
                    passed = max(0, total_manifests - failed)

        # Final consistency check
        total_manifests = passed + failed
        failed_manifests = failed_manifests[:failed]  # Trim to match count

        # Pad failed_manifests if needed
        while len(failed_manifests) < failed:
            failed_manifests.append("unknown")

        return TestResult(
            success=success,
            total_manifests=total_manifests,
            passed=passed,
            failed=failed,
            failed_manifests=failed_manifests,
        )

    except subprocess.TimeoutExpired:
        return TestResult(
            success=False,
            total_manifests=0,
            passed=0,
            failed=0,
            failed_manifests=[],
        )
    except FileNotFoundError:
        return TestResult(
            success=False,
            total_manifests=1 if manifest else 0,
            passed=0,
            failed=1 if manifest else 0,
            failed_manifests=[manifest] if manifest else [],
        )
    except Exception:
        return TestResult(
            success=False,
            total_manifests=1 if manifest else 0,
            passed=0,
            failed=1 if manifest else 0,
            failed_manifests=[manifest] if manifest else [],
        )
