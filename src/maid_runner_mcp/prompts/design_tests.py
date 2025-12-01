"""MCP prompt for MAID Phase 2 behavioral test creation.

Provides a structured prompt template to guide AI agents through
creating behavioral tests that USE artifacts from the manifest.
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
async def design_tests(manifest_path: str) -> list[Message]:
    """MCP prompt handler that returns a behavioral test creation template for the given manifest.

    Guides AI agents through MAID Phase 2 (Behavioral Test Creation) to create
    tests that import and USE each artifact from the manifest. Tests should
    cover realistic scenarios and not just check for existence.

    Args:
        manifest_path: Path to the manifest file (e.g., manifests/task-XXX.manifest.json)

    Returns:
        A list of Message dicts containing the behavioral test creation template
    """
    content = f"""# Phase 2: Behavioral Test Creation

Create behavioral tests from the manifest: `{manifest_path}`

See CLAUDE.md for MAID methodology details.

---

## Your Task

### Step 1: Read the Manifest

```bash
cat {manifest_path}
```

Understand the `expectedArtifacts` - each artifact (function, class, attribute) that needs
to be tested. Pay attention to:
- Function/method names and their parameters (args)
- Return types
- Class definitions and their methods

---

### Step 2: Create Test Files

Create test files in `tests/` directory following the naming convention:
- `tests/test_task_XXX_description.py`

**CRITICAL: Tests must IMPORT and USE each artifact, not just check existence!**

For each artifact in `expectedArtifacts`, write tests that:
- **Import** the artifact from the target module
- **Call** functions with realistic argument values
- **Instantiate** classes and invoke their methods
- **Cover all parameters** from the manifest
- Use **realistic scenarios**, not just existence checks

**Example - GOOD (behavioral test that USES the artifact):**
```python
async def test_my_function_processes_data():
    from mymodule import my_function

    result = await my_function(arg1="test_value", arg2=42)

    assert isinstance(result, ExpectedType)
    assert "expected_key" in result
```

**Example - BAD (existence check only):**
```python
def test_my_function_exists():
    from mymodule import my_function
    assert callable(my_function)  # This is NOT behavioral testing!
```

---

### Step 3: Validate Tests USE Artifacts (Behavioral Mode)

**CRITICAL** - Run maid_validate with behavioral mode:

```bash
maid validate {manifest_path} --validation-mode behavioral --use-manifest-chain
```

Or use the MCP tool:
```
maid_validate(manifest_path="{manifest_path}", validation_mode="behavioral", use_manifest_chain=true)
```

This validates that your tests actually import and call the artifacts defined in the manifest.

---

### Step 4: Verify Red Phase (Tests Should Fail)

Run the tests to confirm they fail:

```bash
pytest tests/test_task_XXX_*.py -v
```

**Expected:** Tests should fail with `ImportError` or `ModuleNotFoundError`
because the implementation doesn't exist yet.

This confirms:
- Tests are properly written to import the artifacts
- Tests will pass once implementation is complete (Green phase)
- TDD Red-Green-Refactor cycle is being followed

---

## Test Design Checklist

For each artifact in `expectedArtifacts`:

- [ ] Test imports the artifact from the correct module
- [ ] Test calls the function/method with all required arguments
- [ ] Test uses realistic argument values (not just `None` or empty strings)
- [ ] Test verifies the return type matches the manifest
- [ ] Test covers edge cases if applicable

---

## Success Criteria

- Behavioral validation passes (`maid validate --validation-mode behavioral`)
- Tests fail appropriately with ImportError/ModuleNotFoundError (Red phase)
- Tests are ready for implementation (Green phase)
- All parameters from manifest artifacts are covered in tests
"""

    return [_Message(role="user", content=content)]
