"""Behavioral tests for maid_validate MCP tool (Task 002).

These tests verify the expected artifacts defined in the manifest:
- ValidateResult: TypedDict for validation results
- maid_validate(): Async function that validates manifests using MAID Runner

Tests follow MAID behavioral testing pattern - they USE the artifacts
rather than just checking existence.
"""

import pytest


class TestValidateResult:
    """Tests for the ValidateResult TypedDict."""

    def test_validate_result_is_typed_dict(self):
        """Test that ValidateResult is a TypedDict.

        The manifest specifies:
        - type: class
        - name: ValidateResult
        - description: TypedDict for validation results
        """
        from maid_runner_mcp.tools.validate import ValidateResult
        from typing import get_type_hints

        # TypedDict classes have __annotations__
        assert hasattr(
            ValidateResult, "__annotations__"
        ), "ValidateResult should have __annotations__ (TypedDict requirement)"

    def test_validate_result_has_required_fields(self):
        """Test that ValidateResult has all required fields."""
        from maid_runner_mcp.tools.validate import ValidateResult

        annotations = ValidateResult.__annotations__

        required_fields = {
            "success": bool,
            "mode": str,
            "manifest": str,
            "target_file": str,
            "used_chain": bool,
            "errors": list,
        }

        for field_name in required_fields:
            assert field_name in annotations, f"ValidateResult should have '{field_name}' field"

    def test_validate_result_has_optional_file_tracking(self):
        """Test that ValidateResult has optional file_tracking field."""
        from maid_runner_mcp.tools.validate import ValidateResult

        annotations = ValidateResult.__annotations__

        assert "file_tracking" in annotations, "ValidateResult should have 'file_tracking' field"


class TestMaidValidateFunction:
    """Tests for the maid_validate async function."""

    def test_maid_validate_is_callable(self):
        """Test that maid_validate exists and is callable.

        The manifest specifies:
        - type: function
        - name: maid_validate
        """
        from maid_runner_mcp.tools.validate import maid_validate

        assert callable(maid_validate), "maid_validate should be callable"

    def test_maid_validate_is_async(self):
        """Test that maid_validate is an async function."""
        import asyncio
        from maid_runner_mcp.tools.validate import maid_validate

        assert asyncio.iscoroutinefunction(
            maid_validate
        ), "maid_validate should be an async function"

    def test_maid_validate_has_correct_signature(self):
        """Test that maid_validate has the expected parameters.

        The manifest specifies:
        - manifest_path: str (required)
        - validation_mode: str (default: "implementation")
        - use_manifest_chain: bool (default: False)
        - manifest_dir: str | None (default: None)
        - quiet: bool (default: True)
        """
        import inspect
        from maid_runner_mcp.tools.validate import maid_validate

        sig = inspect.signature(maid_validate)
        params = sig.parameters

        # Check required parameter
        assert "manifest_path" in params, "maid_validate should have 'manifest_path' parameter"
        assert (
            params["manifest_path"].default is inspect.Parameter.empty
        ), "manifest_path should be a required parameter (no default)"

        # Check optional parameters with defaults
        assert "validation_mode" in params, "maid_validate should have 'validation_mode' parameter"
        assert (
            params["validation_mode"].default == "implementation"
        ), "validation_mode should default to 'implementation'"

        assert (
            "use_manifest_chain" in params
        ), "maid_validate should have 'use_manifest_chain' parameter"
        assert (
            params["use_manifest_chain"].default is False
        ), "use_manifest_chain should default to False"

        assert "manifest_dir" in params, "maid_validate should have 'manifest_dir' parameter"
        assert params["manifest_dir"].default is None, "manifest_dir should default to None"

        assert "quiet" in params, "maid_validate should have 'quiet' parameter"
        assert params["quiet"].default is True, "quiet should default to True"


@pytest.mark.asyncio
class TestMaidValidateBehavior:
    """Tests for maid_validate behavior when called."""

    async def test_maid_validate_returns_validate_result(self):
        """Test that maid_validate returns a ValidateResult-compatible dict."""
        from maid_runner_mcp.tools.validate import maid_validate
        from unittest.mock import AsyncMock, MagicMock

        # Create a mock context
        mock_ctx = MagicMock()
        mock_session = MagicMock()
        mock_session.list_roots = AsyncMock(
            return_value=MagicMock(roots=[MagicMock(uri="file:///tmp/test")])
        )
        mock_ctx.session = mock_session

        # Call with an invalid path to trigger error handling
        result = await maid_validate(manifest_path="nonexistent.json", ctx=mock_ctx)

        # Result should have the required fields
        assert "success" in result, "Result should have 'success' field"
        assert "mode" in result, "Result should have 'mode' field"
        assert "manifest" in result, "Result should have 'manifest' field"
        assert "target_file" in result, "Result should have 'target_file' field"
        assert "used_chain" in result, "Result should have 'used_chain' field"
        assert "errors" in result, "Result should have 'errors' field"

    async def test_maid_validate_error_handling(self):
        """Test that maid_validate handles errors gracefully."""
        from maid_runner_mcp.tools.validate import maid_validate
        from unittest.mock import AsyncMock, MagicMock

        # Create a mock context
        mock_ctx = MagicMock()
        mock_session = MagicMock()
        mock_session.list_roots = AsyncMock(
            return_value=MagicMock(roots=[MagicMock(uri="file:///tmp/test")])
        )
        mock_ctx.session = mock_session

        # Call with a nonexistent manifest
        result = await maid_validate(manifest_path="nonexistent.json", ctx=mock_ctx)

        # Should return success=False with errors
        assert result["success"] is False, "Should return success=False for invalid manifest"
        assert isinstance(result["errors"], list), "errors should be a list"
        assert len(result["errors"]) > 0, "Should have at least one error message"

    async def test_maid_validate_with_valid_manifest(self):
        """Test maid_validate with a valid manifest file."""
        from maid_runner_mcp.tools.validate import maid_validate
        from unittest.mock import AsyncMock, MagicMock

        # Create a mock context
        mock_ctx = MagicMock()
        mock_session = MagicMock()
        mock_session.list_roots = AsyncMock(
            return_value=MagicMock(roots=[MagicMock(uri="file:///tmp/test")])
        )
        mock_ctx.session = mock_session

        # Use the existing task-001 manifest which should be valid
        result = await maid_validate(
            manifest_path="manifests/task-001-mcp-server-core.manifest.json",
            ctx=mock_ctx
        )

        # Result should have proper structure regardless of success
        assert "success" in result
        assert "mode" in result
        assert result["mode"] == "implementation"
        assert "manifest" in result
        assert "task-001" in result["manifest"]
