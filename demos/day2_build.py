"""Day 2: a local coding task using the real core tools.

Concept: connect tool contracts and a permissive demo policy to the Day 1 loop.
Design rules: isolate demo writes in a scratch directory and print every action.
"""

import tempfile
from pathlib import Path

from Assembler.loop import run_loop
from Assembler.provider import DEFAULT_MODEL
from Assembler.security import Policy
from Assembler.tools import core_tools


def print_event(kind: str, payload: dict) -> None:
    """Print assistant turns and tool boundaries for a visible transcript."""
    print(f"{kind}: {payload}")


def main() -> None:
    """Ask the harness to create, run, and verify an iterative Fibonacci script."""
    with tempfile.TemporaryDirectory(prefix="assembler-day2-") as scratch:
        task = "Create fib.py with an iterative fib(n), a main printing fib(30), run it and confirm the output is 832040"
        tools = {item.name: item for item in core_tools(Path(scratch))}
        answer = run_loop(
            DEFAULT_MODEL, "Use the available tools to complete and verify the task.",
            [{"role": "user", "text": task}], tools, print_event, Policy("yolo").check,
        )
        print("final:", answer)


if __name__ == "__main__":
    main()
