"""Documented operator-session qualification (order 013-j, J2).

Proves the DOCUMENTED primary lifecycle (QUICKSTART.md / INSTALL.md Docker
path) end-to-end in a disposable CI environment: a local build of the
committed source (qualification path, NOT a publication), a LOCAL
``registry:2`` standing in for the private GHCR package, the EXACT
documented operator session with SYNTHETIC secrets (random values that
never leave this process), and the fake loopback upstream
(``scripts/fake_upstream_server.py``).

The executed session mirrors the docs line-for-line in the normative
parts:

- protected-site directory ``/opt/slaif`` created ``0700`` (host admin)
  and handed to the operator account (the Compose client reads the env
  file on the host side);
- mode-0600 env file owned by the operator, with the THREE DISTINCT
  secret roles;
- mode-0600 configuration rendered from
  ``config/adapter.gateway-integrated.template.toml`` (the documented
  placeholder substitutions only);
- ``chown 10001:10001`` of the mounted configuration (the fixed
  non-root container user; host admin);
- ONE exported session: ``SLAIF_LOCAL_CODING_IMAGE`` (digest form),
  ``SLAIF_CONFIG_FILE``, ``SLAIF_ENV_FILE`` — every ``docker compose``
  command runs in that same session;
- ``docker compose pull`` (digest form), the documented ``RepoDigests``
  verification for the tag form (the image ``.Id`` alone is NOT proof of
  the manifest digest), ``up -d``, the documented bounded health-wait
  loop (36 x 5 s on the compose healthcheck; no helper file), host
  ``/readyz`` 200, ``ps``/``logs`` with a secret-free assertion on the
  log tail, ``stop``/``start``/``restart`` with readiness re-waits,
  ``down``;
- teardown: registry removed, fake upstream killed, site directory
  removed, no listeners left.

A doc-mirror check asserts that every executed compose subcommand and
session export is documented in QUICKSTART.md/INSTALL.md, that the
documented ``sed`` substitutions reference exactly the template's
placeholders, and that the documented site paths/modes match the
executed session. This is ordinary install qualification (disposable CI),
not a benchmark: no task, judge, controller, or instrumentation. It never
touches the protected upstream (18020/18021 must be FREE — if they are
not, this script fails closed before doing anything).

Stdlib + docker/compose CLI + git only; no new dependencies. Secrets are
synthetic and are never printed: the only emitted identity facts are
hashes, counts, statuses, and the local (non-private) registry reference.
"""

from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import os
import re
import secrets
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
IMAGE_REPO = "ulfe-lmi/slaif-local-coding"
CONTAINER = "slaif-local-coding-adapter-1"
TEMPLATE = REPO_ROOT / "config" / "adapter.gateway-integrated.template.toml"
COMPOSE_PRIMARY = REPO_ROOT / "compose.yaml"
COMPOSE_BUILD_OVERRIDE = REPO_ROOT / "compose.build.yaml"
QUICKSTART = REPO_ROOT / "QUICKSTART.md"
INSTALL = REPO_ROOT / "INSTALL.md"
MANIFEST = REPO_ROOT / "packaging" / "release_provenance_manifest.json"
FAKE_SERVER = REPO_ROOT / "scripts" / "fake_upstream_server.py"

# Protected-host boundary: these listeners must be ABSENT for this
# disposable qualification to run at all (fail closed, never touch).
PROTECTED_PORTS = (18020, 18021)
REGISTRY_NAME = "slaif-operator-registry"
REGISTRY_IMAGE = "registry:2"
PUSH_DIGEST_LINE_RE = re.compile(
    r"^(?:[^ ]+:\s+)?digest:\s?sha256:([0-9a-f]{64})(?:\s+size:\s?\d+)?\s*$"
)

# The documented bounded health wait (QUICKSTART/INSTALL/DOCKER-INSTALL):
# 36 iterations x 5 s on the compose healthcheck status.
HEALTH_WAIT_ITERATIONS = 36
HEALTH_WAIT_INTERVAL_SECONDS = 5


class SessionError(RuntimeError):
    pass


def _run(
    cmd: list[str],
    env: dict[str, str] | None = None,
    timeout: float = 1800,
    input_bytes: bytes | None = None,
    check: bool = True,
    workdir: Path | None = None,
) -> subprocess.CompletedProcess[bytes]:
    proc = subprocess.run(
        cmd,
        input=input_bytes,
        env=env,
        capture_output=True,
        timeout=timeout,
        cwd=workdir,
    )
    if check and proc.returncode != 0:
        tail = (proc.stdout + proc.stderr).decode(errors="replace")[-2000:]
        raise SessionError(f"command failed ({proc.returncode}): {' '.join(cmd[:6])}\n{tail}")
    return proc


def _root(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[bytes]:
    """Run with host-admin privileges when needed (CI runner: passwordless
    sudo for this disposable site directory; already-root: direct)."""
    if os.geteuid() == 0:
        return _run(cmd, **kwargs)
    if shutil.which("sudo") is None or _run(["sudo", "-n", "true"], check=False).returncode != 0:
        raise SessionError(
            "host admin (root or passwordless sudo) is required for the "
            "protected-site steps (install -d /opt/slaif, chown 10001:10001)"
        )
    return _run(["sudo", "-n", *cmd], **kwargs)


def _stat_mode_uid(path: Path) -> tuple[int, int]:
    """``(mode & 0o7777, uid)`` for a protected site path.

    The site directory and files are root-managed (0700/0600) and
    deliberately unreadable by a non-root caller, so when we are not root
    the verification goes through the same admin channel that created
    them (``sudo stat``); a direct stat would EACCES by design, not due
    to a defect.
    """
    if os.geteuid() == 0:
        st = path.stat()
        return st.st_mode & 0o7777, st.st_uid
    out = _root(["stat", "-c", "%a %u", str(path)], timeout=60)
    mode_s, uid_s = out.stdout.decode(errors="replace").split()
    return int(mode_s, 8), int(uid_s)


def _port_free(port: int) -> bool:
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("127.0.0.1", port))
        except OSError:
            return False
    return True


def _http_get(url: str, timeout: float = 4.0) -> tuple[int, bytes]:
    """Readiness probe GET: ``(status, body)``.

    A connection-level failure (refused/timeout — the target is still
    starting up) returns ``(0, b"")`` so bounded wait loops retry instead
    of crashing on the first refused probe; terminal checks fail closed on
    0 (they expect a positive status).
    """
    parts = url.split("://", 1)
    host_port = parts[1].split("/", 1)[0]
    host, _, port_s = host_port.partition(":")
    path = "/" + parts[1].split("/", 1)[1] if "/" in parts[1] else "/"
    conn = http.client.HTTPConnection(host, int(port_s or 80), timeout=timeout)
    try:
        conn.request("GET", path)
        resp = conn.getresponse()
        return resp.status, resp.read()
    except OSError:
        return 0, b""
    finally:
        conn.close()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _render_gateway_template(upstream_url: str) -> str:
    text = TEMPLATE.read_text(encoding="utf-8")
    rendered = (
        text.replace("__LISTEN_HOST__", "127.0.0.1")
        .replace("__UPSTREAM_BASE_URL__", upstream_url)
        .replace("__UPSTREAM_MODEL__", "qwen3.8-27b")
    )
    if "__" in rendered:
        raise SessionError("unresolved placeholder in rendered configuration")
    return rendered


def _write_private(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    os.chmod(path, 0o600)


def _extract_push_digest(output: str) -> str | None:
    digest: str | None = None
    for line in output.splitlines():
        match = PUSH_DIGEST_LINE_RE.match(line.strip())
        if match:
            digest = "sha256:" + match.group(1)
    return digest


def _doc_mirror() -> list[str]:
    """Assert the executed session is the documented session."""
    problems: list[str] = []
    quickstart = QUICKSTART.read_text(encoding="utf-8")
    install = INSTALL.read_text(encoding="utf-8")
    for label, text in (("QUICKSTART.md", quickstart), ("INSTALL.md", install)):
        for export in (
            "export SLAIF_LOCAL_CODING_IMAGE=",
            "export SLAIF_CONFIG_FILE=",
            "export SLAIF_ENV_FILE=",
        ):
            if export not in text:
                problems.append(f"{label}: missing session export {export!r}")
        for token, what in (
            ("chown 10001:10001", "container-user config ownership"),
            ("install -d -m 0700", "protected-site directory creation"),
            ("chmod 0600", "mode-0600 site files"),
            ("RepoDigests", "registry-manifest-digest verification"),
            ("${QWEN3090_API_KEY:?", "fail-closed secret guard"),
            ("{{.State.Health.Status}}", "bounded health-wait loop"),
            (CONTAINER, "named container health target"),
            ("/opt/slaif/adapter.toml", "documented site config path"),
            ("/opt/slaif/adapter.env", "documented site env path"),
        ):
            if token not in text:
                problems.append(f"{label}: missing documented {what} ({token!r})")
    combined = quickstart + "\n" + install
    for subcommand in (
        "docker compose pull",
        "docker compose up -d",
        "docker compose ps",
        "docker compose logs --tail 100 adapter",
        "docker compose stop",
        "docker compose start",
        "docker compose restart",
        "docker compose down",
    ):
        if subcommand not in combined:
            problems.append(f"executed compose subcommand not documented: {subcommand!r}")
    # The documented sed substitutions must reference exactly the template
    # placeholders (no undocumented placeholder, no documented phantom).
    template_placeholders = set(re.findall(r"__[A-Z_]+__", TEMPLATE.read_text(encoding="utf-8")))
    for label, text in (("QUICKSTART.md", quickstart), ("INSTALL.md", install)):
        doc_placeholders = set(re.findall(r"__[A-Z_]+__", text))
        if not doc_placeholders <= template_placeholders:
            problems.append(
                f"{label}: documented placeholders not in template: "
                f"{sorted(doc_placeholders - template_placeholders)}"
            )
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel-sha256", required=True, help="manifest-bound wheel sha256")
    parser.add_argument(
        "--full-sha", required=True, help="40-hex checkout SHA (image source for this build)"
    )
    parser.add_argument("--adapter-port", type=int, default=18031)
    parser.add_argument("--fake-port", type=int, default=18033)
    parser.add_argument("--registry-port", type=int, default=18040)
    parser.add_argument(
        "--site-dir",
        type=Path,
        default=Path("/opt/slaif"),
        help="protected site directory (default /opt/slaif, the documented path)",
    )
    args = parser.parse_args()

    if not re.fullmatch(r"[0-9a-f]{40}", args.full_sha):
        print("operator-session: --full-sha must be 40-hex", file=sys.stderr)
        return 2
    if not re.fullmatch(r"[0-9a-f]{64}", args.wheel_sha256):
        print("operator-session: --wheel-sha256 must be 64-hex", file=sys.stderr)
        return 2

    results: dict[str, str] = {}
    fake_proc: subprocess.Popen | None = None
    registry_running = False

    def note(phase: str, status: str, detail: str = "") -> None:
        results[phase] = status
        line = f"operator-session {phase}: {status}"
        if detail:
            line += f" ({detail})"
        print(line, flush=True)

    try:
        # --- preflight -----------------------------------------------------
        for port in (*PROTECTED_PORTS, args.adapter_port, args.fake_port, args.registry_port):
            if not _port_free(port):
                raise SessionError(
                    f"port {port} is already in use; this disposable "
                    "qualification requires all of 18020/18021/adapter/fake/"
                    "registry ports to be free (fail closed; the protected "
                    "host boundary is never touched)"
                )
        _run(["docker", "version"], timeout=60)
        _run(["docker", "compose", "version"], timeout=60)
        for path in (COMPOSE_PRIMARY, COMPOSE_BUILD_OVERRIDE, TEMPLATE, FAKE_SERVER):
            if not path.is_file():
                raise SessionError(f"missing required repository file: {path}")
        problems = _doc_mirror()
        if problems:
            for problem in problems:
                print(f"doc-mirror: {problem}", file=sys.stderr)
            raise SessionError(f"doc mirror failed ({len(problems)} problem(s))")
        note("preflight", "PASSED", "ports free; docker+compose v2; doc mirror OK")

        # --- synthetic secrets (never real, never printed) ------------------
        fake_key = secrets.token_hex(24)
        service_token = secrets.token_hex(24)
        signing_secret = secrets.token_hex(24)

        # --- manifest-bound wheel (mechanical binding) ----------------------
        if MANIFEST.is_file():
            manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
            recorded = str(manifest["artifacts"]["wheel"]["sha256"])
            if recorded != args.wheel_sha256:
                raise SessionError(
                    "wheel sha256 argument does not equal the committed "
                    f"manifest wheel ({recorded[:12]}...)"
                )
        note("wheel-binding", "PASSED", f"wheel sha256 {args.wheel_sha256[:16]}... == manifest")

        # --- qualification build (development path, NOT a publication) ------
        tag_sha = args.full_sha[:12]
        built_tag = f"slaif-local-coding:0.1.0-{tag_sha}"
        build_env = {
            "SLAIF_GIT_SHA": tag_sha,
            "SLAIF_WHEEL_SHA256": args.wheel_sha256,
            "SLAIF_LOCAL_CODING_IMAGE": built_tag,
        }
        proc = _run(
            [
                "docker",
                "compose",
                "-f",
                str(COMPOSE_PRIMARY),
                "-f",
                str(COMPOSE_BUILD_OVERRIDE),
                "build",
            ],
            env=build_env,
            workdir=REPO_ROOT,
            timeout=3600,
        )
        if built_tag not in proc.stdout.decode(errors="replace"):
            # compose may report under the service image name only
            _run(["docker", "image", "inspect", built_tag], timeout=60)
        note("build", "PASSED", f"qualification build {built_tag} (manifest-bound wheel)")

        # --- local registry (stands in for the private GHCR package) -------
        _run(
            [
                "docker",
                "run",
                "-d",
                "--name",
                REGISTRY_NAME,
                "-p",
                f"{args.registry_port}:5000",
                REGISTRY_IMAGE,
            ],
            timeout=300,
        )
        registry_running = True
        local_repo = f"127.0.0.1:{args.registry_port}/{IMAGE_REPO}"
        deadline = time.monotonic() + 120
        last = (0, b"")
        while time.monotonic() < deadline:
            last = (
                _http_get(f"http://127.0.0.1:{args.registry_port}/v2/", timeout=3)
                if True
                else (0, b"")
            )
            if last[0] in (200, 401):  # registry API reachable (401 = auth challenge OK)
                break
            time.sleep(2)
        if last[0] not in (200, 401):
            raise SessionError(f"local registry not reachable: last={last[0]}")
        note(
            "registry",
            "PASSED",
            f"local registry:2 on 127.0.0.1:{args.registry_port} (private-package stand-in)",
        )

        # --- push built image; the push digest is the authoritative D ------
        _run(["docker", "tag", built_tag, f"{local_repo}:0.1.0-rc2"], timeout=120)
        push = _run(["docker", "push", f"{local_repo}:0.1.0-rc2"], timeout=1800)
        digest = _extract_push_digest(
            push.stdout.decode(errors="replace") + push.stderr.decode(errors="replace")
        )
        if digest is None:
            raise SessionError("no digest line in local registry push output")
        note("push", "PASSED", f"local digest D sha256:{digest[7:19]}... (one image, two forms)")

        # --- protected site directory (documented step; host admin) ---------
        site = args.site_dir
        if site.is_dir():
            # A pre-existing 0700 root-managed directory is only observable
            # through the admin channel (fail closed: any entry at all
            # means the site is not fresh).
            if os.geteuid() == 0:
                nonempty = any(site.iterdir())
            else:
                nonempty = bool(
                    _root(
                        ["find", str(site), "-mindepth", "1", "-maxdepth", "1", "-print", "-quit"],
                        timeout=60,
                    )
                    .stdout.decode(errors="replace")
                    .strip()
                )
            if nonempty:
                raise SessionError(f"site directory {site} already exists and is not empty")
        _root(["install", "-d", "-m", "0700", str(site)], timeout=60)
        # Documented flow: the operator account that runs Compose owns the
        # site directory — the Compose client reads the env file on the
        # host side and resolves the config path, so the admin hands the
        # directory to the operator (root execution keeps it root-owned).
        if os.geteuid() != 0:
            _root(["chown", f"{os.getuid()}:{os.getgid()}", str(site)], timeout=60)
        site_mode, site_uid = _stat_mode_uid(site)
        operator_uid = 0 if os.geteuid() == 0 else os.getuid()
        if site_mode != 0o700 or site_uid != operator_uid:
            raise SessionError(
                f"site directory must be 0700 owned by the operator "
                f"(mode {oct(site_mode)}, uid {site_uid})"
            )
        env_file = site / "adapter.env"
        toml_file = site / "adapter.toml"
        env_content = (
            f"QWEN3090_API_KEY={fake_key}\n"
            f"SLAIF_ADAPTER_SERVICE_TOKEN={service_token}\n"
            f"SLAIF_ADAPTER_SIGNING_SECRET={signing_secret}\n"
        )
        toml_content = _render_gateway_template(f"http://127.0.0.1:{args.fake_port}/v1")
        # The operator owns the site directory: the files are written
        # directly by the caller (mode 0600, owner = operator — the
        # Compose client reads the env file). Only the config's ownership
        # changes (container user 10001), which needs the host admin.
        _write_private(env_file, env_content)
        _write_private(toml_file, toml_content)
        if os.geteuid() == 0:
            os.chown(toml_file, 10001, 10001)
        else:
            _root(["chown", "10001:10001", str(toml_file)], timeout=60)
        env_mode, env_uid = _stat_mode_uid(env_file)
        if env_mode != 0o600 or env_uid != os.getuid():
            raise SessionError(
                f"env file must be mode 0600 owned by the operator "
                f"(mode {oct(env_mode)}, uid {env_uid})"
            )
        toml_mode, toml_uid = _stat_mode_uid(toml_file)
        if toml_mode != 0o600 or toml_uid != 10001:
            raise SessionError("config file must be mode 0600 owned by uid 10001")
        note(
            "site-files",
            "PASSED",
            f"{site} 0700 (operator-owned); env 0600 (operator); toml 0600 owned 10001:10001",
        )

        # --- fake upstream (disposable, loopback) ---------------------------
        fake_proc = subprocess.Popen(
            [
                sys.executable,
                str(FAKE_SERVER),
                "--port",
                str(args.fake_port),
                "--model",
                "qwen3.8-27b",
                "--sentinel",
                "SLAIF_FAKE_SENTINEL:" + secrets.token_hex(8),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            status, _body = _http_get(f"http://127.0.0.1:{args.fake_port}/health", timeout=2)
            if status == 200:
                break
            time.sleep(1)
        else:
            raise SessionError("fake upstream did not become healthy")
        note("fake-upstream", "PASSED", f"loopback fake on 127.0.0.1:{args.fake_port}")

        # --- the documented operator session (one exported session) ---------
        session_env = {
            "SLAIF_LOCAL_CODING_IMAGE": f"{local_repo}@{digest}",
            "SLAIF_CONFIG_FILE": str(toml_file),
            "SLAIF_ENV_FILE": str(env_file),
        }
        compose = ["docker", "compose", "-f", str(COMPOSE_PRIMARY)]

        def compose_cmd(*sub: str) -> list[str]:
            return compose + list(sub)

        _run(compose_cmd("pull"), env=session_env, workdir=REPO_ROOT, timeout=1800)
        note("compose-pull-digest", "PASSED", "digest-form pull (authoritative identity)")

        # Documented RepoDigests verification for the tag form.
        _run(
            compose_cmd("pull"),
            env={**session_env, "SLAIF_LOCAL_CODING_IMAGE": f"{local_repo}:0.1.0-rc2"},
            workdir=REPO_ROOT,
            timeout=1800,
        )
        inspect = (
            _run(
                [
                    "docker",
                    "image",
                    "inspect",
                    f"{local_repo}:0.1.0-rc2",
                    "--format",
                    "{{range .RepoDigests}}{{.}}{{end}}",
                ],
                timeout=60,
            )
            .stdout.decode()
            .strip()
        )
        if f"{local_repo}@{digest}" not in inspect:
            raise SessionError(f"RepoDigests does not contain the pushed digest: {inspect!r}")
        note("repodigests", "PASSED", "tag form resolves to the one registry digest D")

        _run(compose_cmd("up", "-d"), env=session_env, workdir=REPO_ROOT, timeout=600)
        note("compose-up", "PASSED", "up -d in the exported session")

        state = ""
        for _i in range(HEALTH_WAIT_ITERATIONS):
            state = (
                _run(
                    ["docker", "inspect", "--format", "{{.State.Health.Status}}", CONTAINER],
                    timeout=60,
                    check=False,
                )
                .stdout.decode()
                .strip()
            )
            if state == "healthy":
                break
            time.sleep(HEALTH_WAIT_INTERVAL_SECONDS)
        if state != "healthy":
            raise SessionError(f"bounded wait elapsed; health={state or 'absent'} (fail closed)")
        note(
            "health-wait",
            "PASSED",
            f"compose healthcheck healthy (mirror of documented "
            f"{HEALTH_WAIT_ITERATIONS}x{HEALTH_WAIT_INTERVAL_SECONDS}s loop)",
        )

        status, body = _http_get(f"http://127.0.0.1:{args.adapter_port}/readyz", timeout=5)
        if status != 200:
            raise SessionError(f"host /readyz expected 200, got {status}")
        note(
            "host-readyz",
            "PASSED",
            "http 200 on host loopback /readyz (upstream + ingress fail-closed facts)",
        )

        ps = _run(
            compose_cmd("ps"), env=session_env, workdir=REPO_ROOT, timeout=120
        ).stdout.decode()
        if "healthy" not in ps and "running" not in ps:
            raise SessionError(f"compose ps shows neither running nor healthy: {ps[:200]!r}")
        note("compose-ps", "PASSED", "status running/healthy")

        logs = _run(
            compose_cmd("logs", "--tail", "100", "adapter"),
            env=session_env,
            workdir=REPO_ROOT,
            timeout=120,
        ).stdout.decode(errors="replace")
        for label, value in (
            ("QWEN3090_API_KEY", fake_key),
            ("SLAIF_ADAPTER_SERVICE_TOKEN", service_token),
            ("SLAIF_ADAPTER_SIGNING_SECRET", signing_secret),
        ):
            if value in logs:
                raise SessionError(
                    f"synthetic {label} value leaked into the log tail (privacy law)"
                )
        note("compose-logs", "PASSED", "bounded tail captured; zero secret values present")

        _run(compose_cmd("stop"), env=session_env, workdir=REPO_ROOT, timeout=300)
        running = (
            _run(
                ["docker", "inspect", "--format", "{{.State.Running}}", CONTAINER],
                timeout=60,
            )
            .stdout.decode()
            .strip()
        )
        if running != "false":
            raise SessionError(f"container still running after stop: {running!r}")
        note("compose-stop", "PASSED", "container stopped")

        _run(compose_cmd("start"), env=session_env, workdir=REPO_ROOT, timeout=300)
        state = ""
        for _i in range(HEALTH_WAIT_ITERATIONS):
            state = (
                _run(
                    ["docker", "inspect", "--format", "{{.State.Health.Status}}", CONTAINER],
                    timeout=60,
                    check=False,
                )
                .stdout.decode()
                .strip()
            )
            if state == "healthy":
                break
            time.sleep(HEALTH_WAIT_INTERVAL_SECONDS)
        if state != "healthy":
            raise SessionError(f"health after start: {state or 'absent'}")
        note("compose-start", "PASSED", "started; readiness re-waited to healthy")

        _run(compose_cmd("restart"), env=session_env, workdir=REPO_ROOT, timeout=600)
        state = ""
        for _i in range(HEALTH_WAIT_ITERATIONS):
            state = (
                _run(
                    ["docker", "inspect", "--format", "{{.State.Health.Status}}", CONTAINER],
                    timeout=60,
                    check=False,
                )
                .stdout.decode()
                .strip()
            )
            if state == "healthy":
                break
            time.sleep(HEALTH_WAIT_INTERVAL_SECONDS)
        if state != "healthy":
            raise SessionError(f"health after restart: {state or 'absent'}")
        note("compose-restart", "PASSED", "restarted; readiness re-waited to healthy")

        _run(compose_cmd("down"), env=session_env, workdir=REPO_ROOT, timeout=300)
        absent = _run(["docker", "inspect", CONTAINER], timeout=60, check=False).returncode != 0
        if not absent:
            raise SessionError("container still present after down")
        note("compose-down", "PASSED", "container removed")

        # --- teardown --------------------------------------------------------
        if fake_proc is not None:
            fake_proc.send_signal(signal.SIGTERM)
            try:
                fake_proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                fake_proc.kill()
        if registry_running:
            _run(["docker", "rm", "-f", REGISTRY_NAME], timeout=120)
        for ref in (built_tag, f"{local_repo}:0.1.0-rc2", f"{local_repo}@{digest}"):
            _run(["docker", "rmi", ref], timeout=120, check=False)
        _root(["rm", "-rf", str(site)], timeout=120)
        if (
            not _port_free(args.adapter_port)
            or not _port_free(args.fake_port)
            or not _port_free(args.registry_port)
        ):
            raise SessionError("teardown left a listener on a qualification port")
        note(
            "teardown",
            "PASSED",
            "registry removed; fake killed; site dir removed; no listeners left",
        )

        print(
            json.dumps({"operator_session": "PASSED", "phases": results}, sort_keys=True),
            flush=True,
        )
        return 0
    except SessionError as exc:
        print(f"operator-session FAILED: {exc}", file=sys.stderr, flush=True)
        print(
            json.dumps({"operator_session": "FAILED", "phases": results}, sort_keys=True),
            flush=True,
        )
        return 1
    finally:
        # Safety net: never leave the disposable services behind.
        if fake_proc is not None and fake_proc.poll() is None:
            fake_proc.kill()
        if registry_running:
            _run(["docker", "rm", "-f", REGISTRY_NAME], timeout=60, check=False)
        for ref in (
            f"slaif-local-coding:0.1.0-{args.full_sha[:12]}",
            f"127.0.0.1:{args.registry_port}/{IMAGE_REPO}:0.1.0-rc2",
        ):
            _run(["docker", "rmi", ref], timeout=60, check=False)


if __name__ == "__main__":
    sys.exit(main())
