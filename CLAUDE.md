# CLAUDE.md

**⚠️ CRITICAL: This project dogfoods MAID v1.2. Every code change MUST follow the MAID workflow.**

## Project Overview

MAID Runner MCP is a Model Context Protocol server that exposes MAID Runner validation tools to AI agents. It provides MCP tools, resources, and prompts for seamless integration with AI development tools like Claude Code.

## MAID Workflow (Required for ALL changes)

### Phase 1: Goal Definition

Confirm the high-level goal with user before proceeding.

### Phase 2: Planning Loop

**Before ANY implementation - iterative refinement:**

1. Draft manifest (`manifests/task-XXX.manifest.json`) - **PRIMARY CONTRACT**
2. Draft behavioral tests (`tests/test_task_XXX_*.py`) to support and verify the manifest
3. Run structural validation (checks manifest↔tests AND implementation↔history):
   `uv run maid validate manifests/task-XXX.manifest.json --use-manifest-chain`
4. Refine BOTH tests & manifest together until validation passes

### Phase 3: Implementation

1. Load ONLY files from manifest (`editableFiles` + `readonlyFiles`)
2. Implement code to pass tests
3. Run behavioral validation (from `validationCommand`)
4. Iterate until all tests pass

### Phase 3.5: Refactoring

1. After tests pass, improve code quality
2. Maintain public API and manifest compliance
3. Apply clean code principles and patterns
4. Validate tests still pass after each change

### Phase 4: Integration

Verify complete chain: `uv run python -m pytest tests/ -v`

## Key Rules

**NEVER:** Modify code without manifest | Skip validation | Access unlisted files
**ALWAYS:** Manifest first → Tests → Implementation → Validate

## Quick Commands

```bash
# Find next manifest number
ls manifests/task-*.manifest.json | tail -1

# Validation Flow
# 1. Structural validation (pre-implementation)
uv run maid validate manifests/task-XXX.manifest.json --use-manifest-chain

# 2. Behavioral test execution (run actual tests)
uv run python -m pytest tests/test_task_XXX_*.py -v

# Full test suite
make test  # or: uv run python -m pytest tests/ -v

# Code quality
make lint        # Run ruff linter
make format      # Format code with black
make type-check  # Run mypy type checking
make validate    # Validate all manifests
```

## Architecture

### Core Components

1. **MCP Server** (`src/maid_runner_mcp/server.py`)

   - FastMCP-based server implementation
   - Exposes tools, resources, and prompts
   - Handles stdio transport (default)

2. **Tools** (`src/maid_runner_mcp/tools/`)

   - Wrap MAID Runner CLI commands
   - Return structured JSON responses
   - Handle errors and validation

3. **Resources** (`src/maid_runner_mcp/resources/`)

   - Expose read-only data (manifests, schemas, etc.)
   - Support URI-based access
   - Cache validation results

4. **Prompts** (`src/maid_runner_mcp/prompts/`)
   - Guide AI agents through MAID workflow
   - Support Phase 1-4 of MAID methodology
   - Template-based prompt generation

### MCP Components

**Tools** (Actions with side effects):

- `maid_validate` - Validate manifests
- `maid_snapshot` - Generate snapshots
- `maid_test` - Run validation commands
- `maid_list_manifests` - List manifests for a file
- `maid_init` - Initialize MAID project
- `maid_get_schema` - Get manifest schema

**Resources** (Read-only data):

- `manifest://{name}` - Manifest content
- `schema://manifest` - JSON schema
- `validation://{name}/result` - Validation results
- `snapshot://system` - System snapshot
- `graph://query` - Knowledge graph queries
- `file-tracking://analysis` - File tracking status

**Prompts** (Workflow guidance):

- `plan-task` - Guide manifest creation
- `implement-task` - Guide implementation
- `refactor-code` - Guide refactoring
- `review-manifest` - Guide manifest review

## Manifest Template

```json
{
  "goal": "Clear task description",
  "taskType": "edit|create|refactor",
  "supersedes": [],
  "creatableFiles": [],
  "editableFiles": [],
  "readonlyFiles": [],
  "expectedArtifacts": {
    "file": "path/to/file.py",
    "contains": [
      {
        "type": "function|class|attribute",
        "name": "artifact_name",
        "class": "ParentClass",
        "args": [{ "name": "arg1", "type": "str" }],
        "returns": "ReturnType"
      }
    ]
  },
  "validationCommand": ["pytest tests/test_file.py -v"]
}
```

## Testing Strategy

- **Unit tests**: Test individual components with mocking
- **Integration tests**: Test MCP server with test clients
- **Async tests**: Use pytest-asyncio for async code
- All tests follow naming: `test_task_NNN_description.py`

## Dependencies

- **maid-runner>=0.1.0**: Core validation framework
- **mcp>=1.0.0**: MCP Python SDK (FastMCP)
- **pytest-asyncio**: Async testing support

## Key Design Patterns

### Error Handling

- Catch `SystemExit` from MAID Runner CLI
- Parse stderr for error messages
- Structure errors as JSON arrays
- Return structured error responses

### Output Parsing

- Capture stdout/stderr from MAID Runner
- Parse validation output for structured data
- Convert to structured JSON responses
- Cache results where appropriate

### Path Safety

- Validate all file paths
- Prevent directory traversal
- Resolve paths relative to project root

## Task Completion Checklist

**Before declaring any task complete:**

```bash
make lint          # Check linting
make format        # Format code
make type-check    # Type checking
make test          # Run tests
make validate      # Validate manifests
```

**All checks must pass.**

## Code Quality Standards

- **No workarounds** - Fix root causes, not symptoms
- **Proper solutions only** - Build it right the first time
- **Test thoroughly** - All tests must pass
- **Type hints required** - All public APIs must have type hints
- **Async where needed** - Use async/await for I/O operations

## Documentation Standards

**Focus on current state, not temporal comparisons:**

**NEVER use:**

- ❌ Temporal markers: "NEW", "UPDATED", "ADDED"
- ❌ Temporal comparisons: "Before/After"
- ❌ Marketing language: "Exciting new feature"
- ❌ Date-based qualifiers: "As of today", "Recently added"

**ALWAYS:**

- ✅ State facts clearly: "System supports X"
- ✅ Use present tense: "This validates"
- ✅ Document current capabilities: "The system provides"

## MCP Integration Notes

### Transport Support

- **stdio** (default): For local process communication
- **SSE** (future): For server-sent events
- **WebSocket** (future): For bidirectional communication

### Protocol Compliance

- Follow MCP specification strictly
- Return structured JSON-RPC responses
- Handle all MCP lifecycle events
- Support tool/resource/prompt discovery

### Client Compatibility

- Test with Claude Code
- Test with MCP Inspector
- Provide integration examples
- Document configuration

## Related Projects

- **MAID Runner**: Core validation framework (sibling package)
- **MAID Agents**: Claude Code automation (optional integration)

## References

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MAID Methodology](../../docs/maid_specs.md)
- [Issue #89: MCP Server Foundation](https://github.com/mamertofabian/maid-runner/issues/89)


========================================

# MAID Methodology

**This project uses Manifest-driven AI Development (MAID) v1.3**

MAID is a methodology for developing software with AI assistance by explicitly declaring:
- What files can be modified for each task
- What code artifacts (functions, classes) should be created or modified
- How to validate that the changes meet requirements

This project is compatible with MAID-aware AI agents including Claude Code and other tools that understand the MAID workflow.

## MAID Workflow

### Phase 1: Goal Definition
Confirm the high-level goal before proceeding.

### Phase 2: Planning Loop
**Before ANY implementation - iterative refinement:**
1. Draft manifest (`manifests/task-XXX.manifest.json`)
2. Draft behavioral tests (`tests/test_task_XXX_*.py`)
3. Run validation: `maid validate manifests/task-XXX.manifest.json --validation-mode behavioral`
4. Refine both tests & manifest until validation passes

### Phase 3: Implementation
1. Load ONLY files from manifest (`editableFiles` + `readonlyFiles`)
2. Implement code to pass tests
3. Run behavioral validation (from `validationCommand`)
4. Iterate until all tests pass

### Phase 4: Integration
Verify complete chain: `pytest tests/ -v`

## Manifest Template

**⚠️ CRITICAL: `expectedArtifacts` is an OBJECT, not an array!**

- `expectedArtifacts` defines artifacts for **ONE file only**
- For multi-file tasks: Create **separate manifests** for each file
- Structure: `{"file": "...", "contains": [...]}`
- **NOT** an array of file objects

```json
{
  "goal": "Clear task description",
  "taskType": "edit|create|refactor",
  "supersedes": [],  // Optional: paths to obsolete manifests
  "creatableFiles": [],  // New files (Strict Mode)
  "editableFiles": [],   // Existing files (Permissive Mode)
  "readonlyFiles": [],   // Dependencies and tests
  "expectedArtifacts": {
    "file": "path/to/file.py",  // ← Single file path
    "contains": [                // ← Array of artifacts for THIS file
      {
        "type": "function|class|attribute",
        "name": "artifact_name",
        "class": "ParentClass",  // For methods/attributes
        "args": [{"name": "arg1", "type": "str"}],  // For functions
        "returns": "ReturnType"  // Optional
      }
    ]
  },
  "validationCommand": ["pytest tests/test_file.py -v"]
}
```

## MAID CLI Commands

```bash
# Validate a manifest
maid validate <manifest-path> [--validation-mode behavioral|implementation]

# Generate a snapshot manifest from existing code
maid snapshot <file-path> [--output-dir <dir>]

# List manifests that reference a file
maid manifests <file-path> [--manifest-dir <dir>]

# Run all validation commands
maid test [--manifest-dir <dir>]

# Get help
maid --help
```

## Validation Modes

- **Strict Mode** (`creatableFiles`): Implementation must EXACTLY match `expectedArtifacts`
- **Permissive Mode** (`editableFiles`): Implementation must CONTAIN `expectedArtifacts` (allows existing code)

## Key Rules

**NEVER:** Modify code without manifest | Skip validation | Access unlisted files
**ALWAYS:** Manifest first → Tests → Implementation → Validate

## Artifact Rules

- **Public** (no `_` prefix): MUST be in manifest
- **Private** (`_` prefix): Optional in manifest
- **creatableFiles**: Strict validation (exact match)
- **editableFiles**: Permissive validation (contains at least)

## Getting Started

1. Create your first manifest in `manifests/task-001-<description>.manifest.json`
2. Write behavioral tests in `tests/test_task_001_*.py`
3. Validate: `maid validate manifests/task-001-<description>.manifest.json --validation-mode behavioral`
4. Implement the code
5. Run tests to verify: `maid test`

## Additional Resources

- **Full MAID Specification**: See `.maid/docs/maid_specs.md` for complete methodology details
- **MAID Runner Repository**: https://github.com/mamertofabian/maid-runner
