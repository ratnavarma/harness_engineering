"""Day 5: the interactive and headless front doors for Assembler.

Concept: connect a human or automation to the same composed harness.
Design rules: show actions concisely, default people to approval, and preserve
the session log when an interactive run is interrupted.
"""

import argparse

from .harness import Harness
from .security import Policy


def main(argv=None) -> int:
    """Run Assembler in headless single-task or interactive prompt-loop mode."""
    parser = argparse.ArgumentParser(description="A small sharp coding harness")
    parser.add_argument("-p", "--prompt", help="Run one headless task")
    parser.add_argument("-d", "--workdir", default=".", help="Working-directory jail")
    parser.add_argument("-m", "--model", help="Model name")
    parser.add_argument("--mode", choices=("safe", "yolo", "read-only"))
    parser.add_argument("--resume", action="store_true", help="Resume the newest session")
    parser.add_argument("--max-turns", type=int, default=120)
    args = parser.parse_args(argv)
    mode = args.mode or ("yolo" if args.prompt else "safe")
    harness = Harness(args.workdir, args.model, Policy(mode, _approve),
                      on_event=_print_event, max_turns=args.max_turns)
    if args.resume:
        harness.resume()
    if args.prompt:
        print(harness.run(args.prompt))
        return 0
    print(f"Assembler · model={harness.model} · mode={mode} · jail={harness.workdir}")
    while True:
        try:
            task = input("assembler> ")
        except EOFError:
            print()
            return 0
        if not task.strip():
            continue
        try:
            print(harness.run(task))
        except KeyboardInterrupt:
            print("\nInterrupted. The session log is safe; --resume continues it.")


def _print_event(kind: str, payload: dict) -> None:
    """Render assistant prose, tool calls, and first-line tool results."""
    if kind == "assistant":
        if payload["text"]:
            print(payload["text"])
        for call in payload["tool_calls"]:
            args = ", ".join(f"{key}={str(value)[:80]!r}" for key, value in call["args"].items())
            print(f"→ {call['name']}({args})")
    elif kind == "tool_end":
        print(f"\033[2m  {payload['text'].splitlines()[0] if payload['text'] else ''}\033[0m")


def _approve(call: dict, reason: str) -> bool:
    """Ask a person to approve one side-effecting tool call."""
    args = ", ".join(f"{key}={str(value)[:120]!r}" for key, value in call["args"].items())
    return input(f"approve {call['name']}({args})? [y/N] ").strip().lower() in {"y", "yes"}
