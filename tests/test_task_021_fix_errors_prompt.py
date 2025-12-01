"""Behavioral tests for fix_errors MCP prompt (Task 021).

Tests verify that the fix_errors prompt:
1. Accepts an optional 'error_context' argument with default empty string
2. Returns a properly formatted prompt template (list of Message dicts)
3. Contains guidance for MAID Phase 3 Support - fixing validation errors
4. Guides on collecting errors via maid validate and maid test
5. Guides on fixing one issue at a time
6. Emphasizes validating ALL manifests after each fix
7. Includes error_context in prompt when provided
"""

import inspect

import pytest


@pytest.mark.asyncio
async def test_fix_errors_prompt_returns_messages() -> None:
    """Test that fix_errors returns a list of Message dicts."""
    from maid_runner_mcp.prompts.fix_errors import fix_errors

    result = await fix_errors()

    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(msg, dict) for msg in result)


@pytest.mark.asyncio
async def test_fix_errors_prompt_returns_messages_with_error_context() -> None:
    """Test that fix_errors returns a list of Message dicts when error_context is provided."""
    from maid_runner_mcp.prompts.fix_errors import fix_errors

    result = await fix_errors(error_context="ImportError: No module named 'foo'")

    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(msg, dict) for msg in result)


@pytest.mark.asyncio
async def test_fix_errors_prompt_includes_error_context_in_content() -> None:
    """Test that the error_context argument is included in the prompt content when provided."""
    from maid_runner_mcp.prompts.fix_errors import fix_errors

    test_error = "AssertionError: expected True but got False in test_foo"
    result = await fix_errors(error_context=test_error)

    # Find the content containing the error context
    content_found = False
    for msg in result:
        if "content" in msg:
            content = msg["content"]
            if isinstance(content, str) and test_error in content:
                content_found = True
                break
            elif isinstance(content, dict) and test_error in str(content):
                content_found = True
                break

    assert content_found, f"Error context '{test_error}' not found in prompt content"


@pytest.mark.asyncio
async def test_fix_errors_prompt_handles_empty_error_context() -> None:
    """Test that prompt handles empty error_context gracefully."""
    from maid_runner_mcp.prompts.fix_errors import fix_errors

    # Should not raise an error with empty error_context (default)
    result = await fix_errors(error_context="")

    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_fix_errors_prompt_contains_error_collection_guidance() -> None:
    """Test that prompt includes guidance for collecting errors.

    The guidance should mention:
    - maid validate command
    - maid test command
    """
    from maid_runner_mcp.prompts.fix_errors import fix_errors

    result = await fix_errors()
    all_content = str(result).lower()

    # Should mention maid validate
    assert (
        "maid validate" in all_content or "maid_validate" in all_content
    ), "Prompt should mention maid validate for collecting errors"

    # Should mention maid test
    assert (
        "maid test" in all_content or "maid_test" in all_content
    ), "Prompt should mention maid test for collecting errors"


@pytest.mark.asyncio
async def test_fix_errors_prompt_contains_one_at_a_time_guidance() -> None:
    """Test that prompt guides fixing one issue at a time.

    The guidance should mention:
    - Fixing one issue at a time
    - Analyzing error message
    - Checking manifest for expected artifact
    - Making targeted fix
    """
    from maid_runner_mcp.prompts.fix_errors import fix_errors

    result = await fix_errors()
    all_content = str(result).lower()

    # Should mention fixing one at a time or targeted/focused approach
    assert (
        (
            "one" in all_content
            and ("issue" in all_content or "error" in all_content or "time" in all_content)
        )
        or "targeted" in all_content
        or "focus" in all_content
    ), "Prompt should guide fixing one issue at a time"

    # Should mention analyzing error
    assert (
        "analyz" in all_content or "error message" in all_content
    ), "Prompt should mention analyzing error messages"


@pytest.mark.asyncio
async def test_fix_errors_prompt_contains_manifest_check_guidance() -> None:
    """Test that prompt guides checking manifest for expected artifacts."""
    from maid_runner_mcp.prompts.fix_errors import fix_errors

    result = await fix_errors()
    all_content = str(result).lower()

    # Should mention checking manifest
    assert "manifest" in all_content, "Prompt should mention checking manifest"

    # Should mention expected artifact or artifact
    assert (
        "artifact" in all_content or "expected" in all_content
    ), "Prompt should mention checking for expected artifacts"


@pytest.mark.asyncio
async def test_fix_errors_prompt_emphasizes_validate_after_each_fix() -> None:
    """Test that prompt emphasizes validating ALL manifests after each fix.

    This is a CRITICAL step in the error fixing workflow.
    """
    from maid_runner_mcp.prompts.fix_errors import fix_errors

    result = await fix_errors()
    all_content = str(result).lower()

    # Should mention validating after each fix
    assert "validat" in all_content, "Prompt should mention validation"

    # Should mention "all" or "entire" in context of validation
    assert (
        "all" in all_content or "entire" in all_content or "each" in all_content
    ), "Prompt should emphasize validating all manifests or after each fix"


@pytest.mark.asyncio
async def test_fix_errors_prompt_contains_iteration_guidance() -> None:
    """Test that prompt guides iterating until all errors resolved."""
    from maid_runner_mcp.prompts.fix_errors import fix_errors

    result = await fix_errors()
    all_content = str(result).lower()

    # Should mention iteration or repeating
    assert (
        "repeat" in all_content
        or "iter" in all_content
        or "until" in all_content
        or "loop" in all_content
    ), "Prompt should guide iterating until errors are resolved"


@pytest.mark.asyncio
async def test_fix_errors_prompt_has_user_role() -> None:
    """Test that at least one message has the user role."""
    from maid_runner_mcp.prompts.fix_errors import fix_errors

    result = await fix_errors()

    has_user_role = any(msg.get("role") == "user" for msg in result)
    assert has_user_role, "Prompt should have at least one message with 'user' role"


@pytest.mark.asyncio
async def test_fix_errors_has_optional_error_context_parameter() -> None:
    """Test that fix_errors has an optional error_context parameter with default empty string."""
    from maid_runner_mcp.prompts.fix_errors import fix_errors

    sig = inspect.signature(fix_errors)
    params = sig.parameters

    assert "error_context" in params, "fix_errors must have an 'error_context' parameter"

    # Check that error_context parameter has a default value of ""
    error_context_param = params["error_context"]
    assert (
        error_context_param.default == ""
    ), "error_context parameter should have default value of empty string"


@pytest.mark.asyncio
async def test_fix_errors_can_be_called_without_arguments() -> None:
    """Test that fix_errors can be called without any arguments."""
    from maid_runner_mcp.prompts.fix_errors import fix_errors

    # Should not raise an error when called without arguments
    result = await fix_errors()

    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_fix_errors_prompt_mentions_success_criteria() -> None:
    """Test that prompt mentions success criteria.

    Success should include:
    - All validations pass
    - All tests pass
    - No new errors introduced
    """
    from maid_runner_mcp.prompts.fix_errors import fix_errors

    result = await fix_errors()
    all_content = str(result).lower()

    # Should mention success or pass
    assert (
        "success" in all_content or "pass" in all_content or "resolve" in all_content
    ), "Prompt should mention success criteria or passing tests"
