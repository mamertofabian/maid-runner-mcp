"""Behavioral tests for audit_compliance MCP prompt (Task 022).

Tests verify that the audit_compliance prompt:
1. Accepts 'manifest_path' (optional, defaults to "") and 'scope' (optional, defaults to "all") arguments
2. Returns a properly formatted prompt template (list of Message dicts)
3. Contains guidance for cross-cutting MAID compliance auditing
4. Includes validation commands (maid validate, maid test)
5. Provides guidance on categorizing violations by severity
6. Includes remediation guidance
"""

import inspect

import pytest


@pytest.mark.asyncio
async def test_audit_compliance_prompt_returns_messages() -> None:
    """Test that audit_compliance returns a list of Message dicts."""
    from maid_runner_mcp.prompts.audit_compliance import audit_compliance

    result = await audit_compliance()

    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(msg, dict) for msg in result)


@pytest.mark.asyncio
async def test_audit_compliance_prompt_with_no_args() -> None:
    """Test that audit_compliance works with no arguments (uses defaults)."""
    from maid_runner_mcp.prompts.audit_compliance import audit_compliance

    result = await audit_compliance()

    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_audit_compliance_prompt_with_manifest_path_only() -> None:
    """Test that audit_compliance works with manifest_path argument only."""
    from maid_runner_mcp.prompts.audit_compliance import audit_compliance

    test_manifest_path = "manifests/task-001-example.manifest.json"
    result = await audit_compliance(manifest_path=test_manifest_path)

    assert isinstance(result, list)
    assert len(result) > 0

    # The manifest path should be included in the content
    all_content = str(result)
    assert (
        test_manifest_path in all_content
    ), f"Manifest path '{test_manifest_path}' should be in prompt content"


@pytest.mark.asyncio
async def test_audit_compliance_prompt_with_scope_only() -> None:
    """Test that audit_compliance works with scope argument only."""
    from maid_runner_mcp.prompts.audit_compliance import audit_compliance

    test_scope = "tests"
    result = await audit_compliance(scope=test_scope)

    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_audit_compliance_prompt_with_both_args() -> None:
    """Test that audit_compliance works with both arguments."""
    from maid_runner_mcp.prompts.audit_compliance import audit_compliance

    test_manifest_path = "manifests/task-022-audit-compliance-prompt.manifest.json"
    test_scope = "implementation"
    result = await audit_compliance(manifest_path=test_manifest_path, scope=test_scope)

    assert isinstance(result, list)
    assert len(result) > 0

    # Both arguments should be reflected in the content
    all_content = str(result)
    assert (
        test_manifest_path in all_content
    ), f"Manifest path '{test_manifest_path}' should be in prompt content"


@pytest.mark.asyncio
async def test_audit_compliance_has_optional_parameters_with_defaults() -> None:
    """Test that audit_compliance has optional parameters with correct defaults."""
    from maid_runner_mcp.prompts.audit_compliance import audit_compliance

    sig = inspect.signature(audit_compliance)
    params = sig.parameters

    # Check manifest_path parameter
    assert "manifest_path" in params, "audit_compliance must have a 'manifest_path' parameter"
    manifest_path_param = params["manifest_path"]
    assert (
        manifest_path_param.default == ""
    ), "manifest_path parameter should default to empty string"

    # Check scope parameter
    assert "scope" in params, "audit_compliance must have a 'scope' parameter"
    scope_param = params["scope"]
    assert scope_param.default == "all", "scope parameter should default to 'all'"


@pytest.mark.asyncio
async def test_audit_compliance_prompt_contains_validation_commands() -> None:
    """Test that prompt includes maid validate and maid test commands.

    The guidance should mention:
    - maid validate (without arguments for full codebase)
    - maid test (without arguments for full codebase)
    """
    from maid_runner_mcp.prompts.audit_compliance import audit_compliance

    result = await audit_compliance()
    all_content = str(result).lower()

    # Should mention maid validate
    assert (
        "maid validate" in all_content or "maid_validate" in all_content
    ), "Prompt should mention 'maid validate' command"

    # Should mention maid test
    assert (
        "maid test" in all_content or "maid_test" in all_content
    ), "Prompt should mention 'maid test' command"


@pytest.mark.asyncio
async def test_audit_compliance_prompt_contains_violation_types() -> None:
    """Test that prompt includes guidance on types of violations to check.

    Should mention checking for:
    - Public APIs not in manifest
    - Tests that don't USE artifacts
    - TODO/FIXME/debug in code
    - Files accessed outside manifest
    """
    from maid_runner_mcp.prompts.audit_compliance import audit_compliance

    result = await audit_compliance()
    all_content = str(result).lower()

    # Should mention violations or compliance issues
    assert (
        "violation" in all_content or "compliance" in all_content
    ), "Prompt should mention violations or compliance"

    # Should mention manifest
    assert "manifest" in all_content, "Prompt should mention manifest"


@pytest.mark.asyncio
async def test_audit_compliance_prompt_contains_severity_categories() -> None:
    """Test that prompt includes severity categories for issues.

    The guidance should mention severity levels:
    - CRITICAL: Must fix
    - HIGH: Should fix immediately
    - MEDIUM: Should address
    - LOW: Nice to have
    """
    from maid_runner_mcp.prompts.audit_compliance import audit_compliance

    result = await audit_compliance()
    all_content = str(result).lower()

    # Should mention severity levels
    assert "critical" in all_content, "Prompt should mention CRITICAL severity"
    assert "high" in all_content, "Prompt should mention HIGH severity"

    # Should have some form of categorization guidance
    assert (
        "severity" in all_content or "categorize" in all_content or "priority" in all_content
    ), "Prompt should provide categorization guidance"


@pytest.mark.asyncio
async def test_audit_compliance_prompt_contains_remediation_guidance() -> None:
    """Test that prompt includes remediation guidance."""
    from maid_runner_mcp.prompts.audit_compliance import audit_compliance

    result = await audit_compliance()
    all_content = str(result).lower()

    # Should mention remediation or fixing issues
    assert (
        "remediat" in all_content
        or "fix" in all_content
        or "address" in all_content
        or "resolve" in all_content
    ), "Prompt should include remediation guidance"


@pytest.mark.asyncio
async def test_audit_compliance_prompt_has_user_role() -> None:
    """Test that at least one message has the user role."""
    from maid_runner_mcp.prompts.audit_compliance import audit_compliance

    result = await audit_compliance()

    has_user_role = any(msg.get("role") == "user" for msg in result)
    assert has_user_role, "Prompt should have at least one message with 'user' role"


@pytest.mark.asyncio
async def test_audit_compliance_prompt_mentions_file_references() -> None:
    """Test that prompt mentions providing specific file:line references."""
    from maid_runner_mcp.prompts.audit_compliance import audit_compliance

    result = await audit_compliance()
    all_content = str(result).lower()

    # Should mention file references or line numbers
    assert (
        "file" in all_content and "line" in all_content
    ) or "reference" in all_content, "Prompt should mention providing specific file:line references"


@pytest.mark.asyncio
async def test_audit_compliance_prompt_scope_all() -> None:
    """Test that 'all' scope provides comprehensive audit guidance."""
    from maid_runner_mcp.prompts.audit_compliance import audit_compliance

    result = await audit_compliance(scope="all")
    all_content = str(result).lower()

    # Should mention comprehensive or full audit
    assert (
        "all" in all_content
        or "entire" in all_content
        or "comprehensive" in all_content
        or "full" in all_content
    ), "Prompt with 'all' scope should mention comprehensive audit"


@pytest.mark.asyncio
async def test_audit_compliance_prompt_mentions_maid_methodology() -> None:
    """Test that prompt references MAID methodology."""
    from maid_runner_mcp.prompts.audit_compliance import audit_compliance

    result = await audit_compliance()
    all_content = str(result)

    # Should mention MAID
    assert (
        "MAID" in all_content or "maid" in all_content.lower()
    ), "Prompt should reference MAID methodology"


@pytest.mark.asyncio
async def test_audit_compliance_prompt_mentions_compliance_status() -> None:
    """Test that prompt includes guidance on determining compliance status."""
    from maid_runner_mcp.prompts.audit_compliance import audit_compliance

    result = await audit_compliance()
    all_content = str(result).lower()

    # Should mention compliance status or determination
    assert (
        "compliance" in all_content or "status" in all_content
    ), "Prompt should mention determining compliance status"
