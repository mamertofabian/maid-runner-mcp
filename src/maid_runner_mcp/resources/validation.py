"""MCP resource for accessing validation cache results."""

import json
from typing import Any

from maid_runner_mcp.server import mcp

# Module-level cache to store validation results
_validation_cache: dict[str, dict[str, Any]] = {}


@mcp.resource("validation://{manifest_name}/result")
async def get_validation_result(manifest_name: str) -> str:
    """MCP resource handler for accessing cached validation results.

    Provides read-only access to validation results that have been cached
    by the maid_validate tool. Results are stored by manifest name.

    Args:
        manifest_name: Name of the manifest (without path or extension)

    Returns:
        str: Cached validation result as a JSON string

    Raises:
        ValueError: If manifest_name is empty or contains path traversal attempts
        KeyError: If the manifest validation result is not in cache
    """
    # Validate input
    if not manifest_name or not manifest_name.strip():
        raise ValueError("Manifest name cannot be empty")

    # Security: prevent path traversal attacks
    if ".." in manifest_name or "/" in manifest_name or "\\" in manifest_name:
        raise ValueError(f"Invalid manifest name: {manifest_name}")

    # Check if result is in cache
    if manifest_name not in _validation_cache:
        raise KeyError(f"Validation result not found in cache: {manifest_name}")

    # Return cached result as JSON string
    return json.dumps(_validation_cache[manifest_name])
