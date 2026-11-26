"""Bounded fake tests for the 024-a v1 actual-model qualification probe.

The module under test is the opt-in executable
``scripts/v1_actual_model_probe.py``.  These tests exercise it at its
software boundary with fake transports only:

- the full bounded synthetic session through the ACTUAL ``create_app``
  entry point (fake upstream transport, synthetic identity), proving
  actual forwarded-body replacement, required compiled context,
  compiler work/reuse and the endpoint result as bounded content-free
  facts;
- the closed specification, endpoint, artifact-identity, TOML and
  run-lock laws;
- the child-scoped 18031 listener-ownership proof;
- the streaming behavior at event granularity, with the
  close-after-first-event outcome directly observed.

No live inference, no Codex/model-client startup, no protected-fixture
contact.  The opt-in real-invocation layer is the separate
``SLAIF_LIVE_TEST=1`` gate in ``tests/test_live.py``.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import time
import tomllib
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

import httpx
import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
_probe_spec_loader = importlib.util.spec_from_file_location(
    "v1_actual_model_probe", _REPO_ROOT / "scripts" / "v1_actual_model_probe.py"
)
assert _probe_spec_loader is not None and _probe_spec_loader.loader is not None
probe = importlib.util.module_from_spec(_probe_spec_loader)
sys.modules["v1_actual_model_probe"] = probe
_probe_spec_loader.loader.exec_module(probe)

from slaif_local_coding.app import create_app  # noqa: E402
from slaif_local_coding.constitution.bundles.bundle_compiler import (  # noqa: E402
    serialize_compiled_index,
)
from tests.test_app import _v1_settings  # noqa: E402
from tests.test_v1_application import _completion_bytes, _index_for_demand  # noqa: E402

RUN_ID = "0" * 32
PEER_URL = f"http://{probe.PEER_HOST}:{probe.PEER_PORT}/v1"


def _probe_spec(**overrides: Any) -> probe.V1CandidateSpec:  # type: ignore[name-defined]
    kwargs: dict[str, Any] = {
        "declared_model": probe.DEFAULT_DECLARED_MODEL,
        "run_id": RUN_ID,
        "upstream_base_url": PEER_URL,
        "compiler_base_url": PEER_URL,
    }
    kwargs.update(overrides)
    return probe.V1CandidateSpec(**kwargs)


def _refused(call: Any) -> str | None:
    try:
        call()
        return None
    except probe.V1ProbeRefusal as exc:
        return exc.token  # type: ignore[no-any-return]


# -- Closed specification and artifact laws ------------------------------


class TestV1ProbeSpec:
    def test_valid_spec_and_allowed_endpoints(self) -> None:
        spec = _probe_spec()
        spec.validate()
        for path in probe.ALLOWED_MAIN_ENDPOINTS + probe.ALLOWED_OBSERVATION_ENDPOINTS:
            spec.check_endpoint(path)

    @pytest.mark.parametrize(
        ("overrides", "token"),
        [
            ({"declared_model": "other-model"}, probe.REFUSAL_SPEC_INVALID),
            ({"run_id": "xyz"}, probe.REFUSAL_SPEC_INVALID),
            (
                {"upstream_base_url": "http://127.0.0.1:18020/v1"},
                probe.REFUSAL_NON_LOOPBACK_UPSTREAM,
            ),
            (
                {"compiler_base_url": "http://[::1]:18032/v1"},
                probe.REFUSAL_NON_LOOPBACK_UPSTREAM,
            ),
            (
                {"upstream_base_url": "https://127.0.0.1:18032/v1"},
                probe.REFUSAL_NON_LOOPBACK_UPSTREAM,
            ),
            (
                {"upstream_base_url": "http://user:pass@127.0.0.1:18032/v1"},
                probe.REFUSAL_SPEC_INVALID,
            ),
            (
                {"compiler_base_url": "http://127.0.0.1:18032/v1?debug=1"},
                probe.REFUSAL_SPEC_INVALID,
            ),
            (
                {"compiler_base_url": "http://127.0.0.1:18032/v1#frag"},
                probe.REFUSAL_SPEC_INVALID,
            ),
            (
                {"upstream_base_url": "http://127.0.0.1:18032/v2"},
                probe.REFUSAL_SPEC_INVALID,
            ),
            ({"max_main_requests": 0}, probe.REFUSAL_SPEC_INVALID),
            (
                {"max_main_requests": probe.MAX_MAIN_REQUESTS_CEILING + 1},
                probe.REFUSAL_SPEC_INVALID,
            ),
            ({"max_response_bytes": 0}, probe.REFUSAL_SPEC_INVALID),
            (
                {"request_timeout_seconds": float("inf")},
                probe.REFUSAL_SPEC_INVALID,
            ),
            ({"total_budget_seconds": -1.0}, probe.REFUSAL_SPEC_INVALID),
        ],
    )
    def test_spec_refusals(self, overrides: dict[str, Any], token: str) -> None:
        assert _refused(_probe_spec(**overrides).validate) == token

    def test_unsupported_endpoint_refused(self) -> None:
        assert _refused(lambda: _probe_spec().check_endpoint("/v1/responses")) is None
        assert (
            _refused(lambda: _probe_spec().check_endpoint("/v1/responses/compact"))
            == probe.REFUSAL_UNSUPPORTED_ENDPOINT
        )

    def test_refusal_vocabulary_is_closed_and_kept(self) -> None:
        # The credential-reference token stays in the closed
        # vocabulary even though the fixed synthetic names make it
        # unreachable.
        assert probe.REFUSAL_UNRESOLVABLE_CREDENTIAL in probe.REFUSAL_TOOLS
        for token in probe.REFUSAL_TOOLS:
            assert token.startswith("v1-probe-")

    def test_artifact_identity_laws(self, tmp_path: Path) -> None:
        wheel = tmp_path / "wheel.whl"
        wheel.write_bytes(b"synthetic-wheel-bytes")
        good = hashlib.sha256(wheel.read_bytes()).hexdigest()
        probe.verify_artifact_identity(wheel, good)
        assert (
            _refused(lambda: probe.verify_artifact_identity(wheel, "0" * 64))
            == probe.REFUSAL_ARTIFACT_MISMATCH
        )
        assert (
            _refused(lambda: probe.verify_artifact_identity(tmp_path / "missing.whl", good))
            == probe.REFUSAL_ARTIFACT_MISMATCH
        )
        assert (
            _refused(lambda: probe.verify_artifact_identity(wheel, "zz"))
            == probe.REFUSAL_SPEC_INVALID
        )

    def test_toml_builder_is_closed(self, tmp_path: Path) -> None:
        recovery = tmp_path / "recovery"
        cfg = tomllib.loads(probe.build_candidate_config_toml(_probe_spec(), recovery))
        assert cfg["server"]["listen_host"] == "127.0.0.1"
        assert cfg["server"]["listen_port"] == 18031
        assert cfg["upstream"]["base_url"] == PEER_URL
        assert cfg["upstream"]["api_key_env"] == probe.V1_PROBE_UPSTREAM_KEY_ENV
        assert cfg["upstream"]["model"] == probe.DEFAULT_DECLARED_MODEL
        assert cfg["context_cache"]["profile"] == "dependency-bundles-v1"
        assert cfg["context_cache"]["workers"] == 1
        assert cfg["context_cache"]["marker_key_env"] == probe.V1_PROBE_MARKER_KEY_ENV
        compiler = cfg["context_cache"]["compiler"]
        assert compiler["api_key_env"] == probe.V1_PROBE_COMPILER_KEY_ENV
        assert compiler["model_revision"] == probe.PINNED_REVISION
        assert cfg["context_cache"]["recovery"]["root"] == str(recovery)
        # No generated credential value may appear in the file: only
        # the three fixed environment names.
        text = probe.build_candidate_config_toml(_probe_spec(), recovery)
        for name in (
            probe.V1_PROBE_UPSTREAM_KEY_ENV,
            probe.V1_PROBE_COMPILER_KEY_ENV,
            probe.V1_PROBE_MARKER_KEY_ENV,
        ):
            assert name in text
            assert text.count(name) == 1


# -- The serial run lock --------------------------------------------------


class TestV1ProbeRunLock:
    def test_preexisting_lock_is_refused_and_preserved(self, tmp_path: Path) -> None:
        lockfile = tmp_path / "v1-probe.lock"
        holder = subprocess.Popen([sys.executable, "-c", "import time;time.sleep(30)"])
        try:
            time.sleep(0.2)
            original = f"pid={holder.pid} run_id={'a' * 32}\n"
            lockfile.write_text(original)
            assert (
                _refused(lambda: probe.acquire_run_lock(tmp_path, "b" * 32))
                == probe.REFUSAL_RUN_IN_PROGRESS
            )
            # The live foreign marker is byte-preserved.
            assert lockfile.read_text() == original
        finally:
            holder.terminate()
            holder.wait(timeout=10)
        # A stale (dead-pid) marker is refused the same way: the
        # probe's own state lives in an exactly-owned fresh run
        # directory, so there is no stale-lock takeover.
        stale = f"pid={holder.pid} run_id={'a' * 32}\n"
        assert (
            _refused(lambda: probe.acquire_run_lock(tmp_path, "b" * 32))
            == probe.REFUSAL_RUN_IN_PROGRESS
        )
        assert lockfile.read_text() == stale
        # A malformed marker is refused the same way and preserved.
        lockfile.write_text("not-a-lock")
        assert (
            _refused(lambda: probe.acquire_run_lock(tmp_path, "b" * 32))
            == probe.REFUSAL_RUN_IN_PROGRESS
        )
        assert lockfile.read_text() == "not-a-lock"
        # Once the marker is removed, acquisition succeeds.
        lockfile.unlink()
        acquired = probe.acquire_run_lock(tmp_path, "b" * 32)
        assert acquired.exists()
        # A second acquire in the same process is refused (the file
        # exists) and the own marker stays byte-identical.
        own_bytes = acquired.read_bytes()
        assert (
            _refused(lambda: probe.acquire_run_lock(tmp_path, "c" * 32))
            == probe.REFUSAL_RUN_IN_PROGRESS
        )
        assert acquired.read_bytes() == own_bytes
        # Release removes only this invocation's own marker; a fresh
        # acquire after the release succeeds.
        probe.release_run_lock(acquired)
        assert not acquired.exists()
        again = probe.acquire_run_lock(tmp_path, "c" * 32)
        assert again.exists()
        probe.release_run_lock(again)
        assert not again.exists()


class TestV1ProbeCaptureCap:
    """The closed observation caps: extra traffic is refused without
    retention, and the peers answer it with the typed provider
    fault (the candidate's own failure law applies)."""

    def test_capture_refuses_at_closed_limits(self) -> None:
        capture = probe.V1PeerCapture(max_main_bodies=1, max_compile_texts=1)
        capture.add_main_body(b"one")
        capture.add_compile_user_text("t1")
        assert _refused(lambda: capture.add_main_body(b"two")) == probe.REFUSAL_BUDGET_EXHAUSTED
        assert (
            _refused(lambda: capture.add_compile_user_text("t2")) == probe.REFUSAL_BUDGET_EXHAUSTED
        )
        # The refused additions are not retained.
        assert len(capture.main_bodies) == 1
        assert len(capture.compile_user_texts) == 1

    def test_in_process_peer_answers_500_on_overflow(self) -> None:
        capture = probe.V1PeerCapture(max_main_bodies=1, max_compile_texts=1)
        peer = _FakePeer(capture, probe.DEFAULT_DECLARED_MODEL)
        capture.add_main_body(b"one")
        capture.add_compile_user_text("t1")
        base = f"http://{probe.CANDIDATE_HOST}:{probe.CANDIDATE_PORT}"
        main_response = peer.handle(
            httpx.Request(
                "POST",
                f"{base}/v1/responses",
                content=json.dumps({"model": probe.DEFAULT_DECLARED_MODEL, "input": "x"}).encode(),
            )
        )
        assert main_response.status_code == 500
        assert json.loads(main_response.content)["error"]["type"] == "probe_synthetic_fault"
        assert len(capture.main_bodies) == 1
        compile_response = peer.handle(
            httpx.Request(
                "POST",
                f"{base}/v1/chat/completions",
                content=json.dumps(
                    {
                        "model": probe.DEFAULT_DECLARED_MODEL,
                        "messages": [
                            {"role": "system", "content": "s"},
                            {"role": "user", "content": "demand"},
                        ],
                    }
                ).encode(),
            )
        )
        assert compile_response.status_code == 500
        assert len(capture.compile_user_texts) == 1

    def test_http_peer_refuses_main_overflow(self) -> None:
        # The REAL probe peer (closed 18032): at the selected main
        # budget the next forward is the typed provider fault.
        peer = probe.V1FakePeer(_probe_spec(max_main_requests=1))
        peer.start()
        try:
            with httpx.Client(timeout=10.0, trust_env=False) as client:
                base = f"http://{probe.PEER_HOST}:{probe.PEER_PORT}"
                body = json.dumps({"model": probe.DEFAULT_DECLARED_MODEL, "input": "x"}).encode()
                first = client.post(f"{base}/v1/responses", content=body)
                assert first.status_code == 200
                overflow = client.post(f"{base}/v1/responses", content=body)
                assert overflow.status_code == 500
                assert json.loads(overflow.content)["error"]["type"] == "probe_synthetic_fault"
        finally:
            peer.shutdown()
        assert len(peer.capture.main_bodies) == 1


# -- Child-scoped listener ownership ---------------------------------------

_LISTENER_CODE = (
    "import socket,sys,time\n"
    "s=socket.socket()\n"
    "s.bind(('127.0.0.1',int(sys.argv[1])))\n"
    "s.listen(1)\n"
    "print('READY',flush=True)\n"
    "time.sleep(60)\n"
)


class TestV1ProbeOwnership:
    def test_child_scoped_listener_proof(self, tmp_path: Path) -> None:
        port = 28140
        child = subprocess.Popen(
            [sys.executable, "-c", _LISTENER_CODE, str(port)],
            stdout=subprocess.PIPE,
            text=True,
        )
        try:
            assert child.stdout is not None
            assert child.stdout.readline().strip() == "READY"
            time.sleep(0.2)
            assert probe._child_owns_listener(child, port) is True
            # A closed port has no listener to attribute.
            assert probe._child_owns_listener(child, port + 1) is False
        finally:
            child.terminate()
            child.wait(timeout=10)
        # A dead child's fd directory is gone: not provable.
        assert probe._child_owns_listener(child, port) is False

    def test_foreign_child_is_not_credited_with_a_parent_listener(
        self,
    ) -> None:
        # The parent-owned peer listener must not be attributed to a
        # foreign child (no host-process enumeration).
        peer = probe.V1FakePeer(_probe_spec())
        peer.start()
        foreign = subprocess.Popen([sys.executable, "-c", "import time;time.sleep(30)"])
        try:
            time.sleep(0.3)
            assert probe._child_owns_listener(foreign, probe.PEER_PORT) is False
        finally:
            foreign.terminate()
            foreign.wait(timeout=10)
            peer.shutdown()


# -- The bounded synthetic session on the actual app -----------------------


class _SSEChunkStream(httpx.AsyncByteStream):
    """SSE framing in NATIVE chunks (one per yield): the app-level
    pass-through evidence (the bytes the client receives)."""

    def __init__(self, chunks: list[bytes]) -> None:
        self._chunks = list(chunks)

    async def __aiter__(self) -> AsyncIterator[bytes]:
        for chunk in self._chunks:
            yield chunk


class _CountingSSEStream(httpx.AsyncByteStream):
    """The direct-transport SSE stream: the count increments BEFORE
    each yield and the aclose flag records the stream close, so the
    close-after-first-event outcome is directly observed at the
    probe's own client boundary (no ASGI buffering in between)."""

    def __init__(self, chunks: list[bytes]) -> None:
        self._chunks = list(chunks)
        self.consumed = 0
        self.aclosed = False

    async def __aiter__(self) -> AsyncIterator[bytes]:
        for chunk in self._chunks:
            self.consumed += 1
            yield chunk

    async def aclose(self) -> None:
        self.aclosed = True


def _sse_chunks(body: bytes) -> list[bytes]:
    data: Any = json.loads(body.decode("utf-8"))
    created = {
        "type": "response.created",
        "response": {"id": data.get("id", "resp-sse"), "status": "in_progress"},
    }
    completed = {"type": "response.completed", "response": data}
    return [
        f"data: {json.dumps(created)}\n\n".encode(),
        f"data: {json.dumps(completed)}\n\n".encode(),
        b"data: [DONE]\n\n",
    ]


class _FakePeer:
    """The bounded fake upstream behind the ACTUAL app transport:
    health/models, the main responses (the first one issues the read,
    the exact accepted fixture shape) and the echo compiler (the real
    compiler validation still runs in the product code)."""

    def __init__(
        self,
        capture: probe.V1PeerCapture,  # type: ignore[name-defined]
        declared_model: str,
    ) -> None:
        self.capture = capture
        self.declared_model = declared_model
        self.main_count = 0

    def handle(self, request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if request.method == "GET" and path in ("/health", "/v1/health"):
            return httpx.Response(200, json={"status": "ok"})
        if request.method == "GET" and path in ("/v1/models", "/models"):
            return httpx.Response(
                200,
                json={
                    "object": "list",
                    "data": [{"id": self.declared_model, "object": "model"}],
                },
            )
        if request.method == "POST" and path in ("/v1/responses", "/responses"):
            self.main_count += 1
            count = self.main_count
            try:
                self.capture.add_main_body(request.content)
            except probe.V1ProbeRefusal:
                return httpx.Response(
                    500,
                    json={
                        "error": {
                            "message": "synthetic peer fault",
                            "type": "probe_synthetic_fault",
                        }
                    },
                )
            body = probe._resp_issue_bytes() if count == 1 else probe._resp_plain_bytes(count)
            payload: Any = json.loads(request.content)
            if isinstance(payload, dict) and payload.get("stream"):
                return httpx.Response(
                    200,
                    headers={"content-type": "text/event-stream"},
                    stream=_SSEChunkStream(_sse_chunks(body)),
                )
            return httpx.Response(200, content=body, headers={"content-type": "application/json"})
        if request.method == "POST" and path in ("/v1/chat/completions", "/chat/completions"):
            chat: Any = json.loads(request.content)
            user = str(chat["messages"][1]["content"])
            model = str(chat["model"])
            try:
                self.capture.add_compile_user_text(user)
            except probe.V1ProbeRefusal:
                return httpx.Response(
                    500,
                    json={
                        "error": {
                            "message": "synthetic peer fault",
                            "type": "probe_synthetic_fault",
                        }
                    },
                )
            index = _index_for_demand(user, model)
            return httpx.Response(
                200,
                content=_completion_bytes(serialize_compiled_index(index).decode("utf-8")),
                headers={"content-type": "application/json"},
            )
        return httpx.Response(
            404,
            json={"error": {"message": "synthetic peer fault", "type": "fault"}},
        )


def _app_and_peer(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> tuple[Any, _FakePeer, probe.V1PeerCapture]:  # type: ignore[name-defined]
    monkeypatch.setenv("TEST_V1_MARKER_KEY", "0123456789abcdef0123456789abcdef")
    monkeypatch.setenv("TEST_V1_COMPILER_KEY", "test-only-compiler")
    monkeypatch.setenv("TEST_V1_UPSTREAM_KEY", "test-only-upstream")
    settings = _v1_settings(tmp_path)
    recovery_root = settings.context_cache.recovery.root
    assert recovery_root is not None
    recovery_root.mkdir(mode=0o700, parents=True, exist_ok=True)
    recovery_root.chmod(0o700)
    capture = probe.V1PeerCapture()
    peer = _FakePeer(capture, probe.DEFAULT_DECLARED_MODEL)
    app = create_app(settings, httpx.MockTransport(peer.handle))
    return app, peer, capture


async def _client_for(app: Any) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url=f"http://{probe.CANDIDATE_HOST}:{probe.CANDIDATE_PORT}",
        trust_env=False,
    )


class TestV1ProbeSession:
    async def test_full_bounded_session_on_the_actual_app(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        app, peer, capture = _app_and_peer(monkeypatch, tmp_path)
        spec = _probe_spec()
        async with await _client_for(app) as client:
            facts = await probe.run_v1_probe_session(client=client, spec=spec, capture=capture)

        # Observation pass and the declared model/run identity.
        assert (facts.healthz_status, facts.readyz_status, facts.models_status) == (
            200,
            200,
            200,
        )
        assert facts.model_contract_ok is True
        assert facts.declared_model == probe.DEFAULT_DECLARED_MODEL
        assert facts.run_id == RUN_ID

        # All seven rounds 200; exactly seven main forwards and the
        # two actual compiler calls (root, then the acquired file).
        assert [status for _, status in facts.rounds] == [200] * 7
        assert facts.main_forward_count == 7
        assert facts.compiler_call_count == 2
        assert facts.requests_used == 7
        assert facts.deadline_ok is True

        # r1: the root-only bootstrap — the root span replaced, the
        # required compiled root block injected.
        assert facts.r1_root_source_absent is True
        assert (facts.r1_live_markers, facts.r1_evidence_markers) == (1, 0)
        assert facts.r1_compiled_blocks == 1
        assert facts.r1_region_frame is True

        # r2: the issued read completes — root and file spans replaced.
        assert facts.r2_root_source_absent is True
        assert facts.r2_file_source_absent is True
        assert (facts.r2_live_markers, facts.r2_evidence_markers) == (2, 0)
        assert facts.r2_compiled_blocks == 2
        assert facts.r2_region_frame is True

        # r3: the own transformed body resends to the byte-identical
        # fixed point with zero recompile.
        assert facts.r3_fixed_point is True
        assert facts.r3_new_compiler_calls == 0

        # r4: the source-absent request reconstructs the required
        # compiled working set from RAM.
        assert facts.r4_root_source_absent is True
        assert facts.r4_file_source_absent is True
        assert facts.r4_compiled_blocks == 2
        assert facts.r4_region_frame is True
        assert facts.r4_new_compiler_calls == 0

        # r5: the streamed bootstrap — ordinary SSE preservation, the
        # full stream consumed to completion.
        assert facts.r5_first_event == "response.created"
        assert facts.r5_completed is True
        assert facts.r5_root_source_absent is True
        assert facts.r5_compiled_blocks == 2
        assert facts.r5_region_frame is True

        # r6: the stream closed after the first event — the probe's
        # directly observed client-boundary fact (the first event was
        # parsed and the stream closed before completion).  The
        # close-after-first-event outcome at the wire level is proven
        # by the direct MockTransport case below; the application
        # layer's stream-disconnect behavior (the app closes the owned
        # upstream) is the separate existing app test.
        assert facts.r6_cancelled is True
        assert facts.r6_forward_matches_r2 is True

        # r7: after the cancel the session still replays to the
        # byte-identical fixed point.
        assert facts.r7_fixed_point is True
        assert facts.r7_new_compiler_calls == 0

        # The ACTUAL compiler demands carry the exact decoded sources.
        assert facts.root_demand_carries_root_source is True
        assert facts.root_demand_candidate_count == 1
        assert facts.file_demand_carries_file_source is True
        assert facts.file_demand_foreign_candidate_count == 0

        # The facts are content-free and closed-typed.
        assert facts.to_dict()["schema"] == "v1-probe-facts-v1"
        blob = json.dumps(facts.to_dict(), sort_keys=True)
        for forbidden in (
            probe.ROOT_BODY,
            probe.A_BODY,
            probe.READ_CMD,
            probe.WORKSPACE,
        ):
            assert forbidden not in blob

    async def test_model_contract_mismatch_refuses_before_any_forward(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        app, peer, capture = _app_and_peer(monkeypatch, tmp_path)
        peer.declared_model = "some-other-model"
        spec = _probe_spec()
        async with await _client_for(app) as client:
            with pytest.raises(probe.V1ProbeRefusal) as excinfo:
                await probe.run_v1_probe_session(client=client, spec=spec, capture=capture)
        assert excinfo.value.token == probe.REFUSAL_MODEL_CONTRACT
        assert len(capture.main_bodies) == 0
        assert len(capture.compile_user_texts) == 0

    async def test_main_request_budget_exhausts_at_the_closed_bound(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        app, peer, capture = _app_and_peer(monkeypatch, tmp_path)
        spec = _probe_spec(max_main_requests=3)
        async with await _client_for(app) as client:
            with pytest.raises(probe.V1ProbeRefusal) as excinfo:
                await probe.run_v1_probe_session(client=client, spec=spec, capture=capture)
        assert excinfo.value.token == probe.REFUSAL_BUDGET_EXHAUSTED
        # The refusal happens before the fourth forward: the peer saw
        # exactly three main bodies.
        assert len(capture.main_bodies) == 3


class TestV1ProbeCancellation:
    """The close-after-first-event outcome at the probe's own client
    boundary (direct MockTransport: no ASGI buffering between the
    probe client and the stream).  The existing app stream-disconnect
    test supplies the separate application-layer proof."""

    @staticmethod
    async def _bounded_call(
        stream: _CountingSSEStream, cancel: bool
    ) -> tuple[int, bytes, list[str], bool]:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/responses"
            return httpx.Response(
                200,
                headers={"content-type": "text/event-stream"},
                stream=stream,
            )

        spec = _probe_spec()
        payload = json.dumps({"model": probe.DEFAULT_DECLARED_MODEL, "input": "synthetic"}).encode(
            "utf-8"
        )
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(handler),
            base_url=f"http://{probe.CANDIDATE_HOST}:{probe.CANDIDATE_PORT}",
            trust_env=False,
        ) as client:
            return await probe._request_bounded(  # type: ignore[no-any-return]
                client,
                spec,
                "POST",
                "/v1/responses",
                payload,
                stream=True,
                cancel_after_first_event=cancel,
                deadline=time.monotonic() + 10.0,
                requests_used=[0],
            )

    async def test_close_after_first_event_is_directly_observed(self) -> None:
        chunks = _sse_chunks(probe._resp_plain_bytes(1))
        stream = _CountingSSEStream(chunks)
        status, body, events, cancelled = await self._bounded_call(stream, cancel=True)
        assert status == 200
        assert cancelled is True
        assert events == ["response.created"]
        # Only the first native chunk was consumed and the stream was
        # closed: the response did NOT complete.
        assert stream.consumed == 1
        assert stream.aclosed is True
        assert body == chunks[0]

    async def test_completed_stream_is_consumed_in_full(self) -> None:
        chunks = _sse_chunks(probe._resp_plain_bytes(1))
        stream = _CountingSSEStream(chunks)
        status, body, events, cancelled = await self._bounded_call(stream, cancel=False)
        assert status == 200
        assert cancelled is False
        assert events == ["response.created", "response.completed"]
        assert stream.consumed == len(chunks)
        assert stream.aclosed is True
        assert body == b"".join(chunks)
