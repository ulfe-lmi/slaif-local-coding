"""Pure and fake-upstream conformance tests for signed gateway identity v1."""

from __future__ import annotations

import asyncio
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import httpx
import pytest
from pydantic import ValidationError
from starlette.requests import Request

from slaif_local_coding.app import create_app
from slaif_local_coding.config import (
    CacheConfig,
    CompilerConfig,
    ConstitutionIntegrationConfig,
    GatewayIngressConfig,
    RouteConfig,
    ServerConfig,
    Settings,
    UpstreamConfig,
    validate_signing_secret,
)
from slaif_local_coding.constitution.cache import RequestIdentity
from slaif_local_coding.constitution.pipeline import PipelineResult
from slaif_local_coding.gateway_identity import (
    ReplayProtector,
    SignedIdentityError,
    canonical_identity_bytes,
    expected_signature,
    verify_signed_identity,
)

NOW = 1_700_000_000.0
SERVICE_TOKEN = "synthetic-adapter-service-token"


def _vector() -> dict[str, Any]:
    return json.loads(
        Path("tests/fixtures/gateway/signed_identity_v1_vectors.json").read_text(encoding="utf-8")
    )


def _config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Settings:
    monkeypatch.setenv("TEST_SIGNED_SERVICE_TOKEN", SERVICE_TOKEN)
    monkeypatch.setenv("TEST_SIGNED_SECRET", _vector()["secret"]["value"])
    monkeypatch.setenv("TEST_SIGNED_UPSTREAM", "synthetic-upstream-secret")
    monkeypatch.setenv("TEST_SIGNED_COMPILER", "synthetic-compiler-secret")
    return Settings(
        server=ServerConfig(request_body_max_bytes=4096),
        gateway_ingress=GatewayIngressConfig(
            mode="service_bearer_signed_identity_v1",
            service_token_env="TEST_SIGNED_SERVICE_TOKEN",
            signing_secret_env="TEST_SIGNED_SECRET",
            clock_skew_seconds=60,
            replay_ttl_seconds=120,
            max_replay_entries=32,
            nonce_min_length=16,
            nonce_max_length=64,
        ),
        upstream=UpstreamConfig(
            base_url="http://upstream.test/v1",
            api_key_env="TEST_SIGNED_UPSTREAM",
            model="qwen",
        ),
        routes=[
            RouteConfig(
                name="vision",
                model="qwen",
                max_images_per_request=1,
                image_overflow_policy="retain_newest",
                observation_enabled=True,
                constitution_enabled=True,
            )
        ],
        compiler=CompilerConfig(enabled=True, api_key_env="TEST_SIGNED_COMPILER"),
        cache=CacheConfig(root=tmp_path / "cache", fallback_root=tmp_path / "fallback"),
        constitution=ConstitutionIntegrationConfig(
            enabled=True,
            identity_source="signed_request",
        ),
    )


def _request(
    *,
    body: bytes,
    headers: list[tuple[str, str]],
    path: str = "/v1/responses",
    query: bytes = b"b=2&a=1",
    method: str = "POST",
) -> Request:
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "raw_path": path.encode("ascii"),
        "query_string": query,
        "headers": [
            (name.lower().encode("ascii"), value.encode("ascii")) for name, value in headers
        ],
        "client": ("127.0.0.1", 1),
        "server": ("127.0.0.1", 18031),
    }
    return Request(
        scope,
        receive=lambda: {"type": "http.request", "body": body, "more_body": False},
    )


def _identity_headers(
    config: Settings,
    *,
    body: bytes,
    principal: str = "principal-a",
    session: str = "session-a",
    repository: str = "repository-a",
    route: str = "vision",
    nonce: str = "nonce-0123456789",
    timestamp: int = int(NOW),
    query: bytes = b"b=2&a=1",
    path: str = "/v1/responses",
    method: str = "POST",
    secret: bytes | None = None,
) -> list[tuple[str, str]]:
    timestamp_text = str(timestamp)
    canonical = canonical_identity_bytes(
        method=method,
        path=path,
        raw_query=query,
        body=body,
        principal=principal,
        session=session,
        repository=repository,
        route=route,
        timestamp=timestamp_text,
        nonce=nonce,
    )
    signature = expected_signature(
        secret=secret or config.gateway_ingress.signing_secret(), canonical=canonical
    )
    return [
        ("Authorization", f"Bearer {SERVICE_TOKEN}"),
        ("X-SLAIF-Identity-Version", "v1"),
        ("X-SLAIF-Principal", principal),
        ("X-SLAIF-Session", session),
        ("X-SLAIF-Repository", repository),
        ("X-SLAIF-Route", route),
        ("X-SLAIF-Timestamp", timestamp_text),
        ("X-SLAIF-Nonce", nonce),
        ("X-SLAIF-Signature", signature),
    ]


def _verify(
    config: Settings,
    *,
    body: bytes = b'{"model":"qwen"}',
    headers: list[tuple[str, str]] | None = None,
    nonce: str = "nonce-0123456789",
    timestamp: int = int(NOW),
    now: float = NOW,
) -> RequestIdentity:
    request_headers = headers or _identity_headers(
        config, body=body, nonce=nonce, timestamp=timestamp
    )
    return verify_signed_identity(
        _request(body=body, headers=request_headers),
        body,
        config.gateway_ingress,
        ReplayProtector(ttl_seconds=120, max_entries=32),
        now=now,
    )


def test_canonical_bytes_are_exact_and_secret_encoding_is_bounded(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _config(tmp_path, monkeypatch)
    vector = _vector()
    canonical = canonical_identity_bytes(
        method="POST",
        path="/v1/responses",
        raw_query=b"b=2&a=1",
        body=b'{"model":"qwen"}',
        principal="principal-a",
        session="session-a",
        repository="repository-a",
        route="vision",
        timestamp="1700000000",
        nonce="nonce-0123456789",
    )
    assert canonical.endswith(b"nonce-0123456789")
    assert b"\n\n" not in canonical
    assert hashlib.sha256(canonical).hexdigest() == vector["canonical_string_sha256"]
    assert (
        expected_signature(secret=vector["secret"]["value"].encode(), canonical=canonical)
        == vector["expected_hmac"]
    )
    assert hashlib.sha256(b'{"model":"qwen"}').hexdigest() == vector["request"]["body_sha256"]
    assert vector["secret"]["identifier"].startswith("fixture-only-")
    assert validate_signing_secret(vector["secret"]["value"]) == vector["secret"]["value"].encode()
    with pytest.raises(ValueError):
        validate_signing_secret("short")
    with pytest.raises(ValueError):
        validate_signing_secret("x" * 4097)


@pytest.mark.parametrize(
    "mutator",
    [
        lambda headers: headers + [("X-SLAIF-Principal", "duplicate")],
        lambda headers: [item for item in headers if item[0].lower() != "x-slaif-nonce"],
        lambda headers: [
            (name, "bad value" if name.lower() == "x-slaif-principal" else value)
            for name, value in headers
        ],
        lambda headers: [
            (name, "1700000000" if name.lower() == "x-slaif-nonce" else value)
            for name, value in headers
        ],
        lambda headers: headers + [("X-SLAIF-Extra", "rejected")],
    ],
)
def test_header_grammar_duplicate_and_extra_fields_fail_without_exception_leak(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mutator: Any
) -> None:
    config = _config(tmp_path, monkeypatch)
    body = b'{"model":"qwen"}'
    headers = mutator(_identity_headers(config, body=body))
    with pytest.raises(SignedIdentityError) as error:
        _verify(config, body=body, headers=headers)
    assert error.value.status_code == 422
    assert "principal-a" not in str(error.value)


def test_header_names_are_case_insensitive_and_identity_is_immutable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = _config(tmp_path, monkeypatch)
    body = b'{"model":"qwen"}'
    headers = [
        (name.upper(), value)
        for name, value in _identity_headers(config, body=body, nonce="nonce-uppercase1")
    ]
    identity = _verify(config, body=body, headers=headers, nonce="nonce-uppercase1")
    assert identity == RequestIdentity(
        principal="principal-a", session="session-a", repository="repository-a", route="vision"
    )
    with pytest.raises(ValidationError):
        identity.principal = "changed"  # type: ignore[misc]


def test_signature_binds_body_query_path_method_identity_and_route(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = _config(tmp_path, monkeypatch)
    original = _identity_headers(config, body=b"original", nonce="nonce-bindings")
    for body, query, path, method in (
        (b"changed", b"b=2&a=1", "/v1/responses", "POST"),
        (b"original", b"a=1&b=2", "/v1/responses", "POST"),
        (b"original", b"b=2&a=1", "/v1/models", "POST"),
        (b"original", b"b=2&a=1", "/v1/responses", "GET"),
    ):
        with pytest.raises(SignedIdentityError) as error:
            verify_signed_identity(
                _request(body=body, headers=original, query=query, path=path, method=method),
                body,
                config.gateway_ingress,
                ReplayProtector(ttl_seconds=120, max_entries=32),
                now=NOW,
            )
        assert error.value.status_code in {403, 422}


def test_invalid_signature_does_not_reserve_nonce_and_clock_edges_are_inclusive(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = _config(tmp_path, monkeypatch)
    body = b'{"model":"qwen"}'
    valid = _identity_headers(config, body=body, nonce="nonce-invalid-first")
    invalid = [
        (name, "v1=" + "0" * 64 if name.lower() == "x-slaif-signature" else value)
        for name, value in valid
    ]
    replay = ReplayProtector(ttl_seconds=120, max_entries=32)
    with pytest.raises(SignedIdentityError) as error:
        verify_signed_identity(
            _request(body=body, headers=invalid), body, config.gateway_ingress, replay, now=NOW
        )
    assert error.value.code == "signed_identity_signature_mismatch"
    identity = verify_signed_identity(
        _request(body=body, headers=valid), body, config.gateway_ingress, replay, now=NOW
    )
    assert identity.principal == "principal-a"

    edge = _identity_headers(config, body=body, nonce="nonce-edge-window", timestamp=int(NOW + 60))
    assert (
        verify_signed_identity(
            _request(body=body, headers=edge),
            body,
            config.gateway_ingress,
            ReplayProtector(ttl_seconds=120, max_entries=32),
            now=NOW,
        ).route
        == "vision"
    )

    stale = _identity_headers(config, body=body, nonce="nonce-stale-0123", timestamp=int(NOW - 61))
    with pytest.raises(SignedIdentityError) as error:
        verify_signed_identity(
            _request(body=body, headers=stale),
            body,
            config.gateway_ingress,
            ReplayProtector(ttl_seconds=120, max_entries=32),
            now=NOW,
        )
    assert error.value.code == "signed_identity_timestamp_out_of_window"


def test_replay_is_atomic_and_bounded_with_ttl_and_lru() -> None:
    replay = ReplayProtector(ttl_seconds=10, max_entries=2)
    first = hashlib.sha256(b"one").hexdigest()
    second = hashlib.sha256(b"two").hexdigest()
    third = hashlib.sha256(b"three").hexdigest()
    assert replay.reserve(first, now=100.0)
    assert replay.reserve(second, now=100.0)
    assert not replay.reserve(first, now=100.0)
    assert replay.reserve(third, now=100.0)
    assert replay.size == 2
    assert replay.reserve(first, now=111.0)
    assert replay.size == 1

    concurrent = ReplayProtector(ttl_seconds=10, max_entries=32)
    digest = hashlib.sha256(b"concurrent").hexdigest()

    def reserve() -> bool:
        return concurrent.reserve(digest, now=200.0)

    with ThreadPoolExecutor(max_workers=16) as pool:
        results = list(pool.map(lambda _item: reserve(), range(64)))
    assert sum(results) == 1


@pytest.mark.asyncio
async def test_signed_service_auth_route_gate_and_header_stripping(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    settings = _config(tmp_path, monkeypatch)
    observed: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        assert request.headers["authorization"] == "Bearer synthetic-upstream-secret"
        assert not any(name.startswith("x-slaif-") for name in request.headers)
        return httpx.Response(200, json={"ok": True})

    app = create_app(settings, httpx.MockTransport(handler), signed_identity_clock=lambda: NOW)
    body = b'{"model":"qwen","input":"synthetic"}'
    headers = _identity_headers(settings, body=body, nonce="nonce-app-success")
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
    ) as client:
        response = await client.post("/v1/responses?b=2&a=1", content=body, headers=headers)
    assert response.status_code == 200
    assert len(observed) == 1


@pytest.mark.asyncio
async def test_signed_route_mismatch_and_bad_signature_do_no_upstream_work(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    settings = _config(tmp_path, monkeypatch)
    calls = 0

    async def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(200, json={})

    app = create_app(settings, httpx.MockTransport(handler), signed_identity_clock=lambda: NOW)
    body = b'{"model":"qwen","input":"synthetic"}'
    mismatch = _identity_headers(settings, body=body, route="other-route", nonce="nonce-route-0123")
    bad = [
        (name, "v1=" + "f" * 64 if name.lower() == "x-slaif-signature" else value)
        for name, value in _identity_headers(settings, body=body, nonce="nonce-bad-012345")
    ]
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
    ) as client:
        mismatch_response = await client.post(
            "/v1/responses?b=2&a=1", content=body, headers=mismatch
        )
        bad_response = await client.post("/v1/responses?b=2&a=1", content=body, headers=bad)
    assert mismatch_response.status_code == 403
    assert mismatch_response.json()["error"]["code"] == "signed_identity_route_mismatch"
    assert bad_response.status_code == 403
    assert calls == 0
    assert "principal-a" not in mismatch_response.text
    assert "nonce-route-0123" not in mismatch_response.text


@pytest.mark.asyncio
async def test_verified_identity_is_explicitly_passed_to_each_pipeline_request(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    settings = _config(tmp_path, monkeypatch)

    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"ok": True})

    app = create_app(settings, httpx.MockTransport(handler), signed_identity_clock=lambda: NOW)
    pipeline = app.state.constitution_pipeline
    assert pipeline is not None
    captured: list[RequestIdentity] = []

    async def capture(**kwargs: Any) -> PipelineResult:
        captured.append(kwargs["request_identity"])
        return PipelineResult(
            payload=kwargs["payload"],
            body=kwargs["post_image_body"],
            injected=False,
            state="skipped",
            reason="test_capture",
        )

    pipeline.process = capture  # type: ignore[method-assign]
    body = b'{"model":"qwen","input":"synthetic"}'
    first = _identity_headers(
        settings,
        body=body,
        principal="principal-a",
        session="session-a",
        repository="repository-a",
        nonce="nonce-identity-01",
    )
    second = _identity_headers(
        settings,
        body=body,
        principal="principal-b",
        session="session-b",
        repository="repository-b",
        nonce="nonce-identity-02",
    )
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
    ) as client:
        results = await asyncio.gather(
            client.post("/v1/responses?b=2&a=1", content=body, headers=first),
            client.post("/v1/responses?b=2&a=1", content=body, headers=second),
        )
    assert [response.status_code for response in results] == [200, 200]
    assert {(item.principal, item.session, item.repository) for item in captured} == {
        ("principal-a", "session-a", "repository-a"),
        ("principal-b", "session-b", "repository-b"),
    }


@pytest.mark.asyncio
async def test_signed_secret_unavailable_is_readiness_503_and_rotation_is_explicit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    settings = _config(tmp_path, monkeypatch)
    body = b'{"model":"qwen"}'
    old = _identity_headers(settings, body=body, nonce="nonce-old-secret")
    monkeypatch.setenv("TEST_SIGNED_SECRET", "R" * 32)

    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={})

    app = create_app(settings, httpx.MockTransport(handler), signed_identity_clock=lambda: NOW)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
    ) as client:
        rejected = await client.post("/v1/responses", content=body, headers=old)
        monkeypatch.delenv("TEST_SIGNED_SECRET")
        unavailable = await client.post("/v1/responses", content=body, headers=old)
    assert rejected.status_code == 403
    assert unavailable.status_code == 503
    assert "TEST_SIGNED_SECRET" not in unavailable.text


def test_signed_settings_reject_static_fallback_and_preserve_other_modes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    with pytest.raises(ValueError):
        GatewayIngressConfig(
            mode="service_bearer_static_identity",
            service_token_env="SERVICE",
            signing_secret_env="SIGNING",
        )
    with pytest.raises(ValueError):
        ConstitutionIntegrationConfig(enabled=True, identity_source="signed_request", principal="p")
    static = GatewayIngressConfig(
        mode="service_bearer_static_identity", service_token_env="SERVICE"
    )
    assert static.enabled and not static.signed
    assert GatewayIngressConfig().mode == "disabled"
