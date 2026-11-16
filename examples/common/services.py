"""Small deterministic HTTP services bound to 127.0.0.1 for the examples.

Each service runs in a background thread on a free port and is shut down when
the "with" block ends, so the web, LLM and FaaS examples never leave the
machine and never need a real credential.
"""
import csv
import json
import threading
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from common.course import DATA

COURSE_TOKEN = "course-token-not-a-secret"   # a test value for localhost only


def _rows():
    with open(DATA, newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


class _Handler(BaseHTTPRequestHandler):
    calls = []                        # (method, path) of every request served

    def log_message(self, *_):
        pass

    def reply(self, status, payload, content_type="application/json"):
        body = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Request-ID", "req-%03d" % len(self.calls))
        self.end_headers()
        self.wfile.write(body)

    def body(self):
        return self.rfile.read(int(self.headers.get("Content-Length", 0)))


class StationService(_Handler):
    """GET /stations/<id>/latest, GET /private, POST /uploads, GET /busy."""

    def do_GET(self):
        self.calls.append(("GET", self.path))
        url = urlparse(self.path)
        parts = url.path.strip("/").split("/")
        if parts[:1] == ["stations"] and len(parts) == 3 and parts[2] == "latest":
            rows = [r for r in _rows() if r["station"] == parts[1]]
            if not rows:
                return self.reply(404, {"error": "unknown station"})
            row = rows[-1]
            units = parse_qs(url.query).get("units", ["metric"])[0]
            wind = float(row["wind_m_s"]) * (1.943844 if units == "nautical" else 1)
            return self.reply(200, {"station": row["station"], "time_utc": row["time_utc"],
                                    "temperature_c": float(row["temperature_c"]),
                                    "wind": round(wind, 2), "units": units})
        if url.path == "/private":
            if self.headers.get("Authorization") != "Bearer " + COURSE_TOKEN:
                return self.reply(401, {"error": "missing or wrong token"})
            return self.reply(200, {"access": "granted"})
        if url.path == "/busy":
            return self.reply(503, {"error": "try later"})
        return self.reply(404, {"error": "not found"})

    def do_POST(self):
        self.calls.append(("POST", self.path))
        data = self.body()
        if self.path == "/uploads":
            text = data.decode("utf-8", errors="replace")
            return self.reply(201, {"stored": "NAP,2026" in text, "bytes": len(data),
                                    "multipart": "multipart/form-data" in
                                    self.headers.get("Content-Type", "")})
        return self.reply(404, {"error": "not found"})


class ChatService(_Handler):
    """A deterministic subset of the OpenAI-compatible Chat Completions API."""

    def do_POST(self):
        self.calls.append(("POST", self.path))
        if self.path != "/v1/chat/completions":
            return self.reply(404, {"error": "not found"})
        if not self.headers.get("Authorization", "").startswith("Bearer "):
            return self.reply(401, {"error": "no key"})
        request = json.loads(self.body())
        prompt = request["messages"][-1]["content"]
        records = [l for l in prompt.splitlines() if l[:1].isupper() and l.count(",") == 3]
        answer = "Summary of %d records for model %s: %s" % (
            len(records), request.get("model"), prompt.splitlines()[0][:48])
        return self.reply(200, {"id": "chatcmpl-course", "object": "chat.completion",
                                "model": request.get("model"),
                                "choices": [{"index": 0, "message": {
                                    "role": "assistant", "content": answer}}],
                                "usage": {"prompt_tokens": len(prompt.split()),
                                          "completion_tokens": len(answer.split())}})


class FunctionService(_Handler):
    """POST /invoke: a 'serverless' function that averages a list of values."""

    def do_POST(self):
        self.calls.append(("POST", self.path))
        envelope = json.loads(self.body())
        values = envelope["data"]["inputs"]["values"]
        mean = round(sum(values) / len(values), 3)
        return self.reply(200, {"status": "succeeded",
                                "outputs": {"result": {"mean": mean, "n": len(values)}}})


@contextmanager
def serve(handler):
    """Run *handler* on 127.0.0.1 and yield its base URL."""
    handler.calls = []
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield "http://127.0.0.1:%d" % server.server_port
    finally:
        server.shutdown()
        server.server_close()
