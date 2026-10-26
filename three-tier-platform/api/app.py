"""PlatformOps Board REST API. Standard-library HTTP layer; PostgreSQL in deployments."""
from __future__ import annotations
import json, os, sqlite3, threading, time, uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SCHEMA = """CREATE TABLE IF NOT EXISTS tasks (
 id TEXT PRIMARY KEY, title TEXT NOT NULL, status TEXT NOT NULL,
 created_at TEXT NOT NULL)"""
VALID_STATUS = {"open", "in_progress", "done"}

class Database:
    def __init__(self, url):
        self.url = url
        self.sqlite = url.startswith("sqlite:///")
        self.marker = "?" if self.sqlite else "%s"

    @contextmanager
    def connect(self):
        if self.sqlite:
            connection = sqlite3.connect(self.url.removeprefix("sqlite:///"), timeout=5)
        else:
            import psycopg
            connection = psycopg.connect(self.url, connect_timeout=5,
                options="-c statement_timeout=5000")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self):
        # Bootstrap only: versioned migrations are a documented production follow-up.
        with self.connect() as conn:
            conn.execute(SCHEMA)

    def ready(self):
        with self.connect() as conn:
            conn.execute("SELECT 1").fetchone()

    def list_tasks(self):
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT id,title,status,created_at FROM tasks ORDER BY created_at DESC LIMIT 100"
            ).fetchall()
        return [dict(zip(("id","title","status","created_at"), row)) for row in rows]

    def create_task(self, title):
        if not isinstance(title, str) or not 1 <= len(title.strip()) <= 160:
            raise ValueError("title must contain 1 to 160 characters")
        task = dict(id=str(uuid.uuid4()), title=title.strip(), status="open",
                    created_at=datetime.now(timezone.utc).isoformat())
        placeholders = ",".join([self.marker] * 4)
        with self.connect() as conn:
            conn.execute(f"INSERT INTO tasks VALUES ({placeholders})", tuple(task.values()))
        return task

    def update_task(self, task_id, status):
        try:
            uuid.UUID(task_id)
        except (ValueError, AttributeError):
            raise ValueError("invalid task id")
        if not isinstance(status, str) or status not in VALID_STATUS:
            raise ValueError("status must be open, in_progress, or done")
        with self.connect() as conn:
            cursor = conn.execute(
                f"UPDATE tasks SET status={self.marker} WHERE id={self.marker}",
                (status, task_id))
            return cursor.rowcount > 0

class Metrics:
    def __init__(self):
        self.lock = threading.Lock()
        self.requests = self.errors = 0
        self.duration = 0.0

    def record(self, status, elapsed):
        with self.lock:
            self.requests += 1
            self.errors += int(status >= 500)
            self.duration += elapsed

    def render(self):
        with self.lock:
            return (
                "# TYPE platformops_requests_total counter\n"
                f"platformops_requests_total {self.requests}\n"
                "# TYPE platformops_server_errors_total counter\n"
                f"platformops_server_errors_total {self.errors}\n"
                "# TYPE platformops_request_duration_seconds summary\n"
                f"platformops_request_duration_seconds_sum {self.duration:.6f}\n"
                f"platformops_request_duration_seconds_count {self.requests}\n"
            ).encode()

def handler_for(db, metrics):
    class Handler(BaseHTTPRequestHandler):
        server_version = "PlatformOps"
        def setup(self):
            super().setup()
            self.connection.settimeout(10)

        def log_message(self, fmt, *args):
            # Do not log request payloads, credentials, or raw URLs.
            print(json.dumps({"event":"http_request","client":self.client_address[0]}),
                  flush=True)

        def respond(self, status, payload, content_type="application/json"):
            data = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(data)
            return status

        def body(self):
            if self.headers.get("Content-Type","").split(";")[0] != "application/json":
                raise ValueError("Content-Type must be application/json")
            try:
                length = int(self.headers.get("Content-Length","0"))
            except ValueError:
                raise ValueError("invalid content length")
            if not 1 <= length <= 4096:
                raise ValueError("body must be 1 to 4096 bytes")
            try:
                data = json.loads(self.rfile.read(length))
            except (ValueError, UnicodeDecodeError):
                raise ValueError("body must be valid JSON")
            if not isinstance(data, dict):
                raise ValueError("body must be a JSON object")
            return data

        def route(self):
            path = self.path.split("?")[0]
            if self.command == "GET" and path == "/healthz":
                return self.respond(200, {"status":"alive"})
            if self.command == "GET" and path == "/readyz":
                db.ready()
                return self.respond(200, {"status":"ready"})
            if self.command == "GET" and path == "/metrics":
                return self.respond(200, metrics.render(), "text/plain; version=0.0.4")
            if self.command == "GET" and path == "/api/tasks":
                return self.respond(200, {"tasks":db.list_tasks()})
            if self.command == "POST" and path == "/api/tasks":
                return self.respond(201, db.create_task(self.body().get("title")))
            if self.command == "PATCH" and path.startswith("/api/tasks/"):
                task_id = path.removeprefix("/api/tasks/")
                status = self.body().get("status")
                if not db.update_task(task_id, status):
                    return self.respond(404, {"error":"task not found"})
                return self.respond(200, {"id":task_id,"status":status})
            return self.respond(404, {"error":"route not found"})

        def dispatch(self):
            started = time.monotonic()
            status = 500
            try:
                status = self.route()
            except ValueError as error:
                status = self.respond(400, {"error":str(error)})
            except Exception:
                print(json.dumps({"event":"request_failed","method":self.command}), flush=True)
                status = self.respond(503, {"error":"service temporarily unavailable"})
            finally:
                metrics.record(status, time.monotonic() - started)
        do_GET = do_POST = do_PATCH = dispatch
    return Handler

def main():
    db = Database(os.environ["DATABASE_URL"])
    for attempt in range(30):
        try:
            db.initialize()
            break
        except Exception:
            if attempt == 29:
                raise RuntimeError("database initialization failed") from None
            time.sleep(2)
    server = ThreadingHTTPServer(("0.0.0.0", int(os.getenv("PORT","8000"))),
                                handler_for(db, Metrics()))
    server.serve_forever()

if __name__ == "__main__":
    main()
