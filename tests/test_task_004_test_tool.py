"""Behavioral tests for maid_test MCP tool (Task 004).

These tests verify the expected artifacts defined in the manifest:
- TestResult: TypedDict for test results
- maid_test(): Async function that runs validation commands from manifests

Tests follow MAID behavioral testing pattern - they USE the artifacts
rather than just checking existence.
"""

import pytest


class TestTestResult:
    """Tests for the TestResult TypedDict."""

    def test_test_result_is_typed_dict(self):
        """Test that TestResult is a TypedDict.

        The manifest specifies:
        - type: class
        - name: TestResult
        - description: TypedDict for test results
        """
        from maid_runner_mcp.tools.test import TestResult

        # TypedDict classes have __annotations__
        assert hasattr(
            TestResult, "__annotations__"
        ), "TestResult should have __annotations__ (TypedDict requirement)"

    def test_test_result_has_required_fields(self):
        """Test that TestResult has all required fields.

        The manifest specifies fields:
        - success (boolean)
        - total_manifests (integer)
        - passed (integer)
        - failed (integer)
        - failed_manifests (array of strings)
        """
        from maid_runner_mcp.tools.test import TestResult

        annotations = TestResult.__annotations__

        required_fields = ["success", "total_manifests", "passed", "failed", "failed_manifests"]

        for field_name in required_fields:
            assert field_name in annotations, f"TestResult should have '{field_name}' field"

    def test_test_result_field_types(self):
        """Test that TestResult fields have expected types."""
        from maid_runner_mcp.tools.test import TestResult

        annotations = TestResult.__annotations__

        # Check field types
        assert annotations["success"] is bool, "success should be bool"
        assert annotations["total_manifests"] is int, "total_manifests should be int"
        assert annotations["passed"] is int, "passed should be int"
        assert annotations["failed"] is int, "failed should be int"
        # failed_manifests should be list[str]
        assert "failed_manifests" in annotations


class TestMaidTestFunction:
    """Tests for the maid_test async function."""

    def test_maid_test_is_callable(self):
        """Test that maid_test exists and is callable.

        The manifest specifies:
        - type: function
        - name: maid_test
        """
        from maid_runner_mcp.tools.test import maid_test

        assert callable(maid_test), "maid_test should be callable"

    def test_maid_test_is_async(self):
        """Test that maid_test is an async function."""
        import asyncio
        from maid_runner_mcp.tools.test import maid_test

        assert asyncio.iscoroutinefunction(maid_test), "maid_test should be an async function"

    def test_maid_test_has_correct_signature(self):
        """Test that maid_test has the expected parameters.

        The manifest specifies:
        - manifest_dir: str (default: "manifests")
        - manifest: str | None (default: None)
        - fail_fast: bool (default: False)
        - timeout: int (default: 300)
        """
        import inspect
        from maid_runner_mcp.tools.test import maid_test

        sig = inspect.signature(maid_test)
        params = sig.parameters

        # Check manifest_dir parameter with default
        assert "manifest_dir" in params, "maid_test should have 'manifest_dir' parameter"
        assert (
            params["manifest_dir"].default == "manifests"
        ), "manifest_dir should default to 'manifests'"

        # Check manifest parameter with default
        assert "manifest" in params, "maid_test should have 'manifest' parameter"
        assert params["manifest"].default is None, "manifest should default to None"

        # Check fail_fast parameter with default
        assert "fail_fast" in params, "maid_test should have 'fail_fast' parameter"
        assert params["fail_fast"].default is False, "fail_fast should default to False"

        # Check timeout parameter with default
        assert "timeout" in params, "maid_test should have 'timeout' parameter"
        assert params["timeout"].default == 300, "timeout should default to 300"


@pytest.mark.asyncio
class TestMaidTestBehavior:
    """Tests for maid_test behavior when called.

    Note: We use mocking here because calling maid_test() with real manifests
    would trigger pytest recursively (maid test -> pytest -> maid_test -> pytest...).
    """

    async def test_maid_test_returns_test_result(self):
        """Test that maid_test returns a TestResult-compatible dict."""
        from unittest.mock import patch, MagicMock, AsyncMock
        from maid_runner_mcp.tools.test import maid_test

        # Create a mock context
        mock_ctx = MagicMock()
        mock_session = MagicMock()
        mock_session.list_roots = AsyncMock(
            return_value=MagicMock(roots=[MagicMock(uri="file:///tmp/test")])
        )
        mock_ctx.session = mock_session

        # Mock subprocess to avoid recursive test execution
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Summary: 2/2 validation commands passed"
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            result = await maid_test(ctx=mock_ctx)

        # Result should have the required fields
        assert "success" in result, "Result should have 'success' field"
        assert "total_manifests" in result, "Result should have 'total_manifests' field"
        assert "passed" in result, "Result should have 'passed' field"
        assert "failed" in result, "Result should have 'failed' field"
        assert "failed_manifests" in result, "Result should have 'failed_manifests' field"

    async def test_maid_test_field_types(self):
        """Test that maid_test returns correctly typed fields."""
        from unittest.mock import patch, MagicMock, AsyncMock
        from maid_runner_mcp.tools.test import maid_test

        # Create a mock context
        mock_ctx = MagicMock()
        mock_session = MagicMock()
        mock_session.list_roots = AsyncMock(
            return_value=MagicMock(roots=[MagicMock(uri="file:///tmp/test")])
        )
        mock_ctx.session = mock_session

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Summary: 2/2 validation commands passed"
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            result = await maid_test(ctx=mock_ctx)

        assert isinstance(result["success"], bool), "success should be bool"
        assert isinstance(result["total_manifests"], int), "total_manifests should be int"
        assert isinstance(result["passed"], int), "passed should be int"
        assert isinstance(result["failed"], int), "failed should be int"
        assert isinstance(result["failed_manifests"], list), "failed_manifests should be list"

    async def test_maid_test_with_nonexistent_manifest(self):
        """Test maid_test with a nonexistent manifest file."""
        from unittest.mock import patch, MagicMock, AsyncMock
        from maid_runner_mcp.tools.test import maid_test

        # Create a mock context
        mock_ctx = MagicMock()
        mock_session = MagicMock()
        mock_session.list_roots = AsyncMock(
            return_value=MagicMock(roots=[MagicMock(uri="file:///tmp/test")])
        )
        mock_ctx.session = mock_session

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Manifest not found: nonexistent.json"

        with patch("subprocess.run", return_value=mock_result):
            result = await maid_test(ctx=mock_ctx, manifest="nonexistent.json")

        # Should handle gracefully with failure info
        assert "success" in result
        assert "failed_manifests" in result
        assert isinstance(result["failed_manifests"], list)

    async def test_maid_test_with_nonexistent_directory(self):
        """Test maid_test with a nonexistent manifest directory."""
        from unittest.mock import patch, MagicMock, AsyncMock
        from maid_runner_mcp.tools.test import maid_test

        # Create a mock context
        mock_ctx = MagicMock()
        mock_session = MagicMock()
        mock_session.list_roots = AsyncMock(
            return_value=MagicMock(roots=[MagicMock(uri="file:///tmp/test")])
        )
        mock_ctx.session = mock_session

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Directory not found"

        with patch("subprocess.run", return_value=mock_result):
            result = await maid_test(ctx=mock_ctx, manifest_dir="nonexistent_dir")

        # Should handle gracefully
        assert "success" in result
        assert "total_manifests" in result

    async def test_maid_test_counts_are_consistent(self):
        """Test that passed + failed equals total_manifests."""
        from unittest.mock import patch, MagicMock, AsyncMock
        from maid_runner_mcp.tools.test import maid_test

        # Create a mock context
        mock_ctx = MagicMock()
        mock_session = MagicMock()
        mock_session.list_roots = AsyncMock(
            return_value=MagicMock(roots=[MagicMock(uri="file:///tmp/test")])
        )
        mock_ctx.session = mock_session

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Summary: 3/3 validation commands passed"
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            result = await maid_test(ctx=mock_ctx)

        # The counts should be consistent
        total = result["total_manifests"]
        passed = result["passed"]
        failed = result["failed"]

        assert (
            passed + failed == total
        ), f"passed ({passed}) + failed ({failed}) should equal total_manifests ({total})"

    async def test_maid_test_failed_manifests_matches_failed_count(self):
        """Test that failed_manifests list length matches failed count."""
        from unittest.mock import patch, MagicMock, AsyncMock
        from maid_runner_mcp.tools.test import maid_test

        # Create a mock context
        mock_ctx = MagicMock()
        mock_session = MagicMock()
        mock_session.list_roots = AsyncMock(
            return_value=MagicMock(roots=[MagicMock(uri="file:///tmp/test")])
        )
        mock_ctx.session = mock_session

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Summary: 2/2 validation commands passed"
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            result = await maid_test(ctx=mock_ctx)

        failed_count = result["failed"]
        failed_list = result["failed_manifests"]

        assert (
            len(failed_list) == failed_count
        ), f"len(failed_manifests) ({len(failed_list)}) should equal failed ({failed_count})"
