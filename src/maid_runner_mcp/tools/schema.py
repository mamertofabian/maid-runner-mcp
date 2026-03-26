"""MCP tool for MAID manifest schema retrieval."""

import asyncio
import json
from pathlib import Path
from typing import Any, TypedDict

from mcp.server.fastmcp import Context

from maid_runner_mcp.server import mcp
from maid_runner_mcp.utils.roots import get_working_directory

# Resolve the schema file from the installed maid_runner package
_SCHEMA_FILE = Path(__file__).resolve().parents[0]  # placeholder, resolved at runtime


def _get_schema_path() -> Path:
    """Get the path to the maid_runner manifest JSON schema file."""
    import maid_runner.core.manifest as manifest_mod

    schema_dir = Path(manifest_mod.__file__).parent.parent / "schemas"
    return schema_dir / "manifest.v2.schema.json"


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
    await get_working_directory(ctx)

    loop = asyncio.get_event_loop()
    try:
        schema = await loop.run_in_executor(
            None,
            lambda: json.loads(_get_schema_path().read_text()),
        )

        return SchemaResult(
            success=True,
            json_schema=schema,
            errors=[],
        )

    except FileNotFoundError:
        return SchemaResult(
            success=False,
            json_schema={},
            errors=["MAID Runner schema file not found"],
        )
    except json.JSONDecodeError as e:
        return SchemaResult(
            success=False,
            json_schema={},
            errors=[f"Failed to parse schema JSON: {e}"],
        )
    except Exception as e:
        return SchemaResult(
            success=False,
            json_schema={},
            errors=[str(e)],
        )
