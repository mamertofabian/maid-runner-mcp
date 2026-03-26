"""MCP tool for listing manifests that reference a file."""

import asyncio
from typing import TypedDict

from mcp.server.fastmcp import Context

from maid_runner import ManifestChain
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
    cwd = await get_working_directory(ctx)

    loop = asyncio.get_event_loop()
    try:
        project_root = cwd or "."

        chain = await loop.run_in_executor(
            None,
            lambda: ManifestChain(manifest_dir, project_root=project_root),
        )

        manifests = await loop.run_in_executor(
            None,
            lambda: chain.manifests_for_file(file_path),
        )

        created_by: list[str] = []
        edited_by: list[str] = []
        read_by: list[str] = []

        for m in manifests:
            slug = m.slug
            create_paths = [fs.path for fs in m.files_create]
            edit_paths = [fs.path for fs in m.files_edit]
            read_paths = list(m.files_read)

            if file_path in create_paths:
                created_by.append(slug)
            if file_path in edit_paths:
                edited_by.append(slug)
            if file_path in read_paths:
                read_by.append(slug)

        total = len(created_by) + len(edited_by) + len(read_by)

        return ListManifestsResult(
            file_path=file_path,
            total_manifests=total,
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
