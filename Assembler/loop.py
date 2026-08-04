"""Day 1: the model-to-tool execution loop.

Concept: let a model request deterministic local actions without owning control
flow. Design rules: preserve a complete neutral transcript and contain tool
failures so one bad action cannot crash the harness.
"""

from . import provider


def run_loop(
    model: str,
    system: str,
    messages: list[dict],
    tools: dict,
    on_event,
    before_tool,
    max_turns: int = 80,
    before_turn=None,
) -> str:
    """Run model turns and requested tools until the model gives a final answer."""
    def call_model(available_tools: list[dict]) -> dict:
        if before_turn is not None:
            updated = before_turn(messages)
            messages[:] = updated
        return provider.complete(model, system, messages, available_tools)

    specs = [tool.spec for tool in tools.values()]
    for _ in range(max_turns):
        reply = call_model(specs)
        assistant = {"role": "assistant", "text": reply["text"], "tool_calls": reply["tool_calls"]}
        messages.append(assistant)
        on_event("assistant", assistant)
        if not reply["tool_calls"]:
            return reply["text"]
        for call in reply["tool_calls"]:
            on_event("tool_start", call)
            result = _run_tool(call, tools, before_tool)
            tool_message = {"role": "tool", "name": call["name"], "text": str(result)}
            messages.append(tool_message)
            on_event("tool_end", tool_message)

    messages.append({"role": "user", "text": "Turn limit reached; wrap up now."})
    reply = call_model([])
    assistant = {"role": "assistant", "text": reply["text"], "tool_calls": reply["tool_calls"]}
    messages.append(assistant)
    on_event("assistant", assistant)
    return reply["text"]


def _run_tool(call: dict, tools: dict, before_tool) -> str:
    """Run one requested tool, converting policy and execution failures to text."""
    blocked = before_tool(call)
    if blocked is not None:
        return f"BLOCKED: {blocked}"
    tool = tools.get(call["name"])
    if tool is None:
        return f"ERROR: unknown tool {call['name']}"
    try:
        return str(tool.run(**call.get("args", {})))
    except Exception as error:
        return f"ERROR: {type(error).__name__}: {error}"
