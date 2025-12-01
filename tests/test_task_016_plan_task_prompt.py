"""Behavioral tests for plan_task MCP prompt (Task 016).

Tests verify that the plan_task prompt:
1. Accepts 'goal', 'file_path', and 'task_type' arguments
2. Returns a properly formatted prompt template (list of Message dicts)
3. Contains guidance for MAID Phase 1 manifest creation workflow
4. Includes goal in the prompt content
5. Provides task type context when specified
6. Provides file path context when specified
7. Guides on using maid_validate for validation
"""

import pytest


@pytest.mark.asyncio
async def test_plan_task_prompt_returns_messages() -> None:
    """Test that plan_task returns a list of Message dicts."""
    from maid_runner_mcp.prompts.plan_task import plan_task

    result = await plan_task(goal="implement user authentication", file_path="", task_type="create")

    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(msg, dict) for msg in result)


@pytest.mark.asyncio
async def test_plan_task_prompt_includes_goal_in_content() -> None:
    """Test that the goal argument is included in the prompt content."""
    from maid_runner_mcp.prompts.plan_task import plan_task

    test_goal = "add caching layer for database queries"
    result = await plan_task(goal=test_goal, file_path="", task_type="edit")

    # Find the content containing the goal
    content_found = False
    for msg in result:
        if "content" in msg:
            content = msg["content"]
            if isinstance(content, str) and test_goal in content:
                content_found = True
                break
            elif isinstance(content, dict) and test_goal in str(content):
                content_found = True
                break

    assert content_found, f"Goal '{test_goal}' not found in prompt content"


@pytest.mark.asyncio
async def test_plan_task_prompt_contains_planning_loop_guidance() -> None:
    """Test that prompt includes MAID Planning Loop (Phase 2) guidance.

    The guidance should cover:
    1. Draft the manifest (primary contract)
    2. Draft behavioral tests
    3. Validate structure
    4. Iterate until validation passes
    """
    from maid_runner_mcp.prompts.plan_task import plan_task

    result = await plan_task(goal="test feature", file_path="", task_type="create")
    all_content = str(result).lower()

    # Should mention manifest creation
    assert "manifest" in all_content, "Prompt should mention creating a manifest"

    # Should mention validation
    assert "validat" in all_content, "Prompt should mention validation (validate/validation)"

    # Should mention test or behavioral
    assert (
        "test" in all_content or "behavioral" in all_content
    ), "Prompt should mention tests or behavioral validation"


@pytest.mark.asyncio
async def test_plan_task_prompt_contains_manifest_structure_guidance() -> None:
    """Test that prompt includes manifest structure guidance.

    Should mention key manifest fields:
    - goal
    - taskType
    - creatableFiles/editableFiles
    - expectedArtifacts
    - validationCommand
    """
    from maid_runner_mcp.prompts.plan_task import plan_task

    result = await plan_task(goal="test feature", file_path="", task_type="create")
    all_content = str(result).lower()

    # Key manifest fields should be mentioned
    assert "goal" in all_content, "Prompt should mention 'goal' field"
    assert "tasktype" in all_content or "task_type" in all_content, "Prompt should mention taskType"
    assert (
        "creatablefiles" in all_content or "editablefiles" in all_content
    ), "Prompt should mention file lists"
    assert "expectedartifacts" in all_content, "Prompt should mention expectedArtifacts"
    assert (
        "validationcommand" in all_content or "validation" in all_content
    ), "Prompt should mention validation"


@pytest.mark.asyncio
async def test_plan_task_prompt_includes_file_path_context() -> None:
    """Test that file_path is included in prompt when provided."""
    from maid_runner_mcp.prompts.plan_task import plan_task

    test_file_path = "src/mymodule/handler.py"
    result = await plan_task(goal="add error handling", file_path=test_file_path, task_type="edit")

    all_content = str(result)
    assert (
        test_file_path in all_content
    ), f"File path '{test_file_path}' should be in prompt when provided"


@pytest.mark.asyncio
async def test_plan_task_prompt_handles_empty_file_path() -> None:
    """Test that prompt handles empty file_path gracefully."""
    from maid_runner_mcp.prompts.plan_task import plan_task

    # Should not raise an error with empty file_path
    result = await plan_task(goal="test feature", file_path="", task_type="create")

    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_plan_task_prompt_includes_task_type_context() -> None:
    """Test that task_type is reflected in the prompt content."""
    from maid_runner_mcp.prompts.plan_task import plan_task

    # Test with 'create' task type
    result_create = await plan_task(goal="new feature", file_path="", task_type="create")
    all_content_create = str(result_create).lower()

    # Test with 'edit' task type
    result_edit = await plan_task(goal="modify feature", file_path="", task_type="edit")
    all_content_edit = str(result_edit).lower()

    # Both should contain task type guidance
    assert (
        "create" in all_content_create or "new" in all_content_create
    ), "Prompt should reflect create task type"
    assert (
        "edit" in all_content_edit or "modify" in all_content_edit
    ), "Prompt should reflect edit task type"


@pytest.mark.asyncio
async def test_plan_task_prompt_mentions_maid_validate() -> None:
    """Test that prompt mentions using maid_validate for validation."""
    from maid_runner_mcp.prompts.plan_task import plan_task

    result = await plan_task(goal="test feature", file_path="", task_type="create")
    all_content = str(result).lower()

    # Should mention maid_validate or maid validate
    assert (
        "maid_validate" in all_content or "maid validate" in all_content
    ), "Prompt should mention maid_validate tool for validation"


@pytest.mark.asyncio
async def test_plan_task_prompt_has_user_role() -> None:
    """Test that at least one message has the user role."""
    from maid_runner_mcp.prompts.plan_task import plan_task

    result = await plan_task(goal="test feature", file_path="", task_type="create")

    has_user_role = any(msg.get("role") == "user" for msg in result)
    assert has_user_role, "Prompt should have at least one message with 'user' role"


@pytest.mark.asyncio
async def test_plan_task_has_required_parameters() -> None:
    """Test that plan_task has the expected parameters."""
    from maid_runner_mcp.prompts.plan_task import plan_task
    import inspect

    sig = inspect.signature(plan_task)
    params = sig.parameters

    assert "goal" in params, "plan_task must have a 'goal' parameter"
    assert "file_path" in params, "plan_task must have a 'file_path' parameter"
    assert "task_type" in params, "plan_task must have a 'task_type' parameter"


@pytest.mark.asyncio
async def test_plan_task_prompt_mentions_schema_reference() -> None:
    """Test that prompt mentions checking the manifest schema."""
    from maid_runner_mcp.prompts.plan_task import plan_task

    result = await plan_task(goal="test feature", file_path="", task_type="create")
    all_content = str(result).lower()

    # Should mention schema or maid_get_schema
    assert "schema" in all_content, "Prompt should mention checking the manifest schema"


@pytest.mark.asyncio
async def test_plan_task_prompt_emphasizes_manifest_as_contract() -> None:
    """Test that prompt emphasizes manifest as the primary contract."""
    from maid_runner_mcp.prompts.plan_task import plan_task

    result = await plan_task(goal="test feature", file_path="", task_type="create")
    all_content = str(result).lower()

    # Should mention manifest as contract or primary
    assert (
        "contract" in all_content or "primary" in all_content
    ), "Prompt should emphasize manifest as the primary contract"
