"""IT Support Trainer — local server.

Serves the single-file game (index.html) and adds a small backend so the
"Spar" (answer grading) and "Sensei" (tutor) features can talk to a local
Claude Code install. No API key is used — it shells out to the `claude` CLI
on this machine, so it runs on your Claude Code subscription.

Endpoints:
  POST /save-game    -> game/dojo-progress.json   (game state + Claude coaching report)
  POST /ask-claude   -> runs `claude -p` headless on this machine and returns the reply.
                        Body: {"prompt": str, "system": str?, "model": str?}
  GET  /claude-check -> {"ok": bool}  is the claude CLI available on this machine

The game works fully offline as static HTML (Course, Match, the Board, progress,
XP). Only Spar grading and the Sensei tutor need this server + a local Claude CLI;
without it they degrade gracefully and the rest of the game is unaffected.

Run:  python serve.py   then open http://localhost:8377/
"""
import json, os, shutil, subprocess
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
os.makedirs('game', exist_ok=True)

# claude -p runs from the repo root so it picks up any local project context/memory
PROJECT_DIR = ROOT

def find_claude():
    p = shutil.which('claude')
    if p:
        return p
    candidates = [
        os.path.expandvars(r'%APPDATA%\npm\claude.cmd'),
        os.path.expandvars(r'%APPDATA%\npm\claude'),
        os.path.expandvars(r'%LOCALAPPDATA%\Programs\claude\claude.exe'),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

CLAUDE = find_claude()
print('claude CLI:', CLAUDE or 'NOT FOUND (Spar/Sensei will be offline)')

def ask_claude(payload):
    prompt = payload.get('prompt', '')
    system = payload.get('system', '')
    model = payload.get('model', 'sonnet')
    cmd = [CLAUDE, '-p', '--model', model]
    if system:
        cmd += ['--append-system-prompt', system]
    r = subprocess.run(cmd, input=prompt.encode('utf-8'),
                       capture_output=True, timeout=240, cwd=PROJECT_DIR)
    out = r.stdout.decode('utf-8', 'replace').strip()
    if not out:
        err = r.stderr.decode('utf-8', 'replace').strip()
        raise RuntimeError(err[:600] or 'empty reply from claude CLI')
    return out


class Handler(SimpleHTTPRequestHandler):
    def _json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        n = int(self.headers.get('Content-Length', 0))
        return json.loads(self.rfile.read(n).decode('utf-8'))

    def do_GET(self):
        if self.path.split('?')[0].rstrip('/').endswith('claude-check'):
            return self._json(200, {'ok': bool(CLAUDE)})
        return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        route = self.path.split('?')[0].rstrip('/')
        try:
            if route.endswith('ask-claude'):
                if not CLAUDE:
                    return self._json(503, {'ok': False, 'error': 'claude CLI not found on this machine'})
                data = self._read_body()
                try:
                    text = ask_claude(data)
                    return self._json(200, {'ok': True, 'text': text})
                except subprocess.TimeoutExpired:
                    return self._json(504, {'ok': False, 'error': 'claude timed out'})
                except Exception as e:
                    return self._json(500, {'ok': False, 'error': str(e)[:600]})

            elif route.endswith('save-game'):
                data = self._read_body()
                with open(os.path.join('game', 'dojo-progress.json'), 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                return self._json(200, {'ok': True})

            else:
                self.send_response(404); self.end_headers()
        except Exception as e:
            print('POST failed:', e)
            try:
                self._json(500, {'ok': False, 'error': str(e)[:300]})
            except Exception:
                pass

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        SimpleHTTPRequestHandler.end_headers(self)

    def log_message(self, *args):
        pass


print('IT Support Trainer:  http://localhost:8377/   (Ctrl+C to stop)')
ThreadingHTTPServer(('127.0.0.1', 8377), Handler).serve_forever()
