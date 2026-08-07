# Assembler

Assembler is a small, standard-library-only coding-agent harness. It owns the
agent loop, real tools, policy gate, context engine, durable sessions, and
sub-agent delegation rather than wrapping an agent SDK.

## Run it

Configure a Gemini key and optionally choose a model:

```bash
export GEMINI_API_KEY="..."
export ASSEMBLER_MODEL="gemini-3.1-pro-preview"
```

Interactive safe mode:

```bash
python3 -m Assembler -d path/to/project
```

One headless task, automatically permitted inside its jail:

```bash
python3 -m Assembler -d path/to/project -p "Create a README and verify it"
```

Resume the newest durable session:

```bash
python3 -m Assembler -d path/to/project --resume
```

## Anatomy

| Day | Layer | Files | Responsibility |
| --- | --- | --- | --- |
| 1 | Loop | `provider.py`, `loop.py` | Model calls, neutral messages, tool turns |
| 2 | Tools | `tools.py`, `security.py` | Confined actions and approval policy |
| 3 | Context | `context.py`, `memory.py`, `skills.py` | Compaction, durable facts, expertise files |
| 4 | Durability | `session.py`, `subagent.py`, `harness.py` | Resume repair, delegation, composition |
| 5 | Orchestration | `cli.py`, `fleet.py`, `__main__.py` | Human interface and bounded parallel jobs |

## Compose one extra tool

```python
from Assembler import Harness, tool

@tool("Return a friendly greeting", name="Person to greet")
def greet(name: str) -> str:
    return f"Hello, {name}!"

harness = Harness(".", extra_tools=[greet])
print(harness.run("Use greet for Ada, then report the result."))
```
