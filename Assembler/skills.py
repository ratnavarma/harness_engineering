"""Day 3: filesystem-backed skill discovery and loading.

Concept: make focused instructions available without bloating every prompt.
Design rules: catalog only named skill files, expose concise descriptions, and
return plain text so the harness decides when and how to inject a skill.
"""

from pathlib import Path

SKILLS_DIR = "skills"


def catalog(workdir: str | Path) -> dict[str, dict[str, str]]:
    """Return every named skill's description and absolute SKILL.md path."""
    root = Path(workdir).resolve() / SKILLS_DIR
    if not root.exists():
        return {}
    skills = {}
    for path in sorted(root.glob("*/SKILL.md")):
        skills[path.parent.name] = {
            "description": _description(path.read_text(encoding="utf-8")),
            "path": str(path),
        }
    return skills


def catalog_prompt(workdir: str | Path) -> str:
    """Render a compact prompt section advertising the available skills."""
    skills = catalog(workdir)
    if not skills:
        return ""
    lines = ["Skills available (load one with the use_skill tool when relevant):"]
    lines.extend(f"- {name}: {item['description']}" for name, item in skills.items())
    return "\n".join(lines)


def read_skill(workdir: str | Path, name: str) -> str:
    """Read one complete skill file, or describe the available names on a miss."""
    skills = catalog(workdir)
    if name not in skills:
        return f"ERROR: no skill named {name}. Available: {', '.join(skills)}"
    return Path(skills[name]["path"]).read_text(encoding="utf-8")


def _description(text: str) -> str:
    """Read a description line only from leading YAML-style front matter."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return ""
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith("description:"):
            return line.split(":", 1)[1].strip().strip('"').strip("'")
    return ""
