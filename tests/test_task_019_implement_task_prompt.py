"""Behavioral tests for implement_task MCP prompt (Task 019).

Tests verify that the implement_task prompt:
1. Accepts a 'manifest_path' argument (required)
2. Returns a properly formatted prompt template (list of Message dicts)
3. Contains guidance for MAID Phase 3 implementation workflow (TDD)
4. Includes Red-Green-Refactor TDD guidance
5. Includes validation commands guidance
6. Includes code quality checks guidance
7. Mirrors .claude/agents/maid-developer.md behavior
"""

import pytest


@pytest.mark.asyncio
async def test_implement_task_prompt_returns_messages() -> None:
    """Test that implement_task returns a list of Message dicts."""
    from maid_runner_mcp.prompts.implement_task import implement_task

    result = await implement_task(manifest_path="manifests/task-001-example.manifest.json")

    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(msg, dict) for msg in result)


@pytest.mark.asyncio
async def test_implement_task_prompt_includes_manifest_path_in_content() -> None:
    """Test that the manifest_path argument is included in the prompt content."""
    from maid_runner_mcp.prompts.implement_task import implement_task

    test_manifest_path = "manifests/task-042-feature.manifest.json"
    result = await implement_task(manifest_path=test_manifest_path)

    # Find the content containing the manifest path
    content_found = False
    for msg in result:
        if "content" in msg:
            content = msg["content"]
            if isinstance(content, str) and test_manifest_path in content:
                content_found = True
                break
            elif isinstance(content, dict) and test_manifest_path in str(content):
                content_found = True
                break

    assert content_found, f"Manifest path '{test_manifest_path}' not found in prompt content"


@pytest.mark.asyncio
async def test_implement_task_prompt_contains_tdd_workflow_guidance() -> None:
    """Test that prompt includes TDD workflow guidance.

    The guidance should cover Red-Green-Refactor:
    1. Red phase - confirm tests fail
    2. Green phase - implement to make tests pass
    3. Refactor phase - improve code while keeping tests green
    """
    from maid_runner_mcp.prompts.implement_task import implement_task

    result = await implement_task(manifest_path="manifests/task-001.manifest.json")
    all_content = str(result).lower()

    # Should mention Red phase (tests should fail initially)
    assert (
        "red" in all_content or "fail" in all_content
    ), "Prompt should mention Red phase or tests failing"

    # Should mention Green phase (make tests pass)
    assert (
        "green" in all_content or "pass" in all_content
    ), "Prompt should mention Green phase or making tests pass"

    # Should mention Refactor
    assert "refactor" in all_content, "Prompt should mention refactoring"


@pytest.mark.asyncio
async def test_implement_task_prompt_contains_validation_commands() -> None:
    """Test that prompt includes validation commands guidance.

    Should mention:
    - maid validate
    - maid test
    - pytest
    """
    from maid_runner_mcp.prompts.implement_task import implement_task

    result = await implement_task(manifest_path="manifests/task-001.manifest.json")
    all_content = str(result).lower()

    # Should mention maid validate
    assert (
        "maid validate" in all_content or "maid_validate" in all_content
    ), "Prompt should mention maid validate command"

    # Should mention testing
    assert (
        "maid test" in all_content or "pytest" in all_content or "maid_test" in all_content
    ), "Prompt should mention running tests"


@pytest.mark.asyncio
async def test_implement_task_prompt_contains_code_quality_checks() -> None:
    """Test that prompt includes code quality checks guidance.

    Should mention:
    - lint/linting
    - type-check/type checking
    """
    from maid_runner_mcp.prompts.implement_task import implement_task

    result = await implement_task(manifest_path="manifests/task-001.manifest.json")
    all_content = str(result).lower()

    # Should mention linting
    assert "lint" in all_content, "Prompt should mention linting"

    # Should mention type checking
    assert "type" in all_content and "check" in all_content, "Prompt should mention type checking"


@pytest.mark.asyncio
async def test_implement_task_prompt_mentions_manifest_artifacts() -> None:
    """Test that prompt mentions matching manifest artifacts."""
    from maid_runner_mcp.prompts.implement_task import implement_task

    result = await implement_task(manifest_path="manifests/task-001.manifest.json")
    all_content = str(result).lower()

    # Should mention artifacts or manifest compliance
    assert (
        "artifact" in all_content or "manifest" in all_content
    ), "Prompt should mention artifacts or manifest"


@pytest.mark.asyncio
async def test_implement_task_prompt_mentions_file_restrictions() -> None:
    """Test that prompt mentions only editing files from manifest."""
    from maid_runner_mcp.prompts.implement_task import implement_task

    result = await implement_task(manifest_path="manifests/task-001.manifest.json")
    all_content = str(result).lower()

    # Should mention file restrictions
    assert (
        "only" in all_content and "file" in all_content
    ) or "edit" in all_content, "Prompt should mention file editing restrictions"


@pytest.mark.asyncio
async def test_implement_task_prompt_has_user_role() -> None:
    """Test that at least one message has the user role."""
    from maid_runner_mcp.prompts.implement_task import implement_task

    result = await implement_task(manifest_path="manifests/task-001.manifest.json")

    has_user_role = any(msg.get("role") == "user" for msg in result)
    assert has_user_role, "Prompt should have at least one message with 'user' role"


@pytest.mark.asyncio
async def test_implement_task_requires_manifest_path_argument() -> None:
    """Test that implement_task requires the manifest_path argument."""
    from maid_runner_mcp.prompts.implement_task import implement_task
    import inspect

    sig = inspect.signature(implement_task)
    params = sig.parameters

    assert "manifest_path" in params, "implement_task must have a 'manifest_path' parameter"

    # Check that manifest_path parameter has no default (is required)
    manifest_path_param = params["manifest_path"]
    assert (
        manifest_path_param.default is inspect.Parameter.empty
    ), "manifest_path parameter should be required (no default)"


@pytest.mark.asyncio
async def test_implement_task_prompt_mentions_success_criteria() -> None:
    """Test that prompt includes success criteria guidance."""
    from maid_runner_mcp.prompts.implement_task import implement_task

    result = await implement_task(manifest_path="manifests/task-001.manifest.json")
    all_content = str(result).lower()

    # Should mention success criteria or completion
    assert (
        "success" in all_content or "pass" in all_content or "complet" in all_content
    ), "Prompt should mention success criteria"


@pytest.mark.asyncio
async def test_implement_task_prompt_mentions_phase_3() -> None:
    """Test that prompt references Phase 3 of MAID methodology."""
    from maid_runner_mcp.prompts.implement_task import implement_task

    result = await implement_task(manifest_path="manifests/task-001.manifest.json")
    all_content = str(result).lower()

    # Should reference Phase 3 or implementation phase
    assert (
        "phase 3" in all_content or "phase3" in all_content or "implementation" in all_content
    ), "Prompt should reference Phase 3 or implementation"


@pytest.mark.asyncio
async def test_implement_task_return_type_is_list_of_message() -> None:
    """Test that implement_task returns list[Message] type."""
    from maid_runner_mcp.prompts.implement_task import implement_task
    import inspect

    sig = inspect.signature(implement_task)
    return_annotation = sig.return_annotation

    # Check that return type annotation exists and mentions list
    assert (
        return_annotation is not inspect.Signature.empty
    ), "Function should have return type annotation"
    return_str = str(return_annotation)
    assert (
        "list" in return_str.lower() or "List" in return_str
    ), "Return type should be list[Message]"


@pytest.mark.asyncio
async def test_implement_task_prompt_message_structure() -> None:
    """Test that each message in the list has proper structure."""
    from maid_runner_mcp.prompts.implement_task import implement_task

    result = await implement_task(manifest_path="manifests/task-001.manifest.json")

    for msg in result:
        # Each message should have at least 'role' and 'content' keys
        assert "role" in msg, "Each message should have a 'role' key"
        assert "content" in msg, "Each message should have a 'content' key"
        # Role should be a string
        assert isinstance(msg["role"], str), "Role should be a string"
