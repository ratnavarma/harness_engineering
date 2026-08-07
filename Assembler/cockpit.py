"""Day 5 extension: a local browser cockpit for Assembler.

Concept: make durable sessions and visible product-building activity inspectable.
Design rules: standard library only, bind to localhost, expose execution modes
explicitly, and confine every requested transcript and run to the selected root.
"""

import argparse
import json
import queue
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from . import session
from .harness import Harness
from .security import Policy


def serve(workdir=".", port: int = 8765, open_browser: bool = True) -> None:
    """Serve a local cockpit for sessions and runs below `workdir`."""
    root = Path(workdir).resolve()
    handler = _handler(root, _RunState(root))
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


def _handler(root: Path, runs):
    """Build one request handler class bound to a fixed cockpit root."""
    class CockpitHandler(BaseHTTPRequestHandler):
        def do_POST(self):  # noqa: N802 - required BaseHTTPRequestHandler name.
            """Start one local harness run from the cockpit prompt form."""
            if urlparse(self.path).path != "/api/run":
                return self._json({"error": "not found"}, 404)
            try:
                size = int(self.headers.get("Content-Length", 0))
                request = json.loads(self.rfile.read(size))
                runs.start(str(request["prompt"]), str(request.get("mode", "safe")))
                self._json({"ok": True})
            except (KeyError, ValueError, json.JSONDecodeError) as error:
                self._json({"error": str(error)}, 400)

        def do_GET(self):  # noqa: N802 - required BaseHTTPRequestHandler name.
            """Serve the cockpit page or its read-only JSON endpoints."""
            parsed = urlparse(self.path)
            if parsed.path == "/api/run":
                return self._json(runs.snapshot())
            return self._get(parsed)

        def _get(self, parsed):
            """Handle browser page and durable-session endpoint requests."""
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


class _RunState:
    """Own one background harness run and a browser-safe visible event trace."""

    def __init__(self, root: Path) -> None:
        """Create an idle run state confined to the selected cockpit root."""
        self.root, self.events, self.lock = root, queue.Queue(), threading.Lock()
        self.running, self.final, self.error = False, "", ""

    def start(self, prompt: str, mode: str) -> None:
        """Start a new local run when no other browser-triggered run is active."""
        if mode not in {"safe", "yolo", "read-only"}:
            raise ValueError("invalid execution mode")
        if not prompt.strip():
            raise ValueError("prompt is required")
        with self.lock:
            if self.running:
                raise ValueError("a run is already active")
            self.running, self.final, self.error = True, "", ""
            self.events = queue.Queue()
        threading.Thread(target=self._run, args=(prompt, mode), daemon=True).start()

    def _run(self, prompt: str, mode: str) -> None:
        """Run the harness and expose only its visible execution events."""
        def event(kind, payload):
            calls = [{"name": call["name"], "args": call.get("args", {})}
                     for call in payload.get("tool_calls", [])]
            self.events.put({"kind": kind, "text": payload.get("text", ""),
                             "name": payload.get("name", ""), "tool_calls": calls})
        try:
            policy = Policy(mode, lambda call, reason: False)
            self.final = Harness(self.root, policy=policy, on_event=event).run(prompt)
        except Exception as error:
            self.error = f"{type(error).__name__}: {error}"
        finally:
            self.running = False

    def snapshot(self) -> dict:
        """Return new trace events and current completion state for polling UI."""
        events = []
        while True:
            try:
                events.append(self.events.get_nowait())
            except queue.Empty:
                break
        final, error = self.final, self.error
        self.final, self.error = "", ""
        return {"running": self.running, "events": events, "final": final, "error": error}


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


_PAGE = r"""<!doctype html><meta charset=utf-8><title>Assembler Cockpit</title>
<style>body{margin:0;background:#101925;color:#eaf1f2;font:15px system-ui}header{padding:20px 7vw;background:#18394a}main{display:grid;grid-template-columns:34% 66%;min-height:calc(100vh - 70px)}section{padding:22px;border-right:1px solid #345}button,select,textarea{font:inherit}button{margin:6px 0;padding:12px;color:#eaf1f2;background:#1b2a38;border:1px solid #456;border-radius:6px}.session{width:100%;text-align:left}.run{background:#e66036;font-weight:bold}.meta{color:#9dc7c3;font-size:12px}textarea{width:100%;min-height:100px;padding:12px;background:#15222e;color:#fff;border:1px solid #456;border-radius:6px}select{margin:8px;padding:8px;background:#15222e;color:#fff}pre{white-space:pre-wrap;word-break:break-word;background:#15222e;padding:16px;border-radius:6px}.tool{color:#f3b27b}.assistant{color:#a9dbd8}.final{border-left:4px solid #50b29f;padding-left:12px}</style>
<header><b>ASSEMBLER COCKPIT</b> <span class=meta>local product builder · visible execution trace, not private reasoning</span></header><main><section><h2>Build</h2><textarea id=build-prompt placeholder="Describe the product you want to build…"></textarea><select id=build-mode><option value=safe>Safe — asks before writes</option><option value=yolo>Yolo — automatic inside this workdir</option><option value=read-only>Read-only</option></select><button class=run id=build-button>Build product</button><p class=meta id=status>Yolo permits local writes automatically. Always-deny commands remain blocked.</p><h2>Sessions</h2><div id=list>Loading…</div></section><section><h2 id=title>Live trace</h2><pre id=tape>Enter a product prompt to start.</pre></section></main>
<script>const $=id=>document.getElementById(id),esc=s=>String(s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c])),promptBox=$('build-prompt'),modeBox=$('build-mode'),status=$('status'),tape=$('tape'),title=$('title'),list=$('list');let trace=[];function show(){tape.innerHTML=trace.map(e=>`<span class=${e.kind==='assistant'?'assistant':'tool'}>${esc(e.kind)}${e.name?' · '+esc(e.name):''}</span>\n${esc(e.text||'')}${e.tool_calls?.length?'\n→ '+e.tool_calls.map(x=>x.name+'('+JSON.stringify(x.args)+')').join(', '):''}`).join('\n\n')}async function run(){status.textContent='Starting…';try{let r=await fetch('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt:promptBox.value,mode:modeBox.value})}),d=await r.json();if(d.error)throw Error(d.error);trace=[];title.textContent='Live trace';status.textContent='Running…';show()}catch(error){status.textContent='Request failed: '+error.message}}$('build-button').addEventListener('click',run);async function poll(){try{let d=await fetch('/api/run').then(r=>r.json());if(d.events.length){trace.push(...d.events);show()}if(d.final){trace.push({kind:'assistant',text:'FINAL: '+d.final});status.textContent='Completed.';show()}if(d.error){trace.push({kind:'tool_end',text:'ERROR: '+d.error});status.textContent='Run failed.';show()}}catch(error){status.textContent='Polling failed: '+error.message}}async function sessions(){let rows=await fetch('/api/sessions').then(r=>r.json());list.innerHTML=rows.map(x=>`<button class=session onclick="openSession('${encodeURIComponent(x.path)}')"><b>${esc(x.path)}</b><br><span class=meta>${x.messages} messages · ${x.turns} turns · ${x.tools} tools</span></button>`).join('')||'No durable sessions found.'}async function openSession(path){let d=await fetch('/api/session?path='+path).then(r=>r.json());trace=d.messages.map(m=>({kind:m.role,name:m.name,text:m.text,tool_calls:m.tool_calls}));title.textContent=decodeURIComponent(path);show()}sessions();setInterval(()=>{sessions();poll()},1500)</script>"""


if __name__ == "__main__":
    raise SystemExit(main())
