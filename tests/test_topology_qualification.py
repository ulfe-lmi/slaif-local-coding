"""Topology reachability qualification tests (order 010-a, workstream E/H7-H8/H13).

Fake/synthetic only: a loopback-only disposable fake "Local candidate" on an
ephemeral port and a per-run sentinel; no protected Qwen/vLLM inference.
The live fresh-namespace probe runs only where a safe namespace mechanism is
available (``unshare -n``, optionally via passwordless sudo); otherwise the
deterministic structural equivalent (the closed decision table) is the
enforced contract and the live probe is SKIPPED, never pass.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import types
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_qualification() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(
        "topology_qualification", REPO_ROOT / "scripts" / "topology_qualification.py"
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load topology qualification")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


QUALIFICATION = _load_qualification()


@pytest.mark.parametrize(
    ("namespace_mode", "address_class", "qualified", "reason"),
    [
        ("shared_host_namespace", "loopback", True, "supported_colocated_loopback"),
        ("shared_host_namespace", "rfc1918_plaintext", False, "local_loopback_only_law"),
        ("shared_host_namespace", "encrypted", False, "local_loopback_only_law"),
        ("separate_namespace", "loopback", False, "loopback_does_not_cross_namespaces"),
        ("separate_namespace", "rfc1918_plaintext", False, "untrusted_plaintext_network"),
        (
            "separate_namespace",
            "encrypted",
            False,
            "multi_host_not_supported_requires_human_decision",
        ),
        ("unknown_mode", "loopback", False, "unknown_transport_fails_closed"),
        ("separate_namespace", "unknown_class", False, "unknown_transport_fails_closed"),
    ],
)
def test_transport_decision_table_fails_closed(
    namespace_mode: str, address_class: str, qualified: bool, reason: str
) -> None:
    assert QUALIFICATION.qualify_transport(namespace_mode, address_class) == (qualified, reason)


def test_manifest_supported_transport_qualifies_and_invalid_assumption_does_not() -> None:
    raw = (REPO_ROOT / "docs" / "topology.manifest.json").read_text(encoding="utf-8")
    manifest = json.loads(raw)
    supported = manifest["transport_decision"]
    qualifies, reason = QUALIFICATION.qualify_transport(
        str(supported["gateway_namespace_mode"]), str(supported["endpoint_address_class"])
    )
    assert qualifies is True
    assert reason == "supported_colocated_loopback"

    invalid = manifest["invalid_assumption"]
    qualifies, reason = QUALIFICATION.qualify_transport(
        str(invalid["gateway_namespace_mode"]), str(invalid["endpoint_address_class"])
    )
    assert qualifies is False
    assert reason == "loopback_does_not_cross_namespaces"
    assert invalid["qualified"] is False

    # H13: the confidentiality requirement is mechanically represented: the
    # supported boundary is exactly no network traversal plus the two
    # mandatory ingress credentials, and Local is non-publicly-reachable.
    assert set(supported["confidentiality_boundary"]) == {
        "no_network_traversal",
        "service_bearer",
        "signed_identity_v1",
    }
    assert supported["local_binding_changes"] is False
    assert supported["multi_host_supported"] is False
    hops = manifest["supported_path"]["hops"]
    local_hops = [hop for hop in hops if hop["to"] in ("local_adapter", "qwen_vllm")]
    assert all(hop["publicly_reachable"] is False for hop in local_hops)
    assert all(hop["endpoint_address_class"] == "loopback" for hop in local_hops)


def test_host_namespace_probe_reaches_exactly_the_fake_candidate() -> None:
    facts = QUALIFICATION.run_probe(fresh_namespace=False)
    assert facts["namespace_mode"] == "shared_host_namespace"
    assert facts["port_collision_free"] is True
    probe = facts["probe"]
    assert probe["reachable"] is True
    assert probe["sentinel_match"] is True
    assert probe["error_class"] == "none"
    assert facts["cleanup"]["listener_absent"] is True


def test_fresh_namespace_probe_fails_closed_for_cross_namespace_loopback() -> None:
    prefix = QUALIFICATION.detect_namespace_prefix()
    if prefix is None:
        pytest.skip(
            "no safe namespace mechanism available; the deterministic "
            "structural equivalent (decision table) is the enforced contract"
        )
    facts = QUALIFICATION.run_probe(fresh_namespace=True, namespace_prefix=prefix)
    assert facts["namespace_mode"] == "separate_namespace"
    probe = facts["probe"]
    assert probe["reachable"] is False
    assert probe["sentinel_match"] is False
    assert probe["error_class"] in QUALIFICATION.CONNECT_FAILURE_CLASSES
    assert facts["cleanup"]["listener_absent"] is True


def test_self_test_contract() -> None:
    facts = QUALIFICATION.self_test()
    assert facts["ok"] is True
    assert facts["manifest"]["supported"]["qualified"] is True
    assert facts["manifest"]["invalid_assumption"]["qualified"] is False
    host = facts["host_namespace_probe"]["probe"]
    assert host["reachable"] is True and host["sentinel_match"] is True
