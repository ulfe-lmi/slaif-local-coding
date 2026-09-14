"""Topology reachability qualification (order 010-a, workstream E).

Disposable, fake-only qualification of the Gateway -> Local transport:

1. A closed decision table (``qualify_transport``) that mechanically
   enforces the address-class / network-namespace contract from
   docs/TOPOLOGY.md: the supported co-located topology is
   (shared host network namespace, loopback endpoint); the invalid
   cross-namespace loopback assumption and every unencrypted separate-
   namespace transport fail closed.
2. A live disposable probe that proves the endpoint configured for the
   simulated Gateway runtime is reachable **from that runtime's network
   namespace** and reaches exactly the Local candidate (per-run sentinel),
   and — where a namespace mechanism is safely available — that the old
   invalid assumption (separate runtime -> ``127.0.0.1``) does NOT
   qualify merely because Local is running elsewhere.

Everything here is synthetic: a loopback-only fake "Local candidate" on an
ephemeral port, a per-run sentinel token, and a bounded probe subprocess.
No protected Qwen/vLLM inference, no credential, no raw payload. The fake
is fully removed with an absence proof.
"""

from __future__ import annotations

import argparse
import http.server
import json
import secrets
import socket
import subprocess
import sys
import threading
from dataclasses import dataclass
from pathlib import Path

SCHEMA = "slaif-topology-qualification-v1"

GATEWAY_NAMESPACE_MODES = ("shared_host_namespace", "separate_namespace")
ENDPOINT_ADDRESS_CLASSES = ("loopback", "rfc1918_plaintext", "encrypted")

# Ports that must never be used or touched by the qualification (protected
# fixture and development port).
PROTECTED_PORTS = frozenset({18020, 18021, 18031})

# Closed failure classes observed when the probe cannot connect.
CONNECT_FAILURE_CLASSES = frozenset(
    {
        "ConnectionRefusedError",
        "ConnectionResetError",
        "ConnectionAbortedError",
        "TimeoutError",
        "OSError",
    }
)

_PROBE_SOURCE = """
import http.client
import json
import socket
import sys

host, port, sentinel = sys.argv[1], int(sys.argv[2]), sys.argv[3]
try:
    conn = http.client.HTTPConnection(host, port, timeout=5.0)
    conn.request("GET", "/probe")
    response = conn.getresponse()
    body = response.read(65536).decode("utf-8", "replace")
    if response.status == 200 and body == sentinel:
        facts = {"reachable": True, "sentinel_match": True, "error_class": "none"}
    else:
        facts = {"reachable": True, "sentinel_match": False, "error_class": "unexpected_response"}
    print(json.dumps(facts))
    conn.close()
except OSError as exc:
    facts = {"reachable": False, "sentinel_match": False, "error_class": type(exc).__name__}
    print(json.dumps(facts))
except Exception:
    facts = {"reachable": False, "sentinel_match": False, "error_class": "unexpected_error"}
    print(json.dumps(facts))
"""


def qualify_transport(gateway_namespace_mode: str, endpoint_address_class: str) -> tuple[bool, str]:
    """Closed decision table for the Gateway -> Local transport contract.

    - (shared_host_namespace, loopback) is the only supported combination
      (co-located deployment, true loopback, no network traversal).
    - (separate_namespace, loopback) is the documented invalid assumption:
      loopback does not cross network namespaces.
    - unencrypted separate-namespace transport puts request content on an
      untrusted plaintext network.
    - encrypted separate-namespace transport would require a human
      architecture decision (Local binding law change) and is NOT supported
      by this objective.
    - anything unknown fails closed.
    """
    if gateway_namespace_mode not in GATEWAY_NAMESPACE_MODES:
        return False, "unknown_transport_fails_closed"
    if endpoint_address_class not in ENDPOINT_ADDRESS_CLASSES:
        return False, "unknown_transport_fails_closed"
    if gateway_namespace_mode == "shared_host_namespace":
        if endpoint_address_class == "loopback":
            return True, "supported_colocated_loopback"
        return False, "local_loopback_only_law"
    if endpoint_address_class == "loopback":
        return False, "loopback_does_not_cross_namespaces"
    if endpoint_address_class == "rfc1918_plaintext":
        return False, "untrusted_plaintext_network"
    return False, "multi_host_not_supported_requires_human_decision"


def detect_namespace_prefix(timeout: float = 5.0) -> list[str] | None:
    """Return the smallest safe namespace mechanism, if one is available.

    Preference: unprivileged ``unshare -n``; then passwordless-sudo
    ``sudo -n unshare -n`` (safe repo-local test-service use); otherwise
    ``None`` (the deterministic structural equivalent still applies).
    """
    for prefix in (["unshare", "-n"], ["sudo", "-n", "unshare", "-n"]):
        try:
            result = subprocess.run(prefix + ["true"], capture_output=True, timeout=timeout)
        except (OSError, subprocess.SubprocessError):
            continue
        if result.returncode == 0:
            return prefix
    return None


@dataclass(frozen=True, slots=True)
class _FakeCandidate:
    port: int
    sentinel: str
    server: http.server.ThreadingHTTPServer
    thread: threading.Thread


def _start_fake_local_candidate() -> _FakeCandidate:
    sentinel = secrets.token_hex(8)

    class _Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 - http.server API
            if self.path == "/probe":
                payload = sentinel.encode("ascii")
                self.send_response(200)
                self.send_header("content-type", "text/plain")
                self.send_header("content-length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, *args: object) -> None:
            return

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    port = server.server_address[1]
    if port in PROTECTED_PORTS:  # pragma: no cover - defensive
        server.server_close()
        raise RuntimeError("fake candidate port collides with a protected port")
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return _FakeCandidate(port=port, sentinel=sentinel, server=server, thread=thread)


def _stop_fake_local_candidate(candidate: _FakeCandidate) -> dict[str, object]:
    candidate.server.shutdown()
    candidate.server.server_close()
    candidate.thread.join(timeout=10)
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    probe.settimeout(2.0)
    try:
        probe.connect(("127.0.0.1", candidate.port))
        listener_absent = False
    except OSError:
        listener_absent = True
    finally:
        probe.close()
    return {"listener_absent": listener_absent}


def run_probe(
    *,
    fresh_namespace: bool = False,
    namespace_prefix: list[str] | None = None,
) -> dict[str, object]:
    """Run one bounded probe against the disposable fake Local candidate.

    ``fresh_namespace=False`` simulates the supported co-located Gateway
    runtime (host network namespace). ``fresh_namespace=True`` simulates a
    separate runtime namespace: the same configured loopback endpoint must
    NOT be reachable.
    """
    candidate = _start_fake_local_candidate()
    cleanup: dict[str, object] = {}
    try:
        command = [
            sys.executable,
            "-c",
            _PROBE_SOURCE,
            "127.0.0.1",
            str(candidate.port),
            candidate.sentinel,
        ]
        if fresh_namespace:
            if namespace_prefix is None:
                namespace_prefix = detect_namespace_prefix()
            if namespace_prefix is None:
                raise RuntimeError("namespace mechanism unavailable")
            command = [*namespace_prefix, *command]
        result = subprocess.run(command, capture_output=True, timeout=30)
        facts = json.loads(result.stdout.decode("utf-8").strip().splitlines()[-1])
    finally:
        cleanup = _stop_fake_local_candidate(candidate)
    if fresh_namespace and facts["reachable"]:  # pragma: no cover - defensive
        raise RuntimeError("cross-namespace loopback unexpectedly reachable")
    return {
        "schema": SCHEMA,
        "endpoint": f"127.0.0.1:{candidate.port}",
        "port": candidate.port,
        "port_collision_free": candidate.port not in PROTECTED_PORTS,
        "namespace_mode": "separate_namespace" if fresh_namespace else "shared_host_namespace",
        "namespace_prefix_used": (
            list(namespace_prefix) if (fresh_namespace and namespace_prefix) else []
        ),
        "probe": {
            "reachable": bool(facts["reachable"]),
            "sentinel_match": bool(facts["sentinel_match"]),
            "error_class": str(facts["error_class"]),
        },
        "cleanup": cleanup,
    }


def _manifest_facts(manifest_path: Path) -> dict[str, object]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    supported = manifest["transport_decision"]
    supported_qualifies, supported_reason = qualify_transport(
        str(supported["gateway_namespace_mode"]), str(supported["endpoint_address_class"])
    )
    invalid = manifest["invalid_assumption"]
    invalid_qualifies, invalid_reason = qualify_transport(
        str(invalid["gateway_namespace_mode"]), str(invalid["endpoint_address_class"])
    )
    return {
        "supported": {
            "gateway_namespace_mode": supported["gateway_namespace_mode"],
            "endpoint_address_class": supported["endpoint_address_class"],
            "qualified": supported_qualifies,
            "reason": supported_reason,
        },
        "invalid_assumption": {
            "gateway_namespace_mode": invalid["gateway_namespace_mode"],
            "endpoint_address_class": invalid["endpoint_address_class"],
            "qualified": invalid_qualifies,
            "reason": invalid_reason,
            "documented_reason": invalid["reason"],
        },
    }


def self_test() -> dict[str, object]:
    repo_root = Path(__file__).resolve().parents[1]
    manifest = _manifest_facts(repo_root / "docs" / "topology.manifest.json")
    if manifest["supported"]["qualified"] is not True:
        raise AssertionError("supported transport must qualify")
    if manifest["invalid_assumption"]["qualified"] is not False:
        raise AssertionError("invalid cross-namespace loopback assumption must not qualify")
    if manifest["invalid_assumption"]["reason"] != "loopback_does_not_cross_namespaces":
        raise AssertionError("invalid assumption must fail for the namespace reason")

    decision_table: dict[str, tuple[bool, str]] = {}
    for mode in GATEWAY_NAMESPACE_MODES:
        for address_class in ENDPOINT_ADDRESS_CLASSES:
            decision_table[f"{mode}+{address_class}"] = qualify_transport(mode, address_class)

    host_probe = run_probe(fresh_namespace=False)
    if not (host_probe["probe"]["reachable"] and host_probe["probe"]["sentinel_match"]):
        raise AssertionError("host-namespace probe must reach exactly the fake candidate")
    if host_probe["cleanup"]["listener_absent"] is not True:
        raise AssertionError("host-namespace probe cleanup failed")

    namespace_prefix = detect_namespace_prefix()
    fresh_probe: dict[str, object] | None = None
    if namespace_prefix is not None:
        fresh_probe = run_probe(fresh_namespace=True, namespace_prefix=namespace_prefix)
        probe = fresh_probe["probe"]
        if probe["reachable"] or probe["sentinel_match"]:
            raise AssertionError("fresh-namespace probe must not reach the fake candidate")
        if probe["error_class"] not in CONNECT_FAILURE_CLASSES:
            raise AssertionError(f"unexpected probe failure class: {probe['error_class']}")
        if fresh_probe["cleanup"]["listener_absent"] is not True:
            raise AssertionError("fresh-namespace probe cleanup failed")

    return {
        "ok": True,
        "decision_table": {key: value[1] for key, value in decision_table.items()},
        "manifest": manifest,
        "host_namespace_probe": host_probe,
        "fresh_namespace_probe": fresh_probe,
        "namespace_mechanism": (
            "unavailable_structural_equivalent_only" if fresh_probe is None else "namespace_probe"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test:
        parser.print_help()
        return 2
    print(json.dumps(self_test(), sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
