"""MCP Resources for MAID Runner.

Resources provide read-only access to MAID data structures
including manifests, schemas, validation results, snapshots, and specs.
"""

from maid_runner_mcp.resources.manifest import get_manifest
from maid_runner_mcp.resources.schema import get_manifest_schema
from maid_runner_mcp.resources import validation
from maid_runner_mcp.resources.validation import get_validation_result
from maid_runner_mcp.resources.snapshot import get_system_snapshot
from maid_runner_mcp.resources.spec import get_maid_spec

__all__ = [
    "get_manifest",
    "get_manifest_schema",
    "get_validation_result",
    "get_system_snapshot",
    "get_maid_spec",
    "validation",
]
