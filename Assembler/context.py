"""Day 3: bounded conversation context through transcript compaction.

Concept: preserve the facts an agent needs while keeping its next prompt small.
Design rules: do nothing while context fits, keep recent action continuity, and
summarize older messages into a neutral, factual user message.
"""

from . import provider

CHARS_PER_TOKEN = 4
KEEP_RECENT = 6
_MESSAGE_CLIP = 1_000
_COMPACTION_SYSTEM = (
    "You compress agent transcripts. Preserve: the original task, every file "
    "created or edited and its purpose, key decisions, unresolved errors, and "
    "what remains to be done. Be dense and factual."
)


def estimate_tokens(messages: list[dict]) -> float:
    """Estimate token use from the character size of neutral messages."""
    return sum(len(str(message)) for message in messages) / CHARS_PER_TOKEN


def compact(model: str, messages: list[dict], budget_tokens: int) -> list[dict]:
    """Summarize old messages when a conversation exceeds its context budget."""
    if estimate_tokens(messages) <= budget_tokens or len(messages) <= KEEP_RECENT + 1:
        return messages
    old, recent = messages[:-KEEP_RECENT], messages[-KEEP_RECENT:]
    summary = provider.complete(
        model, _COMPACTION_SYSTEM,
        [{"role": "user", "text": _transcript(old)}], [],
    )["text"]
    # A tool result without its request is not meaningful to the next model turn.
    while recent and recent[0]["role"] == "tool":
        recent.pop(0)
    return [{"role": "user", "text": f"[Conversation so far, compacted]\n{summary}"}] + recent


def _transcript(messages: list[dict]) -> str:
    """Render neutral messages as compact plain text for the summarizing call."""
    entries = []
    for message in messages:
        label = message["role"]
        if message["role"] == "tool":
            label += f" ({message['name']})"
        text = str(message.get("text", ""))
        if len(text) > _MESSAGE_CLIP:
            text = text[:_MESSAGE_CLIP] + " …[clipped]"
        entries.append(f"{label}: {text}")
        calls = message.get("tool_calls", [])
        if calls:
            entries.append("tool calls: " + ", ".join(call["name"] for call in calls))
    return "\n".join(entries)
