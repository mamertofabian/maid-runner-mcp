"""MCP Resources for MAID Runner.

Resources provide read-only access to MAID data structures
including manifests, schemas, validation results, and snapshots.
"""

from maid_runner_mcp.resources.manifest import get_manifest
from maid_runner_mcp.resources.schema import get_manifest_schema
from maid_runner_mcp.resources import validation
from maid_runner_mcp.resources.validation import get_validation_result

__all__ = ["get_manifest", "get_manifest_schema", "get_validation_result", "validation"]
