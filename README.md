# MAID Runner MCP

**Model Context Protocol server for MAID Runner validation tools.**

MAID Runner MCP exposes [MAID Runner](https://github.com/mamertofabian/maid-runner) validation capabilities via the Model Context Protocol (MCP), enabling seamless integration with AI development tools like Claude Code, Aider, and custom AI agents.

## What Is This?

MAID Runner MCP is a bridge between AI agents and MAID Runner's validation framework. It provides:

- **MCP Tools**: Programmatic access to `maid validate`, `maid snapshot`, `maid test`, and other commands
- **MCP Resources**: Access to manifests, schemas, validation results, and system architecture
- **MCP Prompts**: Workflow guidance for AI agents through MAID methodology phases

Think of it as an API layer that lets AI agents interact with MAID Runner using standardized MCP protocol instead of subprocess calls.

## Status

🚧 **Alpha Release** - Under active development.

This is part of the MAID ecosystem and follows the MAID methodology itself (self-dogfooding).

## Quick Start

### Installation

```bash
# Install from PyPI
pip install maid-runner-mcp

# Or with uv
uv pip install maid-runner-mcp
```

### Running the Server

```bash
# Start MCP server (stdio transport)
maid-runner-mcp

# Or with uv
uv run maid-runner-mcp
```

### Integration with Claude Code

Add to your `.claude/mcp.json`:

```json
{
  "mcpServers": {
    "maid-runner": {
      "command": "uv",
      "args": ["run", "maid-runner-mcp"],
      "env": {
        "MAID_MANIFEST_DIR": "manifests"
      }
    }
  }
}
```

Now Claude Code can:
- Validate manifests via `maid_validate` tool
- Generate snapshots via `maid_snapshot` tool
- Access manifest content via `manifest://` resources
- Get workflow guidance via prompts

## Architecture

```
AI Agents (Claude, GPT-4, etc.)
        ↓
   MCP Protocol (JSON-RPC)
        ↓
  maid-runner-mcp (MCP Server)
        ↓
   MAID Runner (Validation Core)
```

## Features

### Tools (Actions with Side Effects)

- `maid_validate` - Validate manifests (structural + behavioral + implementation)
- `maid_snapshot` - Generate manifest snapshots from existing code
- `maid_test` - Run validation commands from manifests
- `maid_list_manifests` - Find manifests referencing a file
- `maid_init` - Initialize MAID project structure
- `maid_get_schema` - Get manifest JSON schema

### Resources (Read-Only Data Access)

- `manifest://{name}` - Access manifest content
- `schema://manifest` - Get manifest JSON schema
- `validation://{name}/result` - Access cached validation results
- `snapshot://system` - Get system-wide architecture snapshot
- `graph://query` - Query manifest knowledge graph
- `file-tracking://analysis` - Get file tracking status

### Prompts (Workflow Guidance)

- `plan-task` - Guide AI through manifest creation
- `implement-task` - Guide AI through implementation
- `refactor-code` - Guide AI through safe refactoring
- `review-manifest` - Guide AI through manifest review

## How It Relates to MAID Runner

| Component | Role | What It Does |
|-----------|------|--------------|
| **MAID Runner** | Validation framework | CLI tool for validating MAID manifests |
| **MAID Runner MCP** | MCP interface | Exposes MAID Runner to AI agents via MCP |

MAID Runner MCP doesn't replace the CLI—it complements it:
- **CLI** (`maid`): For humans and shell scripts
- **MCP** (`maid-runner-mcp`): For AI agents and programmatic access

Both use the same underlying validation logic.

## Use Cases

### 1. AI-Assisted Development

AI agents can validate code as they generate it:

```python
# AI agent workflow
result = await session.call_tool("maid_validate", {
    "manifest_path": "manifests/task-013.manifest.json",
    "use_manifest_chain": true
})

if not result["success"]:
    # Fix issues based on errors
    ...
```

### 2. Architecture Exploration

AI agents can understand system architecture:

```python
# Get system snapshot
snapshot = await session.read_resource("snapshot://system")

# Query knowledge graph
results = await session.read_resource(
    "graph://query?type=class&name=EmailValidator"
)
```

### 3. Workflow Automation

Custom agents can automate MAID workflow:

```python
# Get planning guidance
prompt = await session.get_prompt("plan-task", {
    "goal": "Add email validation"
})

# Follow prompt to create manifest
...
```

## Documentation

- [Installation & Setup](docs/setup.md)
- [Tools Reference](docs/tools.md)
- [Resources Reference](docs/resources.md)
- [Prompts Reference](docs/prompts.md)
- [Integration Guide](docs/integration.md)
- [Examples](docs/examples/)

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/mamertofabian/maid-runner-mcp
cd maid-runner-mcp

# Install dependencies
uv pip install -e ".[dev]"

# Run tests
pytest tests/ -v
```

### Makefile Commands

```bash
make install      # Install package
make test         # Run tests
make lint         # Check code style
make format       # Format code
make validate     # Validate MAID manifests
```

## MAID Compliance

This project follows the MAID methodology itself:
- All changes have manifests in `manifests/`
- All features have behavioral tests in `tests/`
- Validation enforced via `maid validate --use-manifest-chain`

See `CLAUDE.md` for development guidelines.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development workflow and guidelines.

## License

MIT License - see [LICENSE](LICENSE) file.

## Related Projects

- [MAID Runner](https://github.com/mamertofabian/maid-runner) - Core validation framework
- [MAID Agents](https://github.com/mamertofabian/maid-agents) - Claude Code automation

## Links

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MAID Methodology](https://github.com/mamertofabian/maid-runner/blob/main/docs/maid_specs.md)
