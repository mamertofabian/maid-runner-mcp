"""Behavioral tests for spike_idea MCP prompt (Task 015).

Tests verify that the spike_idea prompt:
1. Accepts an 'idea' argument (required)
2. Returns a properly formatted prompt template (list of Message dicts)
3. Contains all 5 spike exploration guidance steps
4. Reminds about expectedArtifacts being an OBJECT for ONE file only
5. Guides on multi-task vs single-task decision
"""

import pytest


@pytest.mark.asyncio
async def test_spike_idea_prompt_returns_messages() -> None:
    """Test that spike_idea returns a list of Message dicts."""
    from maid_runner_mcp.prompts.spike_idea import spike_idea

    result = await spike_idea(idea="implement user authentication")

    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(msg, dict) for msg in result)


@pytest.mark.asyncio
async def test_spike_idea_prompt_includes_idea_in_content() -> None:
    """Test that the idea argument is included in the prompt content."""
    from maid_runner_mcp.prompts.spike_idea import spike_idea

    test_idea = "add caching layer for database queries"
    result = await spike_idea(idea=test_idea)

    # Find the content containing the idea
    content_found = False
    for msg in result:
        if "content" in msg:
            content = msg["content"]
            if isinstance(content, str) and test_idea in content:
                content_found = True
                break
            elif isinstance(content, dict) and test_idea in str(content):
                content_found = True
                break

    assert content_found, f"Idea '{test_idea}' not found in prompt content"


@pytest.mark.asyncio
async def test_spike_idea_prompt_contains_five_exploration_steps() -> None:
    """Test that prompt includes all 5 spike exploration guidance steps.

    The 5 steps from spike.md are:
    1. Research codebase for related patterns
    2. Identify affected files and components
    3. Outline potential approach
    4. Estimate complexity and scope
    5. Suggest whether this should be one task or multiple
    """
    from maid_runner_mcp.prompts.spike_idea import spike_idea

    result = await spike_idea(idea="test feature")
    all_content = str(result).lower()

    # Step 1: Research codebase
    assert (
        "codebase" in all_content or "research" in all_content
    ), "Prompt should mention researching the codebase"

    # Step 2: Identify affected files
    assert "file" in all_content and (
        "identify" in all_content or "affected" in all_content or "component" in all_content
    ), "Prompt should mention identifying affected files/components"

    # Step 3: Outline approach
    assert (
        "approach" in all_content or "potential" in all_content
    ), "Prompt should mention outlining the approach"

    # Step 4: Estimate complexity/scope
    assert (
        "complexity" in all_content or "scope" in all_content or "estimate" in all_content
    ), "Prompt should mention estimating complexity or scope"

    # Step 5: Multi-task suggestion
    assert "task" in all_content and (
        "multiple" in all_content or "one" in all_content
    ), "Prompt should guide on whether to use one or multiple tasks"


@pytest.mark.asyncio
async def test_spike_idea_prompt_contains_manifest_reminder() -> None:
    """Test that prompt includes the expectedArtifacts OBJECT reminder.

    The critical reminder should mention:
    - expectedArtifacts is an OBJECT (not an array)
    - It defines artifacts for ONE file only
    """
    from maid_runner_mcp.prompts.spike_idea import spike_idea

    result = await spike_idea(idea="test feature")
    all_content = str(result)

    # Check for the critical reminder about expectedArtifacts being an OBJECT
    assert "expectedArtifacts" in all_content, "Prompt should mention 'expectedArtifacts'"
    assert (
        "OBJECT" in all_content or "object" in all_content.lower()
    ), "Prompt should mention that expectedArtifacts is an OBJECT"
    assert (
        "ONE file" in all_content or "one file" in all_content.lower()
    ), "Prompt should mention that expectedArtifacts is for ONE file only"


@pytest.mark.asyncio
async def test_spike_idea_prompt_warns_about_multi_file_features() -> None:
    """Test that prompt reminds about separate manifests for multi-file features."""
    from maid_runner_mcp.prompts.spike_idea import spike_idea

    result = await spike_idea(idea="test feature")
    all_content = str(result).lower()

    # Should mention creating separate manifests for multi-file features
    assert (
        "separate" in all_content or "multi" in all_content
    ), "Prompt should mention handling multi-file features with separate manifests"
    assert "manifest" in all_content, "Prompt should mention manifests in the guidance"


@pytest.mark.asyncio
async def test_spike_idea_prompt_has_user_role() -> None:
    """Test that at least one message has the user role."""
    from maid_runner_mcp.prompts.spike_idea import spike_idea

    result = await spike_idea(idea="test feature")

    has_user_role = any(msg.get("role") == "user" for msg in result)
    assert has_user_role, "Prompt should have at least one message with 'user' role"


@pytest.mark.asyncio
async def test_spike_idea_requires_idea_argument() -> None:
    """Test that spike_idea requires the idea argument."""
    from maid_runner_mcp.prompts.spike_idea import spike_idea
    import inspect

    sig = inspect.signature(spike_idea)
    params = sig.parameters

    assert "idea" in params, "spike_idea must have an 'idea' parameter"

    # Check that idea parameter has no default (is required)
    idea_param = params["idea"]
    assert (
        idea_param.default is inspect.Parameter.empty
    ), "idea parameter should be required (no default)"


@pytest.mark.asyncio
async def test_spike_idea_prompt_suggests_next_steps() -> None:
    """Test that prompt includes guidance for next steps after spike."""
    from maid_runner_mcp.prompts.spike_idea import spike_idea

    result = await spike_idea(idea="test feature")
    all_content = str(result).lower()

    # Should mention next steps or recommendations
    assert (
        "next" in all_content or "recommend" in all_content or "summary" in all_content
    ), "Prompt should include guidance for next steps"
