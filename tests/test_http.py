"""Tests for the HTTP microservice (convert.server).

Uses the standard library only (urllib.request) so no extra dependencies are
required. A real ThreadingHTTPServer is bound to localhost port 0 for each
test and shut down afterwards.
"""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request

import pytest

from convert.server import make_server


class _Server:
    """A ThreadingHTTPServer running on a free localhost port in a daemon thread."""

    def __init__(self):
        self.server = make_server(0)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def url(self, path: str = "/") -> str:
        return f"http://127.0.0.1:{self.port}{path}"

    def shutdown(self):
        self.server.shutdown()
        self.server.server_close()


@pytest.fixture
def http_server():
    server = _Server()
    try:
        yield server
    finally:
        server.shutdown()


def _request(server, method, path, body=None, content_type="application/json"):
    data = None
    headers = {}
    if body is not None:
        if isinstance(body, str):
            data = body.encode("utf-8")
        else:
            data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = content_type
    req = urllib.request.Request(server.url(path), data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, resp.read().decode("utf-8"), dict(resp.headers)
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8"), dict(exc.headers)


def _json_body(body_text: str):
    return json.loads(body_text)


def test_health_returns_ok(http_server):
    status, body, _ = _request(http_server, "GET", "/health")
    assert status == 200
    assert body == "OK"


def test_health_content_type_plain(http_server):
    status, _, headers = _request(http_server, "GET", "/health")
    assert status == 200
    assert "text/plain" in headers.get("Content-Type", "")


def test_convert_txt_to_md(http_server, tmp_path):
    src = tmp_path / "in.txt"
    src.write_text("plain text", encoding="utf-8")
    target = tmp_path / "out.md"

    status, body, headers = _request(
        http_server,
        "POST",
        "/convert",
        {"source": str(src), "format": "md", "target": str(target)},
    )
    assert status == 200
    assert "application/json" in headers.get("Content-Type", "")
    payload = _json_body(body)
    assert payload["content"] == "plain text"
    assert payload["target"] == str(target)
    assert target.exists()
    assert target.read_text(encoding="utf-8") == "plain text"


def test_convert_md_to_txt_strips_markdown(http_server, tmp_path):
    src = tmp_path / "in.md"
    src.write_text("# Title\n\n**bold** text", encoding="utf-8")
    target = tmp_path / "out.txt"

    status, body, _ = _request(
        http_server,
        "POST",
        "/convert",
        {"source": str(src), "format": "txt", "target": str(target)},
    )
    assert status == 200
    payload = _json_body(body)
    assert "Title" in payload["content"]
    assert "bold" in payload["content"]
    assert "#" not in payload["content"]
    assert "**" not in payload["content"]


def test_convert_invalid_json(http_server):
    status, body, headers = _request(
        http_server,
        "POST",
        "/convert",
        body="not json at all",
        content_type="application/json",
    )
    assert status == 400
    assert "application/json" in headers.get("Content-Type", "")
    assert "invalid JSON" in _json_body(body)["error"]


def test_convert_empty_body(http_server):
    # An empty body is treated as "no body" -> missing required fields.
    status, body, _ = _request(http_server, "POST", "/convert", body="")
    assert status == 400
    assert "missing fields" in _json_body(body)["error"]


def test_convert_missing_fields(http_server):
    status, body, _ = _request(http_server, "POST", "/convert", body={})
    assert status == 400
    error = _json_body(body)["error"]
    assert "missing fields" in error
    for field in ("source", "format", "target"):
        assert field in error


def test_convert_partial_missing_fields(http_server):
    status, body, _ = _request(
        http_server, "POST", "/convert", body={"source": "in.txt", "format": "md"}
    )
    assert status == 400
    assert "target" in _json_body(body)["error"]


def test_convert_non_object_body(http_server):
    status, body, _ = _request(http_server, "POST", "/convert", body=[1, 2, 3])
    assert status == 400
    assert "body must be an object" in _json_body(body)["error"]


def test_convert_unknown_format(http_server, tmp_path):
    src = tmp_path / "in.txt"
    src.write_text("hello", encoding="utf-8")
    target = tmp_path / "out.xyz"

    status, body, _ = _request(
        http_server,
        "POST",
        "/convert",
        {"source": str(src), "format": "xyz", "target": str(target)},
    )
    assert status == 400
    assert "No converter registered" in _json_body(body)["error"]


def test_convert_source_not_found(http_server, tmp_path):
    target = tmp_path / "out.md"
    status, body, _ = _request(
        http_server,
        "POST",
        "/convert",
        {"source": str(tmp_path / "does-not-exist.txt"), "format": "md", "target": str(target)},
    )
    assert status == 400
    assert "cannot read source" in _json_body(body)["error"]


def test_convert_unknown_path_returns_404(http_server):
    status, body, _ = _request(http_server, "POST", "/convert2", body={})
    assert status == 404
    assert "not found" in _json_body(body)["error"]

    status, body, _ = _request(http_server, "GET", "/nope")
    assert status == 404


def test_convert_invalid_json_dict_key(http_server):
    """Body is valid JSON but not a dict at top level."""
    status, body, _ = _request(http_server, "POST", "/convert", body='"just a string"')
    assert status == 400
    assert "body must be an object" in _json_body(body)["error"]


def test_convert_converter_raises(http_server, tmp_path, monkeypatch):
    """A converter that raises is reported as a 400 conversion failure."""
    src = tmp_path / "in.txt"
    src.write_text("hello", encoding="utf-8")
    target = tmp_path / "out.md"

    def boom(req):  # noqa: ARG001
        raise RuntimeError("boom")

    monkeypatch.setattr("convert.server.registry.get", lambda src, dst: boom)

    status, body, _ = _request(
        http_server,
        "POST",
        "/convert",
        {"source": str(src), "format": "md", "target": str(target)},
    )
    assert status == 400
    assert "conversion failed" in _json_body(body)["error"]
    assert "boom" in _json_body(body)["error"]


def test_convert_json_has_message(http_server, tmp_path):
    src = tmp_path / "in.txt"
    src.write_text("hello world", encoding="utf-8")
    target = tmp_path / "out.md"

    status, body, _ = _request(
        http_server,
        "POST",
        "/convert",
        {"source": str(src), "format": "md", "target": str(target)},
    )
    assert status == 200
    assert "message" in _json_body(body)
