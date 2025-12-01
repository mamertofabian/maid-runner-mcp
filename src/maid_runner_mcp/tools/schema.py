"""MCP tool for MAID manifest schema retrieval."""

import asyncio
import json
import subprocess
from typing import Any, TypedDict

from maid_runner_mcp.server import mcp


class SchemaResult(TypedDict):
    """Result of manifest schema retrieval.

    Fields:
        success: Whether schema retrieval succeeded
        schema: The JSON schema object (empty dict if failed)
        errors: List of error messages if retrieval failed
    """

    success: bool
    schema: dict[str, Any]
    errors: list[str]


@mcp.tool()
async def maid_get_schema() -> SchemaResult:
    """Get the MAID manifest JSON schema.

    Returns:
        SchemaResult with the manifest schema
    """
    # Build command
    cmd = ["uv", "run", "maid", "schema"]

    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(
            None, lambda: subprocess.run(cmd, capture_output=True, text=True)
        )

        if result.returncode == 0:
            # Parse JSON schema from stdout
            try:
                schema = json.loads(result.stdout)
                return SchemaResult(
                    success=True,
                    schema=schema,
                    errors=[],
                )
            except json.JSONDecodeError as e:
                return SchemaResult(
                    success=False,
                    schema={},
                    errors=[f"Failed to parse schema JSON: {e}"],
                )
        else:
            # Parse error output
            error_output = result.stderr or result.stdout
            errors: list[str] = []
            if error_output:
                errors = [
                    line.strip()
                    for line in error_output.strip().split("\n")
                    if line.strip()
                ]

            return SchemaResult(
                success=False,
                schema={},
                errors=errors,
            )

    except FileNotFoundError:
        return SchemaResult(
            success=False,
            schema={},
            errors=["MAID Runner command not found"],
        )
    except Exception as e:
        return SchemaResult(
            success=False,
            schema={},
            errors=[str(e)],
        )
