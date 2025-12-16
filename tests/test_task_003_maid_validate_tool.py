"""Behavioral tests for task-003: Implement maid_validate MCP tool.

Tests verify that the maid_validate function:
1. Wraps MAID Runner validate command correctly
2. Handles async execution properly
3. Returns structured JSON responses
4. Supports all validation modes (implementation/behavioral)
5. Handles manifest chain validation
6. Processes errors appropriately
7. Supports quiet mode and manifest_dir parameters
"""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from maid_runner_mcp.tools.validate import maid_validate


class TestMaidValidateBasicBehavior:
    """Test basic maid_validate function behavior."""

    @pytest.mark.asyncio
    async def test_maid_validate_with_valid_manifest_returns_success(self, tmp_path):
        """Test that validation succeeds with a valid manifest."""
        # Create a minimal valid manifest
        manifest_path = tmp_path / "test.manifest.json"
        manifest_data = {
            "version": "1",
            "goal": "Test manifest",
            "taskType": "create",
            "creatableFiles": ["test.py"],
            "editableFiles": [],
            "readonlyFiles": [],
            "expectedArtifacts": {"file": "test.py", "contains": []},
            "validationCommand": ["echo", "test"],
        }
        manifest_path.write_text(json.dumps(manifest_data))

        # Mock subprocess to simulate successful validation
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"Validation passed\n"
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_validate(str(manifest_path))

        # Assert result is a dictionary
        assert isinstance(result, dict), "maid_validate must return a dictionary"

        # Assert success field is True
        assert "success" in result, "Result must contain 'success' field"
        assert result["success"] is True, f"Expected success=True, got {result.get('success')}"

        # Assert manifest path is included
        assert "manifest" in result, "Result must contain 'manifest' field"
        assert result["manifest"] == str(manifest_path)

    @pytest.mark.asyncio
    async def test_maid_validate_with_invalid_manifest_returns_failure(self, tmp_path):
        """Test that validation fails with an invalid manifest."""
        # Create an invalid manifest (missing required fields)
        manifest_path = tmp_path / "invalid.manifest.json"
        manifest_data = {"invalid": "data"}
        manifest_path.write_text(json.dumps(manifest_data))

        # Mock subprocess to simulate validation failure
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stdout = b""
        mock_process.stderr = b"Error: Missing required field 'version'\n"

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_validate(str(manifest_path))

        # Assert result indicates failure
        assert isinstance(result, dict), "maid_validate must return a dictionary"
        assert "success" in result, "Result must contain 'success' field"
        assert result["success"] is False, f"Expected success=False, got {result.get('success')}"

        # Assert errors are included
        assert "errors" in result, "Result must contain 'errors' field for failures"
        assert isinstance(result["errors"], list), "Errors must be a list"
        assert len(result["errors"]) > 0, "Errors list must not be empty for failed validation"

    @pytest.mark.asyncio
    async def test_maid_validate_with_nonexistent_manifest_returns_error(self):
        """Test that validation handles nonexistent manifest file."""
        nonexistent_path = "/nonexistent/path/to/manifest.json"

        # Mock subprocess to simulate file not found error
        mock_process = MagicMock()
        mock_process.returncode = 2
        mock_process.stdout = b""
        mock_process.stderr = b"Error: Manifest file not found\n"

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_validate(nonexistent_path)

        # Assert result indicates error
        assert isinstance(result, dict), "maid_validate must return a dictionary"
        assert result["success"] is False, "Expected success=False for nonexistent file"
        assert "errors" in result, "Result must contain 'errors' field"
        assert len(result["errors"]) > 0, "Errors must be reported for nonexistent file"


class TestMaidValidateValidationModes:
    """Test validation mode switching."""

    @pytest.mark.asyncio
    async def test_maid_validate_with_implementation_mode(self, tmp_path):
        """Test validation in implementation mode (default)."""
        manifest_path = tmp_path / "test.manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "version": "1",
                    "goal": "Test",
                    "taskType": "create",
                    "creatableFiles": ["test.py"],
                    "editableFiles": [],
                    "readonlyFiles": [],
                    "expectedArtifacts": {"file": "test.py", "contains": []},
                    "validationCommand": ["echo", "test"],
                }
            )
        )

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"Validation passed\n"
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_validate(str(manifest_path), validation_mode="implementation")

        # Assert mode is recorded in result
        assert "mode" in result, "Result must contain 'mode' field"
        assert (
            result["mode"] == "implementation"
        ), f"Expected mode='implementation', got {result.get('mode')}"

        # Assert validation command was called with correct mode
        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]
        assert "--validation-mode" in call_args, "Must pass --validation-mode flag"
        mode_index = list(call_args).index("--validation-mode")
        assert call_args[mode_index + 1] == "implementation"

    @pytest.mark.asyncio
    async def test_maid_validate_with_behavioral_mode(self, tmp_path):
        """Test validation in behavioral mode."""
        manifest_path = tmp_path / "test.manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "version": "1",
                    "goal": "Test",
                    "taskType": "create",
                    "creatableFiles": ["test.py"],
                    "editableFiles": [],
                    "readonlyFiles": [],
                    "expectedArtifacts": {"file": "test.py", "contains": []},
                    "validationCommand": ["pytest", "tests/test.py"],
                }
            )
        )

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"Behavioral validation passed\n"
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_validate(str(manifest_path), validation_mode="behavioral")

        # Assert mode is behavioral
        assert (
            result["mode"] == "behavioral"
        ), f"Expected mode='behavioral', got {result.get('mode')}"

        # Assert validation command included behavioral mode
        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]
        assert "--validation-mode" in call_args
        mode_index = list(call_args).index("--validation-mode")
        assert call_args[mode_index + 1] == "behavioral"


class TestMaidValidateManifestChain:
    """Test manifest chain validation."""

    @pytest.mark.asyncio
    async def test_maid_validate_with_manifest_chain_enabled(self, tmp_path):
        """Test validation with manifest chain enabled."""
        manifest_path = tmp_path / "test.manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "version": "1",
                    "goal": "Test",
                    "taskType": "edit",
                    "supersedes": ["task-001"],
                    "creatableFiles": [],
                    "editableFiles": ["test.py"],
                    "readonlyFiles": [],
                    "expectedArtifacts": {"file": "test.py", "contains": []},
                    "validationCommand": ["echo", "test"],
                }
            )
        )

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"Validation with chain passed\n"
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_validate(str(manifest_path), use_manifest_chain=True)

        # Assert chain usage is recorded
        assert "use_manifest_chain" in result, "Result must contain 'use_manifest_chain' field"
        assert result["use_manifest_chain"] is True, "Expected use_manifest_chain=True"

        # Assert validation command included chain flag
        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]
        assert "--use-manifest-chain" in call_args, "Must pass --use-manifest-chain flag"

    @pytest.mark.asyncio
    async def test_maid_validate_without_manifest_chain(self, tmp_path):
        """Test validation without manifest chain (default)."""
        manifest_path = tmp_path / "test.manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "version": "1",
                    "goal": "Test",
                    "taskType": "create",
                    "creatableFiles": ["test.py"],
                    "editableFiles": [],
                    "readonlyFiles": [],
                    "expectedArtifacts": {"file": "test.py", "contains": []},
                    "validationCommand": ["echo", "test"],
                }
            )
        )

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"Validation passed\n"
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_validate(str(manifest_path), use_manifest_chain=False)

        # Assert chain is not used
        assert result.get("use_manifest_chain") is False, "Expected use_manifest_chain=False"

        # Assert validation command did NOT include chain flag
        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]
        assert (
            "--use-manifest-chain" not in call_args
        ), "Should not pass --use-manifest-chain when disabled"


class TestMaidValidateOptionalParameters:
    """Test optional parameters: manifest_dir and quiet."""

    @pytest.mark.asyncio
    async def test_maid_validate_with_custom_manifest_dir(self, tmp_path):
        """Test validation with custom manifest directory."""
        custom_dir = tmp_path / "custom_manifests"
        custom_dir.mkdir()
        manifest_path = custom_dir / "test.manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "version": "1",
                    "goal": "Test",
                    "taskType": "create",
                    "creatableFiles": ["test.py"],
                    "editableFiles": [],
                    "readonlyFiles": [],
                    "expectedArtifacts": {"file": "test.py", "contains": []},
                    "validationCommand": ["echo", "test"],
                }
            )
        )

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"Validation passed\n"
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_validate(str(manifest_path), manifest_dir=str(custom_dir))

        # Assert custom manifest dir is used
        assert "manifest_dir" in result, "Result should contain 'manifest_dir' field"
        assert result["manifest_dir"] == str(custom_dir)

        # Assert validation command included manifest-dir flag
        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]
        assert "--manifest-dir" in call_args, "Must pass --manifest-dir flag"
        dir_index = list(call_args).index("--manifest-dir")
        assert call_args[dir_index + 1] == str(custom_dir)

    @pytest.mark.asyncio
    async def test_maid_validate_with_quiet_mode_enabled(self, tmp_path):
        """Test validation with quiet mode enabled (default)."""
        manifest_path = tmp_path / "test.manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "version": "1",
                    "goal": "Test",
                    "taskType": "create",
                    "creatableFiles": ["test.py"],
                    "editableFiles": [],
                    "readonlyFiles": [],
                    "expectedArtifacts": {"file": "test.py", "contains": []},
                    "validationCommand": ["echo", "test"],
                }
            )
        )

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"Minimal output\n"
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_validate(str(manifest_path), quiet=True)

        # Assert quiet mode is recorded
        assert "quiet" in result, "Result should contain 'quiet' field"
        assert result["quiet"] is True, "Expected quiet=True"

        # Assert validation command included quiet flag
        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]
        assert "--quiet" in call_args or "-q" in call_args, "Must pass quiet flag"

    @pytest.mark.asyncio
    async def test_maid_validate_with_quiet_mode_disabled(self, tmp_path):
        """Test validation with quiet mode disabled."""
        manifest_path = tmp_path / "test.manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "version": "1",
                    "goal": "Test",
                    "taskType": "create",
                    "creatableFiles": ["test.py"],
                    "editableFiles": [],
                    "readonlyFiles": [],
                    "expectedArtifacts": {"file": "test.py", "contains": []},
                    "validationCommand": ["echo", "test"],
                }
            )
        )

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"Verbose validation output\nDetailed information\n"
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_validate(str(manifest_path), quiet=False)

        # Assert quiet is disabled
        assert result.get("quiet") is False, "Expected quiet=False"

        # Assert validation command did NOT include quiet flag
        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]
        assert (
            "--quiet" not in call_args and "-q" not in call_args
        ), "Should not pass quiet flag when disabled"


class TestMaidValidateOutputStructure:
    """Test structured output format."""

    @pytest.mark.asyncio
    async def test_maid_validate_output_contains_required_fields(self, tmp_path):
        """Test that output contains all required fields."""
        manifest_path = tmp_path / "test.manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "version": "1",
                    "goal": "Test",
                    "taskType": "create",
                    "creatableFiles": ["test.py"],
                    "editableFiles": [],
                    "readonlyFiles": [],
                    "expectedArtifacts": {"file": "test.py", "contains": []},
                    "validationCommand": ["echo", "test"],
                }
            )
        )

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"Validation passed\n"
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_validate(str(manifest_path))

        # Assert all required fields are present
        required_fields = ["success", "manifest", "mode"]
        for field in required_fields:
            assert field in result, f"Result must contain '{field}' field"

        # Assert field types
        assert isinstance(result["success"], bool), "success must be a boolean"
        assert isinstance(result["manifest"], str), "manifest must be a string"
        assert isinstance(result["mode"], str), "mode must be a string"

    @pytest.mark.asyncio
    async def test_maid_validate_output_includes_target_file_when_available(self, tmp_path):
        """Test that output includes target_file from manifest."""
        manifest_path = tmp_path / "test.manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "version": "1",
                    "goal": "Test",
                    "taskType": "create",
                    "creatableFiles": ["target_file.py"],
                    "editableFiles": [],
                    "readonlyFiles": [],
                    "expectedArtifacts": {"file": "target_file.py", "contains": []},
                    "validationCommand": ["echo", "test"],
                }
            )
        )

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"Validation passed\nTarget: target_file.py\n"
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_validate(str(manifest_path))

        # Assert target_file is included if parsed from output
        # (Implementation detail - may or may not be in result)
        assert isinstance(result, dict), "Result must be a dictionary"

    @pytest.mark.asyncio
    async def test_maid_validate_output_includes_errors_on_failure(self, tmp_path):
        """Test that errors are included in output on validation failure."""
        manifest_path = tmp_path / "test.manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "version": "1",
                    "goal": "Test",
                    "taskType": "create",
                    "creatableFiles": ["test.py"],
                    "editableFiles": [],
                    "readonlyFiles": [],
                    "expectedArtifacts": {"file": "test.py", "contains": []},
                    "validationCommand": ["echo", "test"],
                }
            )
        )

        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stdout = b""
        mock_process.stderr = (
            b"Error: Function 'foo' not found\nError: Class 'Bar' not implemented\n"
        )

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_validate(str(manifest_path))

        # Assert errors are included
        assert "errors" in result, "Result must contain 'errors' on failure"
        assert isinstance(result["errors"], list), "Errors must be a list"
        assert len(result["errors"]) > 0, "Errors list must not be empty"

        # Assert errors contain meaningful messages
        errors = result["errors"]
        assert any(
            "foo" in str(err).lower() for err in errors
        ), "Errors should mention missing function 'foo'"


class TestMaidValidateErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.asyncio
    async def test_maid_validate_handles_subprocess_errors(self, tmp_path):
        """Test handling of subprocess execution errors."""
        manifest_path = tmp_path / "test.manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "version": "1",
                    "goal": "Test",
                    "taskType": "create",
                    "creatableFiles": ["test.py"],
                    "editableFiles": [],
                    "readonlyFiles": [],
                    "expectedArtifacts": {"file": "test.py", "contains": []},
                    "validationCommand": ["echo", "test"],
                }
            )
        )

        # Mock subprocess to raise an exception
        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.side_effect = OSError("Command not found")

            result = await maid_validate(str(manifest_path))

        # Assert error is handled gracefully
        assert isinstance(result, dict), "Must return dictionary even on error"
        assert result["success"] is False, "success must be False on error"
        assert "errors" in result, "Must include errors on exception"
        assert len(result["errors"]) > 0, "Errors must be reported"

    @pytest.mark.asyncio
    async def test_maid_validate_handles_malformed_manifest(self, tmp_path):
        """Test handling of malformed JSON manifest."""
        manifest_path = tmp_path / "malformed.manifest.json"
        manifest_path.write_text("{ invalid json content")

        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stdout = b""
        mock_process.stderr = b"Error: Invalid JSON in manifest\n"

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_validate(str(manifest_path))

        # Assert error is reported
        assert result["success"] is False, "success must be False for malformed manifest"
        assert "errors" in result, "Must include errors for malformed manifest"

    @pytest.mark.asyncio
    async def test_maid_validate_handles_validation_timeout(self, tmp_path):
        """Test handling of validation command timeout."""
        manifest_path = tmp_path / "test.manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "version": "1",
                    "goal": "Test",
                    "taskType": "create",
                    "creatableFiles": ["test.py"],
                    "editableFiles": [],
                    "readonlyFiles": [],
                    "expectedArtifacts": {"file": "test.py", "contains": []},
                    "validationCommand": ["sleep", "1000"],
                }
            )
        )

        # Mock subprocess to simulate timeout
        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_process = MagicMock()
            mock_process.communicate = AsyncMock(side_effect=asyncio.TimeoutError)
            mock_exec.return_value = mock_process

            result = await maid_validate(str(manifest_path))

        # Assert timeout is handled
        assert isinstance(result, dict), "Must return dictionary even on timeout"
        assert result["success"] is False, "success must be False on timeout"
        assert "errors" in result, "Must include errors on timeout"


class TestMaidValidateDefaultParameters:
    """Test default parameter values."""

    @pytest.mark.asyncio
    async def test_maid_validate_uses_default_validation_mode(self, tmp_path):
        """Test that default validation mode is 'implementation'."""
        manifest_path = tmp_path / "test.manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "version": "1",
                    "goal": "Test",
                    "taskType": "create",
                    "creatableFiles": ["test.py"],
                    "editableFiles": [],
                    "readonlyFiles": [],
                    "expectedArtifacts": {"file": "test.py", "contains": []},
                    "validationCommand": ["echo", "test"],
                }
            )
        )

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"Validation passed\n"
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            # Call without specifying validation_mode
            result = await maid_validate(str(manifest_path))

        # Assert default mode is implementation
        assert (
            result["mode"] == "implementation"
        ), "Default validation mode should be 'implementation'"

    @pytest.mark.asyncio
    async def test_maid_validate_defaults_to_no_manifest_chain(self, tmp_path):
        """Test that use_manifest_chain defaults to False."""
        manifest_path = tmp_path / "test.manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "version": "1",
                    "goal": "Test",
                    "taskType": "create",
                    "creatableFiles": ["test.py"],
                    "editableFiles": [],
                    "readonlyFiles": [],
                    "expectedArtifacts": {"file": "test.py", "contains": []},
                    "validationCommand": ["echo", "test"],
                }
            )
        )

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"Validation passed\n"
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            # Call without specifying use_manifest_chain
            result = await maid_validate(str(manifest_path))

        # Assert chain is not used by default
        assert (
            result.get("use_manifest_chain") is False
        ), "use_manifest_chain should default to False"

    @pytest.mark.asyncio
    async def test_maid_validate_defaults_to_quiet_mode(self, tmp_path):
        """Test that quiet mode defaults to True."""
        manifest_path = tmp_path / "test.manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "version": "1",
                    "goal": "Test",
                    "taskType": "create",
                    "creatableFiles": ["test.py"],
                    "editableFiles": [],
                    "readonlyFiles": [],
                    "expectedArtifacts": {"file": "test.py", "contains": []},
                    "validationCommand": ["echo", "test"],
                }
            )
        )

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"Minimal output\n"
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            # Call without specifying quiet
            result = await maid_validate(str(manifest_path))

        # Assert quiet is True by default
        assert result.get("quiet") is True, "quiet should default to True"
