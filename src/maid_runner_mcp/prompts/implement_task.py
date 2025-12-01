"""MCP prompt for MAID Phase 3 implementation (TDD).

Provides a structured prompt template to guide AI agents through
implementing code to make tests pass following Red-Green-Refactor.
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
async def implement_task(manifest_path: str) -> list[Message]:
    """MCP prompt handler that returns an implementation guide for Phase 3 TDD workflow.

    Guides AI agents through MAID Phase 3 (Implementation) following TDD principles.
    The implementation must make tests pass while matching manifest artifacts exactly.

    Args:
        manifest_path: Path to the manifest file for the task being implemented

    Returns:
        A list of Message dicts containing the implementation guidance template
    """
    content = f"""# Phase 3: Implementation (TDD)

Implement code to make tests pass. Follow Red-Green-Refactor. See CLAUDE.md for details.

**Manifest:** `{manifest_path}`

## Your Task

1. **Confirm Red phase**: Run the tests to verify they fail initially
   ```bash
   pytest tests/test_task_XXX_*.py -v
   ```
   (Tests should fail - this confirms the Red phase)

2. **Implement code** (Green phase):
   - Make tests pass
   - Match manifest artifacts exactly
   - Only edit files listed in the manifest

3. **CRITICAL - Validate ALL manifests (no arguments)**:
   ```bash
   maid validate
   maid test
   make lint
   make type-check
   make test
   ```
   **Note**: `maid validate` and `maid test` WITHOUT arguments validates entire codebase

4. **Refactor** if needed while keeping tests green

---

## Implementation Guidelines

### File Restrictions
- Only edit files declared in `editableFiles` or `creatableFiles` from the manifest
- Reference `readonlyFiles` but do not modify them
- Check the manifest at `{manifest_path}` for the exact file list

### Matching Manifest Artifacts
- Implementation must include all artifacts declared in `expectedArtifacts`
- For `creatableFiles`: strict validation (exact match required)
- For `editableFiles`: permissive validation (must contain at least the declared artifacts)
- Public artifacts (no `_` prefix) MUST be in manifest
- Private artifacts (`_` prefix) are optional

### Red-Green-Refactor Cycle

1. **Red**: Tests fail (starting point)
2. **Green**: Write minimum code to make tests pass
3. **Refactor**: Improve code quality while keeping tests green

---

## Validation Commands

Run these commands to verify your implementation:

```bash
# Validate the specific manifest
maid validate {manifest_path} --use-manifest-chain

# Run the task tests
maid test

# Code quality checks
make lint          # Run linter
make type-check    # Run type checker
make test          # Run all tests
```

---

## Success Criteria

Your implementation is complete when:

- All tests pass (Green phase achieved)
- All validations pass (`maid validate` succeeds)
- All code quality checks pass (`make lint`, `make type-check`)
- Manifest artifacts are properly implemented
- Code is refactored for clarity and maintainability
"""

    return [_Message(role="user", content=content)]
