"""Behavioral tests for task-004: Implement maid_snapshot MCP tool.

Tests verify that the maid_snapshot function:
1. Wraps MAID Runner snapshot command correctly
2. Handles async execution properly
3. Returns structured JSON responses with manifest and test paths
4. Supports all snapshot parameters (output_dir, force, skip_test_stub)
5. Processes errors appropriately (missing files, invalid paths)
6. Parses snapshot output to extract manifest and test stub paths
7. Handles superseded manifests correctly
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from maid_runner_mcp.tools.snapshot import maid_snapshot


class TestMaidSnapshotBasicBehavior:
    """Test basic maid_snapshot function behavior."""

    @pytest.mark.asyncio
    async def test_maid_snapshot_with_valid_file_returns_success(self, tmp_path):
        """Test that snapshot generation succeeds with a valid Python file."""
        # Create a sample Python file
        test_file = tmp_path / "sample.py"
        test_file.write_text(
            '''def hello():
    """A test function."""
    return "Hello"
'''
        )

        # Mock subprocess to simulate successful snapshot generation
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = (
            b"Snapshot manifest generated successfully: task-001-snapshot-sample.manifest.json\n"
        )
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_snapshot(str(test_file))

        # Assert result is a dictionary
        assert isinstance(result, dict), "maid_snapshot must return a dictionary"

        # Assert success field is True
        assert "success" in result, "Result must contain 'success' field"
        assert result["success"] is True, f"Expected success=True, got {result.get('success')}"

        # Assert manifest_path is included
        assert "manifest_path" in result, "Result must contain 'manifest_path' field"
        assert isinstance(result["manifest_path"], str), "manifest_path must be a string"
        assert "task-001-snapshot-sample.manifest.json" in result["manifest_path"]

    @pytest.mark.asyncio
    async def test_maid_snapshot_with_test_stub_returns_test_path(self, tmp_path):
        """Test that snapshot generation returns test stub path when generated."""
        test_file = tmp_path / "module.py"
        test_file.write_text("def func(): pass")

        # Mock subprocess to simulate successful snapshot with test stub
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = (
            b"Test stub generated: tests/test_task_001_snapshot_module.py\n"
            b"Snapshot manifest generated successfully: task-001-snapshot-module.manifest.json\n"
        )
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_snapshot(str(test_file))

        # Assert test_stub_path is included
        assert "test_stub_path" in result, "Result must contain 'test_stub_path' field"
        assert result["test_stub_path"] is not None, "test_stub_path should not be None"
        assert isinstance(result["test_stub_path"], str), "test_stub_path must be a string"
        assert "test_task_001_snapshot_module.py" in result["test_stub_path"]

    @pytest.mark.asyncio
    async def test_maid_snapshot_without_test_stub_returns_none(self, tmp_path):
        """Test that snapshot without test stub returns None for test_stub_path."""
        test_file = tmp_path / "module.py"
        test_file.write_text("def func(): pass")

        # Mock subprocess to simulate snapshot without test stub
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = (
            b"Snapshot manifest generated successfully: task-001-snapshot-module.manifest.json\n"
        )
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_snapshot(str(test_file), skip_test_stub=True)

        # Assert test_stub_path is None
        assert "test_stub_path" in result, "Result must contain 'test_stub_path' field"
        assert result["test_stub_path"] is None, "test_stub_path should be None when skipped"

    @pytest.mark.asyncio
    async def test_maid_snapshot_with_nonexistent_file_returns_failure(self):
        """Test that snapshot generation fails with nonexistent file."""
        nonexistent_file = "/nonexistent/path/file.py"

        # Mock subprocess to simulate file not found error
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stdout = b""
        mock_process.stderr = b"Error: File not found: /nonexistent/path/file.py\n"

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_snapshot(nonexistent_file)

        # Assert result indicates failure
        assert isinstance(result, dict), "maid_snapshot must return a dictionary"
        assert "success" in result, "Result must contain 'success' field"
        assert result["success"] is False, f"Expected success=False, got {result.get('success')}"

        # Assert errors are included
        assert "errors" in result, "Result must contain 'errors' field for failures"
        assert isinstance(result["errors"], list), "Errors must be a list"
        assert len(result["errors"]) > 0, "Errors list must not be empty for failed snapshot"

        # Assert error message mentions file not found
        errors_str = " ".join(str(e) for e in result["errors"])
        assert "not found" in errors_str.lower() or "error" in errors_str.lower()


class TestMaidSnapshotParameters:
    """Test snapshot parameter handling."""

    @pytest.mark.asyncio
    async def test_maid_snapshot_with_custom_output_dir(self, tmp_path):
        """Test snapshot generation with custom output directory."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")
        custom_output = str(tmp_path / "custom_manifests")

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = (
            b"Snapshot manifest generated successfully: task-001-snapshot-test.manifest.json\n"
        )
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_snapshot(str(test_file), output_dir=custom_output)

        # Assert success
        assert result["success"] is True, "Snapshot should succeed"

        # Assert command was called with correct output_dir
        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]
        assert "--output-dir" in call_args, "Must pass --output-dir flag"
        dir_index = list(call_args).index("--output-dir")
        assert call_args[dir_index + 1] == custom_output

    @pytest.mark.asyncio
    async def test_maid_snapshot_with_force_flag(self, tmp_path):
        """Test snapshot generation with force flag to overwrite existing."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = (
            b"Snapshot manifest generated successfully: task-001-snapshot-test.manifest.json\n"
        )
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_snapshot(str(test_file), force=True)

        # Assert success
        assert result["success"] is True, "Snapshot should succeed with force"

        # Assert command was called with --force flag
        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]
        assert "--force" in call_args, "Must pass --force flag when force=True"

    @pytest.mark.asyncio
    async def test_maid_snapshot_without_force_flag(self, tmp_path):
        """Test snapshot generation without force flag (default)."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = (
            b"Snapshot manifest generated successfully: task-001-snapshot-test.manifest.json\n"
        )
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_snapshot(str(test_file), force=False)

        # Assert success
        assert result["success"] is True

        # Assert command was NOT called with --force flag
        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]
        assert "--force" not in call_args, "Should not pass --force when force=False"

    @pytest.mark.asyncio
    async def test_maid_snapshot_with_skip_test_stub(self, tmp_path):
        """Test snapshot generation with skip_test_stub enabled."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = (
            b"Snapshot manifest generated successfully: task-001-snapshot-test.manifest.json\n"
        )
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_snapshot(str(test_file), skip_test_stub=True)

        # Assert success
        assert result["success"] is True

        # Assert command was called with --skip-test-stub flag
        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]
        assert "--skip-test-stub" in call_args, "Must pass --skip-test-stub flag"

        # Assert no test stub path in result
        assert result.get("test_stub_path") is None, "Should not have test_stub_path when skipped"

    @pytest.mark.asyncio
    async def test_maid_snapshot_without_skip_test_stub(self, tmp_path):
        """Test snapshot generation with test stub enabled (default)."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = (
            b"Test stub generated: tests/test_task_001_snapshot_test.py\n"
            b"Snapshot manifest generated successfully: task-001-snapshot-test.manifest.json\n"
        )
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_snapshot(str(test_file), skip_test_stub=False)

        # Assert success
        assert result["success"] is True

        # Assert command was NOT called with --skip-test-stub flag
        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]
        assert "--skip-test-stub" not in call_args, "Should not pass --skip-test-stub when False"

        # Assert test stub path is present
        assert result.get("test_stub_path") is not None, "Should have test_stub_path"


class TestMaidSnapshotSupersededManifests:
    """Test superseded manifest handling."""

    @pytest.mark.asyncio
    async def test_maid_snapshot_returns_empty_superseded_list_for_new_file(self, tmp_path):
        """Test that snapshot for new file returns empty superseded list."""
        test_file = tmp_path / "new_module.py"
        test_file.write_text("def new_func(): pass")

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"Snapshot manifest generated successfully: task-001-snapshot-new-module.manifest.json\n"
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_snapshot(str(test_file))

        # Assert superseded_manifests is present and empty
        assert "superseded_manifests" in result, "Result must contain 'superseded_manifests' field"
        assert isinstance(
            result["superseded_manifests"], list
        ), "superseded_manifests must be a list"
        assert (
            len(result["superseded_manifests"]) == 0
        ), "New file should have empty superseded list"

    @pytest.mark.asyncio
    async def test_maid_snapshot_returns_superseded_manifests_for_existing_file(self, tmp_path):
        """Test that snapshot for existing tracked file returns superseded manifests."""
        test_file = tmp_path / "existing.py"
        test_file.write_text("def func(): pass")

        # Simulate output with superseded manifest information
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = (
            b"Superseding previous manifests: task-001-create-existing.manifest.json, task-005-edit-existing.manifest.json\n"
            b"Snapshot manifest generated successfully: task-010-snapshot-existing.manifest.json\n"
        )
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_snapshot(str(test_file))

        # Assert superseded_manifests contains the previous manifests
        assert "superseded_manifests" in result, "Result must contain 'superseded_manifests'"
        assert isinstance(
            result["superseded_manifests"], list
        ), "superseded_manifests must be a list"
        assert len(result["superseded_manifests"]) > 0, "Should have superseded manifests"

        # Assert the superseded manifests are correctly parsed
        superseded = result["superseded_manifests"]
        assert "task-001-create-existing.manifest.json" in superseded
        assert "task-005-edit-existing.manifest.json" in superseded


class TestMaidSnapshotOutputStructure:
    """Test structured output format."""

    @pytest.mark.asyncio
    async def test_maid_snapshot_output_contains_required_fields(self, tmp_path):
        """Test that output contains all required fields."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = (
            b"Snapshot manifest generated successfully: task-001-snapshot-test.manifest.json\n"
        )
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_snapshot(str(test_file))

        # Assert all required fields are present
        required_fields = [
            "success",
            "manifest_path",
            "test_stub_path",
            "superseded_manifests",
            "errors",
        ]
        for field in required_fields:
            assert field in result, f"Result must contain '{field}' field"

        # Assert field types for successful snapshot
        assert isinstance(result["success"], bool), "success must be a boolean"
        assert isinstance(result["manifest_path"], str), "manifest_path must be a string"
        assert result["test_stub_path"] is None or isinstance(
            result["test_stub_path"], str
        ), "test_stub_path must be str or None"
        assert isinstance(
            result["superseded_manifests"], list
        ), "superseded_manifests must be a list"
        assert isinstance(result["errors"], list), "errors must be a list"

    @pytest.mark.asyncio
    async def test_maid_snapshot_success_has_empty_errors_list(self, tmp_path):
        """Test that successful snapshot has empty errors list."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = (
            b"Snapshot manifest generated successfully: task-001-snapshot-test.manifest.json\n"
        )
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_snapshot(str(test_file))

        # Assert errors list is empty on success
        assert result["success"] is True
        assert len(result["errors"]) == 0, "Successful snapshot should have empty errors list"

    @pytest.mark.asyncio
    async def test_maid_snapshot_failure_has_populated_errors_list(self, tmp_path):
        """Test that failed snapshot has populated errors list."""
        test_file = tmp_path / "invalid.txt"  # Invalid file type
        test_file.write_text("not python code")

        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stdout = b""
        mock_process.stderr = b"Error: Unsupported file type: .txt\nOnly .py, .ts, .tsx, .js, .jsx files are supported\n"

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_snapshot(str(test_file))

        # Assert errors are populated
        assert result["success"] is False
        assert len(result["errors"]) > 0, "Failed snapshot must have errors"
        assert any(
            "unsupported" in str(e).lower() or "error" in str(e).lower() for e in result["errors"]
        )


class TestMaidSnapshotErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.asyncio
    async def test_maid_snapshot_handles_subprocess_errors(self, tmp_path):
        """Test handling of subprocess execution errors."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")

        # Mock subprocess to raise an exception
        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.side_effect = OSError("Command not found")

            result = await maid_snapshot(str(test_file))

        # Assert error is handled gracefully
        assert isinstance(result, dict), "Must return dictionary even on error"
        assert result["success"] is False, "success must be False on error"
        assert "errors" in result, "Must include errors on exception"
        assert len(result["errors"]) > 0, "Errors must be reported"
        assert any(
            "command" in str(e).lower() or "error" in str(e).lower() for e in result["errors"]
        )

    @pytest.mark.asyncio
    async def test_maid_snapshot_handles_invalid_python_file(self, tmp_path):
        """Test handling of invalid Python file (syntax errors)."""
        test_file = tmp_path / "invalid.py"
        test_file.write_text("def invalid( syntax error")

        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stdout = b""
        mock_process.stderr = (
            b"Error: Failed to parse Python file: invalid.py\nSyntaxError: invalid syntax\n"
        )

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_snapshot(str(test_file))

        # Assert error is reported
        assert result["success"] is False, "success must be False for invalid Python"
        assert "errors" in result, "Must include errors for invalid file"
        assert len(result["errors"]) > 0
        assert any(
            "syntax" in str(e).lower() or "parse" in str(e).lower() for e in result["errors"]
        )

    @pytest.mark.asyncio
    async def test_maid_snapshot_handles_permission_denied(self, tmp_path):
        """Test handling of permission denied errors."""
        test_file = "/root/restricted.py"  # Typically restricted path

        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stdout = b""
        mock_process.stderr = b"Error: Permission denied: /root/restricted.py\n"

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_snapshot(test_file)

        # Assert permission error is reported
        assert result["success"] is False
        assert len(result["errors"]) > 0
        assert any(
            "permission" in str(e).lower() or "denied" in str(e).lower() for e in result["errors"]
        )

    @pytest.mark.asyncio
    async def test_maid_snapshot_handles_timeout(self, tmp_path):
        """Test handling of snapshot command timeout."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")

        # Mock subprocess to simulate timeout
        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_process = MagicMock()
            mock_process.communicate = AsyncMock(side_effect=asyncio.TimeoutError)
            mock_exec.return_value = mock_process

            result = await maid_snapshot(str(test_file))

        # Assert timeout is handled
        assert isinstance(result, dict), "Must return dictionary even on timeout"
        assert result["success"] is False, "success must be False on timeout"
        assert "errors" in result, "Must include errors on timeout"
        assert any("timeout" in str(e).lower() for e in result["errors"])


class TestMaidSnapshotDefaultParameters:
    """Test default parameter values."""

    @pytest.mark.asyncio
    async def test_maid_snapshot_uses_default_output_dir(self, tmp_path):
        """Test that default output_dir is 'manifests'."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = (
            b"Snapshot manifest generated successfully: task-001-snapshot-test.manifest.json\n"
        )
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            # Call without specifying output_dir
            await maid_snapshot(str(test_file))

        # Assert command was called with default output_dir
        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]
        assert "--output-dir" in call_args
        dir_index = list(call_args).index("--output-dir")
        assert call_args[dir_index + 1] == "manifests", "Default output_dir should be 'manifests'"

    @pytest.mark.asyncio
    async def test_maid_snapshot_defaults_to_no_force(self, tmp_path):
        """Test that force defaults to False."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = (
            b"Snapshot manifest generated successfully: task-001-snapshot-test.manifest.json\n"
        )
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            # Call without specifying force
            await maid_snapshot(str(test_file))

        # Assert --force is not in command
        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]
        assert "--force" not in call_args, "force should default to False (no flag)"

    @pytest.mark.asyncio
    async def test_maid_snapshot_defaults_to_generate_test_stub(self, tmp_path):
        """Test that skip_test_stub defaults to False (generates test stub)."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = (
            b"Test stub generated: tests/test_task_001_snapshot_test.py\n"
            b"Snapshot manifest generated successfully: task-001-snapshot-test.manifest.json\n"
        )
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            # Call without specifying skip_test_stub
            result = await maid_snapshot(str(test_file))

        # Assert --skip-test-stub is not in command
        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]
        assert (
            "--skip-test-stub" not in call_args
        ), "skip_test_stub should default to False (no flag)"

        # Assert test stub was generated
        assert result.get("test_stub_path") is not None, "Should generate test stub by default"


class TestMaidSnapshotCommandConstruction:
    """Test that the command is constructed correctly with all parameters."""

    @pytest.mark.asyncio
    async def test_maid_snapshot_constructs_full_command_with_all_parameters(self, tmp_path):
        """Test command construction with all parameters specified."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")
        custom_output = str(tmp_path / "custom")

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = (
            b"Snapshot manifest generated successfully: task-001-snapshot-test.manifest.json\n"
        )
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            await maid_snapshot(
                str(test_file), output_dir=custom_output, force=True, skip_test_stub=True
            )

        # Assert command includes all parameters
        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]

        # Check base command
        assert call_args[0] == "maid", "First arg should be 'maid'"
        assert call_args[1] == "snapshot", "Second arg should be 'snapshot'"
        assert str(test_file) in call_args, "File path should be in command"

        # Check flags
        assert "--output-dir" in call_args
        assert custom_output in call_args
        assert "--force" in call_args
        assert "--skip-test-stub" in call_args

    @pytest.mark.asyncio
    async def test_maid_snapshot_constructs_minimal_command_with_defaults(self, tmp_path):
        """Test command construction with default parameters."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = (
            b"Snapshot manifest generated successfully: task-001-snapshot-test.manifest.json\n"
        )
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            await maid_snapshot(str(test_file))

        # Assert command has minimal structure
        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]

        # Check base command
        assert call_args[0] == "maid"
        assert call_args[1] == "snapshot"
        assert str(test_file) in call_args

        # Check default output_dir is present
        assert "--output-dir" in call_args
        assert "manifests" in call_args

        # Check optional flags are NOT present
        assert "--force" not in call_args
        assert "--skip-test-stub" not in call_args
