"""MCP prompt for MAID compliance auditing.

Provides a structured prompt template to guide AI agents through
cross-cutting MAID compliance auditing across all phases.
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
async def audit_compliance(manifest_path: str = "", scope: str = "all") -> list[Message]:
    """Guide AI agents through cross-cutting MAID compliance auditing for any phase."""
    # Build manifest context if provided
    manifest_context = ""
    if manifest_path:
        manifest_context = f"""
---

**Target Manifest:**

Auditing manifest: `{manifest_path}`

Focus your audit on:
- This specific manifest's compliance
- Files referenced in this manifest
- Tests associated with this manifest
"""

    # Build scope-specific guidance
    scope_guidance = ""
    if scope == "all":
        scope_guidance = """
**Scope: ALL (Comprehensive Audit)**

Perform a full compliance audit across the entire codebase:
- All manifests in `manifests/` directory
- All test files in `tests/` directory
- All implementation files referenced by manifests
"""
    elif scope == "tests":
        scope_guidance = """
**Scope: TESTS**

Focus on test compliance:
- Verify tests actually USE the artifacts (not just check existence)
- Check test coverage for all public APIs
- Ensure tests follow naming convention `test_task_XXX_*.py`
"""
    elif scope == "implementation":
        scope_guidance = """
**Scope: IMPLEMENTATION**

Focus on implementation compliance:
- Verify all public APIs are declared in manifests
- Check for undocumented public functions/classes
- Ensure implementations match their manifest contracts
"""
    else:
        scope_guidance = f"""
**Scope: {scope.upper()}**

Focus your audit on the specified scope while following MAID compliance rules.
"""

    content = f"""# Cross-Cutting: MAID Compliance Audit

Audit MAID compliance at any phase. See CLAUDE.md for MAID methodology details.
{scope_guidance}
{manifest_context}
---

## Your Task

### Step 1: Run Validations on ALL Manifests

**CRITICAL** - Run validations without arguments to check entire codebase:

```bash
maid validate
maid test
```

**Note**: `maid validate` and `maid test` WITHOUT arguments validates the entire codebase.

### Step 2: Check for Violations

Look for these common compliance issues:

- **Public APIs not in manifest** - Functions/classes without `_` prefix must be declared
- **Tests that don't USE artifacts** - Tests should exercise functionality, not just check existence
- **TODO/FIXME/debug print() in code** - Clean up temporary code before completion
- **Files accessed outside manifest** - All accessed files must be in `editableFiles`, `creatableFiles`, or `readonlyFiles`
- **Skipped phases or validations** - Every task must follow the full MAID workflow

### Step 3: Categorize Issues by Severity

Categorize each finding using these severity levels:

| Severity | Priority | Description | Action |
|----------|----------|-------------|--------|
| CRITICAL | Must fix | Blocks progress, breaks compliance | Fix immediately before proceeding |
| HIGH | Should fix immediately | Significant compliance gap | Address in current session |
| MEDIUM | Should address | Minor compliance issue | Address before next phase |
| LOW | Nice to have | Improvement opportunity | Consider for future |

### Step 4: Report Findings

Provide specific file:line references for each finding:

```
[SEVERITY] file/path.py:42 - Description of the violation
  Remediation: How to fix this issue
```

---

## Violation Types Reference

### Manifest Violations
- Missing `expectedArtifacts` for public APIs
- Incorrect `taskType` (create vs edit)
- Files not listed in manifest but accessed
- Invalid JSON schema

### Test Violations
- Tests only check existence (not behavior)
- Missing tests for public APIs
- Tests access files outside manifest
- Incorrect test file naming

### Implementation Violations
- Undeclared public functions/classes
- Implementation deviates from manifest contract
- Leftover debug code (print statements, TODO comments)
- Type hint mismatches

---

## Remediation Guidance

For each violation type, apply appropriate remediation:

1. **Missing manifest entries** - Add to `expectedArtifacts` or appropriate file list
2. **Weak tests** - Rewrite to actually exercise functionality
3. **Debug code** - Remove or convert to proper logging
4. **File access violations** - Add files to manifest or refactor to avoid access

---

## Success Criteria

The audit is complete when:

- All critical violations have been identified
- Clear remediation guidance has been provided for each issue
- Compliance status has been determined (COMPLIANT / NON-COMPLIANT / PARTIAL)
- A prioritized action list is available

---

## Final Report Template

```markdown
## MAID Compliance Audit Report

**Status**: [COMPLIANT / NON-COMPLIANT / PARTIAL]
**Scope**: {scope}
**Date**: [Current date]

### Summary
- Critical: X issues
- High: X issues
- Medium: X issues
- Low: X issues

### Critical Issues (Must Fix)
[List each with file:line reference and remediation]

### High Priority Issues
[List each with file:line reference and remediation]

### Recommendations
[Overall recommendations for improving compliance]
```
"""

    return [_Message(role="user", content=content)]
