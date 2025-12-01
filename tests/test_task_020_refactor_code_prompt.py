"""Behavioral tests for refactor_code MCP prompt (Task 020).

Tests verify that the refactor_code prompt:
1. Accepts 'file_path' and 'goal' arguments (both required)
2. Returns a properly formatted prompt template (list of Message dicts)
3. Contains guidance for MAID Phase 3.5 code quality improvements
4. Includes file_path and goal in the prompt content
5. Guides on keeping tests green while refactoring
6. Mentions validation commands (pytest, maid validate, maid test)
"""

import pytest


@pytest.mark.asyncio
async def test_refactor_code_prompt_returns_messages() -> None:
    """Test that refactor_code returns a list of Message dicts."""
    from maid_runner_mcp.prompts.refactor_code import refactor_code

    result = await refactor_code(
        file_path="src/mymodule/handler.py", goal="reduce code duplication"
    )

    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(msg, dict) for msg in result)


@pytest.mark.asyncio
async def test_refactor_code_prompt_includes_file_path_in_content() -> None:
    """Test that the file_path argument is included in the prompt content."""
    from maid_runner_mcp.prompts.refactor_code import refactor_code

    test_file_path = "src/maid_runner_mcp/tools/validate.py"
    result = await refactor_code(file_path=test_file_path, goal="improve naming")

    # Find the content containing the file_path
    content_found = False
    for msg in result:
        if "content" in msg:
            content = msg["content"]
            if isinstance(content, str) and test_file_path in content:
                content_found = True
                break
            elif isinstance(content, dict) and test_file_path in str(content):
                content_found = True
                break

    assert content_found, f"File path '{test_file_path}' not found in prompt content"


@pytest.mark.asyncio
async def test_refactor_code_prompt_includes_goal_in_content() -> None:
    """Test that the goal argument is included in the prompt content."""
    from maid_runner_mcp.prompts.refactor_code import refactor_code

    test_goal = "extract common logic into helper functions"
    result = await refactor_code(file_path="src/handler.py", goal=test_goal)

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
async def test_refactor_code_prompt_contains_phase_35_guidance() -> None:
    """Test that prompt includes MAID Phase 3.5 refactoring guidance.

    The guidance should cover:
    1. Ensure tests pass first
    2. Refactor code (remove duplication, improve naming, enhance readability)
    3. Keep public API unchanged
    4. Validate after each change
    """
    from maid_runner_mcp.prompts.refactor_code import refactor_code

    result = await refactor_code(file_path="src/handler.py", goal="improve quality")
    all_content = str(result).lower()

    # Should mention tests passing first
    assert "test" in all_content, "Prompt should mention tests"

    # Should mention refactoring concepts
    assert (
        "refactor" in all_content
        or "duplication" in all_content
        or "naming" in all_content
        or "readability" in all_content
    ), "Prompt should mention refactoring concepts"

    # Should mention keeping API unchanged
    assert (
        "api" in all_content or "public" in all_content
    ), "Prompt should mention keeping public API unchanged"


@pytest.mark.asyncio
async def test_refactor_code_prompt_mentions_validation_commands() -> None:
    """Test that prompt includes validation commands.

    Should mention:
    - pytest for running tests
    - maid validate for manifest compliance
    - maid test for full validation
    """
    from maid_runner_mcp.prompts.refactor_code import refactor_code

    result = await refactor_code(file_path="src/handler.py", goal="improve quality")
    all_content = str(result).lower()

    # Should mention pytest
    assert "pytest" in all_content, "Prompt should mention pytest"

    # Should mention maid validate or maid_validate
    assert (
        "maid validate" in all_content or "maid_validate" in all_content
    ), "Prompt should mention maid validate"


@pytest.mark.asyncio
async def test_refactor_code_prompt_emphasizes_tests_green() -> None:
    """Test that prompt emphasizes keeping tests green while refactoring."""
    from maid_runner_mcp.prompts.refactor_code import refactor_code

    result = await refactor_code(file_path="src/handler.py", goal="improve quality")
    all_content = str(result).lower()

    # Should mention keeping tests passing/green
    assert (
        "pass" in all_content or "green" in all_content
    ), "Prompt should emphasize keeping tests passing"


@pytest.mark.asyncio
async def test_refactor_code_prompt_mentions_quality_checks() -> None:
    """Test that prompt mentions running quality checks (lint, format)."""
    from maid_runner_mcp.prompts.refactor_code import refactor_code

    result = await refactor_code(file_path="src/handler.py", goal="improve quality")
    all_content = str(result).lower()

    # Should mention linting or formatting
    assert (
        "lint" in all_content or "format" in all_content
    ), "Prompt should mention quality checks like lint or format"


@pytest.mark.asyncio
async def test_refactor_code_prompt_has_user_role() -> None:
    """Test that at least one message has the user role."""
    from maid_runner_mcp.prompts.refactor_code import refactor_code

    result = await refactor_code(file_path="src/handler.py", goal="improve quality")

    has_user_role = any(msg.get("role") == "user" for msg in result)
    assert has_user_role, "Prompt should have at least one message with 'user' role"


@pytest.mark.asyncio
async def test_refactor_code_has_required_parameters() -> None:
    """Test that refactor_code has the expected parameters."""
    from maid_runner_mcp.prompts.refactor_code import refactor_code
    import inspect

    sig = inspect.signature(refactor_code)
    params = sig.parameters

    assert "file_path" in params, "refactor_code must have a 'file_path' parameter"
    assert "goal" in params, "refactor_code must have a 'goal' parameter"


@pytest.mark.asyncio
async def test_refactor_code_parameters_are_required() -> None:
    """Test that file_path and goal parameters are required (no defaults)."""
    from maid_runner_mcp.prompts.refactor_code import refactor_code
    import inspect

    sig = inspect.signature(refactor_code)
    params = sig.parameters

    # file_path should be required
    file_path_param = params["file_path"]
    assert (
        file_path_param.default is inspect.Parameter.empty
    ), "file_path parameter should be required (no default)"

    # goal should be required
    goal_param = params["goal"]
    assert (
        goal_param.default is inspect.Parameter.empty
    ), "goal parameter should be required (no default)"


@pytest.mark.asyncio
async def test_refactor_code_prompt_mentions_manifest_compliance() -> None:
    """Test that prompt mentions maintaining manifest compliance."""
    from maid_runner_mcp.prompts.refactor_code import refactor_code

    result = await refactor_code(file_path="src/handler.py", goal="improve quality")
    all_content = str(result).lower()

    # Should mention manifest compliance
    assert "manifest" in all_content, "Prompt should mention manifest compliance"


@pytest.mark.asyncio
async def test_refactor_code_prompt_suggests_validation_after_changes() -> None:
    """Test that prompt suggests validating after each refactoring change."""
    from maid_runner_mcp.prompts.refactor_code import refactor_code

    result = await refactor_code(file_path="src/handler.py", goal="improve quality")
    all_content = str(result).lower()

    # Should mention validating after changes
    assert (
        "after" in all_content or "each" in all_content
    ) and "change" in all_content, "Prompt should suggest validation after changes"
