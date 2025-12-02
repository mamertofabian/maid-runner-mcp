"""Behavioral tests for maid_files MCP tool (Task 023).

These tests verify the expected artifacts defined in the manifest:
- FileInfo: TypedDict for individual file tracking info
- FileTrackingResult: TypedDict for file tracking results
- maid_files(): Async function that provides file-level tracking status

Tests follow MAID behavioral testing pattern - they USE the artifacts
rather than just checking existence. We use mocking to avoid calling the real CLI.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestFileInfoTypedDict:
    """Tests for the FileInfo TypedDict."""

    def test_file_info_is_typed_dict(self):
        """Test that FileInfo is a TypedDict.

        The manifest specifies:
        - type: class
        - name: FileInfo
        - description: TypedDict for individual file tracking info
        """
        from maid_runner_mcp.tools.files import FileInfo

        # TypedDict classes have __annotations__
        assert hasattr(
            FileInfo, "__annotations__"
        ), "FileInfo should have __annotations__ (TypedDict requirement)"

    def test_file_info_has_required_fields(self):
        """Test that FileInfo has all required fields.

        Based on maid files --json output:
        - file (string)
        - status (string)
        - issues (list of strings)
        - manifests (list of strings)
        """
        from maid_runner_mcp.tools.files import FileInfo

        annotations = FileInfo.__annotations__

        required_fields = [
            "file",
            "status",
            "issues",
            "manifests",
        ]

        for field_name in required_fields:
            assert field_name in annotations, f"FileInfo should have '{field_name}' field"


class TestFileTrackingResultTypedDict:
    """Tests for the FileTrackingResult TypedDict."""

    def test_file_tracking_result_is_typed_dict(self):
        """Test that FileTrackingResult is a TypedDict.

        The manifest specifies:
        - type: class
        - name: FileTrackingResult
        - description: TypedDict for file tracking results
        """
        from maid_runner_mcp.tools.files import FileTrackingResult

        # TypedDict classes have __annotations__
        assert hasattr(
            FileTrackingResult, "__annotations__"
        ), "FileTrackingResult should have __annotations__ (TypedDict requirement)"

    def test_file_tracking_result_has_required_fields(self):
        """Test that FileTrackingResult has all required fields.

        Based on maid files --json output:
        - undeclared (list of FileInfo)
        - registered (list of FileInfo)
        - tracked (list of strings)
        """
        from maid_runner_mcp.tools.files import FileTrackingResult

        annotations = FileTrackingResult.__annotations__

        required_fields = [
            "undeclared",
            "registered",
            "tracked",
        ]

        for field_name in required_fields:
            assert field_name in annotations, f"FileTrackingResult should have '{field_name}' field"


class TestMaidFilesFunction:
    """Tests for the maid_files async function."""

    def test_maid_files_is_callable(self):
        """Test that maid_files exists and is callable.

        The manifest specifies:
        - type: function
        - name: maid_files
        """
        from maid_runner_mcp.tools.files import maid_files

        assert callable(maid_files), "maid_files should be callable"

    def test_maid_files_is_async(self):
        """Test that maid_files is an async function."""
        import asyncio
        from maid_runner_mcp.tools.files import maid_files

        assert asyncio.iscoroutinefunction(maid_files), "maid_files should be an async function"

    def test_maid_files_has_correct_signature(self):
        """Test that maid_files has the expected parameters.

        The manifest specifies:
        - manifest_dir: str (default: "manifests")
        - issues_only: bool (default: False)
        - status: str | None (default: None)
        """
        import inspect
        from maid_runner_mcp.tools.files import maid_files

        sig = inspect.signature(maid_files)
        params = sig.parameters

        # Check optional parameter with default
        assert "manifest_dir" in params, "maid_files should have 'manifest_dir' parameter"
        assert (
            params["manifest_dir"].default == "manifests"
        ), "manifest_dir should default to 'manifests'"

        # Check issues_only parameter
        assert "issues_only" in params, "maid_files should have 'issues_only' parameter"
        assert params["issues_only"].default is False, "issues_only should default to False"

        # Check status parameter
        assert "status" in params, "maid_files should have 'status' parameter"
        assert params["status"].default is None, "status should default to None"


@pytest.mark.asyncio
class TestMaidFilesBehavior:
    """Tests for maid_files behavior when called.

    Note: We use mocking here to avoid calling the real CLI and to test
    specific scenarios in isolation.
    """

    async def test_maid_files_returns_file_tracking_result(self):
        """Test that maid_files returns a FileTrackingResult-compatible dict."""
        from maid_runner_mcp.tools.files import maid_files

        # Mock subprocess to avoid real CLI execution
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"undeclared": [], "registered": [], "tracked": ["src/test.py"]}'
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            result = await maid_files()

        # Result should have all required fields
        assert "undeclared" in result, "Result should have 'undeclared' field"
        assert "registered" in result, "Result should have 'registered' field"
        assert "tracked" in result, "Result should have 'tracked' field"

    async def test_maid_files_returns_correct_types(self):
        """Test that maid_files returns correct field types."""
        from maid_runner_mcp.tools.files import maid_files

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"undeclared": [], "registered": [], "tracked": ["src/test.py"]}'
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            result = await maid_files()

        # Verify types match the output schema from maid files --json
        assert isinstance(result["undeclared"], list), "undeclared should be a list"
        assert isinstance(result["registered"], list), "registered should be a list"
        assert isinstance(result["tracked"], list), "tracked should be a list"

    async def test_maid_files_tracked_contains_strings(self):
        """Test that tracked files are strings (file paths)."""
        from maid_runner_mcp.tools.files import maid_files

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = (
            '{"undeclared": [], "registered": [], "tracked": ["src/a.py", "src/b.py"]}'
        )
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            result = await maid_files()

        # tracked should be a list of strings
        assert len(result["tracked"]) > 0, "tracked should have items"
        assert all(isinstance(f, str) for f in result["tracked"]), "tracked should contain strings"

    async def test_maid_files_registered_contains_file_info(self):
        """Test that registered files have FileInfo structure."""
        from maid_runner_mcp.tools.files import maid_files

        # Mock response with registered files
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """{
            "undeclared": [],
            "registered": [
                {"file": "src/new.py", "status": "registered", "issues": [], "manifests": ["task-001"]}
            ],
            "tracked": []
        }"""
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            result = await maid_files()

        # Each registered file should have FileInfo structure
        assert len(result["registered"]) > 0, "registered should have items"
        for file_info in result["registered"]:
            assert "file" in file_info, "FileInfo should have 'file' field"
            assert "status" in file_info, "FileInfo should have 'status' field"
            assert "issues" in file_info, "FileInfo should have 'issues' field"
            assert "manifests" in file_info, "FileInfo should have 'manifests' field"

    async def test_maid_files_undeclared_contains_file_info(self):
        """Test that undeclared files have FileInfo structure."""
        from maid_runner_mcp.tools.files import maid_files

        # Mock response with undeclared files
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """{
            "undeclared": [
                {"file": "src/untracked.py", "status": "undeclared", "issues": ["not in any manifest"], "manifests": []}
            ],
            "registered": [],
            "tracked": []
        }"""
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            result = await maid_files()

        # Each undeclared file should have FileInfo structure
        assert len(result["undeclared"]) > 0, "undeclared should have items"
        for file_info in result["undeclared"]:
            assert "file" in file_info, "FileInfo should have 'file' field"
            assert "status" in file_info, "FileInfo should have 'status' field"
            assert "issues" in file_info, "FileInfo should have 'issues' field"
            assert "manifests" in file_info, "FileInfo should have 'manifests' field"

    async def test_maid_files_with_issues_only_parameter(self):
        """Test that maid_files with issues_only parameter filters correctly."""
        from maid_runner_mcp.tools.files import maid_files

        # Mock response for issues_only mode
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """{
            "undeclared": [
                {"file": "src/issue.py", "status": "undeclared", "issues": ["not tracked"], "manifests": []}
            ],
            "registered": [],
            "tracked": []
        }"""
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            result = await maid_files(issues_only=True)

        # Result should still have all fields
        assert "undeclared" in result
        assert "registered" in result
        assert "tracked" in result

        # Verify the command was called with --issues-only flag
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert "--issues-only" in cmd, "Command should include --issues-only flag"

    async def test_maid_files_with_status_filter(self):
        """Test that maid_files with status filter works."""
        from maid_runner_mcp.tools.files import maid_files

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"undeclared": [], "registered": [], "tracked": ["src/test.py"]}'
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            result = await maid_files(status="tracked")

        # Result should still have all fields
        assert "undeclared" in result
        assert "registered" in result
        assert "tracked" in result

        # Verify the command was called with --status flag
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert "--status" in cmd, "Command should include --status flag"
        # Find the index of --status and check the next argument
        status_idx = cmd.index("--status")
        assert cmd[status_idx + 1] == "tracked", "Status value should be 'tracked'"

    async def test_maid_files_custom_manifest_dir(self):
        """Test that maid_files accepts custom manifest_dir."""
        from maid_runner_mcp.tools.files import maid_files

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"undeclared": [], "registered": [], "tracked": []}'
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            result = await maid_files(manifest_dir="custom_manifests")

        # Should work with explicit manifest_dir
        assert "undeclared" in result
        assert "registered" in result
        assert "tracked" in result

        # Verify the command was called with --manifest-dir flag
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert "--manifest-dir" in cmd, "Command should include --manifest-dir flag"
        # Find the index of --manifest-dir and check the next argument
        dir_idx = cmd.index("--manifest-dir")
        assert cmd[dir_idx + 1] == "custom_manifests", "Manifest dir should be 'custom_manifests'"

    async def test_maid_files_handles_cli_error(self):
        """Test that maid_files handles CLI errors gracefully."""
        from maid_runner_mcp.tools.files import maid_files

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error: manifest directory not found"

        with patch("subprocess.run", return_value=mock_result):
            result = await maid_files()

        # Should return empty result on error, not raise exception
        assert "undeclared" in result
        assert "registered" in result
        assert "tracked" in result
        # All lists should be empty on error
        assert isinstance(result["undeclared"], list)
        assert isinstance(result["registered"], list)
        assert isinstance(result["tracked"], list)

    async def test_maid_files_handles_invalid_json_response(self):
        """Test that maid_files handles invalid JSON gracefully."""
        from maid_runner_mcp.tools.files import maid_files

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Not valid JSON output"
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            result = await maid_files()

        # Should return empty result on parse error
        assert "undeclared" in result
        assert "registered" in result
        assert "tracked" in result
        assert isinstance(result["undeclared"], list)
        assert isinstance(result["registered"], list)
        assert isinstance(result["tracked"], list)

    async def test_maid_files_default_parameters(self):
        """Test that maid_files uses default parameters correctly."""
        from maid_runner_mcp.tools.files import maid_files

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"undeclared": [], "registered": [], "tracked": []}'
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            await maid_files()

        # Verify the command was called with default manifest_dir
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert "--manifest-dir" in cmd
        dir_idx = cmd.index("--manifest-dir")
        assert cmd[dir_idx + 1] == "manifests", "Default manifest_dir should be 'manifests'"

        # Should NOT include --issues-only by default
        assert "--issues-only" not in cmd, "Command should not include --issues-only by default"

        # Should NOT include --status by default
        assert "--status" not in cmd, "Command should not include --status by default"

    async def test_maid_files_uses_json_flag(self):
        """Test that maid_files uses --json flag for structured output."""
        from maid_runner_mcp.tools.files import maid_files

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"undeclared": [], "registered": [], "tracked": []}'
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            await maid_files()

        # Verify the command includes --json flag
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert "--json" in cmd, "Command should include --json flag for structured output"
