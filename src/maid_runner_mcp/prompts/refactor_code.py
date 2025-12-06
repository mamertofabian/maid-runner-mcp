"""MCP prompt for MAID Phase 3.5 refactoring guidance.

Provides a structured prompt template to guide AI agents through
code quality improvements while maintaining test compliance.
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
async def refactor_code(file_path: str, goal: str) -> list[Message]:
    """Guide AI agents through MAID Phase 3.5 code refactoring while maintaining test compliance."""
    content = f"""# Phase 3.5: Refactoring

Improve code quality for: `{file_path}`

**Refactoring Goal:** {goal}

---

## Your Task

### 1. Ensure tests pass first

Before making any changes, verify current tests are passing:

```bash
pytest tests/test_task_XXX_*.py -v
```

If tests fail, fix them before proceeding with refactoring.

### 2. Refactor code

Apply clean code principles to improve the target file:

- **Remove duplication** - Extract common logic into helper functions
- **Improve naming** - Use clear, descriptive names for variables and functions
- **Enhance readability** - Simplify complex logic, add comments where helpful
- **Keep public API unchanged** - Do not modify function signatures or class interfaces

Focus on internal improvements that maintain the existing behavior.

### 3. CRITICAL - Validate after each change

After every refactoring change, run validation to ensure tests still pass:

```bash
pytest tests/test_task_XXX_*.py -v
maid validate
maid test
```

**Note**: Run `maid validate` and `maid test` WITHOUT arguments to validate the entire codebase.

### 4. Run all quality checks

After refactoring is complete, ensure code quality standards are met:

```bash
make lint
make format
make type-check
```

---

## Key Reminders

| Principle | Description |
|-----------|-------------|
| **Tests First** | Always ensure tests pass before and after each change |
| **Small Steps** | Make incremental changes, validate frequently |
| **Public API** | Never change public function signatures or class interfaces |
| **Manifest Compliance** | Keep implementation aligned with manifest artifacts |

---

## Common Refactoring Patterns

1. **Extract Method** - Move duplicated code into a shared helper function
2. **Rename Variable** - Use more descriptive names for clarity
3. **Simplify Conditional** - Replace complex if/else chains with guard clauses
4. **Extract Constant** - Replace magic numbers with named constants
5. **Reduce Parameters** - Group related parameters into objects

---

## Success Criteria

- Tests still pass after all changes
- All manifest compliance maintained
- Code quality improved (readability, maintainability)
- Quality checks pass (lint, format, type-check)
"""

    return [_Message(role="user", content=content)]
