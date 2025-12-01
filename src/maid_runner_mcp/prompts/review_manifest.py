"""MCP prompt for MAID Phase 2 Quality Gate.

Provides a structured prompt template to guide AI agents through
reviewing manifest and tests before implementation begins.
"""

from __future__ import annotations

from typing import TypedDict

from maid_runner_mcp.server import mcp


class _Message(TypedDict):
    """A message in the prompt template.

    Used as a lightweight alternative to MCP's Message class for prompts
    that return simple role/content pairs.
    """

    role: str
    content: str


# Type alias for external reference (used in type annotations)
Message = _Message


@mcp.prompt()
async def review_manifest(manifest_path: str) -> list[Message]:
    """MCP prompt handler that returns a review template for validating manifest and tests quality before implementation.

    Guides AI agents through MAID Phase 2 Quality Gate - reviewing the manifest
    and tests before implementation begins. This ensures the plan is solid
    before committing to code changes.

    Args:
        manifest_path: Path to the manifest file to review

    Returns:
        A list of Message dicts containing the review template
    """
    content = f"""# Phase 2 Quality Gate: Plan Review

Review the manifest and tests for quality before implementation begins.

**Manifest to Review:** `{manifest_path}`

---

## Step 1: Review the Manifest

Check the following aspects of the manifest:

### Goal Review
- [ ] Goal is clear and atomic (single-purpose)
- [ ] Goal describes WHAT will be achieved, not HOW

### File Classification Review
- [ ] Files properly classified as `creatableFiles` (new) vs `editableFiles` (existing)
- [ ] All dependencies listed in `readonlyFiles`
- [ ] Test files included in `readonlyFiles`

### Expected Artifacts Review
- [ ] All public APIs are declared in `expectedArtifacts`
- [ ] Artifact types are correct (function, class, attribute)
- [ ] Argument types and return types are specified
- [ ] Private artifacts (prefixed with `_`) are optional

### Schema Compliance
- [ ] Manifest follows the current schema
- [ ] Run `maid schema` to verify schema requirements

---

## Step 2: Review the Tests

Check the test file(s) associated with this manifest:

### Test Coverage
- [ ] All artifacts declared in `expectedArtifacts` have test coverage
- [ ] Tests USE the artifacts (behavioral tests), not just check existence
- [ ] Test scenarios are realistic and meaningful

### Test Quality
- [ ] Tests will FAIL before implementation (Red phase)
- [ ] Tests import from the correct module paths
- [ ] Tests follow pytest conventions

---

## Step 3: Run Validations

**CRITICAL** - Run these validations with behavioral mode:

```bash
# Validate manifest structure and schema
maid validate {manifest_path} --validation-mode behavioral --use-manifest-chain

# Run tests to verify they fail (Red phase)
pytest tests/test_task_XXX_*.py -v
```

The validation should:
- Pass schema checks
- Verify file classifications
- Confirm test file exists

The pytest run should:
- Show tests FAILING (expected before implementation)
- Confirm tests are syntactically correct

---

## Step 4: Provide Feedback or Approve

Based on your review:

### If Issues Found
Provide specific feedback on:
- What needs to be fixed in the manifest
- What needs to be improved in the tests
- Suggest specific changes

### If Ready for Implementation
Approve the plan and confirm:
- Manifest is complete and correct
- Tests are comprehensive and behavioral
- Ready to proceed to Phase 3 (Implementation)

---

## Quality Gate Checklist Summary

- [ ] Behavioral validation passes (`maid validate ... --use-manifest-chain`)
- [ ] Tests fail appropriately (Red phase confirmed)
- [ ] Plan approved for implementation

---

**Note:** This is Phase 2 of the MAID workflow. Only proceed to implementation
after this quality gate review is complete and approved.
"""

    return [_Message(role="user", content=content)]
