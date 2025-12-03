"""MCP Server for MAID Runner.

Exposes MAID Runner validation tools via Model Context Protocol (MCP).
"""

from mcp.server.fastmcp import FastMCP


# MAID methodology instructions for AI tools consuming this MCP server.
# These instructions help AI agents understand how to use the tools effectively.
MAID_INSTRUCTIONS = """
# MAID Runner MCP Server

This server implements the Manifest-driven AI Development (MAID) methodology.
Use these tools to validate, implement, and manage code following the MAID workflow.

## MAID Workflow Phases

### Phase 1: Goal Definition
Confirm the high-level goal before proceeding.

### Phase 2: Planning Loop
Before ANY implementation:
1. Create manifest (`manifests/task-XXX.manifest.json`) - the PRIMARY CONTRACT
2. Create behavioral tests (`tests/test_task_XXX_*.py`)
3. Validate: `maid_validate` with `--use-manifest-chain`
4. Iterate until validation passes

### Phase 3: Implementation
1. Load ONLY files from manifest (`editableFiles` + `readonlyFiles`)
2. Implement code to pass tests
3. Run `maid_test` to execute validation commands
4. Iterate until all tests pass

### Phase 4: Integration
Verify complete test suite passes.

## Tool Usage Patterns

### Creating a New Task
1. Use `maid_get_schema` to understand manifest structure
2. Create manifest file with goal, files, and expectedArtifacts
3. Use `maid_validate` to check manifest validity
4. Use `maid_generate_stubs` to create test stubs

### Validating Code
1. Use `maid_validate` with specific manifest path
2. Use `--use-manifest-chain` for edit tasks (validates history)
3. Use `maid_test` to run all validation commands

### Working with Existing Code
1. Use `maid_snapshot` to generate manifest from existing file
2. Use `maid_list_manifests` to find manifests for a file
3. Use `maid_files` to check file tracking status

## Key Rules

**NEVER:**
- Modify code without a manifest
- Skip validation steps
- Access files not listed in manifest

**ALWAYS:**
- Manifest first, then tests, then implementation
- Validate before and after changes
- Use `--use-manifest-chain` for edit tasks

## Manifest Structure

**CRITICAL: `expectedArtifacts` is an OBJECT, not an array!**

Structure: `{"file": "path/to/file.py", "contains": [...]}`

For multi-file features: Create SEPARATE manifests for each file.

```json
{
  "goal": "Clear task description",
  "taskType": "create|edit|refactor",
  "creatableFiles": [],
  "editableFiles": [],
  "readonlyFiles": [],
  "expectedArtifacts": {
    "file": "path/to/file.py",
    "contains": [
      {"type": "function", "name": "my_function", "args": [...], "returns": "str"}
    ]
  },
  "validationCommand": ["pytest", "tests/test_*.py", "-v"]
}
```

## Manifest Rules (CRITICAL)

**These rules are non-negotiable for maintaining MAID compliance:**

- **Manifest Immutability**: The current task's manifest (e.g., `task-050.manifest.json`) can be modified while actively working on that task. Once you move to the next task, ALL prior manifests become immutable and part of the permanent audit trail. NEVER modify completed task manifests—this breaks the chronological record of changes.

- **One File Per Manifest**: `expectedArtifacts` is an OBJECT that defines artifacts for a SINGLE file only. It is NOT an array of files. This is a common mistake that will cause validation to fail.

- **Multi-File Changes Require Multiple Manifests**: If your task modifies public APIs in multiple files (e.g., `utils.py` AND `handlers.py`), you MUST create separate sequential manifests—one per file:
  - `task-050-update-utils.manifest.json` → modifies `utils.py`
  - `task-051-update-handlers.manifest.json` → modifies `handlers.py`

- **Definition of Done (Zero Tolerance)**: A task is NOT complete until BOTH validation commands pass with ZERO errors or warnings:
  - `maid_validate <manifest-path>` → Must pass 100%
  - `maid_test` → Must pass 100%

  Partial completion is not acceptable. All errors must be fixed before proceeding to the next task.

## Artifact Rules

- **Public** (no `_` prefix): MUST be in manifest
- **Private** (`_` prefix): Optional in manifest
- **creatableFiles**: Strict validation (exact match)
- **editableFiles**: Permissive validation (contains at least)

## Refactoring Private Implementation

MAID provides flexibility for refactoring private implementation details without requiring new manifests:

- **Private code** (functions, classes, variables with `_` prefix) can be refactored freely
- **Internal logic changes** that don't affect the public API are allowed
- **Code quality improvements** (splitting functions, extracting helpers, renaming privates) are permitted

**Requirements:**
- All tests must continue to pass
- All validations must pass (`maid_validate`, `maid_test`)
- Public API must remain unchanged
- No MAID rules are violated

This breathing room allows practical development without bureaucracy while maintaining accountability for public interface changes.

## Available Tools

- `maid_validate`: Validate manifest against code/tests
- `maid_test`: Run validation commands from manifests
- `maid_snapshot`: Generate manifest from existing code
- `maid_snapshot_system`: Generate system-wide manifest
- `maid_list_manifests`: Find manifests for a file
- `maid_files`: Check file tracking status
- `maid_get_schema`: Get manifest JSON schema
- `maid_init`: Initialize MAID project
- `maid_generate_stubs`: Generate test stubs from manifest

## Available Resources

- `maid://spec`: Full MAID methodology specification document
- `schema://manifest`: JSON schema for manifest validation
- `manifest://{name}`: Read specific manifest content
- `snapshot://system`: System-wide manifest snapshot
""".strip()


# Module-level server instance (singleton)
# Tools are registered via @mcp.tool() decorators in tools modules
_server: FastMCP | None = None


def create_server() -> FastMCP:
    """Get the configured FastMCP server instance.

    Returns the singleton server instance with all registered tools.
    This ensures tools decorated with @mcp.tool() are available.
    The server includes MAID methodology instructions to guide AI agents.

    Returns:
        FastMCP: The configured MCP server with registered tools.
    """
    global _server
    if _server is None:
        _server = FastMCP("maid-runner", instructions=MAID_INSTRUCTIONS)
    return _server


# Initialize the server instance
mcp = create_server()

# Import tools to register them with the server
# Tools use @mcp.tool() decorator from this module
from maid_runner_mcp.tools import files  # noqa: E402, F401
from maid_runner_mcp.tools import generate_stubs  # noqa: E402, F401
from maid_runner_mcp.tools import init  # noqa: E402, F401
from maid_runner_mcp.tools import manifests  # noqa: E402, F401
from maid_runner_mcp.tools import schema  # noqa: E402, F401
from maid_runner_mcp.tools import snapshot  # noqa: E402, F401
from maid_runner_mcp.tools import snapshot_system  # noqa: E402, F401
from maid_runner_mcp.tools import test  # noqa: E402, F401
from maid_runner_mcp.tools import validate  # noqa: E402, F401

# Import resources to register them with the server
# Resources use @mcp.resource() decorator from this module
from maid_runner_mcp.resources import manifest  # noqa: E402, F401
from maid_runner_mcp.resources import schema as schema_resource  # noqa: E402, F401
from maid_runner_mcp.resources import snapshot as snapshot_resource  # noqa: E402, F401
from maid_runner_mcp.resources import spec  # noqa: E402, F401

# Import prompts to register them with the server
from maid_runner_mcp import prompts  # noqa: E402, F401


def main() -> None:
    """Entry point for the MCP server.

    Runs the server using stdio transport (default).
    """
    mcp.run()
