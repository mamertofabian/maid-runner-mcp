# Contributing to MAID Runner MCP

Thank you for your interest in contributing to MAID Runner MCP!

## Development Philosophy

**This project follows the MAID methodology itself (self-dogfooding).**

All contributions must adhere to the MAID workflow. See `CLAUDE.md` for detailed development guidelines.

## Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- Git
- MAID Runner installed (`pip install maid-runner`)

## Setup

```bash
# Clone repository
git clone https://github.com/mamertofabian/maid-runner-mcp
cd maid-runner-mcp

# Install dependencies
uv pip install -e ".[dev]"

# Run tests to verify setup
pytest tests/ -v
```

## MAID Workflow (Required)

Every code change must follow the MAID workflow:

### Phase 1: Goal Definition
1. Open an issue or discuss the change
2. Get consensus on the high-level goal

### Phase 2: Planning Loop
1. Create a manifest in `manifests/task-XXX.manifest.json`
2. Create behavioral tests in `tests/test_task_XXX_*.py`
3. Validate structure: `maid validate manifests/task-XXX.manifest.json --use-manifest-chain`
4. Iterate until validation passes

### Phase 3: Implementation
1. Implement code to pass behavioral tests
2. Run tests: `pytest tests/test_task_XXX_*.py -v`
3. Validate implementation: `maid validate manifests/task-XXX.manifest.json --use-manifest-chain`
4. Iterate until all validations pass

### Phase 3.5: Refactoring (Optional)
1. Improve code quality while maintaining test passage
2. Validate manifest compliance is maintained

### Phase 4: Integration
1. Run full test suite: `pytest tests/ -v`
2. Run all validations: `maid validate --manifest-dir manifests`
3. Ensure code quality: `make lint && make format`

## Making Changes

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Follow MAID Methodology

See `CLAUDE.md` for complete workflow details.

Key principles:
- **Manifest first** - Create the contract before code
- **Tests define success** - Behavioral tests are the source of truth
- **Extreme isolation** - Touch minimal files per task
- **Validate early** - Run `maid validate` before implementation

### 3. Code Quality Standards

Before committing:

```bash
# Format code
make format

# Check linting
make lint

# Run tests
make test

# Validate manifests
make validate
```

All checks must pass.

### 4. Commit Messages

Follow conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

Examples:
- `feat(tools): add maid_validate tool implementation`
- `fix(resources): handle missing manifest files gracefully`
- `docs(readme): update installation instructions`

### 5. Submit Pull Request

1. Push your branch: `git push origin feature/your-feature-name`
2. Open a pull request on GitHub
3. Ensure CI passes
4. Request review

## Testing

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_task_001_*.py -v

# With coverage
pytest tests/ --cov=maid_runner_mcp --cov-report=html
```

### Test Requirements

- All new features must have behavioral tests
- Tests must follow MAID manifest specifications
- Tests must be in `tests/test_task_XXX_*.py` format
- Minimum 80% code coverage for new code

## Code Style

- **Black** for formatting (line length: 100)
- **Ruff** for linting
- **MyPy** for type checking
- **Type hints** required for all public APIs

## Documentation

When adding features:

1. Update relevant documentation in `docs/`
2. Add examples if applicable
3. Update CHANGELOG.md
4. Update README.md if needed

## Questions?

- Open an issue for discussion
- Check existing issues and PRs
- Review `CLAUDE.md` for development guidelines
- Read the [MAID methodology](https://github.com/mamertofabian/maid-runner/blob/main/docs/maid_specs.md)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
