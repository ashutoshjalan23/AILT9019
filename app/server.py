"""Local-only HTTP demo. Session data is held in memory and expires after one hour."""
import argparse
import json
import secrets
import threading
import time
from datetime import datetime
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

from app.engine import BUILDINGS, HK, ROOT, chat
from app.llm import Bailian, load_env


def make_server(port=8000):
    load_env()
    model = Bailian()
    sessions, lock = {}, threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass  # Do not log chat contents, cookies or credentials.

        def reply(self, status, value, cookie=None):
            body = json.dumps(value).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Length', str(len(body)))
            if cookie:
                self.send_header('Set-Cookie', cookie)
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = urlsplit(self.path).path
            if path == '/api/status':
                return self.reply(200, {'buildings': BUILDINGS, 'model_configured': bool(model.enabled and model.key), 'synthetic': True})
            files = {'/': ('index.html', 'text/html'), '/style.css': ('style.css', 'text/css'), '/app.js': ('app.js', 'text/javascript')}
            if path not in files:
                return self.reply(404, {'error': 'Not found'})
            name, mime = files[path]
            body = (ROOT / 'web' / name).read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', mime + '; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            if self.path not in ('/api/chat', '/api/reset'):
                return self.reply(404, {'error': 'Not found'})
            # Local service accepts only same-origin browser requests.
            origin = self.headers.get('Origin')
            allowed = {f'http://127.0.0.1:{self.server.server_port}', f'http://localhost:{self.server.server_port}'}
            if origin and origin not in allowed:
                return self.reply(403, {'error': 'Origin not allowed'})
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= 8192:
                    return self.reply(413, {'error': 'Request too large or empty'})
                payload = json.loads(self.rfile.read(size))
                if not isinstance(payload, dict):
                    raise ValueError()
                cookies = SimpleCookie(self.headers.get('Cookie', ''))
                sid = cookies['session'].value if 'session' in cookies else ''
                with lock:
                    now = time.monotonic()
                    expired = [key for key, value in sessions.items() if now - value['seen'] > 3600]
                    for key in expired:
                        del sessions[key]
                    if sid not in sessions:
                        if len(sessions) >= 200:
                            return self.reply(503, {'error': 'Demo session limit reached'})
                        sid = secrets.token_urlsafe(24)
                        sessions[sid] = {'seen': now, 'state': {}}
                    session = sessions[sid]
                    session['seen'] = now
                    cookie = f'session={sid}; HttpOnly; SameSite=Strict; Path=/; Max-Age=3600'
                    if self.path == '/api/reset':
                        session['state'] = {}
                        return self.reply(200, {'reset': True}, cookie)
                    text = payload.get('message')
                    if not isinstance(text, str) or not text.strip() or len(text) > 1000:
                        return self.reply(400, {'error': 'Enter a message of 1 to 1000 characters'})
                    at = None
                    if payload.get('at'):
                        at = datetime.fromisoformat(payload['at'])
                        at = at.replace(tzinfo=HK) if at.tzinfo is None else at.astimezone(HK)
                    result = chat(text.strip(), session['state'], at, model)
                    return self.reply(200, result, cookie)
            except (ValueError, TypeError, KeyError):
                return self.reply(400, {'error': 'Invalid request or date; use an ISO date and time'})
            except Exception:
                return self.reply(500, {'error': 'The demo could not complete this request. Try again or reset the chat.'})

    return ThreadingHTTPServer(('127.0.0.1', port), Handler)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    server = make_server(args.port)
    print(f'HKU Dining Demo: http://127.0.0.1:{server.server_port} (Ctrl+C to stop)', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
