"""MAID Runner MCP Server.

Minimal MCP server that provides the foundation for MAID Runner tool integration.
Uses stdio transport for communication with MCP clients like Claude Code.
"""

import asyncio
import io

from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from maid_runner_mcp.__version__ import __version__
from maid_runner_mcp.tools.init import maid_init
from maid_runner_mcp.tools.manifests import maid_list_manifests
from maid_runner_mcp.tools.schema import maid_get_schema
from maid_runner_mcp.tools.snapshot import maid_snapshot
from maid_runner_mcp.tools.test import maid_test
from maid_runner_mcp.tools.validate import maid_validate


# Add .result property to ServerResult for compatibility
# (MCP SDK uses .root but some code expects .result)
def _get_server_result(
    self: types.ServerResult,
) -> (
    types.EmptyResult
    | types.InitializeResult
    | types.CompleteResult
    | types.GetPromptResult
    | types.ListPromptsResult
    | types.ListResourcesResult
    | types.ListResourceTemplatesResult
    | types.ReadResourceResult
    | types.CallToolResult
    | types.ListToolsResult
):
    """Provide .result property that aliases .root for backward compatibility."""
    return self.root


types.ServerResult.result = property(_get_server_result)  # type: ignore


def create_server() -> Server:
    """Factory function to create and configure MCP server instance with registered tools.

    Returns:
        Server: Configured MCP server instance with metadata and registered tools.
    """
    server = Server(name="maid-runner-mcp", version=__version__)

    # Register list_tools handler
    @server.list_tools()
    async def _handle_list_tools() -> list[types.Tool]:
        """Return list of all available MAID Runner tools."""
        return [
            types.Tool(
                name="maid_validate",
                description="Validate a MAID manifest against implementation or behavioral tests",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "manifest_path": {
                            "type": "string",
                            "description": "Path to the manifest JSON file to validate",
                        },
                        "validation_mode": {
                            "type": "string",
                            "description": "Validation mode - 'implementation' (default) or 'behavioral'",
                            "enum": ["implementation", "behavioral"],
                            "default": "implementation",
                        },
                        "use_manifest_chain": {
                            "type": "boolean",
                            "description": "Whether to use manifest chain for validation",
                            "default": False,
                        },
                        "manifest_dir": {
                            "type": ["string", "null"],
                            "description": "Optional custom manifest directory path",
                            "default": None,
                        },
                        "quiet": {
                            "type": "boolean",
                            "description": "Enable quiet mode - suppress success messages",
                            "default": True,
                        },
                    },
                    "required": ["manifest_path"],
                },
            ),
            types.Tool(
                name="maid_snapshot",
                description="Generate a snapshot manifest from an existing Python file",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the Python file to snapshot",
                        },
                        "output_dir": {
                            "type": "string",
                            "description": "Directory for output manifest",
                            "default": "manifests",
                        },
                        "force": {
                            "type": "boolean",
                            "description": "Overwrite existing manifest if it exists",
                            "default": False,
                        },
                        "skip_test_stub": {
                            "type": "boolean",
                            "description": "Skip test stub generation",
                            "default": False,
                        },
                    },
                    "required": ["file_path"],
                },
            ),
            types.Tool(
                name="maid_test",
                description="Run validation commands from all non-superseded manifests",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "manifest_dir": {
                            "type": "string",
                            "description": "Directory containing manifests",
                            "default": "manifests",
                        },
                        "manifest": {
                            "type": ["string", "null"],
                            "description": "Run validation for a single manifest (filename or path)",
                            "default": None,
                        },
                        "fail_fast": {
                            "type": "boolean",
                            "description": "Stop execution on first failure",
                            "default": False,
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Command timeout in seconds",
                            "default": 300,
                        },
                    },
                },
            ),
            types.Tool(
                name="maid_list_manifests",
                description="List all manifests referencing a given file, categorized by reference type",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file to search for in manifests",
                        },
                        "manifest_dir": {
                            "type": "string",
                            "description": "Directory containing manifests",
                            "default": "manifests",
                        },
                    },
                    "required": ["file_path"],
                },
            ),
            types.Tool(
                name="maid_init",
                description="Initialize a MAID project structure in the target directory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "target_dir": {
                            "type": "string",
                            "description": "Target directory to initialize",
                            "default": ".",
                        },
                        "force": {
                            "type": "boolean",
                            "description": "Overwrite existing MAID files if they exist",
                            "default": False,
                        },
                    },
                },
            ),
            types.Tool(
                name="maid_get_schema",
                description="Retrieve the MAID manifest JSON schema",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
        ]

    # Register call_tool handler
    @server.call_tool()
    async def _handle_call_tool(
        name: str, arguments: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Route tool calls to the appropriate tool function."""
        import json

        # Route to appropriate tool based on name
        if name == "maid_validate":
            result = await maid_validate(
                manifest_path=arguments["manifest_path"],
                validation_mode=arguments.get("validation_mode", "implementation"),
                use_manifest_chain=arguments.get("use_manifest_chain", False),
                manifest_dir=arguments.get("manifest_dir"),
                quiet=arguments.get("quiet", True),
            )
        elif name == "maid_snapshot":
            result = await maid_snapshot(
                file_path=arguments["file_path"],
                output_dir=arguments.get("output_dir", "manifests"),
                force=arguments.get("force", False),
                skip_test_stub=arguments.get("skip_test_stub", False),
            )
        elif name == "maid_test":
            result = await maid_test(
                manifest_dir=arguments.get("manifest_dir", "manifests"),
                manifest=arguments.get("manifest"),
                fail_fast=arguments.get("fail_fast", False),
                timeout=arguments.get("timeout", 300),
            )
        elif name == "maid_list_manifests":
            result = await maid_list_manifests(
                file_path=arguments["file_path"],
                manifest_dir=arguments.get("manifest_dir", "manifests"),
            )
        elif name == "maid_init":
            result = await maid_init(
                target_dir=arguments.get("target_dir", "."),
                force=arguments.get("force", False),
            )
        elif name == "maid_get_schema":
            result = await maid_get_schema()
        else:
            raise ValueError(f"Unknown tool: {name}")

        # Return result as TextContent
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    return server


def main() -> None:
    """Entry point that runs the MCP server with stdio transport.

    Starts the MCP server using stdio transport (stdin/stdout) for communication
    with MCP clients. Handles KeyboardInterrupt gracefully for clean shutdown.
    """

    async def _run_server() -> None:
        """Async helper to run the server."""
        server = create_server()

        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())

    try:
        asyncio.run(_run_server())
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        pass
    except io.UnsupportedOperation:
        # Handle stdio transport errors gracefully (e.g., in test environments)
        # where stdin/stdout may not be available or readable
        pass
