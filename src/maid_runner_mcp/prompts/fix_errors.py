"""MCP prompt for MAID Phase 3 Support - fixing validation errors and test failures.

Provides a structured prompt template to guide AI agents through
fixing validation errors and test failures iteratively.
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
async def fix_errors(error_context: str = "") -> list[Message]:
    """Guide AI agents through MAID Phase 3 error fixing for validation failures and test errors."""
    # Build error context section if provided
    error_section = ""
    if error_context:
        error_section = f"""
---

**Current Error Context:**

```
{error_context}
```

Analyze this error and follow the steps below to fix it.
"""

    content = f"""# Phase 3 Support: Error Fixing

Fix validation errors and test failures iteratively.

## Your Task

1. **Collect errors**:
   ```bash
   maid validate 2>&1
   maid test 2>&1
   ```

2. **Fix one issue at a time**:
   - Analyze error message
   - Check manifest for expected artifact
   - Make targeted fix

3. **CRITICAL - Validate ALL manifests after each fix (no arguments)**:
   ```bash
   maid validate
   maid test
   ```
   **Note**: `maid validate` and `maid test` WITHOUT arguments validates entire codebase

4. **Repeat** until all errors resolved

## Success

- All validations pass
- All tests pass
- No new errors introduced
{error_section}"""

    return [_Message(role="user", content=content)]
