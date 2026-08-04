"""Day 1: a neutral message adapter for the Gemini generate-content API.

Concept: isolate a model provider behind stable harness-shaped messages.
Design rules: use only the standard library, retain provider-required metadata,
and make transient network failures safe to retry.
"""

import json
import os
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_ROOT = "https://generativelanguage.googleapis.com/v1beta/models"
DEFAULT_MODEL = "gemini-3.1-pro-preview"


def api_key() -> str:
    """Return the Gemini API key from `.env` or the process environment."""
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, value = line.split("=", 1)
            if name.strip() == "GEMINI_API_KEY" and value.strip():
                return value.strip().strip('"').strip("'")
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key
    raise RuntimeError("Gemini API key missing: set GEMINI_API_KEY in .env or the environment.")


def complete(model: str, system: str, messages: list[dict], tools: list[dict]) -> dict:
    """Complete a conversation and return neutral text, calls, and usage data."""
    body = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": _to_wire(messages),
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 65536},
    }
    if tools:
        body["tools"] = [{"functionDeclarations": [tool["schema"] for tool in tools]}]
    url = f"{API_ROOT}/{model}:generateContent?{urlencode({'key': api_key()})}"
    response = _post(url, body)
    candidate = response.get("candidates", [{}])[0]
    parts = candidate.get("content", {}).get("parts", [])
    text = "".join(part["text"] for part in parts if "text" in part and not part.get("thought"))
    calls = [
        {
            "name": part["functionCall"]["name"],
            "args": part["functionCall"].get("args", {}),
            "signature": part.get("thoughtSignature"),
        }
        for part in parts
        if "functionCall" in part
    ]
    usage = response.get("usageMetadata", {})
    return {
        "text": text,
        "tool_calls": calls,
        "usage": {
            "input": usage.get("promptTokenCount", 0),
            "output": usage.get("candidatesTokenCount", 0),
        },
    }


def _to_wire(messages: list[dict]) -> list[dict]:
    """Translate neutral harness messages to Gemini `contents` entries."""
    contents = []
    for message in messages:
        role = message["role"]
        if role == "user":
            contents.append({"role": "user", "parts": [{"text": message["text"]}]})
        elif role == "assistant":
            parts = []
            if message.get("text"):
                parts.append({"text": message["text"]})
            for call in message.get("tool_calls", []):
                part = {"functionCall": {"name": call["name"], "args": call.get("args", {})}}
                # Gemini 3 requires its reasoning signature to round-trip unchanged.
                if call.get("signature") is not None:
                    part["thoughtSignature"] = call["signature"]
                parts.append(part)
            contents.append({"role": "model", "parts": parts})
        elif role == "tool":
            contents.append({
                "role": "user",
                "parts": [{"functionResponse": {
                    "name": message["name"], "response": {"result": message["text"]},
                }}],
            })
        else:
            raise ValueError(f"Unknown message role: {role}")
    return contents


def _post(url: str, body: dict, retries: int = 5) -> dict:
    """POST JSON, retrying transient HTTP and network failures with backoff."""
    data = json.dumps(body).encode("utf-8")
    for attempt in range(retries):
        request = Request(url, data=data, headers={"Content-Type": "application/json"})
        try:
            with urlopen(request, timeout=600) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")[:400]
            if error.code not in (429, 500, 502, 503) or attempt == retries - 1:
                raise RuntimeError(f"Gemini API error {error.code}: {detail}") from error
        except (URLError, TimeoutError) as error:
            if attempt == retries - 1:
                raise RuntimeError(f"Gemini request failed: {error}") from error
        time.sleep(2 ** attempt * 2)
    raise RuntimeError("Gemini request failed after retries")
