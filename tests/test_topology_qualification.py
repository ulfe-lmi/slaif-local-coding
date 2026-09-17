"""Topology reachability qualification tests (order 010-a, workstream E; 011-a G3).

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


# Preserved 010 rows (two-argument form defaults to ingress "none").
@pytest.mark.parametrize(
    ("namespace_mode", "address_class", "qualified", "reason"),
    [
        ("shared_host_namespace", "loopback", True, "supported_colocated_loopback"),
        ("separate_namespace", "loopback", False, "loopback_does_not_cross_namespaces"),
        ("unknown_mode", "loopback", False, "unknown_transport_fails_closed"),
        ("separate_namespace", "unknown_class", False, "unknown_transport_fails_closed"),
    ],
)
def test_transport_decision_table_preserves_010_behavior(
    namespace_mode: str, address_class: str, qualified: bool, reason: str
) -> None:
    assert QUALIFICATION.qualify_transport(namespace_mode, address_class) == (qualified, reason)


# Objective 011-a G2: the signed-contract dimension and the trusted-LAN-
# visible endpoint class. Non-loopback binds are supported if and only if
# the full signed ingress contract is in force; every other non-loopback
# combination fails closed; loopback keeps its 010 behavior in every mode.
@pytest.mark.parametrize(
    ("namespace_mode", "address_class", "contract", "qualified", "reason"),
    [
        # supported LAN-visible signed variants
        (
            "separate_namespace",
            "trusted_lan",
            "full_signed_v1",
            True,
            "supported_lan_visible_signed",
        ),
        (
            "shared_host_namespace",
            "trusted_lan",
            "full_signed_v1",
            True,
            "supported_lan_visible_signed",
        ),
        (
            "separate_namespace",
            "rfc1918_plaintext",
            "full_signed_v1",
            True,
            "supported_lan_visible_signed",
        ),
        (
            "shared_host_namespace",
            "rfc1918_plaintext",
            "full_signed_v1",
            True,
            "supported_lan_visible_signed",
        ),
        (
            "shared_host_namespace",
            "encrypted",
            "full_signed_v1",
            True,
            "supported_lan_visible_signed",
        ),
        # non-loopback without the full signed contract fails closed
        (
            "shared_host_namespace",
            "trusted_lan",
            "none",
            False,
            "non_loopback_bind_requires_full_signed_ingress",
        ),
        (
            "shared_host_namespace",
            "trusted_lan",
            "service_bearer_static",
            False,
            "non_loopback_bind_requires_full_signed_ingress",
        ),
        (
            "shared_host_namespace",
            "rfc1918_plaintext",
            "none",
            False,
            "non_loopback_bind_requires_full_signed_ingress",
        ),
        (
            "shared_host_namespace",
            "encrypted",
            "service_bearer_static",
            False,
            "non_loopback_bind_requires_full_signed_ingress",
        ),
        (
            "separate_namespace",
            "trusted_lan",
            "none",
            False,
            "non_loopback_bind_requires_full_signed_ingress",
        ),
        (
            "separate_namespace",
            "rfc1918_plaintext",
            "service_bearer_static",
            False,
            "non_loopback_bind_requires_full_signed_ingress",
        ),
        (
            "separate_namespace",
            "encrypted",
            "none",
            False,
            "non_loopback_bind_requires_full_signed_ingress",
        ),
        # loopback keeps its 010 behavior regardless of the contract
        (
            "shared_host_namespace",
            "loopback",
            "full_signed_v1",
            True,
            "supported_colocated_loopback",
        ),
        (
            "shared_host_namespace",
            "loopback",
            "service_bearer_static",
            True,
            "supported_colocated_loopback",
        ),
        (
            "separate_namespace",
            "loopback",
            "full_signed_v1",
            False,
            "loopback_does_not_cross_namespaces",
        ),
        (
            "separate_namespace",
            "loopback",
            "none",
            False,
            "loopback_does_not_cross_namespaces",
        ),
        # unknown inputs fail closed
        (
            "shared_host_namespace",
            "trusted_lan",
            "unknown_contract",
            False,
            "unknown_transport_fails_closed",
        ),
    ],
)
def test_transport_decision_table_lan_visible_signed_variant(
    namespace_mode: str,
    address_class: str,
    contract: str,
    qualified: bool,
    reason: str,
) -> None:
    assert QUALIFICATION.qualify_transport(namespace_mode, address_class, contract) == (
        qualified,
        reason,
    )


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


def test_manifest_lan_visible_variant_matches_the_decision_table() -> None:
    manifest = json.loads(
        (REPO_ROOT / "docs" / "topology.manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["schema"] == "slaif-topology-manifest-v2"
    assert manifest["version"] == 2
    lan = manifest["lan_visible_variant"]
    assert lan["binding_law"] == "non_loopback_bind_only_under_full_signed_ingress"
    for entry in lan["supported_combinations"]:
        qualifies, reason = QUALIFICATION.qualify_transport(
            str(entry["gateway_namespace_mode"]),
            str(entry["endpoint_address_class"]),
            str(entry["ingress_contract"]),
        )
        assert qualifies is True, entry
        assert reason == entry["reason"] == "supported_lan_visible_signed", entry
        assert entry["ingress_contract"] == "full_signed_v1"
    for entry in lan["rejected_combinations"]:
        qualifies, reason = QUALIFICATION.qualify_transport(
            str(entry["gateway_namespace_mode"]),
            str(entry["endpoint_address_class"]),
            str(entry["ingress_contract"]),
        )
        assert qualifies is False, entry
        assert reason == entry["reason"], entry
    # The cross-namespace loopback assumption stays rejected even with the
    # full signed contract (impossible hop, not a contract problem).
    rejected_loops = [
        e
        for e in lan["rejected_combinations"]
        if e["endpoint_address_class"] == "loopback" and e["ingress_contract"] == "full_signed_v1"
    ]
    assert rejected_loops and rejected_loops[0]["reason"] == "loopback_does_not_cross_namespaces"
    # The per-hop rows: none of them is publicly reachable.
    assert lan["hops"], "LAN-visible per-hop rows must exist"
    for hop in lan["hops"]:
        assert hop["publicly_reachable"] is False
        assert hop["authentication"].startswith("service_bearer_signed_identity_v1")


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
