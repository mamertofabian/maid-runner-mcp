"""MCP tool for MAID project initialization."""

import asyncio
import subprocess
from typing import TypedDict

from maid_runner_mcp.server import mcp


class InitResult(TypedDict):
    """Result of MAID project initialization.

    Fields:
        success: Whether initialization succeeded
        target_dir: Directory where MAID was initialized
        errors: List of error messages if initialization failed
    """

    success: bool
    target_dir: str
    errors: list[str]


@mcp.tool()
async def maid_init(
    target_dir: str = ".",
    force: bool = False,
) -> InitResult:
    """Initialize a MAID project using MAID Runner.

    Args:
        target_dir: Directory to initialize (defaults to current directory)
        force: Whether to force initialization even if already initialized

    Returns:
        InitResult with initialization outcome
    """
    # Build command
    cmd = ["uv", "run", "maid", "init"]

    if target_dir != ".":
        cmd.extend(["--target-dir", target_dir])

    if force:
        cmd.append("--force")

    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    try:
        # Provide "Y\n" to stdin for interactive prompts
        result = await loop.run_in_executor(
            None,
            lambda: subprocess.run(
                cmd, capture_output=True, text=True, input="Y\nY\nY\n"
            ),
        )

        success = result.returncode == 0
        errors: list[str] = []

        if not success:
            # Parse error output
            error_output = result.stderr or result.stdout
            if error_output:
                errors = [
                    line.strip()
                    for line in error_output.strip().split("\n")
                    if line.strip()
                ]

        return InitResult(
            success=success,
            target_dir=target_dir,
            errors=errors,
        )

    except FileNotFoundError:
        return InitResult(
            success=False,
            target_dir=target_dir,
            errors=[f"Directory not found: {target_dir}"],
        )
    except Exception as e:
        return InitResult(
            success=False,
            target_dir=target_dir,
            errors=[str(e)],
        )
