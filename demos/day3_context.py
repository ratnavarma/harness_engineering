"""Day 3: context compaction, memory, and skill instructions in one loop.

Concept: plug the context engine into Day 1's before-turn socket.
Design rules: work in a scratch directory, keep durable state local, and make
optional skill text explicit in the system prompt.
"""

import tempfile
from pathlib import Path

from Assembler.context import compact
from Assembler.loop import run_loop
from Assembler.memory import build_system_prompt, remember
from Assembler.provider import DEFAULT_MODEL
from Assembler.security import Policy
from Assembler.skills import catalog_prompt
from Assembler.tools import core_tools


def main() -> None:
    """Run a short task with memory, skill cataloging, and compaction enabled."""
    with tempfile.TemporaryDirectory(prefix="assembler-day3-") as scratch:
        root = Path(scratch)
        remember(root, "This scratch project demonstrates durable context.")
        tools = {item.name: item for item in core_tools(root)}
        system = build_system_prompt(root, catalog_prompt(root))
        run_loop(
            DEFAULT_MODEL, system, [{"role": "user", "text": "Create and read hello.txt."}],
            tools, lambda kind, payload: print(kind, payload), Policy("yolo").check,
            before_turn=lambda messages: compact(DEFAULT_MODEL, messages, 1_500),
        )


if __name__ == "__main__":
    main()
