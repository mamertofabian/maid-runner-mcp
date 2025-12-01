"""MCP Resources for MAID Runner.

Resources provide read-only access to MAID data structures
including manifests, schemas, validation results, and snapshots.
"""

from maid_runner_mcp.resources.manifest import get_manifest

__all__ = ["get_manifest"]
