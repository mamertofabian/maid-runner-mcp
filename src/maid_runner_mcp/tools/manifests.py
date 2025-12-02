"""MCP tool for listing manifests that reference a file."""

import asyncio
import re
import subprocess
from typing import TypedDict

from mcp.server.fastmcp import Context

from maid_runner_mcp.server import mcp
from maid_runner_mcp.utils.roots import get_working_directory


class ListManifestsResult(TypedDict):
    """Result of listing manifests for a file.

    Fields:
        file_path: The file path that was queried
        total_manifests: Total number of manifests referencing the file
        created_by: List of manifests where file is in creatableFiles
        edited_by: List of manifests where file is in editableFiles
        read_by: List of manifests where file is in readonlyFiles
    """

    file_path: str
    total_manifests: int
    created_by: list[str]
    edited_by: list[str]
    read_by: list[str]


@mcp.tool()
async def maid_list_manifests(
    file_path: str,
    ctx: Context,
    manifest_dir: str = "manifests",
) -> ListManifestsResult:
    """List manifests that reference a file using MAID Runner.

    **When to use:**
    - Before editing: Check if a file already has manifests
    - Understanding history: See how a file has evolved through manifests
    - Planning edits: Find related manifests to understand context

    **Result categories:**
    - `created_by`: Manifests where file is in `creatableFiles`
    - `edited_by`: Manifests where file is in `editableFiles`
    - `read_by`: Manifests where file is in `readonlyFiles`

    **Tips:**
    - Use before creating a new manifest for an existing file
    - If file is in `creatableFiles`, it was first created by that manifest
    - Use `--use-manifest-chain` in maid_validate for files with history

    Args:
        file_path: Path to the file to check
        manifest_dir: Directory containing manifests (default: "manifests")

    Returns:
        ListManifestsResult with manifest information
    """
    # Get working directory from MCP roots
    cwd = await get_working_directory(ctx)

    # Build command
    cmd = ["uv", "run", "maid", "manifests", file_path]

    if manifest_dir:
        cmd.extend(["--manifest-dir", manifest_dir])

    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(
            None, lambda: subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
        )

        output = result.stdout

        # Parse the output
        created_by: list[str] = []
        edited_by: list[str] = []
        read_by: list[str] = []
        total_manifests = 0

        # Check for "No manifests found" case
        if "No manifests found referencing:" in output:
            return ListManifestsResult(
                file_path=file_path,
                total_manifests=0,
                created_by=[],
                edited_by=[],
                read_by=[],
            )

        # Parse total count
        total_match = re.search(r"Total: (\d+) manifest\(s\)", output)
        if total_match:
            total_manifests = int(total_match.group(1))

        # Parse sections
        current_section: list[str] | None = None
        for line in output.split("\n"):
            line = line.strip()

            # Detect section headers
            if "CREATED BY" in line:
                current_section = created_by
            elif "EDITED BY" in line:
                current_section = edited_by
            elif "READ BY" in line:
                current_section = read_by
            elif line.startswith("- ") and current_section is not None:
                # Extract manifest name
                manifest_name = line[2:].strip()
                current_section.append(manifest_name)

        return ListManifestsResult(
            file_path=file_path,
            total_manifests=total_manifests,
            created_by=created_by,
            edited_by=edited_by,
            read_by=read_by,
        )

    except FileNotFoundError:
        return ListManifestsResult(
            file_path=file_path,
            total_manifests=0,
            created_by=[],
            edited_by=[],
            read_by=[],
        )
    except Exception:
        return ListManifestsResult(
            file_path=file_path,
            total_manifests=0,
            created_by=[],
            edited_by=[],
            read_by=[],
        )
