"""Day 4: compose the harness layers into one durable coding agent.

Concept: connect provider, loop, tools, policy, context, memory, and sessions.
Design rules: keep children ephemeral, persist neutral messages as they arrive,
and make compaction invisible to durable transcript accounting.
"""

import os
from pathlib import Path

from . import context, loop, memory, provider, session, skills
from .security import Policy
from .subagent import subagent_tool
from .tools import core_tools, tool


class Harness:
    """A composed, optionally durable Assembler coding harness."""

    def __init__(self, workdir=".", model=None, policy=None, extra_tools=None,
                 system_extra="", on_event=None, budget_tokens=600_000,
                 max_turns=120, session_path=None, enable_subagents=True,
                 persist=True, _depth=0):
        """Create a harness rooted at one real working directory."""
        self.workdir = Path(workdir).resolve()
        self.workdir.mkdir(parents=True, exist_ok=True)
        self.model = model or os.environ.get("ASSEMBLER_MODEL") or provider.DEFAULT_MODEL
        self.policy = policy or Policy("yolo")
        self.extra_tools = extra_tools or []
        self.system_extra = system_extra
        self.on_event = on_event or (lambda kind, payload: None)
        self.budget_tokens, self.max_turns = budget_tokens, max_turns
        self.session_path = Path(session_path) if session_path else None
        self.persist, self._depth = persist, _depth
        self.messages = []
        self.tools = {item.name: item for item in core_tools(self.workdir)}
        self.tools["remember"] = self._remember_tool()
        if skills.catalog(self.workdir):
            self.tools["use_skill"] = self._skill_tool()
        if enable_subagents:
            self.tools["spawn_agent"] = subagent_tool(self._make_child, _depth)
        self.tools.update({item.name: item for item in self.extra_tools})
        extra = "\n\n".join(part for part in (skills.catalog_prompt(self.workdir), system_extra) if part)
        self.system = memory.build_system_prompt(self.workdir, extra)

    def resume(self, path=None) -> bool:
        """Load the requested or newest durable session into this harness."""
        chosen = Path(path) if path else session.latest(self.workdir)
        if chosen is None:
            return False
        self.messages = session.load(chosen)
        self.session_path = chosen
        return bool(self.messages)

    def run(self, task: str) -> str:
        """Append a task and run the composed loop until it returns an answer."""
        if self.persist and self.session_path is None:
            self.session_path = session.new_session(self.workdir, task[:32])
        recorded = [len(self.messages)]

        def record_new() -> None:
            if len(self.messages) < recorded[0]:
                recorded[0] = len(self.messages)
            if self.persist and self.session_path:
                for message in self.messages[recorded[0]:]:
                    session.append(self.session_path, message)
            recorded[0] = len(self.messages)

        def before_turn(messages):
            record_new()
            updated = context.compact(self.model, messages, self.budget_tokens)
            # Compaction rewrites working memory; session logs retain original turns.
            recorded[0] = min(recorded[0], len(updated))
            return updated

        def event(kind, payload):
            record_new()
            self.on_event(kind, payload)

        self.messages.append({"role": "user", "text": task})
        record_new()
        return loop.run_loop(self.model, self.system, self.messages, self.tools,
                             event, self.policy.check, self.max_turns, before_turn)

    def _remember_tool(self):
        """Build the durable-memory tool bound to this harness directory."""
        @tool("Remember a durable project fact", note="Fact to append to project memory")
        def remember(note: str) -> str:
            """Append one note to the project memory file."""
            return memory.remember(self.workdir, note)
        return remember

    def _skill_tool(self):
        """Build the full-skill loader bound to this harness directory."""
        @tool("Load the full instructions for an available skill", name="Skill name")
        def use_skill(name: str) -> str:
            """Return one skill file's complete instructions."""
            return skills.read_skill(self.workdir, name)
        return use_skill

    def _make_child(self, depth: int):
        """Create a fresh, non-persistent child over the same working directory."""
        return Harness(self.workdir, self.model, self.policy, self.extra_tools,
                       self.system_extra, self.on_event, self.budget_tokens,
                       self.max_turns, enable_subagents=True, persist=False, _depth=depth)
