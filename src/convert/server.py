"""Minimal HTTP microservice for convert.

Exposes the existing convert logic over HTTP on localhost.
No auth, TLS, rate-limiting, or external network access.
"""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# Import converters to register them (mirrors convert.cli).
import convert.converters  # noqa: F401
from convert.models import ConversionRequest, ConversionResult
from convert.registry import registry

_DEFAULT_PORT = 8080
_HOST = "127.0.0.1"


def _port_from_env() -> int:
    """Return the port from CONVERT_PORT env var, falling back to 8080."""
    return int(os.environ.get("CONVERT_PORT", str(_DEFAULT_PORT)))


class _ConvertServer(ThreadingHTTPServer):
    """ThreadingHTTPServer with daemon threads and address reuse."""

    daemon_threads = True
    allow_reuse_address = True


class ConvertHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the convert microservice."""

    def do_GET(self):
        if self.path == "/health":
            body = b"OK"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/convert":
            self._send_json(404, {"error": "not found"})
            return

        length = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(length) if length else b""

        try:
            data = json.loads(raw.decode("utf-8")) if raw else {}
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
            self._send_json(400, {"error": "invalid JSON"})
            return

        if not isinstance(data, dict):
            self._send_json(400, {"error": "invalid JSON: body must be an object"})
            return

        source = data.get("source")
        fmt = data.get("format")
        target = data.get("target")

        missing = [
            name for name, value in (("source", source), ("format", fmt), ("target", target))
            if not value
        ]
        if missing:
            self._send_json(400, {"error": f"missing fields: {', '.join(missing)}"})
            return

        src_fmt = Path(str(source)).suffix.lstrip(".")
        dst_fmt = str(fmt)

        converter = registry.get(src_fmt, dst_fmt)
        if converter is None:
            self._send_json(
                400,
                {"error": f"No converter registered for {src_fmt} -> {dst_fmt}"},
            )
            return

        source_path = Path(str(source))
        target_path = Path(str(target))

        try:
            source_path.read_text(encoding="utf-8")
        except OSError as exc:
            self._send_json(400, {"error": f"cannot read source: {exc}"})
            return

        request = ConversionRequest(
            source_path=source_path,
            target_path=target_path,
            src_fmt=src_fmt,
            dst_fmt=dst_fmt,
        )

        try:
            result: ConversionResult = converter(request)
        except Exception as exc:  # noqa: BLE001 - report conversion errors as HTTP 400
            self._send_json(400, {"error": f"conversion failed: {exc}"})
            return

        try:
            output = result.output_path.read_text(encoding="utf-8")
        except OSError as exc:
            self._send_json(500, {"error": f"cannot read output: {exc}"})
            return

        self._send_json(
            200,
            {
                "content": output,
                "target": str(result.output_path),
                "message": result.message,
            },
        )

    def _send_json(self, status: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):  # noqa: ARG002 - silence default request logging
        return


def make_server(port: int | None = None) -> _ConvertServer:
    """Build (but do not start) an HTTP server bound to localhost."""
    if port is None:
        port = _port_from_env()
    return _ConvertServer((_HOST, port), ConvertHandler)


def run(port: int | None = None) -> None:
    """Serve forever on localhost (Ctrl-C to stop)."""
    server = make_server(port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    run()
