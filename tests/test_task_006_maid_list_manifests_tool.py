"""Behavioral tests for task-006: Implement maid_list_manifests MCP tool.

Tests verify that the maid_list_manifests function:
1. Wraps MAID Runner manifests command correctly
2. Handles async execution properly
3. Returns structured JSON responses with categorized manifest lists
4. Supports manifest_dir parameter
5. Processes errors appropriately (missing files, invalid paths)
6. Parses manifest output to extract created_by, edited_by, read_by lists
7. Handles files not referenced by any manifests
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from maid_runner_mcp.tools.manifests import maid_list_manifests


class TestMaidListManifestsBasicBehavior:
    """Test basic maid_list_manifests function behavior."""

    @pytest.mark.asyncio
    async def test_maid_list_manifests_with_tracked_file_returns_success(self, tmp_path):
        """Test that listing manifests succeeds for a tracked file."""
        test_file = "src/example.py"

        # Mock subprocess to simulate successful manifest listing
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"""Manifests referencing: src/example.py
Total: 3 manifest(s)

================================================================================

\xf0\x9f\x93\x9d CREATED BY (1 manifest(s)):
  - task-001-create-example.manifest.json

\xe2\x9c\x8f\xef\xb8\x8f EDITED BY (1 manifest(s)):
  - task-005-edit-example.manifest.json

\xf0\x9f\x91\x80 READ BY (1 manifest(s)):
  - task-010-read-example.manifest.json

================================================================================
"""
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_list_manifests(test_file)

        # Assert result is a dictionary
        assert isinstance(result, dict), "maid_list_manifests must return a dictionary"

        # Assert success field is True
        assert "success" in result, "Result must contain 'success' field"
        assert result["success"] is True, f"Expected success=True, got {result.get('success')}"

        # Assert file_path is included
        assert "file_path" in result, "Result must contain 'file_path' field"
        assert result["file_path"] == test_file

        # Assert total_manifests is included
        assert "total_manifests" in result, "Result must contain 'total_manifests' field"
        assert result["total_manifests"] == 3

    @pytest.mark.asyncio
    async def test_maid_list_manifests_with_untracked_file_returns_empty_lists(self, tmp_path):
        """Test that listing manifests for untracked file returns empty categorized lists."""
        test_file = "src/untracked.py"

        # Mock subprocess to simulate file with no manifest references
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"""Manifests referencing: src/untracked.py
Total: 0 manifest(s)

================================================================================

No manifests found referencing this file.

================================================================================
"""
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_list_manifests(test_file)

        # Assert result indicates success
        assert isinstance(result, dict), "maid_list_manifests must return a dictionary"
        assert result["success"] is True, "Should succeed even with no manifests"

        # Assert total is 0
        assert result["total_manifests"] == 0, "Expected total_manifests=0 for untracked file"

        # Assert all category lists are empty
        assert len(result["created_by"]) == 0, "created_by should be empty"
        assert len(result["edited_by"]) == 0, "edited_by should be empty"
        assert len(result["read_by"]) == 0, "read_by should be empty"

    @pytest.mark.asyncio
    async def test_maid_list_manifests_with_nonexistent_file_returns_success(self):
        """Test that listing manifests for nonexistent file still succeeds."""
        nonexistent_file = "/nonexistent/file.py"

        # Mock subprocess to simulate no manifests found
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"""Manifests referencing: /nonexistent/file.py
Total: 0 manifest(s)

================================================================================

No manifests found referencing this file.

================================================================================
"""
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_list_manifests(nonexistent_file)

        # Assert result indicates success (command succeeds even for nonexistent files)
        assert isinstance(result, dict), "maid_list_manifests must return a dictionary"
        assert result["success"] is True, "Should succeed for nonexistent file"
        assert result["total_manifests"] == 0


class TestMaidListManifestsCategorization:
    """Test manifest categorization by reference type."""

    @pytest.mark.asyncio
    async def test_maid_list_manifests_returns_created_by_list(self, tmp_path):
        """Test that created_by manifests are correctly parsed."""
        test_file = "src/module.py"

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"""Manifests referencing: src/module.py
Total: 2 manifest(s)

================================================================================

\xf0\x9f\x93\x9d CREATED BY (2 manifest(s)):
  - task-001-create-module.manifest.json
  - task-005-refactor-module.manifest.json

================================================================================
"""
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_list_manifests(test_file)

        # Assert created_by contains correct manifests
        assert "created_by" in result, "Result must contain 'created_by' field"
        assert isinstance(result["created_by"], list), "created_by must be a list"
        assert (
            len(result["created_by"]) == 2
        ), f"Expected 2 manifests, got {len(result['created_by'])}"
        assert "task-001-create-module.manifest.json" in result["created_by"]
        assert "task-005-refactor-module.manifest.json" in result["created_by"]

        # Assert other categories are empty
        assert len(result["edited_by"]) == 0, "edited_by should be empty"
        assert len(result["read_by"]) == 0, "read_by should be empty"

    @pytest.mark.asyncio
    async def test_maid_list_manifests_returns_edited_by_list(self, tmp_path):
        """Test that edited_by manifests are correctly parsed."""
        test_file = "src/module.py"

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"""Manifests referencing: src/module.py
Total: 1 manifest(s)

================================================================================

\xe2\x9c\x8f\xef\xb8\x8f EDITED BY (1 manifest(s)):
  - task-010-update-module.manifest.json

================================================================================
"""
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_list_manifests(test_file)

        # Assert edited_by contains correct manifest
        assert "edited_by" in result, "Result must contain 'edited_by' field"
        assert isinstance(result["edited_by"], list), "edited_by must be a list"
        assert len(result["edited_by"]) == 1
        assert "task-010-update-module.manifest.json" in result["edited_by"]

        # Assert other categories are empty
        assert len(result["created_by"]) == 0, "created_by should be empty"
        assert len(result["read_by"]) == 0, "read_by should be empty"

    @pytest.mark.asyncio
    async def test_maid_list_manifests_returns_read_by_list(self, tmp_path):
        """Test that read_by manifests are correctly parsed."""
        test_file = "src/utils.py"

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"""Manifests referencing: src/utils.py
Total: 3 manifest(s)

================================================================================

\xf0\x9f\x91\x80 READ BY (3 manifest(s)):
  - task-002-use-utils.manifest.json
  - task-007-test-utils.manifest.json
  - task-015-refactor-main.manifest.json

================================================================================
"""
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_list_manifests(test_file)

        # Assert read_by contains correct manifests
        assert "read_by" in result, "Result must contain 'read_by' field"
        assert isinstance(result["read_by"], list), "read_by must be a list"
        assert len(result["read_by"]) == 3
        assert "task-002-use-utils.manifest.json" in result["read_by"]
        assert "task-007-test-utils.manifest.json" in result["read_by"]
        assert "task-015-refactor-main.manifest.json" in result["read_by"]

        # Assert other categories are empty
        assert len(result["created_by"]) == 0, "created_by should be empty"
        assert len(result["edited_by"]) == 0, "edited_by should be empty"

    @pytest.mark.asyncio
    async def test_maid_list_manifests_returns_all_categories_when_present(self, tmp_path):
        """Test parsing when file is referenced in all three categories."""
        test_file = "src/core.py"

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"""Manifests referencing: src/core.py
Total: 5 manifest(s)

================================================================================

\xf0\x9f\x93\x9d CREATED BY (1 manifest(s)):
  - task-001-create-core.manifest.json

\xe2\x9c\x8f\xef\xb8\x8f EDITED BY (2 manifest(s)):
  - task-005-enhance-core.manifest.json
  - task-010-refactor-core.manifest.json

\xf0\x9f\x91\x80 READ BY (2 manifest(s)):
  - task-003-use-core.manifest.json
  - task-008-test-core.manifest.json

================================================================================
"""
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_list_manifests(test_file)

        # Assert total is correct
        assert result["total_manifests"] == 5

        # Assert all categories have correct counts and contents
        assert len(result["created_by"]) == 1
        assert "task-001-create-core.manifest.json" in result["created_by"]

        assert len(result["edited_by"]) == 2
        assert "task-005-enhance-core.manifest.json" in result["edited_by"]
        assert "task-010-refactor-core.manifest.json" in result["edited_by"]

        assert len(result["read_by"]) == 2
        assert "task-003-use-core.manifest.json" in result["read_by"]
        assert "task-008-test-core.manifest.json" in result["read_by"]


class TestMaidListManifestsParameters:
    """Test parameter handling."""

    @pytest.mark.asyncio
    async def test_maid_list_manifests_with_custom_manifest_dir(self, tmp_path):
        """Test listing manifests with custom manifest directory."""
        test_file = "src/module.py"
        custom_dir = str(tmp_path / "custom_manifests")

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"""Manifests referencing: src/module.py
Total: 1 manifest(s)

================================================================================

\xf0\x9f\x93\x9d CREATED BY (1 manifest(s)):
  - task-001-create-module.manifest.json

================================================================================
"""
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_list_manifests(test_file, manifest_dir=custom_dir)

        # Assert success
        assert result["success"] is True

        # Assert command was called with correct manifest_dir
        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]
        assert "--manifest-dir" in call_args, "Must pass --manifest-dir flag"
        dir_index = list(call_args).index("--manifest-dir")
        assert call_args[dir_index + 1] == custom_dir

    @pytest.mark.asyncio
    async def test_maid_list_manifests_with_default_manifest_dir(self, tmp_path):
        """Test listing manifests with default manifest directory."""
        test_file = "src/module.py"

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"""Manifests referencing: src/module.py
Total: 0 manifest(s)

================================================================================

No manifests found referencing this file.

================================================================================
"""
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            # Call without specifying manifest_dir
            result = await maid_list_manifests(test_file)

        # Assert success
        assert result["success"] is True

        # Assert command was called with default manifest_dir
        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]
        assert "--manifest-dir" in call_args
        dir_index = list(call_args).index("--manifest-dir")
        assert call_args[dir_index + 1] == "manifests", "Default manifest_dir should be 'manifests'"


class TestMaidListManifestsOutputStructure:
    """Test structured output format."""

    @pytest.mark.asyncio
    async def test_maid_list_manifests_output_contains_required_fields(self, tmp_path):
        """Test that output contains all required fields."""
        test_file = "src/test.py"

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"""Manifests referencing: src/test.py
Total: 0 manifest(s)

================================================================================

No manifests found referencing this file.

================================================================================
"""
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_list_manifests(test_file)

        # Assert all required fields are present
        required_fields = [
            "success",
            "file_path",
            "total_manifests",
            "created_by",
            "edited_by",
            "read_by",
        ]
        for field in required_fields:
            assert field in result, f"Result must contain '{field}' field"

        # Assert field types
        assert isinstance(result["success"], bool), "success must be a boolean"
        assert isinstance(result["file_path"], str), "file_path must be a string"
        assert isinstance(result["total_manifests"], int), "total_manifests must be an integer"
        assert isinstance(result["created_by"], list), "created_by must be a list"
        assert isinstance(result["edited_by"], list), "edited_by must be a list"
        assert isinstance(result["read_by"], list), "read_by must be a list"

    @pytest.mark.asyncio
    async def test_maid_list_manifests_success_has_no_errors_field(self, tmp_path):
        """Test that successful listing has no errors field."""
        test_file = "src/test.py"

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"""Manifests referencing: src/test.py
Total: 1 manifest(s)

================================================================================

\xf0\x9f\x93\x9d CREATED BY (1 manifest(s)):
  - task-001-test.manifest.json

================================================================================
"""
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_list_manifests(test_file)

        # Assert success
        assert result["success"] is True

        # On success, errors field should not be present (or empty if present)
        if "errors" in result:
            assert len(result["errors"]) == 0, "Successful listing should have no errors"

    @pytest.mark.asyncio
    async def test_maid_list_manifests_failure_has_errors_field(self, tmp_path):
        """Test that failed listing includes errors field."""
        test_file = "src/test.py"

        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stdout = b""
        mock_process.stderr = b"Error: Invalid manifest directory\n"

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_list_manifests(test_file)

        # Assert failure
        assert result["success"] is False

        # Assert errors are included
        assert "errors" in result, "Result must contain 'errors' on failure"
        assert isinstance(result["errors"], list), "Errors must be a list"
        assert len(result["errors"]) > 0, "Errors list must not be empty"


class TestMaidListManifestsErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.asyncio
    async def test_maid_list_manifests_handles_subprocess_errors(self, tmp_path):
        """Test handling of subprocess execution errors."""
        test_file = "src/test.py"

        # Mock subprocess to raise an exception
        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.side_effect = OSError("Command not found")

            result = await maid_list_manifests(test_file)

        # Assert error is handled gracefully
        assert isinstance(result, dict), "Must return dictionary even on error"
        assert result["success"] is False, "success must be False on error"
        assert "errors" in result, "Must include errors on exception"
        assert len(result["errors"]) > 0, "Errors must be reported"

    @pytest.mark.asyncio
    async def test_maid_list_manifests_handles_invalid_manifest_dir(self):
        """Test handling of invalid manifest directory."""
        test_file = "src/test.py"
        invalid_dir = "/nonexistent/manifests"

        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stdout = b""
        mock_process.stderr = b"Error: Manifest directory not found: /nonexistent/manifests\n"

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            result = await maid_list_manifests(test_file, manifest_dir=invalid_dir)

        # Assert error is reported
        assert result["success"] is False, "success must be False for invalid manifest_dir"
        assert "errors" in result, "Must include errors for invalid directory"

    @pytest.mark.asyncio
    async def test_maid_list_manifests_handles_timeout(self, tmp_path):
        """Test handling of manifest listing timeout."""
        test_file = "src/test.py"

        # Mock subprocess to simulate timeout
        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_process = MagicMock()
            mock_process.communicate = AsyncMock(side_effect=asyncio.TimeoutError)
            mock_exec.return_value = mock_process

            result = await maid_list_manifests(test_file)

        # Assert timeout is handled
        assert isinstance(result, dict), "Must return dictionary even on timeout"
        assert result["success"] is False, "success must be False on timeout"
        assert "errors" in result, "Must include errors on timeout"


class TestMaidListManifestsCommandConstruction:
    """Test that the command is constructed correctly."""

    @pytest.mark.asyncio
    async def test_maid_list_manifests_constructs_command_with_all_parameters(self, tmp_path):
        """Test command construction with all parameters specified."""
        test_file = "src/module.py"
        custom_dir = str(tmp_path / "custom")

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"""Manifests referencing: src/module.py
Total: 0 manifest(s)

================================================================================

No manifests found referencing this file.

================================================================================
"""
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            await maid_list_manifests(test_file, manifest_dir=custom_dir)

        # Assert command includes all parameters
        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]

        # Check base command
        assert call_args[0] == "maid", "First arg should be 'maid'"
        assert call_args[1] == "manifests", "Second arg should be 'manifests'"
        assert test_file in call_args, "File path should be in command"

        # Check flags
        assert "--manifest-dir" in call_args
        assert custom_dir in call_args

    @pytest.mark.asyncio
    async def test_maid_list_manifests_constructs_minimal_command_with_defaults(self, tmp_path):
        """Test command construction with default parameters."""
        test_file = "src/test.py"

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"""Manifests referencing: src/test.py
Total: 0 manifest(s)

================================================================================

No manifests found referencing this file.

================================================================================
"""
        mock_process.stderr = b""

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_process
            mock_process.communicate = AsyncMock(
                return_value=(mock_process.stdout, mock_process.stderr)
            )

            await maid_list_manifests(test_file)

        # Assert command has minimal structure
        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]

        # Check base command
        assert call_args[0] == "maid"
        assert call_args[1] == "manifests"
        assert test_file in call_args

        # Check default manifest_dir is present
        assert "--manifest-dir" in call_args
        assert "manifests" in call_args
