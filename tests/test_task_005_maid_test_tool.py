"""Behavioral tests for task-005: Implement maid_test MCP tool.

Tests verify that the maid_test function:
1. Wraps MAID Runner test command correctly
2. Handles async execution properly
3. Returns structured JSON responses
4. Runs all non-superseded manifests by default
5. Supports single manifest testing
6. Handles fail-fast mode
7. Respects timeout parameter
8. Processes errors appropriately
9. Parses test results correctly (total/passed/failed/failed_manifests)
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from maid_runner_mcp.tools.test import maid_test


class TestMaidTestBasicBehavior:
    """Test basic maid_test function behavior."""

    @pytest.mark.asyncio
    async def test_maid_test_runs_all_manifests_successfully(self, tmp_path):
        """Test that test command runs all non-superseded manifests successfully."""
        # Mock subprocess to simulate successful test run
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = (
            b"Running validation commands from 3 manifests...\n"
            b"PASSED task-001-test.manifest.json\n"
            b"PASSED task-002-test.manifest.json\n"
            b"PASSED task-003-test.manifest.json\n"
            b"\n"
            b"Summary: 3 manifests, 3 passed, 0 failed\n"
        )
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_test()

        # Assert result is a dictionary
        assert isinstance(result, dict), "maid_test must return a dictionary"

        # Assert success field is True
        assert "success" in result, "Result must contain 'success' field"
        assert result["success"] is True, f"Expected success=True, got {result.get('success')}"

        # Assert manifest counts
        assert "total_manifests" in result, "Result must contain 'total_manifests'"
        assert "passed" in result, "Result must contain 'passed'"
        assert "failed" in result, "Result must contain 'failed'"
        assert result["total_manifests"] == 3
        assert result["passed"] == 3
        assert result["failed"] == 0

    @pytest.mark.asyncio
    async def test_maid_test_with_failures_returns_failure_info(self):
        """Test that test command handles failures correctly."""
        # Mock subprocess to simulate test failures
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stdout = (
            b"Running validation commands from 4 manifests...\n"
            b"PASSED task-001-test.manifest.json\n"
            b"FAILED task-002-test.manifest.json\n"
            b"PASSED task-003-test.manifest.json\n"
            b"FAILED task-004-test.manifest.json\n"
            b"\n"
            b"Summary: 4 manifests, 2 passed, 2 failed\n"
            b"Failed manifests:\n"
            b"- task-002-test.manifest.json\n"
            b"- task-004-test.manifest.json\n"
        )
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_test()

        # Assert result indicates failure
        assert isinstance(result, dict), "maid_test must return a dictionary"
        assert "success" in result, "Result must contain 'success' field"
        assert result["success"] is False, f"Expected success=False, got {result.get('success')}"

        # Assert failure counts
        assert result["total_manifests"] == 4
        assert result["passed"] == 2
        assert result["failed"] == 2

        # Assert failed manifests list
        assert "failed_manifests" in result, "Result must contain 'failed_manifests'"
        assert isinstance(result["failed_manifests"], list), "failed_manifests must be a list"
        assert len(result["failed_manifests"]) == 2
        assert "task-002-test.manifest.json" in result["failed_manifests"]
        assert "task-004-test.manifest.json" in result["failed_manifests"]

    @pytest.mark.asyncio
    async def test_maid_test_with_no_manifests(self):
        """Test handling when no manifests are found."""
        # Mock subprocess to simulate no manifests scenario
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"No manifests found to test.\n"
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_test()

        # Assert result shows no manifests
        assert isinstance(result, dict), "maid_test must return a dictionary"
        assert result["success"] is True, "Should succeed with no manifests"
        assert result["total_manifests"] == 0
        assert result["passed"] == 0
        assert result["failed"] == 0


class TestMaidTestSingleManifest:
    """Test single manifest testing."""

    @pytest.mark.asyncio
    async def test_maid_test_with_single_manifest_success(self):
        """Test running validation for a single manifest."""
        # Mock subprocess to simulate single manifest test
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = (
            b"Running validation command for task-001-test.manifest.json...\n"
            b"PASSED task-001-test.manifest.json\n"
            b"\n"
            b"Summary: 1 manifest, 1 passed, 0 failed\n"
        )
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_test(manifest="task-001-test.manifest.json")

        # Assert single manifest was tested
        assert result["success"] is True
        assert result["total_manifests"] == 1
        assert result["passed"] == 1
        assert result["failed"] == 0

        # Assert command was called with --manifest flag
        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]
        assert "--manifest" in call_args or "-m" in call_args

    @pytest.mark.asyncio
    async def test_maid_test_with_single_manifest_failure(self):
        """Test running validation for a single failing manifest."""
        # Mock subprocess to simulate single manifest failure
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stdout = (
            b"Running validation command for task-002-test.manifest.json...\n"
            b"FAILED task-002-test.manifest.json\n"
            b"\n"
            b"Summary: 1 manifest, 0 passed, 1 failed\n"
            b"Failed manifests:\n"
            b"- task-002-test.manifest.json\n"
        )
        mock_process.stderr = b"Test command failed: pytest returned exit code 1\n"

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_test(manifest="task-002-test.manifest.json")

        # Assert failure is reported
        assert result["success"] is False
        assert result["total_manifests"] == 1
        assert result["passed"] == 0
        assert result["failed"] == 1
        assert "task-002-test.manifest.json" in result["failed_manifests"]


class TestMaidTestManifestDirectory:
    """Test custom manifest directory."""

    @pytest.mark.asyncio
    async def test_maid_test_with_custom_manifest_dir(self):
        """Test using a custom manifest directory."""
        custom_dir = "custom_manifests"

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = (
            b"Running validation commands from 2 manifests...\n"
            b"PASSED task-001-test.manifest.json\n"
            b"PASSED task-002-test.manifest.json\n"
            b"\n"
            b"Summary: 2 manifests, 2 passed, 0 failed\n"
        )
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_test(manifest_dir=custom_dir)

        # Assert custom directory was used
        assert result["success"] is True
        assert "manifest_dir" in result
        assert result["manifest_dir"] == custom_dir

        # Assert command included manifest-dir flag
        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]
        assert "--manifest-dir" in call_args
        dir_index = list(call_args).index("--manifest-dir")
        assert call_args[dir_index + 1] == custom_dir


class TestMaidTestFailFast:
    """Test fail-fast mode."""

    @pytest.mark.asyncio
    async def test_maid_test_with_fail_fast_enabled(self):
        """Test that fail-fast mode stops on first failure."""
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stdout = (
            b"Running validation commands from 3 manifests...\n"
            b"PASSED task-001-test.manifest.json\n"
            b"FAILED task-002-test.manifest.json\n"
            b"Stopping due to --fail-fast\n"
            b"\n"
            b"Summary: 2 manifests tested, 1 passed, 1 failed\n"
            b"Failed manifests:\n"
            b"- task-002-test.manifest.json\n"
        )
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_test(fail_fast=True)

        # Assert fail-fast stopped early
        assert result["success"] is False
        assert result["total_manifests"] == 2  # Only 2 tested before stopping
        assert result["failed"] == 1

        # Assert command included fail-fast flag
        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]
        assert "--fail-fast" in call_args

    @pytest.mark.asyncio
    async def test_maid_test_without_fail_fast(self):
        """Test that all manifests run when fail-fast is disabled."""
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stdout = (
            b"Running validation commands from 3 manifests...\n"
            b"PASSED task-001-test.manifest.json\n"
            b"FAILED task-002-test.manifest.json\n"
            b"PASSED task-003-test.manifest.json\n"
            b"\n"
            b"Summary: 3 manifests, 2 passed, 1 failed\n"
            b"Failed manifests:\n"
            b"- task-002-test.manifest.json\n"
        )
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_test(fail_fast=False)

        # Assert all manifests were tested
        assert result["total_manifests"] == 3
        assert result["passed"] == 2
        assert result["failed"] == 1

        # Assert command did NOT include fail-fast flag
        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]
        assert "--fail-fast" not in call_args


class TestMaidTestTimeout:
    """Test timeout parameter."""

    @pytest.mark.asyncio
    async def test_maid_test_with_custom_timeout(self):
        """Test using a custom timeout value."""
        custom_timeout = 600

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"Summary: 1 manifest, 1 passed, 0 failed\n"
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_test(timeout=custom_timeout)

        # Assert timeout was used
        assert "timeout" in result
        assert result["timeout"] == custom_timeout

        # Assert command included timeout flag
        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]
        assert "--timeout" in call_args
        timeout_index = list(call_args).index("--timeout")
        assert call_args[timeout_index + 1] == str(custom_timeout)

    @pytest.mark.asyncio
    async def test_maid_test_handles_command_timeout(self):
        """Test handling when the test command times out."""
        # Mock subprocess to simulate timeout
        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_process = MagicMock()
            mock_process.communicate = AsyncMock(side_effect=asyncio.TimeoutError)
            mock_exec.return_value = mock_process

            result = await maid_test(timeout=1)

        # Assert timeout is handled gracefully
        assert isinstance(result, dict), "Must return dictionary even on timeout"
        assert result["success"] is False, "success must be False on timeout"
        assert "errors" in result, "Must include errors on timeout"


class TestMaidTestOutputStructure:
    """Test structured output format."""

    @pytest.mark.asyncio
    async def test_maid_test_output_contains_required_fields(self):
        """Test that output contains all required fields."""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"Summary: 2 manifests, 2 passed, 0 failed\n"
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_test()

        # Assert all required fields are present
        required_fields = ["success", "total_manifests", "passed", "failed"]
        for field in required_fields:
            assert field in result, f"Result must contain '{field}' field"

        # Assert field types
        assert isinstance(result["success"], bool), "success must be a boolean"
        assert isinstance(result["total_manifests"], int), "total_manifests must be an integer"
        assert isinstance(result["passed"], int), "passed must be an integer"
        assert isinstance(result["failed"], int), "failed must be an integer"

    @pytest.mark.asyncio
    async def test_maid_test_output_includes_failed_manifests_list(self):
        """Test that failed_manifests is included when there are failures."""
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stdout = (
            b"FAILED task-001-test.manifest.json\n"
            b"Summary: 1 manifest, 0 passed, 1 failed\n"
            b"Failed manifests:\n"
            b"- task-001-test.manifest.json\n"
        )
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_test()

        # Assert failed_manifests is present
        assert "failed_manifests" in result, "Result must contain 'failed_manifests' on failure"
        assert isinstance(result["failed_manifests"], list), "failed_manifests must be a list"
        assert len(result["failed_manifests"]) > 0

    @pytest.mark.asyncio
    async def test_maid_test_output_empty_failed_list_on_success(self):
        """Test that failed_manifests is empty when all tests pass."""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"Summary: 2 manifests, 2 passed, 0 failed\n"
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_test()

        # Assert failed_manifests is empty
        assert "failed_manifests" in result
        assert result["failed_manifests"] == []


class TestMaidTestErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.asyncio
    async def test_maid_test_handles_subprocess_errors(self):
        """Test handling of subprocess execution errors."""
        # Mock subprocess to raise an exception
        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.side_effect = OSError("Command not found")

            result = await maid_test()

        # Assert error is handled gracefully
        assert isinstance(result, dict), "Must return dictionary even on error"
        assert result["success"] is False, "success must be False on error"
        assert "errors" in result, "Must include errors on exception"
        assert len(result["errors"]) > 0, "Errors must be reported"

    @pytest.mark.asyncio
    async def test_maid_test_handles_invalid_manifest_dir(self):
        """Test handling of invalid manifest directory."""
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stdout = b""
        mock_process.stderr = b"Error: Manifest directory not found: /invalid/path\n"

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_test(manifest_dir="/invalid/path")

        # Assert error is reported
        assert result["success"] is False
        assert "errors" in result
        assert len(result["errors"]) > 0

    @pytest.mark.asyncio
    async def test_maid_test_handles_nonexistent_manifest(self):
        """Test handling when specified manifest doesn't exist."""
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stdout = b""
        mock_process.stderr = b"Error: Manifest file not found: nonexistent.manifest.json\n"

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_test(manifest="nonexistent.manifest.json")

        # Assert error is reported
        assert result["success"] is False
        assert "errors" in result


class TestMaidTestDefaultParameters:
    """Test default parameter values."""

    @pytest.mark.asyncio
    async def test_maid_test_uses_default_manifest_dir(self):
        """Test that default manifest directory is 'manifests'."""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"Summary: 1 manifest, 1 passed, 0 failed\n"
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_test()

        # Assert default manifest_dir is used
        assert result.get("manifest_dir") == "manifests"

    @pytest.mark.asyncio
    async def test_maid_test_defaults_to_no_fail_fast(self):
        """Test that fail_fast defaults to False."""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"Summary: 1 manifest, 1 passed, 0 failed\n"
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            _result = await maid_test()

        # Assert fail-fast is not used by default
        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]
        assert "--fail-fast" not in call_args

    @pytest.mark.asyncio
    async def test_maid_test_uses_default_timeout(self):
        """Test that timeout defaults to 300 seconds."""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"Summary: 1 manifest, 1 passed, 0 failed\n"
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_test()

        # Assert default timeout is 300
        assert result.get("timeout") == 300
