"""Behavioral tests for design_tests MCP prompt (Task 017).

Tests verify that the design_tests prompt:
1. Accepts 'manifest_path' argument (required)
2. Returns a properly formatted prompt template (list of Message dicts)
3. Contains guidance for MAID Phase 2 behavioral test creation workflow
4. Includes manifest_path in the prompt content
5. Guides on importing and USING artifacts (not just existence checks)
6. Explains the Red phase (tests should fail initially)
7. Mentions maid validate with behavioral mode
"""

import pytest


@pytest.mark.asyncio
async def test_design_tests_prompt_returns_messages() -> None:
    """Test that design_tests returns a list of Message dicts."""
    from maid_runner_mcp.prompts.design_tests import design_tests

    result = await design_tests(
        manifest_path="manifests/task-017-design-tests-prompt.manifest.json"
    )

    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(msg, dict) for msg in result)


@pytest.mark.asyncio
async def test_design_tests_prompt_includes_manifest_path_in_content() -> None:
    """Test that the manifest_path argument is included in the prompt content."""
    from maid_runner_mcp.prompts.design_tests import design_tests

    test_manifest_path = "manifests/task-042-custom-feature.manifest.json"
    result = await design_tests(manifest_path=test_manifest_path)

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
async def test_design_tests_prompt_contains_phase2_workflow_guidance() -> None:
    """Test that prompt includes MAID Phase 2 behavioral test creation guidance.

    The guidance should cover:
    1. Read manifest to understand artifacts
    2. Create test files in tests/ directory
    3. Import and USE each artifact
    4. Validate with behavioral mode
    5. Verify Red phase (tests should fail)
    """
    from maid_runner_mcp.prompts.design_tests import design_tests

    result = await design_tests(manifest_path="manifests/task-001-example.manifest.json")
    all_content = str(result).lower()

    # Should mention reading/understanding the manifest
    assert "manifest" in all_content, "Prompt should mention reading the manifest"

    # Should mention creating tests
    assert "test" in all_content, "Prompt should mention creating tests"

    # Should mention behavioral validation or using artifacts
    assert (
        "behavioral" in all_content or "use" in all_content
    ), "Prompt should mention behavioral testing or using artifacts"


@pytest.mark.asyncio
async def test_design_tests_prompt_emphasizes_using_artifacts() -> None:
    """Test that prompt emphasizes USING artifacts, not just checking existence.

    The prompt should guide the agent to:
    - Import and call functions
    - Instantiate classes
    - Test with realistic scenarios
    - NOT just check if artifacts exist
    """
    from maid_runner_mcp.prompts.design_tests import design_tests

    result = await design_tests(manifest_path="manifests/task-001-example.manifest.json")
    all_content = str(result).lower()

    # Should mention importing artifacts
    assert "import" in all_content, "Prompt should mention importing artifacts"

    # Should mention calling/using artifacts
    assert (
        "call" in all_content or "use" in all_content or "invoke" in all_content
    ), "Prompt should mention calling/using artifacts"


@pytest.mark.asyncio
async def test_design_tests_prompt_mentions_red_phase() -> None:
    """Test that prompt explains the Red phase of TDD.

    The prompt should explain:
    - Tests should fail initially (Red phase)
    - Expected failures are ImportError or ModuleNotFoundError
    - This confirms tests are properly written before implementation
    """
    from maid_runner_mcp.prompts.design_tests import design_tests

    result = await design_tests(manifest_path="manifests/task-001-example.manifest.json")
    all_content = str(result).lower()

    # Should mention tests failing or red phase
    assert (
        "fail" in all_content or "red" in all_content
    ), "Prompt should mention tests should fail (Red phase)"


@pytest.mark.asyncio
async def test_design_tests_prompt_mentions_maid_validate_behavioral() -> None:
    """Test that prompt mentions using maid_validate with behavioral mode."""
    from maid_runner_mcp.prompts.design_tests import design_tests

    result = await design_tests(manifest_path="manifests/task-001-example.manifest.json")
    all_content = str(result).lower()

    # Should mention maid validate or maid_validate
    assert (
        "maid_validate" in all_content or "maid validate" in all_content
    ), "Prompt should mention maid_validate"

    # Should mention behavioral mode
    assert "behavioral" in all_content, "Prompt should mention behavioral validation mode"


@pytest.mark.asyncio
async def test_design_tests_prompt_mentions_test_file_naming() -> None:
    """Test that prompt mentions proper test file naming convention."""
    from maid_runner_mcp.prompts.design_tests import design_tests

    result = await design_tests(manifest_path="manifests/task-001-example.manifest.json")
    all_content = str(result).lower()

    # Should mention test file naming like test_task_XXX
    assert (
        "test_task" in all_content or "tests/" in all_content
    ), "Prompt should mention test file naming convention or tests directory"


@pytest.mark.asyncio
async def test_design_tests_prompt_has_user_role() -> None:
    """Test that at least one message has the user role."""
    from maid_runner_mcp.prompts.design_tests import design_tests

    result = await design_tests(manifest_path="manifests/task-001-example.manifest.json")

    has_user_role = any(msg.get("role") == "user" for msg in result)
    assert has_user_role, "Prompt should have at least one message with 'user' role"


@pytest.mark.asyncio
async def test_design_tests_requires_manifest_path_argument() -> None:
    """Test that design_tests requires the manifest_path argument."""
    from maid_runner_mcp.prompts.design_tests import design_tests
    import inspect

    sig = inspect.signature(design_tests)
    params = sig.parameters

    assert "manifest_path" in params, "design_tests must have a 'manifest_path' parameter"

    # Check that manifest_path parameter has no default (is required)
    manifest_path_param = params["manifest_path"]
    assert (
        manifest_path_param.default is inspect.Parameter.empty
    ), "manifest_path parameter should be required (no default)"


@pytest.mark.asyncio
async def test_design_tests_prompt_mentions_coverage_of_parameters() -> None:
    """Test that prompt mentions covering all parameters from manifest."""
    from maid_runner_mcp.prompts.design_tests import design_tests

    result = await design_tests(manifest_path="manifests/task-001-example.manifest.json")
    all_content = str(result).lower()

    # Should mention covering parameters or arguments
    assert (
        "parameter" in all_content or "argument" in all_content or "arg" in all_content
    ), "Prompt should mention covering parameters from manifest"


@pytest.mark.asyncio
async def test_design_tests_prompt_mentions_realistic_scenarios() -> None:
    """Test that prompt mentions using realistic test scenarios."""
    from maid_runner_mcp.prompts.design_tests import design_tests

    result = await design_tests(manifest_path="manifests/task-001-example.manifest.json")
    all_content = str(result).lower()

    # Should mention realistic scenarios or not just existence checks
    assert (
        "realistic" in all_content or "scenario" in all_content or "existence" in all_content
    ), "Prompt should mention realistic scenarios or warn against existence-only checks"


@pytest.mark.asyncio
async def test_design_tests_prompt_mentions_expected_artifacts() -> None:
    """Test that prompt mentions expectedArtifacts from manifest."""
    from maid_runner_mcp.prompts.design_tests import design_tests

    result = await design_tests(manifest_path="manifests/task-001-example.manifest.json")
    all_content = str(result).lower()

    # Should mention expectedArtifacts or artifacts
    assert (
        "expectedartifacts" in all_content or "artifact" in all_content
    ), "Prompt should mention expectedArtifacts from manifest"
