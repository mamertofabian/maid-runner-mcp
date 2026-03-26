"""Behavioral tests for maid_files MCP tool (Task 023).

These tests verify the expected artifacts defined in the manifest:
- FileInfo: TypedDict for individual file tracking info
- FileTrackingResult: TypedDict for file tracking results
- maid_files(): Async function that provides file-level tracking status

Tests follow MAID behavioral testing pattern - they USE the artifacts
rather than just checking existence. We use mocking to avoid calling the real library.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock


def _create_mock_context():
    """Helper to create a mock MCP context for testing."""
    mock_ctx = MagicMock()
    mock_session = MagicMock()
    mock_session.list_roots = AsyncMock(
        return_value=MagicMock(roots=[MagicMock(uri="file:///tmp/test")])
    )
    mock_ctx.session = mock_session
    return mock_ctx


def _mock_entry(data):
    """Create a mock FileTrackingEntry from a dict or string."""
    entry = MagicMock()
    if isinstance(data, str):
        entry.path = data
        entry.status = "tracked"
        entry.issues = ()
        entry.manifests = ()
    else:
        entry.path = data.get("file", "")
        entry.status = data.get("status", "unknown")
        entry.issues = tuple(data.get("issues", []))
        entry.manifests = tuple(data.get("manifests", []))
    return entry


def _create_mock_report(undeclared=None, registered=None, tracked=None):
    """Helper to create a mock FileTrackingReport."""
    report = MagicMock()
    report.undeclared = [_mock_entry(e) for e in (undeclared or [])]
    report.registered = [_mock_entry(e) for e in (registered or [])]
    report.tracked = [_mock_entry(t) for t in (tracked or [])]
    return report


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

    Note: We use mocking here to avoid calling the real library and to test
    specific scenarios in isolation.
    """

    async def test_maid_files_returns_file_tracking_result(self):
        """Test that maid_files returns a FileTrackingResult-compatible dict."""
        from maid_runner_mcp.tools.files import maid_files

        mock_report = _create_mock_report(tracked=["src/test.py"])
        mock_engine = MagicMock()
        mock_engine.run_file_tracking.return_value = mock_report
        mock_chain = MagicMock()

        mock_ctx = _create_mock_context()

        with (
            patch("maid_runner_mcp.tools.files.ManifestChain", return_value=mock_chain),
            patch("maid_runner_mcp.tools.files.ValidationEngine", return_value=mock_engine),
            patch(
                "maid_runner_mcp.tools.files.get_working_directory",
                new_callable=AsyncMock,
                return_value="/tmp/test",
            ),
        ):
            result = await maid_files(ctx=mock_ctx)

        # Result should have all required fields
        assert "undeclared" in result, "Result should have 'undeclared' field"
        assert "registered" in result, "Result should have 'registered' field"
        assert "tracked" in result, "Result should have 'tracked' field"

    async def test_maid_files_returns_correct_types(self):
        """Test that maid_files returns correct field types."""
        from maid_runner_mcp.tools.files import maid_files

        mock_report = _create_mock_report(tracked=["src/test.py"])
        mock_engine = MagicMock()
        mock_engine.run_file_tracking.return_value = mock_report
        mock_chain = MagicMock()

        mock_ctx = _create_mock_context()

        with (
            patch("maid_runner_mcp.tools.files.ManifestChain", return_value=mock_chain),
            patch("maid_runner_mcp.tools.files.ValidationEngine", return_value=mock_engine),
            patch(
                "maid_runner_mcp.tools.files.get_working_directory",
                new_callable=AsyncMock,
                return_value="/tmp/test",
            ),
        ):
            result = await maid_files(ctx=mock_ctx)

        # Verify types match the output schema
        assert isinstance(result["undeclared"], list), "undeclared should be a list"
        assert isinstance(result["registered"], list), "registered should be a list"
        assert isinstance(result["tracked"], list), "tracked should be a list"

    async def test_maid_files_tracked_contains_strings(self):
        """Test that tracked files are strings (file paths)."""
        from maid_runner_mcp.tools.files import maid_files

        mock_report = _create_mock_report(tracked=["src/a.py", "src/b.py"])
        mock_engine = MagicMock()
        mock_engine.run_file_tracking.return_value = mock_report
        mock_chain = MagicMock()

        mock_ctx = _create_mock_context()

        with (
            patch("maid_runner_mcp.tools.files.ManifestChain", return_value=mock_chain),
            patch("maid_runner_mcp.tools.files.ValidationEngine", return_value=mock_engine),
            patch(
                "maid_runner_mcp.tools.files.get_working_directory",
                new_callable=AsyncMock,
                return_value="/tmp/test",
            ),
        ):
            result = await maid_files(ctx=mock_ctx)

        # tracked should be a list of strings
        assert len(result["tracked"]) > 0, "tracked should have items"
        assert all(isinstance(f, str) for f in result["tracked"]), "tracked should contain strings"

    async def test_maid_files_registered_contains_file_info(self):
        """Test that registered files have FileInfo structure."""
        from maid_runner_mcp.tools.files import maid_files

        mock_report = _create_mock_report(
            registered=[
                {
                    "file": "src/new.py",
                    "status": "registered",
                    "issues": [],
                    "manifests": ["task-001"],
                }
            ]
        )
        mock_engine = MagicMock()
        mock_engine.run_file_tracking.return_value = mock_report
        mock_chain = MagicMock()

        mock_ctx = _create_mock_context()

        with (
            patch("maid_runner_mcp.tools.files.ManifestChain", return_value=mock_chain),
            patch("maid_runner_mcp.tools.files.ValidationEngine", return_value=mock_engine),
            patch(
                "maid_runner_mcp.tools.files.get_working_directory",
                new_callable=AsyncMock,
                return_value="/tmp/test",
            ),
        ):
            result = await maid_files(ctx=mock_ctx)

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

        mock_report = _create_mock_report(
            undeclared=[
                {
                    "file": "src/untracked.py",
                    "status": "undeclared",
                    "issues": ["not in any manifest"],
                    "manifests": [],
                }
            ]
        )
        mock_engine = MagicMock()
        mock_engine.run_file_tracking.return_value = mock_report
        mock_chain = MagicMock()

        mock_ctx = _create_mock_context()

        with (
            patch("maid_runner_mcp.tools.files.ManifestChain", return_value=mock_chain),
            patch("maid_runner_mcp.tools.files.ValidationEngine", return_value=mock_engine),
            patch(
                "maid_runner_mcp.tools.files.get_working_directory",
                new_callable=AsyncMock,
                return_value="/tmp/test",
            ),
        ):
            result = await maid_files(ctx=mock_ctx)

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

        mock_report = _create_mock_report(
            undeclared=[
                {
                    "file": "src/issue.py",
                    "status": "undeclared",
                    "issues": ["not tracked"],
                    "manifests": [],
                }
            ]
        )
        mock_engine = MagicMock()
        mock_engine.run_file_tracking.return_value = mock_report
        mock_chain = MagicMock()

        mock_ctx = _create_mock_context()

        with (
            patch("maid_runner_mcp.tools.files.ManifestChain", return_value=mock_chain),
            patch("maid_runner_mcp.tools.files.ValidationEngine", return_value=mock_engine),
            patch(
                "maid_runner_mcp.tools.files.get_working_directory",
                new_callable=AsyncMock,
                return_value="/tmp/test",
            ),
        ):
            result = await maid_files(ctx=mock_ctx, issues_only=True)

        # Result should still have all fields
        assert "undeclared" in result
        assert "registered" in result
        assert "tracked" in result

    async def test_maid_files_with_status_filter(self):
        """Test that maid_files with status filter works."""
        from maid_runner_mcp.tools.files import maid_files

        mock_report = _create_mock_report(
            undeclared=[
                {"file": "src/a.py", "status": "undeclared", "issues": [], "manifests": []}
            ],
            tracked=["src/test.py"],
        )
        mock_engine = MagicMock()
        mock_engine.run_file_tracking.return_value = mock_report
        mock_chain = MagicMock()

        mock_ctx = _create_mock_context()

        with (
            patch("maid_runner_mcp.tools.files.ManifestChain", return_value=mock_chain),
            patch("maid_runner_mcp.tools.files.ValidationEngine", return_value=mock_engine),
            patch(
                "maid_runner_mcp.tools.files.get_working_directory",
                new_callable=AsyncMock,
                return_value="/tmp/test",
            ),
        ):
            result = await maid_files(ctx=mock_ctx, status="tracked")

        # Result should still have all fields
        assert "undeclared" in result
        assert "registered" in result
        assert "tracked" in result

        # With status="tracked", only tracked should have data
        assert result["undeclared"] == [], "undeclared should be empty when filtering by tracked"
        assert result["tracked"] == ["src/test.py"], "tracked should be preserved"

    async def test_maid_files_custom_manifest_dir(self):
        """Test that maid_files accepts custom manifest_dir."""
        from maid_runner_mcp.tools.files import maid_files

        mock_report = _create_mock_report()
        mock_engine = MagicMock()
        mock_engine.run_file_tracking.return_value = mock_report
        mock_chain = MagicMock()

        mock_ctx = _create_mock_context()

        with (
            patch(
                "maid_runner_mcp.tools.files.ManifestChain", return_value=mock_chain
            ) as mock_chain_cls,
            patch("maid_runner_mcp.tools.files.ValidationEngine", return_value=mock_engine),
            patch(
                "maid_runner_mcp.tools.files.get_working_directory",
                new_callable=AsyncMock,
                return_value="/tmp/test",
            ),
        ):
            result = await maid_files(ctx=mock_ctx, manifest_dir="custom_manifests")

        # Should work with explicit manifest_dir
        assert "undeclared" in result
        assert "registered" in result
        assert "tracked" in result

        # Verify ManifestChain was called with the custom manifest_dir
        mock_chain_cls.assert_called_once_with("custom_manifests", project_root="/tmp/test")

    async def test_maid_files_handles_library_error(self):
        """Test that maid_files handles library errors gracefully."""
        from maid_runner_mcp.tools.files import maid_files

        mock_ctx = _create_mock_context()

        with (
            patch(
                "maid_runner_mcp.tools.files.ManifestChain",
                side_effect=RuntimeError("manifest directory not found"),
            ),
            patch(
                "maid_runner_mcp.tools.files.get_working_directory",
                new_callable=AsyncMock,
                return_value="/tmp/test",
            ),
        ):
            result = await maid_files(ctx=mock_ctx)

        # Should return empty result on error, not raise exception
        assert "undeclared" in result
        assert "registered" in result
        assert "tracked" in result
        # All lists should be empty on error
        assert isinstance(result["undeclared"], list)
        assert isinstance(result["registered"], list)
        assert isinstance(result["tracked"], list)

    async def test_maid_files_default_parameters(self):
        """Test that maid_files uses default parameters correctly."""
        from maid_runner_mcp.tools.files import maid_files

        mock_report = _create_mock_report()
        mock_engine = MagicMock()
        mock_engine.run_file_tracking.return_value = mock_report
        mock_chain = MagicMock()

        mock_ctx = _create_mock_context()

        with (
            patch(
                "maid_runner_mcp.tools.files.ManifestChain", return_value=mock_chain
            ) as mock_chain_cls,
            patch("maid_runner_mcp.tools.files.ValidationEngine", return_value=mock_engine),
            patch(
                "maid_runner_mcp.tools.files.get_working_directory",
                new_callable=AsyncMock,
                return_value="/tmp/test",
            ),
        ):
            await maid_files(ctx=mock_ctx)

        # Verify ManifestChain was called with default manifest_dir
        mock_chain_cls.assert_called_once_with("manifests", project_root="/tmp/test")

    async def test_maid_files_calls_run_file_tracking(self):
        """Test that maid_files calls engine.run_file_tracking with the chain."""
        from maid_runner_mcp.tools.files import maid_files

        mock_report = _create_mock_report()
        mock_engine = MagicMock()
        mock_engine.run_file_tracking.return_value = mock_report
        mock_chain = MagicMock()

        mock_ctx = _create_mock_context()

        with (
            patch("maid_runner_mcp.tools.files.ManifestChain", return_value=mock_chain),
            patch("maid_runner_mcp.tools.files.ValidationEngine", return_value=mock_engine),
            patch(
                "maid_runner_mcp.tools.files.get_working_directory",
                new_callable=AsyncMock,
                return_value="/tmp/test",
            ),
        ):
            await maid_files(ctx=mock_ctx)

        # Verify run_file_tracking was called with the chain
        mock_engine.run_file_tracking.assert_called_once_with(mock_chain)
