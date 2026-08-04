"""Day 1: a complete dice-tool conversation.

Concept: a tool is a tiny object with a provider schema and a keyword callable.
Design rules: keep demos readable, print the neutral transcript, and put policy
at the harness boundary rather than inside the tool.
"""

import random

from Assembler.loop import run_loop
from Assembler.provider import DEFAULT_MODEL


class RollDice:
    """Roll a requested count of conventional six-sided dice."""

    spec = {
        "schema": {
            "name": "roll_dice",
            "description": "Roll count six-sided dice",
            "parameters": {
                "type": "object",
                "properties": {"count": {"type": "string", "description": "How many dice"}},
                "required": ["count"],
            },
        },
    }

    def run(self, count: str) -> dict:
        """Return the individual rolls and their total."""
        rolls = [random.randint(1, 6) for _ in range(int(count))]
        return {"rolls": rolls, "total": sum(rolls)}


def print_event(kind: str, payload: dict) -> None:
    """Print each visible model and tool transition in the transcript."""
    if kind == "assistant":
        print("assistant:", payload["text"])
        for call in payload["tool_calls"]:
            print("assistant tool call:", call["name"], call["args"])
    elif kind == "tool_start":
        print("tool start:", payload["name"])
    else:
        print("tool result:", payload["text"])


def allow_tool(call: dict) -> None:
    """Allow this introductory demo's tool request."""
    return None


def main() -> None:
    """Ask the model to roll dice and interpret the resulting total."""
    task = "Roll 3 dice and tell me whether the total beats 10"
    messages = [{"role": "user", "text": task}]
    print("user:", task)
    run_loop(
        DEFAULT_MODEL,
        "Use tools when useful, then answer the user's question plainly.",
        messages,
        {"roll_dice": RollDice()},
        print_event,
        allow_tool,
    )


if __name__ == "__main__":
    main()
