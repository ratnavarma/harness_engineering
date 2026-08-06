"""Day 4: append-only durable sessions with restart repair.

Concept: record a neutral transcript so an interrupted agent can resume safely.
Design rules: make each write independently parseable, tolerate a torn final
line, and synthesize missing tool responses after a process restart.
"""

import json
import re
import time
from pathlib import Path

SESSION_DIR = ".assembler/sessions"


def new_session(workdir: str | Path, label: str = "session") -> Path:
    """Create the session directory and return a timestamped JSONL log path."""
    root = Path(workdir).resolve()
    directory = root / SESSION_DIR
    directory.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")[:40] or "session"
    return directory / f"{int(time.time())}-{slug}.jsonl"


def append(path: str | Path, message: dict) -> None:
    """Append one neutral message as one UTF-8 JSONL record."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(message, ensure_ascii=False) + "\n")


def load(path: str | Path) -> list[dict]:
    """Load complete records, stopping at a torn tail and repairing call pairs."""
    messages = []
    with Path(path).open(encoding="utf-8") as handle:
        for line in handle:
            try:
                messages.append(json.loads(line))
            except json.JSONDecodeError:
                # A crash can leave only the final buffered JSONL line incomplete.
                break
    _repair(messages)
    return messages


def latest(workdir: str | Path) -> Path | None:
    """Return the newest session log in a work directory, when one exists."""
    directory = Path(workdir).resolve() / SESSION_DIR
    paths = list(directory.glob("*.jsonl")) if directory.exists() else []
    return max(paths, key=lambda path: path.stat().st_mtime) if paths else None


def _repair(messages: list[dict]) -> None:
    """Append interruption results for calls left unmatched by a restart."""
    assistant_index = next(
        (index for index in range(len(messages) - 1, -1, -1) if messages[index].get("role") == "assistant"),
        None,
    )
    if assistant_index is None:
        return
    assistant = messages[assistant_index]
    completed = sum(message.get("role") == "tool" for message in messages[assistant_index + 1:])
    for call in assistant.get("tool_calls", [])[completed:]:
        messages.append({
            "role": "tool",
            "name": call["name"],
            "text": "Interrupted before this ran (process restarted).",
        })
