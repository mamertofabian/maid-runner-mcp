"""MCP resource for accessing manifest files."""

from pathlib import Path

from maid_runner_mcp.server import mcp


@mcp.resource("manifest://{manifest_name}")
async def get_manifest(manifest_name: str) -> str:
    """MCP resource handler for accessing manifest files by name.

    Provides read-only access to manifest files in the manifests directory.
    Handles manifest names with or without the .manifest.json extension.

    Args:
        manifest_name: Name of the manifest file (with or without extension)

    Returns:
        str: Content of the manifest file as a JSON string

    Raises:
        ValueError: If manifest_name is empty or contains path traversal attempts
        FileNotFoundError: If the manifest file does not exist
    """
    # Validate input
    if not manifest_name or not manifest_name.strip():
        raise ValueError("Manifest name cannot be empty")

    # Security: prevent path traversal attacks
    if ".." in manifest_name or "/" in manifest_name or "\\" in manifest_name:
        raise ValueError(f"Invalid manifest name: {manifest_name}")

    # Normalize manifest name (remove extension if present)
    if manifest_name.endswith(".manifest.json"):
        manifest_name = manifest_name[: -len(".manifest.json")]

    # Construct path to manifest file
    manifests_dir = Path("manifests")
    manifest_path = manifests_dir / f"{manifest_name}.manifest.json"

    # Check if file exists
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_name}")

    # Read and return file content
    with open(manifest_path, "r", encoding="utf-8") as f:
        return f.read()
