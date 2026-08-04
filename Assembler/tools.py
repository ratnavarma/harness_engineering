"""Day 2: local execution tools with explicit schemas and path confinement.

Concept: expose useful machine actions as small, inspectable contracts.
Design rules: keep arguments text-shaped for the model, resolve every file path
against one root, and return bounded, readable results.
"""

import fnmatch
import inspect
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass
class Tool:
    """A named tool schema and the callable that implements it."""

    name: str
    spec: dict
    run: Callable


def tool(description: str, **params: str):
    """Decorate a function as a string-argument Tool with a Gemini schema."""
    def decorate(function: Callable) -> Tool:
        signature = inspect.signature(function)
        arguments = list(signature.parameters.values())
        required = [argument.name for argument in arguments if argument.default is inspect.Parameter.empty]
        schema = {
            "name": function.__name__,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {
                    argument.name: {"type": "string", "description": params.get(argument.name, "")}
                    for argument in arguments
                },
                "required": required,
            },
        }
        return Tool(function.__name__, {"schema": schema}, function)
    return decorate


def core_tools(workdir: str | Path) -> list[Tool]:
    """Return the six core tools restricted to the real path of `workdir`."""
    root = Path(workdir).resolve()
    ignored = {".git", "node_modules", ".venv"}

    def resolve(path: str) -> Path:
        """Resolve one user path and reject any escape from the working root."""
        candidate = (root / path).resolve()
        try:
            candidate.relative_to(root)
        except ValueError as error:
            raise PermissionError(f"{path!r} escapes the working directory") from error
        return candidate

    def walk_files():
        """Yield files below root while excluding tool and environment directories."""
        for directory, folders, files in os.walk(root):
            folders[:] = sorted(folder for folder in folders if folder not in ignored and "pycache" not in folder)
            for filename in sorted(files):
                path = Path(directory, filename)
                relative = path.relative_to(root)
                yield resolve(str(relative)), str(relative)

    @tool("Read a text file with line numbers", path="File path relative to the working directory")
    def read_file(path: str) -> str:
        """Read up to 4,000 numbered lines from a confined text file."""
        lines = resolve(path).read_text(encoding="utf-8").splitlines()
        rendered = [f"{number}\t{line}" for number, line in enumerate(lines[:4000], 1)]
        if len(lines) > 4000:
            rendered.append(f"... truncated after 4000 lines; file has {len(lines)} lines total")
        return "\n".join(rendered)

    @tool("Write a text file", path="File path relative to the working directory", content="Complete file contents")
    def write_file(path: str, content: str) -> str:
        """Create parent directories and write text to one confined file."""
        target = resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"Wrote {len(content)} chars to {path}"

    @tool("Replace one unique snippet in a text file", path="File path", old="Exact existing snippet", new="Replacement snippet")
    def edit_file(path: str, old: str, new: str) -> str:
        """Replace an exact snippet only when it is unique in the file."""
        target = resolve(path)
        contents = target.read_text(encoding="utf-8")
        matches = contents.count(old)
        # Requiring uniqueness prevents the model from editing an unintended duplicate.
        if matches == 0:
            return "ERROR: snippet not found — read the file and copy it exactly"
        if matches > 1:
            return f"ERROR: snippet appears {matches} times — include more context to make it unique"
        target.write_text(contents.replace(old, new, 1), encoding="utf-8")
        return f"Edited {path}"

    @tool("Run a shell command in the working directory", command="Shell command", timeout="Timeout in seconds")
    def bash(command: str, timeout: str = "120") -> str:
        """Run a command, returning bounded combined output instead of raising."""
        try:
            completed = subprocess.run(
                command, shell=True, cwd=root, text=True, capture_output=True, timeout=float(timeout),
            )
        except subprocess.TimeoutExpired:
            return f"ERROR: timed out after {timeout}s"
        output = completed.stdout + completed.stderr
        if len(output) > 12000:
            output = output[:6000] + "\n... output truncated ...\n" + output[-6000:]
        return output if output else f"(exit {completed.returncode}, no output)"

    @tool("List matching files", pattern="Glob-style relative path pattern")
    def list_files(pattern: str = "**/*") -> str:
        """List up to 500 confined files matching a path or basename pattern."""
        matches = [relative for _, relative in walk_files() if pattern == "**/*" or fnmatch.fnmatch(relative, pattern) or fnmatch.fnmatch(Path(relative).name, pattern)]
        matches.sort()
        if len(matches) > 500:
            return "\n".join(matches[:500] + [f"and {len(matches) - 500} more"])
        return "\n".join(matches)

    @tool("Search text files with a regular expression", regex="Python regular expression", pattern="Glob-style file pattern")
    def grep(regex: str, pattern: str = "*") -> str:
        """Return up to 200 matching, clipped lines from confined text files."""
        expression = re.compile(regex)
        hits = []
        for path, relative in walk_files():
            if not (fnmatch.fnmatch(relative, pattern) or fnmatch.fnmatch(Path(relative).name, pattern)):
                continue
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except (UnicodeDecodeError, OSError):
                continue
            for number, line in enumerate(lines, 1):
                if expression.search(line):
                    hits.append(f"{relative}:{number}: {line[:200]}")
                    if len(hits) == 200:
                        return "\n".join(hits)
        return "\n".join(hits)

    return [read_file, write_file, edit_file, bash, list_files, grep]
