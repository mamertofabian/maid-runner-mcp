"""MCP resource for accessing the full MAID methodology specification."""

from pathlib import Path

from maid_runner_mcp.server import mcp

# Path to the MAID specification document
MAID_SPEC_PATH = Path(".maid/docs/maid_specs.md")


@mcp.resource("maid://spec")
async def get_maid_spec() -> str:
    """MCP resource handler for accessing the full MAID specification.

    Provides read-only access to the complete MAID methodology specification
    document. This allows AI tools to access detailed methodology information
    beyond the concise server instructions.

    Returns:
        str: The full MAID specification as markdown text

    Raises:
        RuntimeError: If the specification file cannot be read
    """
    try:
        if MAID_SPEC_PATH.exists():
            return MAID_SPEC_PATH.read_text()
        else:
            # Try alternative paths
            alt_paths = [
                Path(".maid/docs/maid_specs.md"),
                Path("docs/maid_specs.md"),
                Path("MAID.md"),
            ]
            for path in alt_paths:
                if path.exists():
                    return path.read_text()

            raise RuntimeError(
                f"MAID specification file not found. " f"Expected at: {MAID_SPEC_PATH}"
            )
    except OSError as e:
        raise RuntimeError(f"Failed to read MAID specification: {e}")
