"""Behavioral tests for task-008: Implement maid_get_schema MCP tool.

Tests verify that the maid_get_schema function:
1. Wraps MAID Runner schema command correctly
2. Handles async execution properly
3. Returns structured JSON responses
4. Returns the complete JSON schema for MAID manifests
5. Handles errors appropriately
6. Requires no parameters
"""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from maid_runner_mcp.tools.schema import maid_get_schema


class TestMaidGetSchemaBasicBehavior:
    """Test basic maid_get_schema function behavior."""

    @pytest.mark.asyncio
    async def test_maid_get_schema_returns_success(self):
        """Test that schema retrieval succeeds."""
        # Mock subprocess to simulate successful schema output
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "MAID Task Manifest",
            "type": "object",
            "properties": {
                "goal": {"type": "string"},
                "taskType": {"type": "string"},
            },
        }
        mock_process.stdout = json.dumps(mock_schema).encode("utf-8")
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_get_schema()

        # Assert result is a dictionary
        assert isinstance(result, dict), "maid_get_schema must return a dictionary"

        # Assert success field is True
        assert "success" in result, "Result must contain 'success' field"
        assert result["success"] is True, f"Expected success=True, got {result.get('success')}"

        # Assert schema field is included
        assert "schema" in result, "Result must contain 'schema' field"
        assert isinstance(result["schema"], dict), "Schema must be a dictionary"

    @pytest.mark.asyncio
    async def test_maid_get_schema_returns_complete_schema(self):
        """Test that the full JSON schema is returned."""
        # Mock subprocess to return a complete schema
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "MAID Task Manifest",
            "type": "object",
            "required": ["goal", "readonlyFiles"],
            "properties": {
                "version": {"type": "string"},
                "goal": {"type": "string"},
                "taskType": {"type": "string"},
                "creatableFiles": {"type": "array"},
                "editableFiles": {"type": "array"},
                "readonlyFiles": {"type": "array"},
                "expectedArtifacts": {"type": "object"},
            },
        }
        mock_process.stdout = json.dumps(mock_schema).encode("utf-8")
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_get_schema()

        # Assert schema contains expected top-level fields
        assert result["success"] is True
        schema = result["schema"]
        assert "$schema" in schema, "Schema must contain '$schema' field"
        assert "title" in schema, "Schema must contain 'title' field"
        assert "properties" in schema, "Schema must contain 'properties' field"
        assert schema["title"] == "MAID Task Manifest"

    @pytest.mark.asyncio
    async def test_maid_get_schema_takes_no_parameters(self):
        """Test that maid_get_schema requires no parameters."""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_schema = {"$schema": "http://json-schema.org/draft-07/schema#"}
        mock_process.stdout = json.dumps(mock_schema).encode("utf-8")
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            # Call without any parameters
            result = await maid_get_schema()

        # Assert the function accepts no parameters
        assert isinstance(result, dict), "Must return dictionary even with no parameters"
        assert result["success"] is True

        # Assert the command was called correctly
        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]
        assert call_args == ("maid", "schema"), f"Expected ('maid', 'schema'), got {call_args}"


class TestMaidGetSchemaCommandExecution:
    """Test command execution behavior."""

    @pytest.mark.asyncio
    async def test_maid_get_schema_executes_correct_command(self):
        """Test that the correct CLI command is executed."""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_schema = {"$schema": "http://json-schema.org/draft-07/schema#"}
        mock_process.stdout = json.dumps(mock_schema).encode("utf-8")
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            await maid_get_schema()

        # Assert subprocess was called with correct command
        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]
        assert "maid" in call_args, "Command must include 'maid'"
        assert "schema" in call_args, "Command must include 'schema'"

    @pytest.mark.asyncio
    async def test_maid_get_schema_captures_stdout(self):
        """Test that stdout is properly captured and parsed."""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Test Schema",
            "type": "object",
        }
        mock_process.stdout = json.dumps(mock_schema).encode("utf-8")
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_get_schema()

        # Assert stdout was parsed correctly
        assert result["success"] is True
        assert result["schema"]["title"] == "Test Schema"
        assert result["schema"]["$schema"] == "http://json-schema.org/draft-07/schema#"


class TestMaidGetSchemaErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.asyncio
    async def test_maid_get_schema_handles_command_failure(self):
        """Test handling when schema command fails."""
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stdout = b""
        mock_process.stderr = b"Error: Failed to generate schema\n"

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_get_schema()

        # Assert result indicates failure
        assert isinstance(result, dict), "maid_get_schema must return a dictionary"
        assert "success" in result, "Result must contain 'success' field"
        assert result["success"] is False, f"Expected success=False, got {result.get('success')}"

        # Assert errors are included
        assert "errors" in result, "Result must contain 'errors' field for failures"
        assert isinstance(result["errors"], list), "Errors must be a list"
        assert len(result["errors"]) > 0, "Errors list must not be empty for failed command"

    @pytest.mark.asyncio
    async def test_maid_get_schema_handles_invalid_json_output(self):
        """Test handling when schema command returns invalid JSON."""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"{ invalid json content"
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_get_schema()

        # Assert result indicates error
        assert isinstance(result, dict), "Must return dictionary even on parse error"
        assert result["success"] is False, "Expected success=False for invalid JSON"
        assert "errors" in result, "Result must contain 'errors' field"
        assert len(result["errors"]) > 0, "Errors must be reported for invalid JSON"

    @pytest.mark.asyncio
    async def test_maid_get_schema_handles_subprocess_errors(self):
        """Test handling of subprocess execution errors."""
        # Mock subprocess to raise an exception
        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.side_effect = OSError("Command not found")

            result = await maid_get_schema()

        # Assert error is handled gracefully
        assert isinstance(result, dict), "Must return dictionary even on error"
        assert result["success"] is False, "Expected success=False for subprocess error"
        assert "errors" in result, "Must include errors on exception"
        assert len(result["errors"]) > 0, "Errors must be reported"

    @pytest.mark.asyncio
    async def test_maid_get_schema_handles_timeout(self):
        """Test handling of command timeout."""
        # Mock subprocess to simulate timeout
        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_process = MagicMock()
            mock_process.communicate = AsyncMock(side_effect=asyncio.TimeoutError)
            mock_exec.return_value = mock_process

            result = await maid_get_schema()

        # Assert timeout is handled
        assert isinstance(result, dict), "Must return dictionary even on timeout"
        assert result["success"] is False, "success must be False on timeout"
        assert "errors" in result, "Must include errors on timeout"

    @pytest.mark.asyncio
    async def test_maid_get_schema_handles_empty_output(self):
        """Test handling when schema command returns empty output."""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b""
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_get_schema()

        # Assert error is reported for empty output
        assert result["success"] is False, "Expected success=False for empty output"
        assert "errors" in result, "Result must contain 'errors' for empty output"


class TestMaidGetSchemaOutputStructure:
    """Test structured output format."""

    @pytest.mark.asyncio
    async def test_maid_get_schema_output_contains_required_fields(self):
        """Test that output contains all required fields."""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "MAID Task Manifest",
        }
        mock_process.stdout = json.dumps(mock_schema).encode("utf-8")
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_get_schema()

        # Assert all required fields are present
        required_fields = ["success", "schema"]
        for field in required_fields:
            assert field in result, f"Result must contain '{field}' field"

        # Assert field types
        assert isinstance(result["success"], bool), "success must be a boolean"
        assert isinstance(result["schema"], dict), "schema must be a dictionary"

    @pytest.mark.asyncio
    async def test_maid_get_schema_output_includes_errors_on_failure(self):
        """Test that errors are included in output on failure."""
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stdout = b""
        mock_process.stderr = b"Error: Schema generation failed\n"

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_get_schema()

        # Assert errors are included
        assert "errors" in result, "Result must contain 'errors' on failure"
        assert isinstance(result["errors"], list), "Errors must be a list"
        assert len(result["errors"]) > 0, "Errors list must not be empty"

        # Assert errors contain meaningful messages
        errors = result["errors"]
        assert any("schema" in str(err).lower() for err in errors), "Errors should mention schema"
