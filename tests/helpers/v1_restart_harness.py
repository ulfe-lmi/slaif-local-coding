"""The bounded Python-only v1 app harness for the 023-c real
process-boundary restart case (order 023-c section 2).

Two modes, each a standalone Python process over the SAME protected
test store (fake transports only: no live upstream, no network):

- ``prepare``: prepares MORE THAN ONE persisted session in ONE
  process (two distinct session identities, identical principal /
  repository / fixture bytes), committing a durable protected
  generation per session, and exits cleanly (the composed teardown
  releases the exclusive writers).
- ``resume``: in a FRESH process, resumes ONLY the requested session
  from the same store (selected-address-only reads), performs the
  new-epoch rebuild and the later ordinary hit, and exits.

The harness emits content-free JSON facts (counts, the process ID,
closed outcome names and match booleans; never source, values,
identifiers, paths or credentials) to the ``--out`` path.  Any
assertion failure exits non-zero (the parent test fails closed on
the captured stderr).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
from pathlib import Path
from typing import Any
from unittest import mock

import httpx

from slaif_local_coding.app import create_app
from slaif_local_coding.config import (
    ConstitutionIntegrationConfig,
    ContextCacheConfig,
    ContextCacheRecoveryConfig,
    ContextCacheRouteContract,
    RouteConfig,
    ServerConfig,
    Settings,
    UpstreamConfig,
)
from slaif_local_coding.constitution.bundles.bundle_budget import BundleBudgetConfig
from slaif_local_coding.constitution.bundles.bundle_compiler import (
    BundleCompilerConfig,
)
from slaif_local_coding.constitution.bundles.ram_state_models import RamStateBounds
from slaif_local_coding.constitution.bundles.recovery_store import RecoverySession
from slaif_local_coding.constitution.bundles.v1_application import build_session_address
from slaif_local_coding.constitution.cache import RequestIdentity
from tests.test_causal_history import exec_call, frame, out_item, root_item
from tests.test_v1_application import _echo_compiler_handler

ROOT_BODY = "Follow `docs/A.md` before acting.\n"
A_BODY = "A content.\n"
_ENTRY_CLASS_RE = re.compile(r"entry_class='([a-z_]+)'")


def _settings(store_root: Path, session: str) -> Settings:
    """The closed v1 settings bound to the shared protected store
    root (the operator-prepared 0700 root the store never creates)
    with the explicit per-process session identity."""
    return Settings(
        server=ServerConfig(request_body_max_bytes=4096),
        upstream=UpstreamConfig(
            base_url="http://127.0.0.1:18020/v1",
            api_key_env="TEST_V1_UPSTREAM_KEY",
            model="qwen38-27b",
        ),
        routes=[
            RouteConfig(
                name="text",
                model="qwen38-27b",
                max_images_per_request=0,
                image_overflow_policy="reject",
                observation_enabled=True,
                constitution_enabled=True,
            )
        ],
        constitution=ConstitutionIntegrationConfig(
            enabled=True,
            identity_source="static",
            principal="local-principal",
            session=session,
            repository="local-repository",
        ),
        context_cache=ContextCacheConfig(
            profile="dependency-bundles-v1",
            budget=BundleBudgetConfig(context_tokens=32_768),
            compiler=BundleCompilerConfig(
                model="qwen38-27b",
                base_url="http://127.0.0.1:18020/v1",
                model_revision="a" * 40,
                compatibility_identity="slaif-rtx3090-compat-1",
                api_key_env="TEST_V1_COMPILER_KEY",
            ),
            ram=RamStateBounds(
                session_max_owned_bytes=128 * 1024 * 1024,
                process_max_owned_bytes=512 * 1024 * 1024,
            ),
            recovery=ContextCacheRecoveryConfig(
                enabled=True,
                root=store_root,
            ),
            marker_key_env="TEST_V1_MARKER_KEY",
            route_contracts={
                "text": ContextCacheRouteContract(model="qwen38-27b", context_tokens=32_768)
            },
        ),
    )


def _root_payload() -> dict[str, Any]:
    return {"model": "qwen38-27b", "input": [root_item(ROOT_BODY)]}


def _read_payload() -> dict[str, Any]:
    return {
        "model": "qwen38-27b",
        "input": [
            root_item(ROOT_BODY),
            exec_call("c1", "cat docs/A.md"),
            out_item("c1", frame(A_BODY)),
        ],
    }


def _write_facts(path: Path, facts: dict[str, Any]) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        json.dump(facts, handle, sort_keys=True)


def _texts(data: Any) -> list[str]:
    texts: list[str] = []

    def walk(value: Any) -> None:
        if isinstance(value, str):
            texts.append(value)
        elif isinstance(value, list):
            for item in value:
                walk(item)
        elif isinstance(value, dict):
            for item in value.values():
                walk(item)

    walk(data)
    return texts


async def _prepare_session(store_root: Path, name: str) -> dict[str, Any]:
    settings = _settings(store_root, name)
    captured_main: list[httpx.Request] = []
    captured_compile: list[httpx.Request] = []
    compiler_echo = _echo_compiler_handler(captured_compile)

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/chat/completions":
            return compiler_echo(request)
        assert request.url.path == "/v1/responses"
        n = len(captured_main) + 1
        captured_main.append(request)
        if n == 1:
            return httpx.Response(
                200,
                json={
                    "id": f"resp-{name}-1",
                    "status": "completed",
                    "output": (
                        {
                            "type": "function_call",
                            "id": f"fc-c1-{name}",
                            "call_id": "c1",
                            "name": "exec_command",
                            "arguments": json.dumps({"cmd": "cat docs/A.md"}),
                        },
                    ),
                },
            )
        return httpx.Response(200, json={"id": f"resp-{name}-{n}"})

    app = create_app(settings, httpx.MockTransport(handler))
    assert app.state.v1_runtime is not None
    runtime = app.state.v1_runtime
    identity = RequestIdentity(
        principal="local-principal",
        session=name,
        repository="local-repository",
        route="text",
    )
    address = build_session_address(
        runtime, identity, settings.routes[0], settings.context_cache.route_contracts["text"]
    )
    facts: dict[str, Any] | None = None
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
    ) as client:
        response1 = await client.post("/v1/responses", json=_root_payload())
        assert response1.status_code == 200, response1.text
        response2 = await client.post("/v1/responses", json=_read_payload())
        assert response2.status_code == 200, response2.text
        # Capture the retained state while the app is still
        # alive (the composed teardown clears the session table).
        session = app.state.v1_sessions.get(address)
        assert session is not None, f"prepared session {name} not live"
        assert session.last_publish is not None
        snapshot = session.owner.snapshot
        assert snapshot is not None
        facts = {
            "main_forwards": len(captured_main),
            "compiles": len(captured_compile),
            "generation": session.last_publish.generation,
            "epoch": snapshot.epoch,
            "revision": snapshot.revision,
            "resumed": session.resumed,
        }
    # The composed teardown releases the exclusive writer so a
    # fresh process can own the session.
    async with app.router.lifespan_context(app):
        pass
    assert facts is not None
    return facts


async def _prepare(store_root: Path, sessions: list[str], out: Path) -> int:
    per_session: dict[str, dict[str, Any]] = {}
    for name in sessions:
        per_session[name] = await _prepare_session(store_root, name)
    _write_facts(
        out,
        {"command": "prepare", "pid": os.getpid(), "sessions": per_session},
    )
    return 0


async def _resume(store_root: Path, session: str, out: Path) -> int:
    settings = _settings(store_root, session)
    captured_main: list[httpx.Request] = []
    captured_compile: list[httpx.Request] = []
    compiler_echo = _echo_compiler_handler(captured_compile)

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/chat/completions":
            return compiler_echo(request)
        assert request.url.path == "/v1/responses"
        n = len(captured_main) + 1
        captured_main.append(request)
        return httpx.Response(200, json={"id": f"resp-{session}-r{n}"})

    recorders: list[Any] = []
    loads: list[str] = []
    real_load = RecoverySession.load

    def counting_load(self: RecoverySession, *args: Any, **kwargs: Any) -> Any:
        loads.append(self.address.lineage_key)
        return real_load(self, *args, **kwargs)

    patcher = mock.patch.object(RecoverySession, "load", counting_load)
    patcher.start()
    app = create_app(
        settings,
        httpx.MockTransport(handler),
        v1_stage_observer=recorders.append,
    )
    assert app.state.v1_runtime is not None
    runtime = app.state.v1_runtime
    identity = RequestIdentity(
        principal="local-principal",
        session=session,
        repository="local-repository",
        route="text",
    )
    address = build_session_address(
        runtime, identity, settings.routes[0], settings.context_cache.route_contracts["text"]
    )
    try:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
        ) as client:
            # The FIRST resumed request carries the root envelope but
            # NOT the already-persisted dependency: the ACTUAL
            # compiler demand for that dependency (absent from this
            # request's history) proves it came from recovery -- the
            # direct new-epoch rebuild.
            response1 = await client.post("/v1/responses", json=_root_payload())
            assert response1.status_code == 200, response1.text
            body1 = captured_main[0].content
            # The later ordinary request resends the OWN transformed
            # body: the normal hit with source-absent reinjection,
            # kept as a SEPARATE request fact.  The recovery-content
            # load and compiler counts captured BEFORE and AFTER it
            # make the ordered zero-work claim direct (the normal
            # hit performs no recovery-source content read and no
            # compile).
            loads_before_hit = len(loads)
            compiles_before_hit = len(captured_compile)
            response2 = await client.post(
                "/v1/responses",
                content=body1,
                headers={"content-type": "application/json"},
            )
            assert response2.status_code == 200, response2.text
            loads_after_hit = len(loads)
            compiles_after_hit = len(captured_compile)
            # Capture the retained state while the app is still
            # alive (the composed teardown clears the session table).
            v1_session = app.state.v1_sessions.get(address)
            assert v1_session is not None, "resumed session not live"
            assert v1_session.resumed is True
            snapshot = v1_session.owner.snapshot
            assert snapshot is not None
            resumed_epoch = snapshot.epoch
            resumed_generation = (
                v1_session.last_publish.generation if v1_session.last_publish is not None else None
            )
        async with app.router.lifespan_context(app):
            pass
    finally:
        patcher.stop()
    decoded = json.loads(body1)
    demand_entry_classes: list[str] = []
    for request in captured_compile:
        message = str(json.loads(request.content)["messages"][1]["content"])
        match = _ENTRY_CLASS_RE.search(message)
        assert match is not None, "compiler demand entry class missing"
        demand_entry_classes.append(match.group(1))
    _write_facts(
        out,
        {
            "command": "resume",
            "pid": os.getpid(),
            "resumed": True,
            "epoch": resumed_epoch,
            "generation": resumed_generation,
            "compiles": len(captured_compile),
            "compile_demand_entry_classes": demand_entry_classes,
            "main_forwards": len(captured_main),
            "loads": len(loads),
            "loads_before_hit": loads_before_hit,
            "loads_after_hit": loads_after_hit,
            "compiles_before_hit": compiles_before_hit,
            "compiles_after_hit": compiles_after_hit,
            "all_loads_expected": bool(loads) and all(key == address.lineage_key for key in loads),
            "marker_count": body1.count(b"[slaif-live:v"),
            "compiled_block_count": str(decoded.get("instructions", "")).count(
                "<slaif-compiled-block"
            ),
            "region_present": b"[slaif-compiled-context:v1:" in body1,
            "source_absent": all(A_BODY not in text for text in _texts(decoded)),
            "fixed_point": captured_main[1].content == body1,
            "reuse_r1": [e.outcome for e in recorders[0].events if e.stage.value == "reuse_class"],
            "reuse_r2": [e.outcome for e in recorders[1].events if e.stage.value == "reuse_class"],
        },
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser("prepare")
    prepare.add_argument("--store", required=True, type=Path)
    prepare.add_argument("--out", required=True, type=Path)
    prepare.add_argument("--sessions", required=True, type=str)
    resume = sub.add_parser("resume")
    resume.add_argument("--store", required=True, type=Path)
    resume.add_argument("--out", required=True, type=Path)
    resume.add_argument("--session", required=True, type=str)
    args = parser.parse_args(argv)
    for name in ("TEST_V1_MARKER_KEY", "TEST_V1_COMPILER_KEY", "TEST_V1_UPSTREAM_KEY"):
        assert os.environ.get(name), f"{name} must be set by the parent test"
    store_root = args.store
    assert store_root.is_dir(), "the protected store root must be operator-prepared"
    if args.command == "prepare":
        sessions = args.sessions.split(",")
        assert len(sessions) >= 2, "the prepare mode requires more than one session"
        return asyncio.run(_prepare(store_root, sessions, args.out))
    return asyncio.run(_resume(store_root, args.session, args.out))


if __name__ == "__main__":
    raise SystemExit(main())
