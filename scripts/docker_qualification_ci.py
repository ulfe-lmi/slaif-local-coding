"""Docker CI qualification orchestrator (order 011-a, workstream C).

Stdlib-only repository tooling (excluded from both artifacts). Runs the
disposable Docker qualification on a non-protected runner: compose rendered
validation, fake upstream, host-network adapter stack on the canonical port,
in-image provenance proof, signed-request evidence from a separate
bridge-network namespace (the simulated Gateway runtime), negative/contract
evidence, fail-closed readiness, image content/hardening/label scans, and the
stop/start/recreate/upgrade/rollback operations sequence with a teardown
absence proof.

No protected service is touched; no secret value is ever printed (fake
credential values are generated here, passed only through 0600 files, and
never recorded in output). One bounded JSON evidence line per phase; exit 0
iff every phase is PASSED.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import secrets
import shutil
import signal
import subprocess
import sys
import tarfile
import time
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
IMAGE_REPO = "slaif-local-coding"
PACKAGE_VERSION = "0.1.0"
CANONICAL_PROJECT = "slaif-local-coding"  # compose `name:`


class QualificationError(RuntimeError):
    def __init__(self, phase: str, code: str, detail: str = "") -> None:
        super().__init__(f"{phase}: {code}: {detail}")
        self.phase = phase
        self.code = code
        self.detail = detail[:4000]


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_private(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(content)


def _container_identity() -> tuple[int, int]:
    """The fixed non-root uid/gid created in the image (single source of
    truth: the Dockerfile ARGs)."""
    text = (REPO_ROOT / "Dockerfile").read_text(encoding="utf-8")
    uid = gid = None
    for line in text.splitlines():
        m = re.match(r"^ARG SLAIF_UID=(\d+)\s*$", line)
        if m:
            uid = int(m.group(1))
        m = re.match(r"^ARG SLAIF_GID=(\d+)\s*$", line)
        if m:
            gid = int(m.group(1))
    if uid is None or gid is None:
        raise QualificationError("container_identity", "dockerfile_arg_missing")
    return uid, gid


def _own_for_container(path: Path) -> None:
    """Make a bind-mounted file readable by the fixed container runtime user
    (the non-root container cannot read a file owned by another host uid at
    0600). Preferred: chown to the image uid/gid (0600 preserved) — used on
    hosts where the operator has the privilege (e.g. the protected-host D6
    run via the docker admin). GitHub-hosted runners drop CAP_CHOWN even for
    root, so fall back to making the disposable file world-readable: CI site
    files contain only generated fake values (no real credentials, never
    recorded), and the runner is disposable and non-protected. The canonical
    operator deployment keeps mode 0600 with owner 10001 (documented in
    docs/DOCKER-INSTALL.md)."""
    uid, gid = _container_identity()
    stat = path.stat()
    if stat.st_uid == uid and stat.st_gid == gid:
        return
    try:
        os.chown(path, uid, gid)
    except PermissionError:
        path.chmod(0o644)


def _run(
    cmd: list[str], *, cwd: Path | None = None, env: dict | None = None, timeout: float = 600
) -> subprocess.CompletedProcess:
    merged = dict(os.environ)
    if env:
        merged.update(env)
    return subprocess.run(cmd, cwd=cwd, env=merged, capture_output=True, timeout=timeout)


def _compose(env: dict[str, str], *args: str, timeout: float = 600) -> subprocess.CompletedProcess:
    return _run(["docker", "compose", *args], cwd=REPO_ROOT, env=env, timeout=timeout)


def _http_status(url: str, timeout: float = 5.0) -> tuple[int, bytes]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.status, response.read(1_048_576)
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(1_048_576)


def _wait_http(url: str, predicate, limit_seconds: float, phase: str) -> tuple[int, bytes]:
    deadline = time.monotonic() + limit_seconds
    last: tuple[int, bytes] = (0, b"")
    while time.monotonic() < deadline:
        try:
            last = _http_status(url)
        except OSError:
            last = (0, b"")
        if predicate(last):
            return last
        time.sleep(2)
    raise QualificationError(phase, "bounded_wait_elapsed", f"last={last[0]}")


def _container_name() -> str:
    return f"{CANONICAL_PROJECT}-adapter-1"


def _container_health(name: str) -> str:
    proc = _run(
        [
            "docker",
            "inspect",
            "--format",
            "{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}",
            name,
        ]
    )
    if proc.returncode != 0:
        return "absent"
    return proc.stdout.decode().strip()


def _wait_healthy(name: str, limit_seconds: float, phase: str) -> str:
    deadline = time.monotonic() + limit_seconds
    last = "absent"
    while time.monotonic() < deadline:
        last = _container_health(name)
        if last == "healthy":
            return last
        if last in {"unhealthy", "exited", "dead"}:
            raise QualificationError(phase, "container_not_healthy", f"state={last}")
        time.sleep(3)
    raise QualificationError(phase, "bounded_wait_elapsed", f"health={last}")


def _render_gateway_template(
    listen_host: str, upstream_url: str, model: str, listen_port: int = 18031
) -> str:
    text = (REPO_ROOT / "config" / "adapter.gateway-integrated.template.toml").read_text(
        encoding="utf-8"
    )
    rendered = (
        text.replace("__LISTEN_HOST__", listen_host)
        .replace("__UPSTREAM_BASE_URL__", upstream_url)
        .replace("__UPSTREAM_MODEL__", model)
    )
    if listen_port != 18031:
        rendered = rendered.replace("listen_port = 18031", f"listen_port = {listen_port}")
    assert "__" not in rendered
    return rendered


class Qualification:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.image_tag = f"{IMAGE_REPO}:{PACKAGE_VERSION}-{args.tag_sha}"
        self.image_tag_upgrade = f"{IMAGE_REPO}:{PACKAGE_VERSION}-{args.tag_sha}-b"
        self.workdir = REPO_ROOT / ".ci-docker"
        self.sentinel = f"SLAIF_FAKE_SENTINEL:{secrets.token_hex(8)}"
        self.fake = secrets.token_hex(24)
        self.svc = secrets.token_hex(24)
        self.sgn = secrets.token_hex(24)
        self.fake_proc: subprocess.Popen | None = None
        self.fake_log: Path | None = None
        self.results: dict[str, str] = {}
        self.env = {
            "SLAIF_GIT_SHA": args.tag_sha,
            "SLAIF_WHEEL_SHA256": args.wheel_sha256,
            "SLAIF_CONFIG_FILE": str(self.workdir / "slaif-adapter.toml"),
            "SLAIF_ENV_FILE": str(self.workdir / "slaif-adapter.env"),
        }

    # -- lifecycle ---------------------------------------------------------
    def setup_site_files(self) -> None:
        _write_private(
            self.workdir / "slaif-adapter.env",
            f"QWEN3090_API_KEY={self.fake}\n"
            f"SLAIF_ADAPTER_SERVICE_TOKEN={self.svc}\n"
            f"SLAIF_ADAPTER_SIGNING_SECRET={self.sgn}\n",
        )
        _write_private(
            self.workdir / "slaif-adapter.toml",
            _render_gateway_template(
                "0.0.0.0",
                f"http://127.0.0.1:{self.args.fake_port}/v1",
                "qwen3.8-27b",
            ),
        )
        # Simulated Gateway runtime credential file (same shared values the
        # Gateway route would carry; 0600, mounted read-only into the bridge
        # container, never passed on a command line).
        _write_private(
            self.workdir / "sim-gateway.env",
            f"SLAIF_SIM_SERVICE_TOKEN={self.svc}\nSLAIF_SIM_SIGNING_SECRET={self.sgn}\n",
        )
        # The non-root container runtime user (fixed in the image) reads the
        # bind-mounted files inside the container: hand them to that uid/gid
        # (0600 preserved, owner changed).
        _own_for_container(self.workdir / "slaif-adapter.toml")
        _own_for_container(self.workdir / "sim-gateway.env")

    def _phase(self, name: str, fn) -> dict:
        started = time.monotonic()
        try:
            result = fn() or {}
            status = "PASSED"
        except QualificationError as exc:
            result = {"error_class": exc.code, "detail": exc.detail}
            status = "FAILED"
        except Exception as exc:  # noqa: BLE001 - report any phase failure exactly
            result = {"error_class": type(exc).__name__, "detail": str(exc)[:4000]}
            status = "FAILED"
        self.results[name] = status
        line = {
            "phase": name,
            "status": status,
            "wall_seconds": round(time.monotonic() - started, 1),
            **result,
        }
        print(json.dumps(line, sort_keys=True), flush=True)
        return line

    def run(self) -> int:
        try:
            self.setup_site_files()
            for name in (
                "verify_wheel_binding",
                "compose_rendered_validation",
                "image_build",
                "fake_upstream_start",
                "adapter_stack_up",
                "in_image_provenance",
                "bridge_positive_signed",
                "bridge_negative_contract",
                "config_time_rejection",
                "fail_closed_readiness",
                "image_content_scan",
                "hardening_and_labels",
                "operations_stop_start_recreate_upgrade_rollback",
                "teardown_absence_proof",
            ):
                line = self._phase(name, getattr(self, f"_do_{name}"))
                if line["status"] != "PASSED":
                    return 1
            print(
                json.dumps(
                    {
                        "summary": "PASSED",
                        "phases": self.results,
                        "endpoint_address_class": "host_bridge_ip_from_separate_namespace",
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
            return 0
        finally:
            self._cleanup()

    def _cleanup(self) -> None:
        try:
            if self.fake_proc is not None and self.fake_proc.poll() is None:
                self.fake_proc.send_signal(signal.SIGTERM)
                try:
                    self.fake_proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.fake_proc.kill()
            _compose(self.env, "down", "--remove-orphans", timeout=120)
        except Exception:
            pass
        scan = f"slaif-image-scan-{os.getpid()}"
        try:
            _run(["docker", "rm", "-f", scan], timeout=60)
        except Exception:
            pass
        for tag in (self.image_tag, self.image_tag_upgrade):
            try:
                _run(["docker", "image", "rm", "-f", tag], timeout=60)
            except Exception:
                pass
        shutil.rmtree(self.workdir, ignore_errors=True)

    # -- phases ------------------------------------------------------------
    def _do_verify_wheel_binding(self) -> dict:
        manifest = json.loads(
            (REPO_ROOT / "packaging" / "release_provenance_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        wheel = manifest["artifacts"]["wheel"]
        if wheel["sha256"] != self.args.wheel_sha256:
            raise QualificationError(
                "verify_wheel_binding",
                "wheel_hash_mismatch",
                "freshly built wheel does not match the committed provenance manifest",
            )
        return {
            "wheel_sha256": wheel["sha256"],
            "manifest_status": manifest["status"],
            "image_bound_to_committed_artifact": True,
        }

    def _do_compose_rendered_validation(self) -> dict:
        proc = _compose(self.env, "config", "--quiet")
        if proc.returncode != 0:
            raise QualificationError(
                "compose_rendered_validation",
                "render_failed",
                proc.stderr.decode()[:2000],
            )
        rendered = _compose(self.env, "config")
        if rendered.returncode != 0:
            raise QualificationError(
                "compose_rendered_validation",
                "render_failed",
                rendered.stderr.decode()[:2000],
            )
        rendered_bytes = rendered.stdout
        spec = importlib.util.spec_from_file_location(
            "artifact_policy_check", REPO_ROOT / "scripts" / "artifact_policy_check.py"
        )
        if spec is None or spec.loader is None:
            raise QualificationError("compose_rendered_validation", "checker_unavailable")
        checker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(checker)
        violations: list[str] = []
        checker._check_content(
            "rendered_compose", "compose.yaml", {"rendered": rendered_bytes}, violations
        )
        if violations:
            raise QualificationError(
                "compose_rendered_validation", "forbidden_content", "; ".join(violations)
            )
        source = (REPO_ROOT / "compose.yaml").read_bytes()
        for label, pattern in checker.FORBIDDEN_CONTENT_PATTERNS:
            if pattern.search(source):
                raise QualificationError(
                    "compose_rendered_validation", "forbidden_content_in_source", label
                )
        return {"rendered_valid": True, "secret_values_in_rendered_output": False}

    def _do_image_build(self) -> dict:
        proc = _compose(self.env, "build")
        if proc.returncode != 0:
            raise QualificationError(
                "image_build", "compose_build_failed", proc.stderr.decode()[:2000]
            )
        image_id = proc.stdout.decode().strip().splitlines()[-1][:200]
        return {
            "image": self.image_tag,
            "label_revision": self.args.full_sha,
            "build_output_tail": image_id,
        }

    def _do_fake_upstream_start(self) -> dict:
        self.fake_log = self.workdir / "fake_upstream.log"
        self.fake_proc = subprocess.Popen(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "fake_upstream_server.py"),
                "--port",
                str(self.args.fake_port),
                "--model",
                "qwen3.8-27b",
                "--sentinel",
                self.sentinel,
            ],
            stdout=self.fake_log.open("wb"),
            stderr=subprocess.STDOUT,
        )
        status, _ = _wait_http(
            f"http://127.0.0.1:{self.args.fake_port}/health",
            lambda pair: pair[0] == 200,
            30,
            "fake_upstream_start",
        )
        return {"fake_upstream_port": self.args.fake_port, "health": status, "sentinel_set": True}

    def _do_adapter_stack_up(self) -> dict:
        proc = _compose(self.env, "up", "-d")
        if proc.returncode != 0:
            raise QualificationError(
                "adapter_stack_up", "compose_up_failed", proc.stderr.decode()[:2000]
            )
        name = _container_name()
        health = _wait_healthy(name, 240, "adapter_stack_up")
        return {
            "container": name,
            "health": health,
            "listen": f"0.0.0.0:{self.args.adapter_port}",
            "network_mode": "host",
        }

    def _do_in_image_provenance(self) -> dict:
        code = "\n".join(
            [
                "import hashlib,importlib.metadata as md,slaif_local_coding as m",
                "dist=md.distribution('slaif-local-coding')",
                "assert dist.version=='0.1.0',dist.version",
                "loc=m.__file__",
                "assert '/site-packages/slaif_local_coding/' in loc,loc",
                "wheel='/opt/slaif/artifacts/slaif_local_coding-0.1.0-py3-none-any.whl'",
                "d=hashlib.sha256(open(wheel,'rb').read()).hexdigest()",
                "import json;print(json.dumps({'version':dist.version,'module_path':loc,"
                "'wheel_sha256':d}))",
            ]
        )
        proc = _run(
            [
                "docker",
                "run",
                "--rm",
                "--network",
                "none",
                "--entrypoint",
                "/opt/slaif/venv/bin/python",
                self.image_tag,
                "-c",
                code,
            ],
            timeout=180,
        )
        if proc.returncode != 0:
            raise QualificationError(
                "in_image_provenance", "import_check_failed", proc.stderr.decode()[:2000]
            )
        facts = json.loads(proc.stdout.decode().strip().splitlines()[-1])
        if facts["wheel_sha256"] != self.args.wheel_sha256:
            raise QualificationError("in_image_provenance", "wheel_hash_mismatch")
        version_proc = _run(
            [
                "docker",
                "run",
                "--rm",
                "--network",
                "none",
                "--entrypoint",
                "/opt/slaif/venv/bin/slaif-local-coding",
                self.image_tag,
                "--version",
            ],
            timeout=180,
        )
        if version_proc.returncode != 0 or PACKAGE_VERSION not in version_proc.stdout.decode():
            raise QualificationError(
                "in_image_provenance", "version_check_failed", version_proc.stdout.decode()[:200]
            )
        return {
            "module_path": facts["module_path"],
            "version": facts["version"],
            "wheel_sha256": facts["wheel_sha256"],
            "non_editable": True,
        }

    def _bridge_run(self, operation: str, endpoint: str) -> dict:
        proc = _run(
            [
                "docker",
                "run",
                "--rm",
                "--network",
                "bridge",
                "--entrypoint",
                "/bin/sh",
                "--mount",
                f"type=bind,source={self.workdir / 'sim-gateway.env'},"
                "target=/opt/sim/sim.env,readonly",
                "--mount",
                f"type=bind,source={REPO_ROOT / 'scripts' / 'sim_gateway_client.py'},"
                "target=/opt/sim/sim_gateway_client.py,readonly",
                self.image_tag,
                "-c",
                "set -a; . /opt/sim/sim.env; set +a; exec python "
                "/opt/sim/sim_gateway_client.py --operation "
                + operation
                + " --endpoint "
                + endpoint
                + " --expect-sentinel "
                + self.sentinel,
            ],
            timeout=300,
        )
        line = proc.stdout.decode().strip().splitlines()
        try:
            facts = json.loads(line[-1]) if line else {}
        except json.JSONDecodeError:
            raise QualificationError(
                "bridge_run",
                "client_output_unparseable",
                proc.stderr.decode()[:2000],
            ) from None
        if proc.returncode != 0 or facts.get("ok") is not True:
            raise QualificationError("bridge_run", f"{operation}_failed", json.dumps(facts)[:2000])
        return facts

    def _do_bridge_positive_signed(self) -> dict:
        endpoint = f"http://172.17.0.1:{self.args.adapter_port}"
        results = {}
        for operation in ("models", "chat", "chat-stream", "tool-roundtrip"):
            facts = self._bridge_run(operation, endpoint)
            results[operation] = {key: value for key, value in facts.items() if key != "operation"}
        return {
            "endpoint": endpoint,
            "endpoint_address_class": "host_bridge_ip",
            "results": results,
        }

    def _do_bridge_negative_contract(self) -> dict:
        endpoint = f"http://172.17.0.1:{self.args.adapter_port}"
        results = {}
        for operation in (
            "neg-cross-namespace",
            "neg-missing-token",
            "neg-bad-signature",
            "neg-replay",
        ):
            target = (
                f"http://127.0.0.1:{self.args.adapter_port}"
                if operation == "neg-cross-namespace"
                else endpoint
            )
            facts = self._bridge_run(operation, target)
            results[operation] = {key: value for key, value in facts.items() if key != "operation"}
        cross = results["neg-cross-namespace"]
        if cross.get("class") in (None, "unexpectedly_reachable"):
            raise QualificationError(
                "bridge_negative_contract", "cross_namespace_loopback_reachable"
            )
        return {"results": results}

    def _do_config_time_rejection(self) -> dict:
        from slaif_local_coding.config import load_settings

        text = (REPO_ROOT / "config" / "adapter.gateway-integrated.template.toml").read_text(
            encoding="utf-8"
        )
        base = (
            text.replace("__LISTEN_HOST__", "172.17.0.1")
            .replace("__UPSTREAM_BASE_URL__", f"http://127.0.0.1:{self.args.fake_port}/v1")
            .replace("__UPSTREAM_MODEL__", "qwen3.8-27b")
        )

        def _render(mode: str) -> str:
            rendered = base.replace(
                'mode = "service_bearer_signed_identity_v1"',
                f'mode = "{mode}"',
            )
            if mode != "service_bearer_signed_identity_v1":
                rendered = rendered.replace(
                    'signing_secret_env = "SLAIF_ADAPTER_SIGNING_SECRET"\n', ""
                )
                rendered = rendered.replace(
                    'identity_source = "signed_request"', 'identity_source = "static"'
                )
                rendered = rendered.replace(
                    'enabled = true\nidentity_source = "static"',
                    'enabled = true\nidentity_source = "static"\n'
                    'principal = "a"\nsession = "b"\nrepository = "c"',
                    1,
                )
            return rendered

        outdir = self.workdir / "config-rejection"
        outdir.mkdir(parents=True, exist_ok=True)
        outcome = {}
        for mode in ("disabled", "service_bearer_static_identity"):
            path = outdir / f"{mode}.toml"
            path.write_text(_render(mode), encoding="utf-8")
            try:
                load_settings(path)
            except ValueError as exc:
                outcome[mode] = "service_bearer_signed_identity_v1" in str(exc)
            else:
                outcome[mode] = False
        path = outdir / "signed.toml"
        path.write_text(_render("service_bearer_signed_identity_v1"), encoding="utf-8")
        settings = load_settings(path)
        outcome["signed_non_loopback"] = settings.server.listen_host == "172.17.0.1"
        if not all(outcome.values()):
            raise QualificationError("config_time_rejection", "matrix_failed", json.dumps(outcome))
        return outcome

    def _do_fail_closed_readiness(self) -> dict:
        cfg_dir = self.workdir / "failclosed"
        cfg_dir.mkdir(parents=True, exist_ok=True)
        _write_private(
            cfg_dir / "adapter.toml",
            _render_gateway_template(
                "0.0.0.0",
                f"http://127.0.0.1:{self.args.fake_port}/v1",
                "qwen3.8-27b",
                listen_port=self.args.failclosed_port,
            ),
        )
        _write_private(
            cfg_dir / "adapter.env",
            f"QWEN3090_API_KEY={self.fake}\nSLAIF_ADAPTER_SERVICE_TOKEN={self.svc}\n",
        )
        _own_for_container(cfg_dir / "adapter.toml")
        health_cmd = (
            "import os,sys,urllib.request; sys.exit(0 if "
            "urllib.request.urlopen('http://'+os.environ.get("
            "'SLAIF_HEALTH_ENDPOINT','127.0.0.1:18031')+'/readyz',timeout=4)"
            ".status==200 else 1)"
        )
        compose = f"""name: slaif-failclosed-{os.getpid()}

services:
  adapter:
    image: {self.image_tag}
    network_mode: host
    read_only: true
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    tmpfs:
      - /tmp:size=64m
      - /dev/shm:size=256m
    volumes:
      - {cfg_dir / "adapter.toml"}:/etc/slaif/adapter.toml:ro
    env_file:
      - {cfg_dir / "adapter.env"}
    environment:
      SLAIF_HEALTH_ENDPOINT: 127.0.0.1:{self.args.failclosed_port}
    healthcheck:
      test:
        [
          "CMD",
          "python",
          "-c",
          "{health_cmd}",
        ]
      interval: 5s
      timeout: 5s
      retries: 3
      start_period: 10s
"""
        compose_path = cfg_dir / "compose.yaml"
        compose_path.write_text(compose, encoding="utf-8")
        env = {
            "SLAIF_HEALTH_ENDPOINT": f"127.0.0.1:{self.args.failclosed_port}",
        }
        proc = _compose(env, "-f", str(compose_path), "up", "-d")
        if proc.returncode != 0:
            raise QualificationError(
                "fail_closed_readiness", "compose_up_failed", proc.stderr.decode()[:2000]
            )
        try:
            name = f"slaif-failclosed-{os.getpid()}-adapter-1"
            status, body = _wait_http(
                f"http://127.0.0.1:{self.args.failclosed_port}/readyz",
                lambda pair: pair[0] == 503,
                60,
                "fail_closed_readiness",
            )
            payload = json.loads(body.decode())
            if payload.get("gateway_ingress") != "unavailable":
                raise QualificationError(
                    "fail_closed_readiness",
                    "unexpected_ingress_state",
                    str(payload)[:200],
                )
            deadline = time.monotonic() + 120
            health = ""
            while time.monotonic() < deadline:
                health = _container_health(name)
                if health == "unhealthy":
                    break
                time.sleep(3)
            if health != "unhealthy":
                raise QualificationError(
                    "fail_closed_readiness", "healthcheck_not_unhealthy", f"health={health}"
                )
            return {
                "readyz_status": status,
                "gateway_ingress": "unavailable",
                "healthcheck": "unhealthy",
            }
        finally:
            _compose(env, "-f", str(compose_path), "down", "--remove-orphans", timeout=120)

    def _do_image_content_scan(self) -> dict:
        scan = f"slaif-image-scan-{os.getpid()}"
        proc = _run(["docker", "create", "--name", scan, self.image_tag, "true"])
        if proc.returncode != 0:
            raise QualificationError(
                "image_content_scan", "docker_create_failed", proc.stderr.decode()[:1000]
            )
        export_dir = self.workdir / "image-fs"
        export_dir.mkdir(parents=True, exist_ok=True)
        tar_path = self.workdir / "image-fs.tar"
        with tar_path.open("wb") as stream:
            export = subprocess.run(
                ["docker", "export", scan], stdout=stream, stderr=subprocess.PIPE
            )
        if export.returncode != 0:
            raise QualificationError(
                "image_content_scan",
                "docker_export_failed",
                export.stderr.decode()[:2000],
            )
        with tarfile.open(tar_path, "r") as tar:
            # "tar" (not "data"): a docker-export rootfs is a trusted archive
            # of our own image; "data" rejects the base image's absolute
            # /etc/alternatives symlinks (AbsoluteLinkError).
            tar.extractall(export_dir, filter="tar")
        tar_path.unlink()
        _run(["docker", "rm", scan])

        spec = importlib.util.spec_from_file_location(
            "artifact_policy_check", REPO_ROOT / "scripts" / "artifact_policy_check.py"
        )
        if spec is None or spec.loader is None:
            raise QualificationError("image_content_scan", "checker_unavailable")
        checker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(checker)

        forbidden_components = {
            ".git",
            "oap",
            "tests",
            "references",
            "scripts",
            "dist",
            "build",
            ".venv",
            "Local",
            "clean",
            "unchanged",
        }
        violations: list[str] = []
        site_packages = None
        wheel_path = None
        file_count = 0
        for root, dirs, files in os.walk(export_dir):
            rel_root = Path(root).relative_to(export_dir)
            at_image_root = rel_root == Path(".")
            # docker export snapshots the kernel pseudo-filesystems; they are
            # not image content (and the host mount table is host state, not
            # image material).
            if at_image_root:
                # Repository source components and build residue are forbidden
                # at the IMAGE ROOT (the build stage's /build is already wiped
                # by the Dockerfile); identical component names inside
                # installed dependency trees (e.g. pip/_internal/operations/
                # build, certifi/tests) are legitimate package content.
                for name in dirs:
                    if name in forbidden_components:
                        violations.append(f"forbidden_dir:{rel_root / name}")
                for cache in ("root/.cache", "opt/slaif/.cache"):
                    if (export_dir / cache).is_dir():
                        violations.append(f"forbidden_cache:{cache}")
                for name in files:
                    if name in forbidden_components:
                        violations.append(f"forbidden_file:{rel_root / name}")
            for name in files:
                if name in forbidden_components and not at_image_root:
                    continue
                if name.endswith((".pyc", ".pyo")) or name == "runtime.env":
                    violations.append(f"forbidden_file:{rel_root / name}")
                path = Path(root) / name
                rel = path.relative_to(export_dir)
                if "site-packages" in rel.parts and "slaif_local_coding" in rel.parts:
                    site_packages = site_packages or (
                        [p for p in rel.parts if p == "site-packages"][0],
                        path,
                    )
                if (
                    rel.parts
                    and rel.parts[0] == "opt"
                    and "artifacts" in rel.parts
                    and name.endswith(".whl")
                ):
                    wheel_path = path
                file_count += 1
                # Symlink policy: never follow links into the kernel pseudo-
                # filesystems (/proc, /sys, /dev) — docker export snapshots
                # them with HOST state, which is not image content — and
                # scan the link target string instead of failing on broken
                # links (base-image cert links).
                if os.path.islink(path):
                    target = os.readlink(path)
                    if target.startswith(("/proc/", "/sys/", "/dev/")) or not os.path.exists(path):
                        data = target.encode()
                    else:
                        data = path.read_bytes()
                else:
                    data = path.read_bytes()
                for label, pattern in checker.FORBIDDEN_CONTENT_PATTERNS:
                    if pattern.search(data):
                        violations.append(f"forbidden_content:{label}:{rel}")
        if violations:
            raise QualificationError(
                "image_content_scan", "forbidden_material", "; ".join(violations[:10])
            )
        if site_packages is None:
            raise QualificationError("image_content_scan", "package_missing")
        if wheel_path is None:
            raise QualificationError("image_content_scan", "wheel_artifact_missing")
        if _sha256_file(wheel_path) != self.args.wheel_sha256:
            raise QualificationError("image_content_scan", "wheel_hash_mismatch")
        return {
            "files_scanned": file_count,
            "forbidden_entries": 0,
            "forbidden_content_matches": 0,
            "wheel_sha256": self.args.wheel_sha256,
        }

    def _do_hardening_and_labels(self) -> dict:
        proc = _run(["docker", "inspect", _container_name()])
        if proc.returncode != 0:
            raise QualificationError("hardening_and_labels", "inspect_failed")
        info = json.loads(proc.stdout.decode())[0]
        host_config = info.get("HostConfig", {})
        config = info.get("Config", {})
        checks = {
            "non_root_user": config.get("User") in {"10001", "slaif"},
            "read_only_rootfs": host_config.get("ReadonlyRootfs") is True,
            "no_new_privileges": host_config.get("NoNewPrivileges") is True,
            "cap_drop_all": host_config.get("CapDrop") == ["ALL"],
            "not_privileged": host_config.get("Privileged") is False,
            "network_mode_host": host_config.get("NetworkMode") == "host",
            "no_docker_socket": all(
                "/var/run/docker.sock" not in str(b) for b in host_config.get("Binds") or []
            ),
            "restart_policy": host_config.get("RestartPolicy", {}).get("Name") == "unless-stopped",
        }
        binds = host_config.get("Binds") or []
        config_binds = [b for b in binds if "/etc/slaif/adapter.toml" in b]
        checks["single_readonly_config_bind"] = len(config_binds) == 1 and config_binds[0].endswith(
            ":ro"
        )
        checks["no_repo_source_bind"] = not any(
            str(REPO_ROOT / "src") in b or ":ro" not in b for b in binds
        )
        mounts = {m["Destination"]: m.get("Type") for m in info.get("Mounts", [])}
        checks["tmpfs_tmp"] = mounts.get("/tmp") == "tmpfs"
        checks["tmpfs_dev_shm"] = mounts.get("/dev/shm") == "tmpfs"
        labels = config.get("Labels") or {}
        label_checks = {
            "oci_source": labels.get("org.opencontainers.image.source")
            == "https://github.com/ulfe-lmi/slaif-local-coding",
            "oci_revision": labels.get("org.opencontainers.image.revision") == self.args.full_sha,
            "oci_version": labels.get("org.opencontainers.image.version") == PACKAGE_VERSION,
            "oci_created": bool(labels.get("org.opencontainers.image.created")),
            "wheel_sha256_label": labels.get("slaif-local-coding.wheel.sha256")
            == self.args.wheel_sha256,
            "gateway_peer_label": bool(labels.get("slaif-local-coding.gateway.peer.sha")),
            "topology_label": bool(labels.get("slaif-local-coding.topology.mode")),
            "qualification_label": "not released"
            in (labels.get("slaif-local-coding.qualification") or ""),
        }
        failures = [k for k, v in {**checks, **label_checks}.items() if not v]
        if failures:
            raise QualificationError("hardening_and_labels", "checks_failed", ",".join(failures))
        return {**checks, **label_checks}

    def _do_operations_stop_start_recreate_upgrade_rollback(self) -> dict:
        config_path = self.workdir / "slaif-adapter.toml"
        config_hash = _sha256_file(config_path)
        name = _container_name()
        sequence = []

        def step(label: str, fn, wait_seconds: float = 240) -> None:
            fn()
            _wait_healthy(name, wait_seconds, f"operations:{label}")
            after = _sha256_file(config_path)
            if after != config_hash:
                raise QualificationError("operations", "config_hash_changed", label)
            sequence.append({"step": label, "health": "healthy", "config_hash_unchanged": True})

        def stop() -> None:
            proc = _compose(self.env, "stop", timeout=120)
            if proc.returncode != 0:
                raise QualificationError("operations", "stop_failed")

        def start() -> None:
            proc = _compose(self.env, "start", timeout=120)
            if proc.returncode != 0:
                raise QualificationError("operations", "start_failed")

        def recreate() -> None:
            proc = _compose(self.env, "up", "-d", "--force-recreate", timeout=300)
            if proc.returncode != 0:
                raise QualificationError("operations", "recreate_failed")

        def upgrade() -> None:
            tag = _run(["docker", "tag", self.image_tag, self.image_tag_upgrade])
            if tag.returncode != 0:
                raise QualificationError("operations", "upgrade_tag_failed")
            env = dict(self.env)
            env["SLAIF_GIT_SHA"] = f"{self.args.tag_sha}-b"
            proc = _compose(env, "up", "-d", "--force-recreate", timeout=300)
            if proc.returncode != 0:
                raise QualificationError("operations", "upgrade_failed")

        def rollback() -> None:
            proc = _compose(self.env, "up", "-d", "--force-recreate", timeout=300)
            if proc.returncode != 0:
                raise QualificationError("operations", "rollback_failed")

        stop()
        step("start", start)
        step("recreate", recreate)
        step("upgrade", upgrade)
        step("rollback", rollback)
        return {"config_sha256": config_hash, "sequence": sequence}

    def _do_teardown_absence_proof(self) -> dict:
        proc = _compose(self.env, "down", "--remove-orphans", timeout=180)
        if proc.returncode != 0:
            raise QualificationError("teardown_absence_proof", "compose_down_failed")
        for tag in (self.image_tag, self.image_tag_upgrade):
            _run(["docker", "image", "rm", "-f", tag], timeout=60)
        ports = {self.args.adapter_port, self.args.fake_port, self.args.failclosed_port}
        listeners = []
        for path in ("/proc/net/tcp", "/proc/net/tcp6"):
            try:
                lines = Path(path).read_text().splitlines()[1:]
            except OSError:
                lines = []
            for line in lines:
                parts = line.split()
                if len(parts) > 3 and parts[3] == "0A":  # LISTEN
                    local = parts[1]
                    try:
                        port = int(local.rsplit(":", 1)[1], 16)
                    except ValueError:
                        continue
                    if port in ports:
                        listeners.append(port)
        containers = (
            _run(
                [
                    "docker",
                    "ps",
                    "-a",
                    "--filter",
                    f"name={CANONICAL_PROJECT}",
                    "--format",
                    "{{.Names}}",
                ]
            )
            .stdout.decode()
            .strip()
        )
        images = (
            _run(["docker", "images", IMAGE_REPO, "--format", "{{.Tag}}"]).stdout.decode().strip()
        )
        if listeners or containers or images:
            raise QualificationError(
                "teardown_absence_proof",
                "leftover_state",
                f"listeners={listeners} containers={containers!r} images={images!r}",
            )
        return {
            "listeners_absent": True,
            "containers_absent": True,
            "images_absent": True,
            "ports_checked": sorted(ports),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag-sha", required=True)
    parser.add_argument("--full-sha", required=True)
    parser.add_argument("--wheel-sha256", required=True)
    parser.add_argument("--adapter-port", type=int, default=18031)
    parser.add_argument("--fake-port", type=int, default=18033)
    parser.add_argument("--failclosed-port", type=int, default=18034)
    args = parser.parse_args()
    return Qualification(args).run()


if __name__ == "__main__":
    sys.exit(main())
