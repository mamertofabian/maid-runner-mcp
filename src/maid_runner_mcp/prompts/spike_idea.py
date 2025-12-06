"""MCP prompt for spike idea exploration.

Provides a structured prompt template to guide AI agents through
exploratory spikes before creating MAID manifests.
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
async def spike_idea(idea: str) -> list[Message]:
    """Guide AI agents through exploratory spike to understand an idea before creating a manifest."""
    content = f"""Explore the idea: {idea}

Quick exploratory spike (no manifest yet):

1. **Research codebase for related patterns**
   - Search for similar implementations in the codebase
   - Identify existing patterns that could be reused

2. **Identify affected files and components**
   - List files that will need modification
   - Note any new files that need to be created

3. **Outline potential approach**
   - Describe the high-level implementation strategy
   - Consider alternative approaches

4. **Estimate complexity and scope**
   - Rate complexity (low/medium/high)
   - Estimate effort required

5. **Suggest whether this should be one task or multiple**
   - Single task: If changes are focused on one file
   - Multiple tasks: If changes span multiple files or components

---

**CRITICAL REMINDER for Manifest Creation:**

- `expectedArtifacts` is an **OBJECT** (not an array) that defines artifacts for **ONE file only**
- Structure: `{{"file": "path/to/file.py", "contains": [...]}}`
- For multi-file features: Create **separate manifests** for each file

---

**Next Steps:**

After completing this spike, you should:
1. Summarize your findings
2. Recommend whether to proceed with implementation
3. If proceeding, create manifest(s) following the MAID workflow
4. Consider breaking large features into smaller, focused tasks
"""

    return [_Message(role="user", content=content)]
