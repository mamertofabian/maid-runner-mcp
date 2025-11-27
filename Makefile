.PHONY: help install install-dev test lint lint-fix format type-check validate clean build publish

help:
	@echo "MAID Runner MCP - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install       Install package in editable mode"
	@echo "  make install-dev   Install package with dev dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test          Run all tests"
	@echo "  make validate      Validate all MAID manifests"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint          Run linting checks (ruff)"
	@echo "  make lint-fix      Run linting with auto-fix"
	@echo "  make format        Format code (black)"
	@echo "  make type-check    Run type checking (mypy)"
	@echo ""
	@echo "Build & Publish:"
	@echo "  make clean         Clean build artifacts"
	@echo "  make build         Build distribution packages"
	@echo "  make publish       Publish to PyPI (requires credentials)"

install:
	uv pip install -e .

install-dev:
	uv pip install -e ".[dev]"

test:
	pytest tests/ -v

lint:
	ruff check src/maid_runner_mcp/

lint-fix:
	ruff check --fix src/maid_runner_mcp/

format:
	black src/maid_runner_mcp/ tests/

type-check:
	mypy src/maid_runner_mcp/

validate:
	maid validate --manifest-dir manifests

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete

build: clean
	python -m build

publish: build
	twine upload dist/*
