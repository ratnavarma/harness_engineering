"""Day 4: bounded delegation to fresh child harnesses.

Concept: give an agent a narrow way to outsource a self-contained task.
Design rules: children never inherit their parent's conversation and delegation
depth is capped so a recursive request cannot create an unbounded fleet.
"""

from .tools import Tool, tool


def subagent_tool(make_harness, depth: int = 0, max_depth: int = 2) -> Tool:
    """Build the `spawn_agent` tool for a harness at the supplied depth."""
    @tool(
        "Delegate a self-contained task to a fresh sub-agent with its own clean context. "
        "The child cannot see this conversation and returns its final report.",
        task="Self-contained task for the child agent",
    )
    def spawn_agent(task: str) -> str:
        """Run one child harness, unless delegation has reached its depth limit."""
        if depth >= max_depth:
            return "ERROR: sub-agent depth limit reached; do this task yourself"
        child = make_harness(depth + 1)
        return child.run(task)

    return spawn_agent
