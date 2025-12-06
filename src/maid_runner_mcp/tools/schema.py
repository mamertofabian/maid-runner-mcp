"""MCP tool for MAID manifest schema retrieval."""

import asyncio
import json
import subprocess
from typing import Any, TypedDict

from mcp.server.fastmcp import Context

from maid_runner_mcp.server import mcp
from maid_runner_mcp.utils.roots import get_working_directory


class SchemaResult(TypedDict):
    """Result of manifest schema retrieval.

    Fields:
        success: Whether schema retrieval succeeded
        json_schema: The JSON schema object (empty dict if failed)
        errors: List of error messages if retrieval failed
    """

    success: bool
    json_schema: dict[str, Any]
    errors: list[str]


@mcp.tool()
async def maid_get_schema(ctx: Context) -> SchemaResult:
    """Get the MAID manifest JSON schema.

    **When to use:**
    - Phase 2 (Planning): Understand manifest structure before creating one
    - Debugging: Verify manifest fields are correctly named and typed
    - Learning: Explore available manifest options

    **Key information in schema:**
    - Required fields: `goal`, `readonlyFiles`, `expectedArtifacts`/`systemArtifacts`
    - File lists: `creatableFiles`, `editableFiles`, `readonlyFiles`
    - Artifact types: function, class, attribute, etc.
    - Validation commands: `validationCommand` or `validationCommands`

    **Tips:**
    - Review schema before writing your first manifest
    - Use schema to validate manifest structure
    - Check artifact type options for expectedArtifacts.contains[]

    Args:
        ctx: MCP context for accessing client roots

    Returns:
        SchemaResult with the manifest schema
    """
    # Get working directory from MCP roots
    cwd = await get_working_directory(ctx)

    # Build command
    cmd = ["uv", "run", "maid", "schema"]

    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(
            None, lambda: subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
        )

        if result.returncode == 0:
            # Parse JSON schema from stdout
            try:
                schema = json.loads(result.stdout)
                return SchemaResult(
                    success=True,
                    json_schema=schema,
                    errors=[],
                )
            except json.JSONDecodeError as e:
                return SchemaResult(
                    success=False,
                    json_schema={},
                    errors=[f"Failed to parse schema JSON: {e}"],
                )
        else:
            # Parse error output
            error_output = result.stderr or result.stdout
            errors: list[str] = []
            if error_output:
                errors = [line.strip() for line in error_output.strip().split("\n") if line.strip()]

            return SchemaResult(
                success=False,
                json_schema={},
                errors=errors,
            )

    except FileNotFoundError:
        return SchemaResult(
            success=False,
            json_schema={},
            errors=["MAID Runner command not found"],
        )
    except Exception as e:
        return SchemaResult(
            success=False,
            json_schema={},
            errors=[str(e)],
        )
