# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-03-26

### Changed
- Migrate all tools from subprocess CLI calls to maid-runner v2.0.0 library API
- Migrate schema and snapshot resources from subprocess to library imports
- Bump maid-runner dependency from >=0.7.0 to >=2.0.0
- Update tests to mock library objects instead of subprocess.run
- Update MAID manifests for v2 validator compliance

## [0.1.0] - 2026-01-03

### Added
- Model Context Protocol server implementation
- Core MCP tools: `maid_validate`, `maid_snapshot`, `maid_snapshot_system`, `maid_list_manifests`, `maid_init`, `maid_get_schema`, `maid_generate_stubs`, `maid_files`
- MCP resources: `manifest://`, `schema://manifest`, `validation://`, `file-tracking://analysis`
- MCP prompts: `plan-task`, `implement-task`, `refactor-code`, `review-manifest`
- Integration with MAID Runner validation framework
- Support for stdio transport
- Structured JSON responses for all tools
- Documentation and integration guides

[Unreleased]: https://github.com/mamertofabian/maid-runner-mcp/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/mamertofabian/maid-runner-mcp/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/mamertofabian/maid-runner-mcp/releases/tag/v0.1.0
