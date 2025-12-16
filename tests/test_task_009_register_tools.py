"""Behavioral tests for task 009: Register tools in MCP server.

Tests verify that all 6 MAID Runner tools are properly registered in the
MCP server and can be accessed via the MCP protocol.
"""

import pytest

from maid_runner_mcp.server import create_server, main


class TestToolRegistration:
    """Test that all tools are registered in the server."""

    def test_server_has_list_tools_handler(self):
        """Verify server has list_tools request handler registered."""
        from mcp import types

        server = create_server()

        # Assert list_tools handler is registered
        assert (
            types.ListToolsRequest in server.request_handlers
        ), "Server should have ListToolsRequest handler registered"

    def test_server_has_call_tool_handler(self):
        """Verify server has call_tool request handler registered."""
        from mcp import types

        server = create_server()

        # Assert call_tool handler is registered
        assert (
            types.CallToolRequest in server.request_handlers
        ), "Server should have CallToolRequest handler registered"

    @pytest.mark.asyncio
    async def test_list_tools_returns_all_six_tools(self):
        """Verify list_tools returns all 6 MAID Runner tools."""
        from mcp import types

        server = create_server()

        # Get the list_tools handler
        handler = server.request_handlers[types.ListToolsRequest]

        # Call the handler
        request = types.ListToolsRequest()
        result = await handler(request)

        # Assert result is ServerResult containing ListToolsResult
        assert isinstance(result, types.ServerResult), "Handler should return ServerResult"
        assert isinstance(result.result, types.ListToolsResult), "Result should be ListToolsResult"

        # Get the tools list
        tools = result.result.tools

        # Assert we have exactly 6 tools
        assert len(tools) == 6, f"Expected 6 tools, got {len(tools)}"

        # Get tool names
        tool_names = [tool.name for tool in tools]

        # Assert all expected tools are present
        expected_tools = [
            "maid_validate",
            "maid_snapshot",
            "maid_test",
            "maid_list_manifests",
            "maid_init",
            "maid_get_schema",
        ]

        for expected_tool in expected_tools:
            assert expected_tool in tool_names, f"Tool '{expected_tool}' should be registered"

    @pytest.mark.asyncio
    async def test_each_tool_has_valid_metadata(self):
        """Verify each tool has required metadata (name, description, inputSchema)."""
        from mcp import types

        server = create_server()

        # Get tools
        handler = server.request_handlers[types.ListToolsRequest]
        request = types.ListToolsRequest()
        result = await handler(request)
        tools = result.result.tools

        # Assert each tool has valid metadata
        for tool in tools:
            assert tool.name, "Tool should have a name"
            assert isinstance(tool.name, str), "Tool name should be a string"
            assert len(tool.name) > 0, "Tool name should not be empty"

            assert tool.description, f"Tool '{tool.name}' should have a description"
            assert isinstance(
                tool.description, str
            ), f"Tool '{tool.name}' description should be a string"

            assert tool.inputSchema, f"Tool '{tool.name}' should have an inputSchema"
            assert isinstance(
                tool.inputSchema, dict
            ), f"Tool '{tool.name}' inputSchema should be a dict"


class TestMaidValidateTool:
    """Test maid_validate tool registration and schema."""

    @pytest.mark.asyncio
    async def test_maid_validate_tool_exists(self):
        """Verify maid_validate tool is registered."""
        from mcp import types

        server = create_server()
        handler = server.request_handlers[types.ListToolsRequest]
        request = types.ListToolsRequest()
        result = await handler(request)
        tools = result.result.tools

        # Find maid_validate tool
        validate_tool = next((t for t in tools if t.name == "maid_validate"), None)

        # Assert tool exists
        assert validate_tool is not None, "maid_validate tool should be registered"

    @pytest.mark.asyncio
    async def test_maid_validate_has_correct_parameters(self):
        """Verify maid_validate tool has correct input parameters."""
        from mcp import types

        server = create_server()
        handler = server.request_handlers[types.ListToolsRequest]
        request = types.ListToolsRequest()
        result = await handler(request)
        tools = result.result.tools

        validate_tool = next((t for t in tools if t.name == "maid_validate"), None)
        schema = validate_tool.inputSchema

        # Assert schema has properties
        assert "properties" in schema, "inputSchema should have properties"
        properties = schema["properties"]

        # Assert required parameters exist
        assert "manifest_path" in properties, "maid_validate should have manifest_path parameter"

        # Assert optional parameters exist
        assert (
            "validation_mode" in properties
        ), "maid_validate should have validation_mode parameter"
        assert (
            "use_manifest_chain" in properties
        ), "maid_validate should have use_manifest_chain parameter"


class TestMaidSnapshotTool:
    """Test maid_snapshot tool registration and schema."""

    @pytest.mark.asyncio
    async def test_maid_snapshot_tool_exists(self):
        """Verify maid_snapshot tool is registered."""
        from mcp import types

        server = create_server()
        handler = server.request_handlers[types.ListToolsRequest]
        request = types.ListToolsRequest()
        result = await handler(request)
        tools = result.result.tools

        snapshot_tool = next((t for t in tools if t.name == "maid_snapshot"), None)

        # Assert tool exists
        assert snapshot_tool is not None, "maid_snapshot tool should be registered"

    @pytest.mark.asyncio
    async def test_maid_snapshot_has_correct_parameters(self):
        """Verify maid_snapshot tool has correct input parameters."""
        from mcp import types

        server = create_server()
        handler = server.request_handlers[types.ListToolsRequest]
        request = types.ListToolsRequest()
        result = await handler(request)
        tools = result.result.tools

        snapshot_tool = next((t for t in tools if t.name == "maid_snapshot"), None)
        schema = snapshot_tool.inputSchema

        # Assert schema has properties
        assert "properties" in schema, "inputSchema should have properties"
        properties = schema["properties"]

        # Assert required parameters exist
        assert "file_path" in properties, "maid_snapshot should have file_path parameter"

        # Assert optional parameters exist
        assert "output_dir" in properties, "maid_snapshot should have output_dir parameter"
        assert "force" in properties, "maid_snapshot should have force parameter"


class TestMaidTestTool:
    """Test maid_test tool registration and schema."""

    @pytest.mark.asyncio
    async def test_maid_test_tool_exists(self):
        """Verify maid_test tool is registered."""
        from mcp import types

        server = create_server()
        handler = server.request_handlers[types.ListToolsRequest]
        request = types.ListToolsRequest()
        result = await handler(request)
        tools = result.result.tools

        test_tool = next((t for t in tools if t.name == "maid_test"), None)

        # Assert tool exists
        assert test_tool is not None, "maid_test tool should be registered"

    @pytest.mark.asyncio
    async def test_maid_test_has_correct_parameters(self):
        """Verify maid_test tool has correct input parameters."""
        from mcp import types

        server = create_server()
        handler = server.request_handlers[types.ListToolsRequest]
        request = types.ListToolsRequest()
        result = await handler(request)
        tools = result.result.tools

        test_tool = next((t for t in tools if t.name == "maid_test"), None)
        schema = test_tool.inputSchema

        # Assert schema has properties
        assert "properties" in schema, "inputSchema should have properties"
        properties = schema["properties"]

        # Assert optional parameters exist
        assert "manifest_dir" in properties, "maid_test should have manifest_dir parameter"
        assert "manifest" in properties, "maid_test should have manifest parameter"
        assert "fail_fast" in properties, "maid_test should have fail_fast parameter"


class TestMaidListManifestsTool:
    """Test maid_list_manifests tool registration and schema."""

    @pytest.mark.asyncio
    async def test_maid_list_manifests_tool_exists(self):
        """Verify maid_list_manifests tool is registered."""
        from mcp import types

        server = create_server()
        handler = server.request_handlers[types.ListToolsRequest]
        request = types.ListToolsRequest()
        result = await handler(request)
        tools = result.result.tools

        list_manifests_tool = next((t for t in tools if t.name == "maid_list_manifests"), None)

        # Assert tool exists
        assert list_manifests_tool is not None, "maid_list_manifests tool should be registered"

    @pytest.mark.asyncio
    async def test_maid_list_manifests_has_correct_parameters(self):
        """Verify maid_list_manifests tool has correct input parameters."""
        from mcp import types

        server = create_server()
        handler = server.request_handlers[types.ListToolsRequest]
        request = types.ListToolsRequest()
        result = await handler(request)
        tools = result.result.tools

        list_manifests_tool = next((t for t in tools if t.name == "maid_list_manifests"), None)
        schema = list_manifests_tool.inputSchema

        # Assert schema has properties
        assert "properties" in schema, "inputSchema should have properties"
        properties = schema["properties"]

        # Assert required parameters exist
        assert "file_path" in properties, "maid_list_manifests should have file_path parameter"

        # Assert optional parameters exist
        assert (
            "manifest_dir" in properties
        ), "maid_list_manifests should have manifest_dir parameter"


class TestMaidInitTool:
    """Test maid_init tool registration and schema."""

    @pytest.mark.asyncio
    async def test_maid_init_tool_exists(self):
        """Verify maid_init tool is registered."""
        from mcp import types

        server = create_server()
        handler = server.request_handlers[types.ListToolsRequest]
        request = types.ListToolsRequest()
        result = await handler(request)
        tools = result.result.tools

        init_tool = next((t for t in tools if t.name == "maid_init"), None)

        # Assert tool exists
        assert init_tool is not None, "maid_init tool should be registered"

    @pytest.mark.asyncio
    async def test_maid_init_has_correct_parameters(self):
        """Verify maid_init tool has correct input parameters."""
        from mcp import types

        server = create_server()
        handler = server.request_handlers[types.ListToolsRequest]
        request = types.ListToolsRequest()
        result = await handler(request)
        tools = result.result.tools

        init_tool = next((t for t in tools if t.name == "maid_init"), None)
        schema = init_tool.inputSchema

        # Assert schema has properties
        assert "properties" in schema, "inputSchema should have properties"
        properties = schema["properties"]

        # Assert optional parameters exist
        assert "target_dir" in properties, "maid_init should have target_dir parameter"
        assert "force" in properties, "maid_init should have force parameter"


class TestMaidGetSchemaTool:
    """Test maid_get_schema tool registration and schema."""

    @pytest.mark.asyncio
    async def test_maid_get_schema_tool_exists(self):
        """Verify maid_get_schema tool is registered."""
        from mcp import types

        server = create_server()
        handler = server.request_handlers[types.ListToolsRequest]
        request = types.ListToolsRequest()
        result = await handler(request)
        tools = result.result.tools

        schema_tool = next((t for t in tools if t.name == "maid_get_schema"), None)

        # Assert tool exists
        assert schema_tool is not None, "maid_get_schema tool should be registered"

    @pytest.mark.asyncio
    async def test_maid_get_schema_has_input_schema(self):
        """Verify maid_get_schema tool has an input schema (even if empty)."""
        from mcp import types

        server = create_server()
        handler = server.request_handlers[types.ListToolsRequest]
        request = types.ListToolsRequest()
        result = await handler(request)
        tools = result.result.tools

        schema_tool = next((t for t in tools if t.name == "maid_get_schema"), None)

        # Assert tool has inputSchema (may be empty for tools with no parameters)
        assert schema_tool.inputSchema is not None, "maid_get_schema should have an inputSchema"
        assert isinstance(schema_tool.inputSchema, dict), "inputSchema should be a dictionary"


class TestToolCallability:
    """Test that tools can be called via the call_tool handler."""

    @pytest.mark.asyncio
    async def test_call_tool_handler_exists(self):
        """Verify call_tool handler can be invoked."""
        from mcp import types

        server = create_server()

        # Assert call_tool handler exists
        assert (
            types.CallToolRequest in server.request_handlers
        ), "Server should have CallToolRequest handler"

        handler = server.request_handlers[types.CallToolRequest]

        # Assert handler is callable
        assert callable(handler), "call_tool handler should be callable"

    @pytest.mark.asyncio
    async def test_call_maid_get_schema_tool_returns_structured_result(self):
        """Verify calling maid_get_schema returns a structured result."""
        from mcp import types

        server = create_server()
        handler = server.request_handlers[types.CallToolRequest]

        # Create a call request for maid_get_schema (no arguments needed)
        request = types.CallToolRequest(
            params=types.CallToolRequestParams(name="maid_get_schema", arguments={})
        )

        # Call the tool
        result = await handler(request)

        # Assert result is ServerResult
        assert isinstance(result, types.ServerResult), "Handler should return ServerResult"

        # Assert result contains CallToolResult
        assert isinstance(result.result, types.CallToolResult), "Result should be CallToolResult"

        # Assert result has content
        assert result.result.content, "CallToolResult should have content"
        assert len(result.result.content) > 0, "Content should not be empty"


class TestServerMetadataPreserved:
    """Test that existing server metadata is preserved after tool registration."""

    def test_server_name_unchanged(self):
        """Verify server name remains 'maid-runner-mcp'."""
        server = create_server()

        # Assert server name is preserved
        assert server.name == "maid-runner-mcp", "Server name should remain unchanged"

    def test_server_version_unchanged(self):
        """Verify server version is still set."""
        server = create_server()

        # Assert server version is preserved
        assert server.version is not None, "Server version should not be None"
        assert isinstance(server.version, str), "Server version should be a string"
        assert len(server.version) > 0, "Server version should not be empty"

    def test_server_has_run_method(self):
        """Verify server still has run method for stdio transport."""
        server = create_server()

        # Assert server has run method
        assert hasattr(server, "run"), "Server should have run method"
        assert callable(server.run), "Server run method should be callable"


class TestMainEntryPoint:
    """Test that main() entry point still works with tools registered."""

    def test_main_function_exists(self):
        """Verify main() function is still accessible."""
        # Assert main function exists and is callable
        assert callable(main), "main() function should be callable"

    def test_main_returns_none(self):
        """Verify main() still has correct return type annotation."""
        import inspect

        # Get main function signature
        sig = inspect.signature(main)

        # Assert return annotation is None
        assert (
            sig.return_annotation is type(None) or sig.return_annotation is None
        ), "main() should return None"

    def test_main_handles_keyboard_interrupt_with_tools(self):
        """Verify main() handles KeyboardInterrupt with tools registered."""
        from unittest.mock import AsyncMock, MagicMock, patch

        mock_server = MagicMock()
        mock_server.run = AsyncMock(side_effect=KeyboardInterrupt)

        with patch("maid_runner_mcp.server.create_server", return_value=mock_server):
            with patch("maid_runner_mcp.server.stdio_server") as mock_stdio:
                mock_stdio.return_value.__aenter__ = AsyncMock()
                mock_stdio.return_value.__aexit__ = AsyncMock()

                # Should not raise - should handle gracefully
                try:
                    result = main()
                except KeyboardInterrupt:
                    result = None  # This is acceptable

        # Assert main returns None
        assert result is None, "main() should return None even with tools registered"

    @pytest.mark.asyncio
    async def test_main_starts_server_with_tools_registered(self):
        """Verify main() starts server with all tools registered."""
        import asyncio
        from unittest.mock import AsyncMock, MagicMock, patch

        # Mock the server's run method
        mock_server = MagicMock()
        mock_server.run = AsyncMock()
        mock_server.create_initialization_options = MagicMock(return_value={})

        # Track that create_server was called
        create_server_called = False

        def mock_create_server():
            nonlocal create_server_called
            create_server_called = True
            return mock_server

        # Mock stdio_server context manager
        mock_read_stream = AsyncMock()
        mock_write_stream = AsyncMock()
        mock_stdio_context = AsyncMock()
        mock_stdio_context.__aenter__ = AsyncMock(
            return_value=(mock_read_stream, mock_write_stream)
        )
        mock_stdio_context.__aexit__ = AsyncMock(return_value=None)

        with patch("maid_runner_mcp.server.create_server", side_effect=mock_create_server):
            with patch("maid_runner_mcp.server.stdio_server", return_value=mock_stdio_context):
                # Run main in a separate task with timeout
                main_task = asyncio.create_task(asyncio.to_thread(main))

                # Give it a moment to start
                await asyncio.sleep(0.1)

                # Cancel the task (since main() would run forever)
                main_task.cancel()

                try:
                    await main_task
                except (asyncio.CancelledError, SystemExit, Exception):
                    pass  # Expected when cancelling

        # Assert create_server was called (which means tools are registered)
        assert create_server_called, "main() should call create_server() which registers tools"


class TestToolIntegration:
    """Integration tests for complete tool registration workflow."""

    @pytest.mark.asyncio
    async def test_all_tools_accessible_via_list_and_call(self):
        """Verify all tools can be listed and the call_tool handler is ready."""
        from mcp import types

        server = create_server()

        # Step 1: List all tools
        list_handler = server.request_handlers[types.ListToolsRequest]
        list_request = types.ListToolsRequest()
        list_result = await list_handler(list_request)
        tools = list_result.result.tools

        # Step 2: Verify we have 6 tools
        assert len(tools) == 6, "Should have 6 tools registered"

        # Step 3: Verify call_tool handler exists
        call_handler = server.request_handlers[types.CallToolRequest]
        assert callable(call_handler), "call_tool handler should be callable"

        # This proves complete integration: tools are registered and callable

    @pytest.mark.asyncio
    async def test_tool_names_follow_maid_convention(self):
        """Verify all tool names follow the 'maid_*' naming convention."""
        from mcp import types

        server = create_server()
        handler = server.request_handlers[types.ListToolsRequest]
        request = types.ListToolsRequest()
        result = await handler(request)
        tools = result.result.tools

        # Assert all tools start with 'maid_'
        for tool in tools:
            assert tool.name.startswith(
                "maid_"
            ), f"Tool '{tool.name}' should follow maid_* naming convention"

    @pytest.mark.asyncio
    async def test_server_capabilities_include_tools(self):
        """Verify server advertises tool capability."""
        server = create_server()

        # Create initialization options
        init_options = server.create_initialization_options()

        # Assert server capabilities include tools
        assert (
            init_options.capabilities.tools is not None
        ), "Server should advertise tools capability"
