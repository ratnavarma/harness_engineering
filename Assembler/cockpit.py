"""Day 5 extension: a read-only local browser cockpit for Assembler.

Concept: make durable sessions and completed work inspectable without granting
browser clients tool authority. Design rules: standard library only, bind to
localhost, and confine every requested transcript to the selected root.
"""

import argparse
import json
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from . import session


def serve(workdir=".", port: int = 8765, open_browser: bool = True) -> None:
    """Serve a local read-only cockpit for sessions below `workdir`."""
    root = Path(workdir).resolve()
    handler = _handler(root)
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    url = f"http://127.0.0.1:{server.server_port}"
    print(f"Assembler cockpit: {url} · root={root}")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nCockpit stopped.")
    finally:
        server.server_close()


def main(argv=None) -> int:
    """Parse cockpit options and start its local browser server."""
    parser = argparse.ArgumentParser(description="Read-only Assembler cockpit")
    parser.add_argument("-d", "--workdir", default=".")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args(argv)
    serve(args.workdir, args.port, not args.no_browser)
    return 0


def _handler(root: Path):
    """Build one request handler class bound to a fixed cockpit root."""
    class CockpitHandler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802 - required BaseHTTPRequestHandler name.
            """Serve the cockpit page or its read-only JSON endpoints."""
            parsed = urlparse(self.path)
            if parsed.path == "/":
                return self._send("text/html; charset=utf-8", _PAGE.encode())
            if parsed.path == "/api/sessions":
                return self._json(_sessions(root))
            if parsed.path == "/api/session":
                requested = parse_qs(parsed.query).get("path", [""])[0]
                try:
                    path = (root / requested).resolve()
                    path.relative_to(root)
                    return self._json({"path": requested, "messages": session.load(path)})
                except (OSError, ValueError):
                    return self._json({"error": "session not found"}, 404)
            self._json({"error": "not found"}, 404)

        def log_message(self, format, *args):
            """Keep normal browser polling out of the terminal transcript."""

        def _json(self, value, status=200):
            self._send("application/json; charset=utf-8", json.dumps(value, ensure_ascii=False).encode(), status)

        def _send(self, content_type, body, status=200):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
    return CockpitHandler


def _sessions(root: Path) -> list[dict]:
    """Summarize every durable session under a cockpit root."""
    records = []
    for path in sorted(root.rglob(".assembler/sessions/*.jsonl"), key=lambda item: item.stat().st_mtime, reverse=True):
        messages = session.load(path)
        records.append({
            "path": str(path.relative_to(root)), "updated": int(path.stat().st_mtime),
            "messages": len(messages), "turns": sum(item.get("role") == "assistant" for item in messages),
            "tools": sum(item.get("role") == "tool" for item in messages),
            "final": next((item.get("text", "") for item in reversed(messages) if item.get("role") == "assistant"), ""),
        })
    return records


_PAGE = """<!doctype html><meta charset=utf-8><title>Assembler Cockpit</title>
<style>body{margin:0;background:#101925;color:#eaf1f2;font:15px system-ui}header{padding:24px 7vw;background:#18394a}main{display:grid;grid-template-columns:38% 62%;min-height:calc(100vh - 78px)}section{padding:22px;border-right:1px solid #345}button{width:100%;margin:6px 0;padding:12px;text-align:left;color:#eaf1f2;background:#1b2a38;border:1px solid #456;border-radius:6px}button:hover{background:#25475a}.meta{color:#9dc7c3;font-size:12px}pre{white-space:pre-wrap;word-break:break-word;background:#15222e;padding:16px;border-radius:6px}.tool{color:#f3b27b}.assistant{color:#a9dbd8}</style>
<header><b>ASSEMBLER COCKPIT</b> <span class=meta>read-only session telemetry · refreshes every 5 seconds</span></header><main><section><h2>Sessions</h2><div id=list>Loading…</div></section><section><h2 id=title>Transcript</h2><pre id=tape>Select a session.</pre></section></main>
<script>let selected='';const esc=s=>String(s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));async function sessions(){let rows=await fetch('/api/sessions').then(r=>r.json());list.innerHTML=rows.length?rows.map(x=>`<button onclick="openSession('${encodeURIComponent(x.path)}')"><b>${esc(x.path)}</b><br><span class=meta>${x.messages} messages · ${x.turns} turns · ${x.tools} tools</span><br>${esc(x.final).slice(0,120)}</button>`).join(''):'No durable sessions found.'}async function openSession(path){selected=decodeURIComponent(path);let d=await fetch('/api/session?path='+encodeURIComponent(selected)).then(r=>r.json());title.textContent=selected;tape.innerHTML=d.messages.map(m=>`<span class=${m.role}>${esc(m.role)}${m.name?' · '+esc(m.name):''}</span>\n${esc(m.text||'')}${m.tool_calls?'\n→ '+m.tool_calls.map(x=>x.name).join(', '):''}`).join('\n\n')}sessions();setInterval(sessions,5000)</script>"""


if __name__ == "__main__":
    raise SystemExit(main())
