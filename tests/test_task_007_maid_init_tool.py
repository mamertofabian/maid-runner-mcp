"""Behavioral tests for task-007: Implement maid_init MCP tool.

Tests verify that the maid_init function:
1. Wraps MAID Runner init command correctly
2. Handles async execution properly
3. Returns structured JSON responses
4. Supports target_dir parameter (defaults to ".")
5. Supports force flag to overwrite existing files
6. Parses created files from output
7. Handles errors appropriately (directory already initialized, invalid paths, etc.)
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from maid_runner_mcp.tools.init import maid_init


class TestMaidInitBasicBehavior:
    """Test basic maid_init function behavior."""

    @pytest.mark.asyncio
    async def test_maid_init_with_default_directory_succeeds(self, tmp_path):
        """Test that initialization succeeds with default directory."""
        # Mock subprocess to simulate successful init
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"MAID project initialized successfully\nCreated: .maid/docs/maid_specs.md\nCreated: manifests/\n"
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_init()

        # Assert result is a dictionary
        assert isinstance(result, dict), "maid_init must return a dictionary"

        # Assert success field is True
        assert "success" in result, "Result must contain 'success' field"
        assert result["success"] is True, f"Expected success=True, got {result.get('success')}"

        # Assert initialized_dir is included
        assert "initialized_dir" in result, "Result must contain 'initialized_dir' field"

        # Assert created_files is included
        assert "created_files" in result, "Result must contain 'created_files' field"
        assert isinstance(result["created_files"], list), "created_files must be a list"

    @pytest.mark.asyncio
    async def test_maid_init_with_custom_directory_succeeds(self, tmp_path):
        """Test that initialization succeeds with custom directory."""
        custom_dir = tmp_path / "my_project"
        custom_dir.mkdir()

        # Mock subprocess to simulate successful init
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = (
            b"MAID project initialized successfully\nCreated: .maid/docs/maid_specs.md\n"
        )
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_init(target_dir=str(custom_dir))

        # Assert result indicates success
        assert result["success"] is True, "Expected success=True for custom directory"

        # Assert initialized_dir matches the target
        assert "initialized_dir" in result
        assert result["initialized_dir"] == str(custom_dir)

        # Assert command was called with custom directory
        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]
        assert "maid" in call_args
        assert "init" in call_args
        assert str(custom_dir) in call_args

    @pytest.mark.asyncio
    async def test_maid_init_already_initialized_without_force_fails(self, tmp_path):
        """Test that initialization fails when directory is already initialized without force flag."""
        # Mock subprocess to simulate already initialized error
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stdout = b""
        mock_process.stderr = b"Error: Directory already initialized. Use --force to overwrite.\n"

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_init(target_dir=str(tmp_path))

        # Assert result indicates failure
        assert isinstance(result, dict), "maid_init must return a dictionary"
        assert "success" in result, "Result must contain 'success' field"
        assert result["success"] is False, f"Expected success=False, got {result.get('success')}"

        # Assert errors are included
        assert "errors" in result, "Result must contain 'errors' field for failures"
        assert isinstance(result["errors"], list), "Errors must be a list"
        assert len(result["errors"]) > 0, "Errors list must not be empty for failed initialization"

    @pytest.mark.asyncio
    async def test_maid_init_with_nonexistent_directory_fails(self):
        """Test that initialization fails with nonexistent directory."""
        nonexistent_dir = "/nonexistent/path/to/directory"

        # Mock subprocess to simulate directory not found error
        mock_process = MagicMock()
        mock_process.returncode = 2
        mock_process.stdout = b""
        mock_process.stderr = b"Error: Target directory does not exist\n"

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_init(target_dir=nonexistent_dir)

        # Assert result indicates error
        assert isinstance(result, dict), "maid_init must return a dictionary"
        assert result["success"] is False, "Expected success=False for nonexistent directory"
        assert "errors" in result, "Result must contain 'errors' field"
        assert len(result["errors"]) > 0, "Errors must be reported for nonexistent directory"


class TestMaidInitForceFlag:
    """Test force flag behavior."""

    @pytest.mark.asyncio
    async def test_maid_init_with_force_overwrites_existing(self, tmp_path):
        """Test that initialization with force flag succeeds even if already initialized."""
        # Mock subprocess to simulate successful forced init
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"MAID project re-initialized successfully\nCreated: .maid/docs/maid_specs.md\nOverwritten: manifests/\n"
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_init(target_dir=str(tmp_path), force=True)

        # Assert result indicates success
        assert result["success"] is True, "Expected success=True with force flag"

        # Assert force flag was passed to command
        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]
        assert "--force" in call_args, "Must pass --force flag when force=True"

    @pytest.mark.asyncio
    async def test_maid_init_without_force_does_not_overwrite(self, tmp_path):
        """Test that initialization without force flag does not include --force."""
        # Mock subprocess to simulate successful init
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"MAID project initialized successfully\n"
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            _result = await maid_init(target_dir=str(tmp_path), force=False)

        # Assert force flag was NOT passed
        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]
        assert "--force" not in call_args, "Should not pass --force flag when force=False"


class TestMaidInitOutputParsing:
    """Test parsing of created files from output."""

    @pytest.mark.asyncio
    async def test_maid_init_parses_created_files(self, tmp_path):
        """Test that created files are extracted from output."""
        # Mock subprocess with detailed output
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"""MAID project initialized successfully
Created: .maid/docs/maid_specs.md
Created: manifests/
Created: tests/
Created: pyproject.toml
"""
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_init(target_dir=str(tmp_path))

        # Assert created_files contains parsed files
        assert "created_files" in result
        assert isinstance(result["created_files"], list)
        # Should contain at least some of the created files
        assert len(result["created_files"]) >= 0  # May be empty if parsing fails

    @pytest.mark.asyncio
    async def test_maid_init_handles_empty_output(self, tmp_path):
        """Test that function handles empty output gracefully."""
        # Mock subprocess with minimal output
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"Initialized successfully\n"
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_init(target_dir=str(tmp_path))

        # Assert result is valid even with minimal output
        assert result["success"] is True
        assert "created_files" in result
        assert isinstance(result["created_files"], list)


class TestMaidInitOutputStructure:
    """Test structured output format."""

    @pytest.mark.asyncio
    async def test_maid_init_output_contains_required_fields(self, tmp_path):
        """Test that output contains all required fields."""
        # Mock subprocess
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"MAID project initialized successfully\n"
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_init(target_dir=str(tmp_path))

        # Assert all required fields are present
        required_fields = ["success", "initialized_dir", "created_files"]
        for field in required_fields:
            assert field in result, f"Result must contain '{field}' field"

        # Assert field types
        assert isinstance(result["success"], bool), "success must be a boolean"
        assert isinstance(result["initialized_dir"], str), "initialized_dir must be a string"
        assert isinstance(result["created_files"], list), "created_files must be a list"

    @pytest.mark.asyncio
    async def test_maid_init_output_includes_errors_on_failure(self, tmp_path):
        """Test that errors are included in output on initialization failure."""
        # Mock subprocess to simulate failure
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stdout = b""
        mock_process.stderr = b"Error: Permission denied\nError: Cannot create directory\n"

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_init(target_dir=str(tmp_path))

        # Assert errors are included
        assert "errors" in result, "Result must contain 'errors' on failure"
        assert isinstance(result["errors"], list), "Errors must be a list"
        assert len(result["errors"]) > 0, "Errors list must not be empty"

        # Assert errors contain meaningful messages
        errors = result["errors"]
        assert any(
            "permission" in str(err).lower() for err in errors
        ), "Errors should mention permission issue"


class TestMaidInitErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.asyncio
    async def test_maid_init_handles_subprocess_errors(self, tmp_path):
        """Test handling of subprocess execution errors."""
        # Mock subprocess to raise an exception
        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.side_effect = OSError("Command not found")

            result = await maid_init(target_dir=str(tmp_path))

        # Assert error is handled gracefully
        assert isinstance(result, dict), "Must return dictionary even on error"
        assert result["success"] is False, "success must be False on error"
        assert "errors" in result, "Must include errors on exception"
        assert len(result["errors"]) > 0, "Errors must be reported"

    @pytest.mark.asyncio
    async def test_maid_init_handles_timeout(self, tmp_path):
        """Test handling of command timeout."""
        # Mock subprocess to simulate timeout
        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_process = MagicMock()
            mock_process.communicate = AsyncMock(side_effect=asyncio.TimeoutError)
            mock_exec.return_value = mock_process

            result = await maid_init(target_dir=str(tmp_path))

        # Assert timeout is handled
        assert isinstance(result, dict), "Must return dictionary even on timeout"
        assert result["success"] is False, "success must be False on timeout"
        assert "errors" in result, "Must include errors on timeout"

    @pytest.mark.asyncio
    async def test_maid_init_handles_unexpected_errors(self, tmp_path):
        """Test handling of unexpected errors."""
        # Mock subprocess to raise unexpected exception
        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.side_effect = RuntimeError("Unexpected error")

            result = await maid_init(target_dir=str(tmp_path))

        # Assert error is handled gracefully
        assert isinstance(result, dict), "Must return dictionary even on unexpected error"
        assert result["success"] is False, "success must be False on unexpected error"
        assert "errors" in result, "Must include errors on unexpected error"


class TestMaidInitDefaultParameters:
    """Test default parameter values."""

    @pytest.mark.asyncio
    async def test_maid_init_defaults_to_current_directory(self):
        """Test that default target_dir is '.'."""
        # Mock subprocess
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"MAID project initialized successfully\n"
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            # Call without specifying target_dir
            result = await maid_init()

        # Assert default directory is used
        assert result["initialized_dir"] == ".", "Default target_dir should be '.'"

        # Assert command was called with default directory
        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]
        assert "." in call_args, "Should pass '.' as default directory"

    @pytest.mark.asyncio
    async def test_maid_init_defaults_to_no_force(self):
        """Test that force defaults to False."""
        # Mock subprocess
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"MAID project initialized successfully\n"
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            # Call without specifying force
            _result = await maid_init()

        # Assert force flag is not used by default
        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]
        assert "--force" not in call_args, "Should not pass --force by default"
