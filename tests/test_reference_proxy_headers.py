"""Reference-proxy header regressions; no listener or upstream connection."""

from __future__ import annotations

import importlib.util
import io
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest


def reference_proxy() -> ModuleType:
    path = Path(__file__).resolve().parents[1] / "references/qwen38_vision_image_cap_proxy.py"
    spec = importlib.util.spec_from_file_location("reference_proxy", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def forward(monkeypatch: pytest.MonkeyPatch, headers: list[tuple[str, str]]) -> bytes:
    module = reference_proxy()
    response = SimpleNamespace(
        status=200,
        reason="OK\r\nInjected-Reason: bad",
        getheaders=lambda: headers,
        read=lambda size: b"",
    )
    connection = SimpleNamespace(
        request=lambda *args, **kwargs: None,
        getresponse=lambda: response,
        close=lambda: None,
    )
    monkeypatch.setattr(module.http.client, "HTTPConnection", lambda *a, **kw: connection)
    handler = object.__new__(module.Proxy)
    handler.command = "GET"
    handler.path = "/v1/models"
    handler.request_version = "HTTP/1.1"
    handler.requestline = "GET /v1/models HTTP/1.1"
    handler.headers = {"Content-Length": "0"}
    handler.rfile = io.BytesIO()
    handler.wfile = io.BytesIO()
    handler._forward()
    return bytes(handler.wfile.getvalue())


@pytest.mark.parametrize(
    "header",
    [
        ("X-Test\r\nInjected: bad", "value"),
        ("X-Test\nInjected", "value"),
        ("X-Test", "value\r\nInjected: bad"),
        ("X-Test", "value\nInjected: bad"),
        ("X-Test", "value\rInjected: bad"),
        ("Bad:Name", "value"),
        ("Bad Name", "value"),
        ("", "value"),
    ],
)
def test_invalid_response_headers_rejected_before_response_starts(
    monkeypatch: pytest.MonkeyPatch, header: tuple[str, str]
) -> None:
    wire = forward(monkeypatch, [("X-Valid", "ok"), header])
    assert wire.startswith(b"HTTP/1.0 502 ")
    assert b"Injected" not in wire
    assert b"X-Valid" not in wire
    assert b"HTTP/1.0 200" not in wire


def test_valid_headers_forwarded_and_upstream_reason_never_echoed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    wire = forward(monkeypatch, [("Content-Type", "application/json"), ("Connection", "bad")])
    assert wire.startswith(b"HTTP/1.0 200 OK\r\n")
    assert b"Content-Type: application/json\r\n" in wire
    assert b"Connection: close\r\n" in wire
    assert b"Connection: bad" not in wire
    assert b"Injected-Reason" not in wire
