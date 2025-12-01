"""Behavioral tests for review_manifest MCP prompt (Task 018).

Tests verify that the review_manifest prompt:
1. Accepts 'manifest_path' argument (required)
2. Returns a properly formatted prompt template (list of Message dicts)
3. Contains guidance for MAID Phase 2 Quality Gate - reviewing manifest and tests
4. Includes manifest_path in the prompt content
5. Provides manifest review checklist (goal, files, expectedArtifacts)
6. Provides test review checklist (coverage, behavioral, realistic)
7. Guides on running validations with behavioral mode
8. Mentions approval workflow (provide feedback or approve)
"""

import pytest


@pytest.mark.asyncio
async def test_review_manifest_prompt_returns_messages() -> None:
    """Test that review_manifest returns a list of Message dicts."""
    from maid_runner_mcp.prompts.review_manifest import review_manifest

    result = await review_manifest(manifest_path="manifests/task-001-example.manifest.json")

    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(msg, dict) for msg in result)


@pytest.mark.asyncio
async def test_review_manifest_prompt_includes_manifest_path_in_content() -> None:
    """Test that the manifest_path argument is included in the prompt content."""
    from maid_runner_mcp.prompts.review_manifest import review_manifest

    test_path = "manifests/task-042-special-feature.manifest.json"
    result = await review_manifest(manifest_path=test_path)

    # Find the content containing the manifest_path
    content_found = False
    for msg in result:
        if "content" in msg:
            content = msg["content"]
            if isinstance(content, str) and test_path in content:
                content_found = True
                break
            elif isinstance(content, dict) and test_path in str(content):
                content_found = True
                break

    assert content_found, f"Manifest path '{test_path}' not found in prompt content"


@pytest.mark.asyncio
async def test_review_manifest_prompt_contains_manifest_review_checklist() -> None:
    """Test that prompt includes manifest review checklist.

    The manifest review should cover:
    - Goal is clear and atomic
    - Files properly classified (creatable vs editable)
    - All public APIs in expectedArtifacts
    """
    from maid_runner_mcp.prompts.review_manifest import review_manifest

    result = await review_manifest(manifest_path="manifests/task-001.manifest.json")
    all_content = str(result).lower()

    # Should mention goal review
    assert "goal" in all_content, "Prompt should mention reviewing the goal"

    # Should mention file classification (creatable/editable)
    assert (
        "creatable" in all_content or "editable" in all_content or "file" in all_content
    ), "Prompt should mention file classification review"

    # Should mention expectedArtifacts
    assert (
        "expectedartifacts" in all_content or "artifacts" in all_content
    ), "Prompt should mention expectedArtifacts review"


@pytest.mark.asyncio
async def test_review_manifest_prompt_contains_test_review_checklist() -> None:
    """Test that prompt includes test review checklist.

    The test review should cover:
    - All artifacts have test coverage
    - Tests USE artifacts (not just check existence)
    - Test scenarios are realistic
    """
    from maid_runner_mcp.prompts.review_manifest import review_manifest

    result = await review_manifest(manifest_path="manifests/task-001.manifest.json")
    all_content = str(result).lower()

    # Should mention test coverage
    assert (
        "test" in all_content and "coverage" in all_content
    ) or "test" in all_content, "Prompt should mention test coverage"

    # Should mention behavioral testing (USE artifacts, not just existence)
    assert (
        "use" in all_content or "behavioral" in all_content or "exist" in all_content
    ), "Prompt should mention behavioral testing approach"


@pytest.mark.asyncio
async def test_review_manifest_prompt_mentions_behavioral_validation() -> None:
    """Test that prompt mentions running validation with behavioral mode."""
    from maid_runner_mcp.prompts.review_manifest import review_manifest

    result = await review_manifest(manifest_path="manifests/task-001.manifest.json")
    all_content = str(result).lower()

    # Should mention behavioral validation mode
    assert (
        "behavioral" in all_content or "validation" in all_content
    ), "Prompt should mention behavioral validation mode"

    # Should mention maid validate command
    assert (
        "maid" in all_content and "validate" in all_content
    ) or "maid_validate" in all_content, "Prompt should mention maid validate command"


@pytest.mark.asyncio
async def test_review_manifest_prompt_mentions_pytest() -> None:
    """Test that prompt mentions running pytest to verify tests fail."""
    from maid_runner_mcp.prompts.review_manifest import review_manifest

    result = await review_manifest(manifest_path="manifests/task-001.manifest.json")
    all_content = str(result).lower()

    # Should mention pytest
    assert "pytest" in all_content, "Prompt should mention running pytest"


@pytest.mark.asyncio
async def test_review_manifest_prompt_mentions_approval_workflow() -> None:
    """Test that prompt includes approval/feedback workflow.

    Should mention:
    - Provide feedback if issues found
    - Approve if ready for implementation
    """
    from maid_runner_mcp.prompts.review_manifest import review_manifest

    result = await review_manifest(manifest_path="manifests/task-001.manifest.json")
    all_content = str(result).lower()

    # Should mention approval or feedback
    assert (
        "approv" in all_content or "feedback" in all_content or "issue" in all_content
    ), "Prompt should mention approval/feedback workflow"


@pytest.mark.asyncio
async def test_review_manifest_prompt_has_user_role() -> None:
    """Test that at least one message has the user role."""
    from maid_runner_mcp.prompts.review_manifest import review_manifest

    result = await review_manifest(manifest_path="manifests/task-001.manifest.json")

    has_user_role = any(msg.get("role") == "user" for msg in result)
    assert has_user_role, "Prompt should have at least one message with 'user' role"


@pytest.mark.asyncio
async def test_review_manifest_requires_manifest_path_argument() -> None:
    """Test that review_manifest requires the manifest_path argument."""
    from maid_runner_mcp.prompts.review_manifest import review_manifest
    import inspect

    sig = inspect.signature(review_manifest)
    params = sig.parameters

    assert "manifest_path" in params, "review_manifest must have a 'manifest_path' parameter"

    # Check that manifest_path parameter has no default (is required)
    manifest_path_param = params["manifest_path"]
    assert (
        manifest_path_param.default is inspect.Parameter.empty
    ), "manifest_path parameter should be required (no default)"


@pytest.mark.asyncio
async def test_review_manifest_prompt_mentions_schema_check() -> None:
    """Test that prompt mentions checking the manifest schema."""
    from maid_runner_mcp.prompts.review_manifest import review_manifest

    result = await review_manifest(manifest_path="manifests/task-001.manifest.json")
    all_content = str(result).lower()

    # Should mention schema check
    assert "schema" in all_content, "Prompt should mention checking the manifest schema"


@pytest.mark.asyncio
async def test_review_manifest_prompt_mentions_quality_gate() -> None:
    """Test that prompt identifies this as Phase 2 Quality Gate."""
    from maid_runner_mcp.prompts.review_manifest import review_manifest

    result = await review_manifest(manifest_path="manifests/task-001.manifest.json")
    all_content = str(result).lower()

    # Should mention quality gate or phase 2
    assert (
        "quality" in all_content or "phase" in all_content or "gate" in all_content
    ), "Prompt should identify this as Phase 2 Quality Gate"


@pytest.mark.asyncio
async def test_review_manifest_prompt_mentions_manifest_chain() -> None:
    """Test that prompt mentions using manifest chain validation."""
    from maid_runner_mcp.prompts.review_manifest import review_manifest

    result = await review_manifest(manifest_path="manifests/task-001.manifest.json")
    all_content = str(result).lower()

    # Should mention manifest chain flag
    assert (
        "manifest-chain" in all_content
        or "use-manifest-chain" in all_content
        or "chain" in all_content
    ), "Prompt should mention using manifest chain validation"
