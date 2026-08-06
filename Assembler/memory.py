"""Day 3: durable project memory as prompt infrastructure.

Concept: carry stable project facts across otherwise fresh conversations.
Design rules: keep memory human-readable, inject it deliberately into the
system prompt, and make writes append-only and easy to audit.
"""

import platform
from pathlib import Path

MEMORY_FILE = "Assembler.md"
# The base prompt is behavior infrastructure, not a conversational greeting.
BASE_SYSTEM_PROMPT = """You are Assembler, a small sharp coding agent working inside one directory with the tools provided.
Act, don't narrate. Inspect before assuming. Prefer edit_file for small changes.
Verify after building by running or re-reading. Never repeat a failing call unchanged.
When complete, reply with a short summary and stop calling tools."""


def build_system_prompt(workdir: str | Path, extra: str = "") -> str:
    """Build the system prompt from platform facts, project memory, and extras.

    Memory is read only at prompt construction so one conversation has a stable
    view; a later fresh conversation deliberately observes appended notes.
    """
    root = Path(workdir).resolve()
    sections = [
        BASE_SYSTEM_PROMPT,
        f"Platform: {platform.system()}; working directory: {root}",
    ]
    memory = root / MEMORY_FILE
    if memory.exists():
        sections.append(f"Project memory ({MEMORY_FILE}):\n{memory.read_text(encoding='utf-8')}")
    if extra:
        sections.append(extra)
    return "\n\n".join(sections)


def remember(workdir: str | Path, note: str) -> str:
    """Append one durable fact to the project's Assembler memory file.

    A Markdown bullet keeps the persistent state inspectable by both people and
    the read_file tool without requiring a database or hidden session state.
    """
    memory = Path(workdir).resolve() / MEMORY_FILE
    with memory.open("a", encoding="utf-8") as handle:
        handle.write(f"- {note}\n")
    return f"Remembered in {MEMORY_FILE}"
