"""MCP prompt for MAID Phase 1 manifest creation.

Provides a structured prompt template to guide AI agents through
creating MAID task manifests following the Planning Loop workflow.
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
async def plan_task(goal: str, file_path: str, task_type: str) -> list[Message]:
    """MCP prompt handler that returns a manifest creation template for the given goal.

    Guides AI agents through MAID Phase 1 (Planning Loop) to create a task manifest.
    The manifest serves as the primary contract for implementation.

    Args:
        goal: The task goal or feature description
        file_path: Optional target file path for the task
        task_type: Type of task (create, edit, or refactor)

    Returns:
        A list of Message dicts containing the manifest creation template
    """
    # Build file path context if provided
    file_context = ""
    if file_path:
        file_context = f"""
---

**Target File Context:**

Target file: `{file_path}`

Consider this file when:
- Determining if this should be `creatableFiles` (new file) or `editableFiles` (existing file)
- Defining `expectedArtifacts` for this file
- Setting up the `validationCommand` test path
"""

    # Build task type guidance
    task_type_guidance = ""
    if task_type == "create":
        task_type_guidance = """
**Task Type: CREATE (New File)**
- Use `creatableFiles` for new files (strict validation - exact match required)
- All public artifacts must be declared in `expectedArtifacts`
- Implementation must exactly match the manifest specification
"""
    elif task_type == "edit":
        task_type_guidance = """
**Task Type: EDIT (Existing File)**
- Use `editableFiles` for modifying existing files (permissive validation)
- Declare only the NEW or MODIFIED public artifacts in `expectedArtifacts`
- Implementation must contain at least the declared artifacts (existing code preserved)
"""
    elif task_type == "refactor":
        task_type_guidance = """
**Task Type: REFACTOR**
- Use `editableFiles` for the file being refactored
- Use `supersedes` to reference the original manifest if applicable
- Maintain all existing public APIs while improving internal structure
- Run `maid_snapshot` first to capture current state if no manifest exists
"""

    content = f"""You are creating a MAID task manifest for: {goal}

The manifest is the **PRIMARY CONTRACT** for this task. Tests support and verify the manifest.

---

## MAID Planning Loop (Phase 1-2)

Follow these steps to create a valid manifest:

### Step 1: Find Next Task Number

```bash
ls manifests/task-*.manifest.json | tail -1
```

### Step 2: Check the Manifest Schema

Use `maid_get_schema` or run:
```bash
maid schema
```

Review the schema to understand all available fields and their requirements.

### Step 3: Create the Manifest

Create `manifests/task-XXX-description.manifest.json` with this structure:

```json
{{
  "goal": "Clear, concise task description",
  "taskType": "{task_type}",
  "supersedes": [],
  "creatableFiles": [],
  "editableFiles": [],
  "readonlyFiles": ["tests/test_task_XXX_*.py"],
  "expectedArtifacts": {{
    "file": "path/to/target/file.py",
    "contains": [
      {{
        "type": "function|class|attribute",
        "name": "artifact_name",
        "description": "What this artifact does",
        "args": [{{"name": "arg1", "type": "str"}}],
        "returns": "ReturnType"
      }}
    ]
  }},
  "validationCommand": ["uv", "run", "python", "-m", "pytest", "tests/test_task_XXX_*.py", "-v"]
}}
```
{task_type_guidance}

### Step 4: Validate the Manifest

**CRITICAL** - Run validation with the specific manifest path:

```bash
maid_validate manifests/task-XXX.manifest.json --use-manifest-chain
```

Or via CLI:
```bash
maid validate manifests/task-XXX.manifest.json --use-manifest-chain
```

### Step 5: Iterate Until Valid

- Fix any schema validation errors
- Ensure all required fields are present
- Verify file paths are correct
- Check that `expectedArtifacts` structure is valid

---

## Key Manifest Fields

| Field | Description |
|-------|-------------|
| `goal` | Clear, single-sentence task description |
| `taskType` | `create`, `edit`, or `refactor` |
| `creatableFiles` | NEW files (strict validation) |
| `editableFiles` | EXISTING files (permissive validation) |
| `readonlyFiles` | Dependencies and test files |
| `expectedArtifacts` | Public API contract (ONE file only!) |
| `validationCommand` | Test command to verify implementation |

---

## Important Reminders

1. **expectedArtifacts is an OBJECT** - defines artifacts for ONE file only
2. **For multi-file tasks** - create SEPARATE manifests for each file
3. **Public artifacts only** - private (`_prefix`) artifacts are optional
4. **Tests come next** - after manifest validation passes, create behavioral tests
{file_context}

---

## Success Criteria

✓ Manifest JSON is valid
✓ Schema validation passes
✓ `maid_validate` passes with `--use-manifest-chain`
✓ Ready for Phase 2 (test creation)
"""

    return [_Message(role="user", content=content)]
