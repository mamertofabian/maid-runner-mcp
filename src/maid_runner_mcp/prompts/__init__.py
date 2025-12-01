"""MCP Prompts for MAID Runner.

Prompts provide workflow guidance templates for AI agents
following the MAID methodology phases.
"""

# Import all prompt modules to register them with the MCP server
# Each module uses @mcp.prompt() decorator for registration
from maid_runner_mcp.prompts import audit_compliance  # noqa: F401
from maid_runner_mcp.prompts import design_tests  # noqa: F401
from maid_runner_mcp.prompts import fix_errors  # noqa: F401
from maid_runner_mcp.prompts import implement_task  # noqa: F401
from maid_runner_mcp.prompts import plan_task  # noqa: F401
from maid_runner_mcp.prompts import refactor_code  # noqa: F401
from maid_runner_mcp.prompts import review_manifest  # noqa: F401
from maid_runner_mcp.prompts import spike_idea  # noqa: F401

__all__: list[str] = []
