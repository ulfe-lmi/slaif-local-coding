"""018-a: typed graph foundation records — validation, privacy, invariants."""

from __future__ import annotations

import hashlib

import pytest
from pydantic import ValidationError

from slaif_local_coding.constitution.bundles import (
    GRAPH_CONTRACT_VERSION,
    REFERENCE_GRAMMAR,
    GraphBounds,
    GraphEdge,
    GraphLimitation,
    GraphNamespace,
    GraphOutcome,
    GraphSnapshot,
    NodeStatus,
    SourceDocument,
    SourceKind,
    SourceOccurrence,
    make_graph_namespace,
)
from slaif_local_coding.constitution.bundles.observation_models import (
    EMPTY_SOURCE_SHA256,
    CharSpan,
)
from slaif_local_coding.constitution.cache import RequestIdentity

IDENTITY_KWARGS = dict(
    principal="synthetic-principal",
    session="synthetic-session",
    repository="synthetic-repository",
    route="synthetic-route",
)
CANARY = "SYNTHETIC_PRIVATE_SOURCE_CANARY_c20e"


def identity(**overrides: str) -> RequestIdentity:
    kwargs = dict(IDENTITY_KWARGS)
    kwargs.update(overrides)
    return RequestIdentity(**kwargs)


def make_namespace(**overrides: object) -> GraphNamespace:
    kwargs: dict[str, object] = dict(
        identity=identity(),
        model_identity="synthetic-model",
        config_fingerprint="a" * 64,
        workspace="/work",
        bounds=GraphBounds(),
    )
    kwargs.update(overrides)
    return make_graph_namespace(**kwargs)  # type: ignore[arg-type]


class TestNamespaceFactoryAndValidation:
    def test_factory_roundtrip_binds_identity_workspace_and_bounds(self) -> None:
        bounds = GraphBounds(max_nodes=7)
        ns = make_namespace(bounds=bounds)
        assert ns.principal == IDENTITY_KWARGS["principal"]
        assert ns.session == IDENTITY_KWARGS["session"]
        assert ns.repository == IDENTITY_KWARGS["repository"]
        assert ns.route == IDENTITY_KWARGS["route"]
        assert ns.model_identity == "synthetic-model"
        assert ns.config_fingerprint == "a" * 64
        assert ns.workspace == "/work"
        assert ns.bounds == bounds
        assert len(ns.namespace_key) == 64 and len(ns.scoped_key) == 64

    @pytest.mark.parametrize("field", ["principal", "session", "repository", "route"])
    def test_identity_components_required(self, field: str) -> None:
        with pytest.raises(ValidationError) as exc:
            make_namespace(identity=identity(**{field: ""}))
        assert CANARY not in str(exc)

    def test_fingerprint_must_be_64_hex(self) -> None:
        # Factory prechecks raise fixed ValueErrors (no input echo).
        with pytest.raises(ValueError):
            make_namespace(config_fingerprint="nothex")
        with pytest.raises(ValueError):
            make_namespace(config_fingerprint="a" * 63)

    def test_effective_bounds_binding_distinct_namespaces(self) -> None:
        base = make_namespace()
        other = make_namespace(bounds=GraphBounds(max_nodes=7))
        assert base.scoped_key != other.scoped_key

    def test_same_identity_and_bounds_stable_key(self) -> None:
        assert make_namespace().scoped_key == make_namespace().scoped_key

    def test_workspace_canonical_spelling_required(self) -> None:
        for bad in ("/work/", "//work", "/work/./", "/work//sub", "work"):
            with pytest.raises((ValidationError, ValueError)):
                make_namespace(workspace=bad)

    def test_direct_namespace_actual_path_bound_enforced(self) -> None:
        # A workspace wider than the configured path bound is refused at
        # every entry point (the factory cannot ignore actual bounds).
        with pytest.raises((ValidationError, ValueError)):
            make_namespace(
                workspace="/work",
                bounds=GraphBounds(max_path_bytes=4),
            )

    def test_direct_namespace_path_bound_is_the_failure(self) -> None:
        # Direct model construction with CORRECTLY RECOMPUTED keys for a
        # 10-byte workspace under an 8-byte bound: shape and key
        # integrity all hold, so the refusal can only be the ACTUAL
        # configured workspace bound — not stale keys or factory
        # prevalidation.
        ns = make_namespace(bounds=GraphBounds(max_path_bytes=8))
        long_workspace = "/work-long"  # 10 bytes at the 8-byte bound
        assert len(long_workspace.encode("utf-8")) == 10
        scoped_key = hashlib.sha256(
            (ns.namespace_key + "\0" + long_workspace).encode("utf-8")
        ).hexdigest()
        with pytest.raises(ValidationError, match="path bound"):
            GraphNamespace(
                principal=ns.principal,
                session=ns.session,
                repository=ns.repository,
                route=ns.route,
                model_identity=ns.model_identity,
                config_fingerprint=ns.config_fingerprint,
                workspace=long_workspace,
                bounds=ns.bounds,
                namespace_key=ns.namespace_key,
                scoped_key=scoped_key,
            )

    def test_direct_namespace_key_integrity(self) -> None:
        # Direct model construction cannot retain forged scoped keys:
        # the key must bind identity/config/bounds/workspace.
        ns = make_namespace()
        with pytest.raises(ValidationError):
            GraphNamespace(
                principal=ns.principal,
                session=ns.session,
                repository=ns.repository,
                route=ns.route,
                model_identity=ns.model_identity,
                config_fingerprint="b" * 64,  # different fingerprint...
                workspace=ns.workspace,
                bounds=ns.bounds,
                namespace_key=ns.namespace_key,  # ...with the old key
                scoped_key=ns.scoped_key,
            )

    def test_namespace_repr_never_echoes_private_values(self) -> None:
        secret = "PRIVATE-IDENTITY-" + "z" * 32
        ns = make_namespace(
            identity=identity(principal=secret),
            model_identity="model-" + secret,
        )
        for text in (str(ns), repr(ns)):
            assert secret not in text


class TestFrozenAndEnums:
    def test_frozen_and_extra_forbid(self) -> None:
        ns = make_namespace()
        with pytest.raises(ValidationError):
            ns.principal = "x"  # frozen at runtime; mypy sees plain assignment
        with pytest.raises(ValidationError):
            GraphSnapshot(
                namespace=ns,
                outcome=GraphOutcome.NO_ROOT,
                bogus_field="x",  # type: ignore[call-arg]
            )

    def test_enum_vocabulary_fixed(self) -> None:
        assert {o.value for o in GraphOutcome} == {
            "complete",
            "no_root",
            "workspace_unproven",
            "root_conflict",
            "version_conflict",
            "over_bound",
        }
        assert {s.value for s in NodeStatus} == {
            "acquired",
            "acquired_empty",
            "discovered_content_missing",
            "version_conflict",
        }
        assert GraphLimitation.DIAGNOSTICS_FULL.value == "diagnostics_full"
        assert GraphLimitation.BOUNDS_MISMATCH.value == "bounds_mismatch"
        assert GraphLimitation.CANDIDATE_DIGEST_MISMATCH.value == ("candidate_digest_mismatch")
        assert GRAPH_CONTRACT_VERSION == "cache-graph/v1"
        assert REFERENCE_GRAMMAR == "reference-grammar/v1"

    def test_snapshot_rejects_unknown_conflict_strings(self) -> None:
        ns = make_namespace()
        with pytest.raises(ValidationError):
            GraphSnapshot(namespace=ns, outcome=GraphOutcome.NO_ROOT, conflicts=("bogus",))  # type: ignore[arg-type]


class TestPrivacySafeDiagnostics:
    def test_diagnostics_closed_vocabulary_rejects_arbitrary_text(self) -> None:
        ns = make_namespace()
        with pytest.raises(ValidationError) as exc:
            GraphSnapshot(namespace=ns, outcome=GraphOutcome.NO_ROOT, diagnostics=(CANARY,))  # type: ignore[arg-type]
        assert CANARY not in str(exc)

    def test_diagnostics_accept_fixed_enum_and_never_echo(self) -> None:
        ns = make_namespace()
        snap = GraphSnapshot(
            namespace=ns,
            outcome=GraphOutcome.NO_ROOT,
            diagnostics=(GraphLimitation.NO_ROOT,),
        )
        assert snap.diagnostics == (GraphLimitation.NO_ROOT,)
        assert CANARY not in str(snap)

    def test_validation_errors_hide_input_values(self) -> None:
        with pytest.raises(ValidationError) as exc:
            SourceDocument(
                path=CANARY,
                scoped_key="a" * 64,
                digest="1" * 64,
                status=NodeStatus.ACQUIRED,
                kind=SourceKind.ROOT,
                occurrences=(),
            )
        assert CANARY not in str(exc)


class TestEdgeDepthAndEmptySource:
    def test_edge_depth_zero_allowed_for_root_self_reference(self) -> None:
        edge = GraphEdge(
            scoped_key="a" * 64,
            from_path="AGENTS.md",
            to_path="AGENTS.md",
            referring_digest="1" * 64,
            occurrence_index=0,
            depth=0,
        )
        assert edge.depth == 0
        with pytest.raises(ValidationError):
            GraphEdge(
                scoped_key="a" * 64,
                from_path="AGENTS.md",
                to_path="AGENTS.md",
                referring_digest="1" * 64,
                occurrence_index=0,
                depth=-1,
            )

    def test_acquired_empty_requires_exact_empty_source_digest(self) -> None:
        # Empty source proof = exact empty digest plus a REAL zero-width
        # original carrier occurrence (the 017 zero-width carrier law).
        zero_occ = SourceOccurrence(
            request_index=0,
            carrier_location="$.input[1]",
            piece_index=0,
            span=CharSpan(start=3, end=3),
        )
        ok = SourceDocument(
            path="docs/A.md",
            scoped_key="a" * 64,
            digest=EMPTY_SOURCE_SHA256,
            byte_length=0,
            char_length=0,
            status=NodeStatus.ACQUIRED_EMPTY,
            kind=SourceKind.READ,
            occurrences=(zero_occ,),
        )
        assert ok.digest == hashlib.sha256(b"").hexdigest()
        with pytest.raises(ValidationError):
            SourceDocument(
                path="docs/A.md",
                scoped_key="a" * 64,
                digest="2" * 64,  # a non-empty 64-hex digest is NOT empty proof
                byte_length=0,
                char_length=0,
                status=NodeStatus.ACQUIRED_EMPTY,
                kind=SourceKind.READ,
                # Same REAL zero-width occurrence as the valid case:
                # only the digest changes, so the refusal isolates the
                # exact-empty-digest invariant (empty occurrences would
                # independently invalidate and confound the test).
                occurrences=(zero_occ,),
            )

    def test_missing_node_requires_no_fabricated_source_fields(self) -> None:
        doc = SourceDocument(
            path="docs/GONE.md",
            scoped_key="a" * 64,
            status=NodeStatus.DISCOVERED_CONTENT_MISSING,
        )
        assert doc.digest is None
        assert doc.kind is None
        assert doc.occurrences == ()
        assert doc.byte_length is None

    def test_char_span_reuse_law(self) -> None:
        span = CharSpan(start=1, end=4)
        assert (span.start, span.end) == (1, 4)
        with pytest.raises(ValidationError):
            CharSpan(start=4, end=1)
