"""Durable model, recipe, bounds and namespace revalidation tests
for the 018-e pure nonroot currentness overlay (INERT).

The record invariants port the ROOT-reviewed constructor
counterexamples (record-invariants v1/v2/v3 captures, preserved
under the strategic directory): the five overcorrection negatives,
the mixed-blocker GROUP historical-candidate law, the global
path antichain law and the reverse-index subset law (checked
BEFORE any status shortcut).  The namespace tests port the
D3 full-field-shape revalidation counterexamples: coherent keys
cannot rescue an invalid actual lineage or an unsupported
actual version.
"""

from __future__ import annotations

import hashlib
import inspect
from typing import Any

import pytest
from pydantic import ValidationError

from slaif_local_coding.constitution.bundles.bundle_admission_models import (
    AdmissionMode,
    BoundaryClass,
    _canonical_namespace_fields,
)
from slaif_local_coding.constitution.bundles.causal_history import (
    observe_causal_history,
)
from slaif_local_coding.constitution.bundles.causal_history_models import (
    CausalHistoryNamespace,
    CausalHistoryOutcome,
    _canonical_history_fields,
)
from slaif_local_coding.constitution.bundles.currentness import (
    derive_currentness_overlay,
)
from slaif_local_coding.constitution.bundles.currentness_models import (
    CURRENTNESS_POLICY_VERSION,
    CurrentnessBounds,
    CurrentnessGroupRecord,
    CurrentnessLimitation,
    CurrentnessOutcome,
    CurrentnessOverlay,
    CurrentnessPathRecord,
    CurrentnessReason,
    CurrentnessResult,
    CurrentnessStatus,
    GroupPathRow,
    OpaqueGroupFacts,
    currentness_scope_key,
    opaque_group_identity,
)
from tests.test_causal_history import (
    ENDPOINTS,
    MODES,
    empty_state,
    make_ns,
    root_request,
)


def _hex64(seed: str) -> str:
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


# --- The versioned opaque-group recipe ---------------------------------


def test_opaque_recipe_is_deterministic_and_versioned() -> None:
    first = opaque_group_identity(
        BoundaryClass.BOUNDARYLESS, ("A.md", "B.md"), _hex64("g1"), (None, None)
    )
    again = opaque_group_identity(
        BoundaryClass.BOUNDARYLESS, ("A.md", "B.md"), _hex64("g1"), (None, None)
    )
    assert first == again
    # Ordered member occurrences: AB and BA are DISTINCT group
    # identities even when the aggregate bytes happen to match.
    inverted = opaque_group_identity(
        BoundaryClass.BOUNDARYLESS, ("B.md", "A.md"), _hex64("g1"), (None, None)
    )
    assert first != inverted
    # Group-local shape only: identical shape at DIFFERENT positions,
    # indices or proof coordinates keeps the SAME identity (the
    # standalone-vs-isolated group law).
    isolated = opaque_group_identity(
        BoundaryClass.BOUNDARYLESS, ("A.md", "B.md"), _hex64("g1"), (None, None)
    )
    assert isolated == first
    # A different exact group bytes digest is a different identity.
    other_bytes = opaque_group_identity(
        BoundaryClass.BOUNDARYLESS, ("A.md", "B.md"), _hex64("g2"), (None, None)
    )
    assert other_bytes != first
    # A granted per-member digest changes the semantic shape.
    known = opaque_group_identity(
        BoundaryClass.BOUNDARYLESS, ("A.md", "B.md"), _hex64("g1"), (_hex64("a"), None)
    )
    assert known != first
    # The boundary class is part of the shape.
    proven = opaque_group_identity(BoundaryClass.PROVEN, ("A.md",), _hex64("a"), (_hex64("a"),))
    assert proven != first


def test_opaque_recipe_binds_all_three_versions() -> None:
    base = dict(
        boundary_class=BoundaryClass.BOUNDARYLESS,
        members=("A.md", "B.md"),
        group_digest=_hex64("g1"),
        member_digests=(None, None),
    )
    for field in ("policy_version", "proof_version", "observation_version"):
        changed = dict(base, **{field: "other-recipe/v99"})
        assert opaque_group_identity(**changed) != opaque_group_identity(**base)  # type: ignore[arg-type]


def test_opaque_group_facts_recompute_identity_and_boundary_law() -> None:
    digest = _hex64("member-a")
    facts = OpaqueGroupFacts(
        boundary_class=BoundaryClass.PROVEN,
        members=("A.md",),
        group_digest=digest,
        member_digests=(digest,),
        identity=opaque_group_identity(BoundaryClass.PROVEN, ("A.md",), digest, (digest,)),
    )
    assert facts.identity == opaque_group_identity(
        BoundaryClass.PROVEN, ("A.md",), digest, (digest,)
    )
    # A forged identity is refused: the recipe is recomputed.
    with pytest.raises(ValidationError):
        OpaqueGroupFacts(
            boundary_class=BoundaryClass.PROVEN,
            members=("A.md",),
            group_digest=digest,
            member_digests=(digest,),
            identity=_hex64("forged"),
        )
    # A proven singleton's group digest IS the granted member digest.
    with pytest.raises(ValidationError):
        OpaqueGroupFacts(
            boundary_class=BoundaryClass.PROVEN,
            members=("A.md",),
            group_digest=_hex64("other"),
            member_digests=(digest,),
            identity=opaque_group_identity(
                BoundaryClass.PROVEN, ("A.md",), _hex64("other"), (digest,)
            ),
        )
    # A boundaryless group never carries a per-file digest and has
    # no proven singleton form.
    with pytest.raises(ValidationError):
        OpaqueGroupFacts(
            boundary_class=BoundaryClass.BOUNDARYLESS,
            members=("A.md", "B.md"),
            group_digest=_hex64("g"),
            member_digests=(digest, None),
            identity=opaque_group_identity(
                BoundaryClass.BOUNDARYLESS,
                ("A.md", "B.md"),
                _hex64("g"),
                (digest, None),
            ),
        )
    with pytest.raises(ValidationError):
        OpaqueGroupFacts(
            boundary_class=BoundaryClass.BOUNDARYLESS,
            members=("A.md",),
            group_digest=_hex64("g"),
            member_digests=(None,),
            identity=opaque_group_identity(
                BoundaryClass.BOUNDARYLESS, ("A.md",), _hex64("g"), (None,)
            ),
        )
    # A PROVEN multi-member segment cannot be represented by the
    # accepted boundary law (it is boundaryless, never proven).
    with pytest.raises(ValidationError):
        OpaqueGroupFacts(
            boundary_class=BoundaryClass.PROVEN,
            members=("A.md", "B.md"),
            group_digest=_hex64("g"),
            member_digests=(None, None),
            identity=opaque_group_identity(
                BoundaryClass.PROVEN, ("A.md", "B.md"), _hex64("g"), (None, None)
            ),
        )


# --- Group path rows (historical candidate law) ------------------------


def _row(
    status: CurrentnessStatus,
    reasons: tuple[CurrentnessReason, ...],
    witnesses: tuple[str, ...] = (),
    path: str = "A.md",
) -> GroupPathRow:
    return GroupPathRow(path=path, status=status, reasons=reasons, witnesses=witnesses)


def test_group_row_current_forms_carry_no_blockers() -> None:
    for status in (
        CurrentnessStatus.CURRENT_KNOWN,
        CurrentnessStatus.CURRENT_OPAQUE,
    ):
        assert _row(status, ()).status is status
        with pytest.raises(ValidationError):
            _row(
                status,
                (CurrentnessReason.OWNERSHIP_AMBIGUITY,),
                witnesses=(_hex64("w"),),
            )


def test_group_row_mixed_incomparable_blockers_retained() -> None:
    """A known candidate meeting incomparable known-different AND
    unknown witnesses concurrently: status priority
    CONTENT_CONFLICT, BOTH reasons and witnesses retained (the v3
    overcorrection counterexample)."""
    known_w, opaque_w = sorted((_hex64("known-witness"), _hex64("opaque-witness")))
    row = _row(
        CurrentnessStatus.CONTENT_CONFLICT,
        (CurrentnessReason.KNOWN_CONTENT_CONFLICT, CurrentnessReason.OWNERSHIP_AMBIGUITY),
        witnesses=(known_w, opaque_w),
    )
    assert row.status is CurrentnessStatus.CONTENT_CONFLICT
    assert row.reasons == (
        CurrentnessReason.KNOWN_CONTENT_CONFLICT,
        CurrentnessReason.OWNERSHIP_AMBIGUITY,
    )
    assert row.witnesses == (known_w, opaque_w)
    # A conflict row without its known-content blocker is invalid.
    with pytest.raises(ValidationError):
        _row(
            CurrentnessStatus.CONTENT_CONFLICT,
            (CurrentnessReason.OWNERSHIP_AMBIGUITY,),
            witnesses=(_hex64("w"),),
        )


def test_group_row_stale_priority_and_ambiguity_exclusivity() -> None:
    # Stale reasons force STALE by worst priority (any combination).
    w_a, w_b = sorted((_hex64("stale-a"), _hex64("stale-b")))
    assert (
        _row(
            CurrentnessStatus.STALE,
            (
                CurrentnessReason.OWNERSHIP_AMBIGUITY,
                CurrentnessReason.PROVEN_CHANGE,
            ),
            witnesses=(w_a, w_b),
        ).status
        is CurrentnessStatus.STALE
    )
    with pytest.raises(ValidationError):
        _row(
            CurrentnessStatus.CONTENT_CONFLICT,
            (CurrentnessReason.PROVEN_CHANGE,),
            witnesses=(_hex64("w"),),
        )
    with pytest.raises(ValidationError):
        _row(
            CurrentnessStatus.OWNERSHIP_AMBIGUITY,
            (CurrentnessReason.UNPROVEN_OWNERSHIP,),
            witnesses=(_hex64("w"),),
        )
    # An ambiguity row cannot carry the known-conflict priority.
    with pytest.raises(ValidationError):
        _row(
            CurrentnessStatus.OWNERSHIP_AMBIGUITY,
            (
                CurrentnessReason.KNOWN_CONTENT_CONFLICT,
                CurrentnessReason.OWNERSHIP_AMBIGUITY,
            ),
            witnesses=(_hex64("w"),),
        )
    # A stale row must carry a stale blocker reason.
    with pytest.raises(ValidationError):
        _row(
            CurrentnessStatus.STALE,
            (CurrentnessReason.KNOWN_CONTENT_CONFLICT,),
            witnesses=(_hex64("w"),),
        )
    # Unsorted/duplicated witnesses are refused.
    with pytest.raises(ValidationError):
        _row(
            CurrentnessStatus.OWNERSHIP_AMBIGUITY,
            (CurrentnessReason.OWNERSHIP_AMBIGUITY,),
            witnesses=(w_b, w_a),
        )


# --- Group records -------------------------------------------------------


def _group_record(
    members: tuple[str, ...],
    member_digests: tuple[str | None, ...],
    path_rows: tuple[GroupPathRow, ...],
    group_status: CurrentnessStatus,
    root_path: str | None = None,
    group_index: int = 0,
) -> CurrentnessGroupRecord:
    boundary = (
        BoundaryClass.PROVEN
        if len(members) == 1 and member_digests[0] is not None
        else BoundaryClass.BOUNDARYLESS
    )
    if boundary is BoundaryClass.PROVEN:
        assert member_digests[0] is not None
        group_digest = member_digests[0]
    else:
        group_digest = _hex64("g")
    return CurrentnessGroupRecord(
        occurrence_id=_hex64("occ"),
        group_index=group_index,
        boundary_class=boundary,
        members=members,
        member_digests=member_digests,
        root_path=root_path,
        opaque_identity=opaque_group_identity(boundary, members, group_digest, member_digests),
        path_rows=path_rows,
        group_status=group_status,
    )


def test_group_record_path_coverage_and_root_scope() -> None:
    # Path rows cover EXACTLY the represented nonroot paths: the
    # proven root member carries no row.
    row = _row(CurrentnessStatus.CURRENT_OPAQUE, ())
    record = _group_record(
        ("AGENTS.md", "A.md"),
        (None, None),
        (row,),
        CurrentnessStatus.CURRENT_OPAQUE,
        root_path="AGENTS.md",
    )
    assert record.root_path == "AGENTS.md"
    assert [r.path for r in record.path_rows] == ["A.md"]
    with pytest.raises(ValidationError):
        _group_record(
            ("AGENTS.md", "A.md"),
            (None, None),
            (row, GroupPathRow(path="AGENTS.md", status=CurrentnessStatus.CURRENT_OPAQUE)),
            CurrentnessStatus.CURRENT_OPAQUE,
            root_path="AGENTS.md",
        )
    # A group with NO nonroot members (root-only proof) is
    # current-opaque ONLY.
    assert (
        _group_record(
            ("AGENTS.md",), (None,), (), CurrentnessStatus.CURRENT_OPAQUE, root_path="AGENTS.md"
        ).group_status
        is CurrentnessStatus.CURRENT_OPAQUE
    )
    with pytest.raises(ValidationError):
        _group_record(
            ("AGENTS.md",),
            (None,),
            (),
            CurrentnessStatus.CURRENT_KNOWN,
            root_path="AGENTS.md",
        )


def test_group_record_status_is_exact_worst_of_rows() -> None:
    a = _row(CurrentnessStatus.CURRENT_KNOWN, (), path="A.md")
    b = _row(
        CurrentnessStatus.CONTENT_CONFLICT,
        (CurrentnessReason.KNOWN_CONTENT_CONFLICT,),
        witnesses=(_hex64("w"),),
        path="B.md",
    )
    assert (
        _group_record(
            ("A.md", "B.md"),
            (None, None),
            (a, b),
            CurrentnessStatus.CONTENT_CONFLICT,
        ).group_status
        is CurrentnessStatus.CONTENT_CONFLICT
    )
    with pytest.raises(ValidationError):
        _group_record(
            ("A.md", "B.md"),
            (None, None),
            (a, b),
            CurrentnessStatus.OWNERSHIP_AMBIGUITY,
        )


# --- Global path records (frontier antichain law) -----------------------


def _path_record(
    status: CurrentnessStatus,
    known_digest: str | None = None,
    opaque_identity: str | None = None,
    reasons: tuple[CurrentnessReason, ...] = (),
    witnesses: tuple[str, ...] | None = None,
    overlapping: tuple[str, ...] | None = None,
) -> CurrentnessPathRecord:
    w = witnesses if witnesses is not None else (_hex64("w"),)
    o = overlapping if overlapping is not None else w
    return CurrentnessPathRecord(
        path="A.md",
        status=status,
        known_digest=known_digest,
        opaque_identity=opaque_identity,
        reasons=reasons,
        witnesses=w,
        overlapping_occurrences=o,
    )


def test_path_record_can_never_be_stale() -> None:
    with pytest.raises(ValidationError):
        _path_record(
            CurrentnessStatus.STALE,
            reasons=(CurrentnessReason.PROVEN_CHANGE,),
        )


def test_path_record_reverse_index_subset_checked_first() -> None:
    """The maximal-witness subset of the reverse path index is
    checked BEFORE any status shortcut: even a current-known record
    with a foreign witness is refused."""
    foreign, other = sorted((_hex64("foreign"), _hex64("other")))
    a, b = sorted((_hex64("occ-a"), _hex64("occ-b")))
    with pytest.raises(ValidationError):
        _path_record(
            CurrentnessStatus.CURRENT_KNOWN,
            known_digest=_hex64("d"),
            witnesses=(foreign,),
            overlapping=(other,),
        )
    # The legal form: witnesses are a subset of ALL overlapping
    # occurrences (dominated witnesses included in the index).
    record = _path_record(
        CurrentnessStatus.CURRENT_KNOWN,
        known_digest=_hex64("d"),
        witnesses=(a,),
        overlapping=(a, b),
    )
    assert record.overlapping_occurrences == (a, b)


def test_path_record_canonical_dominant_reason() -> None:
    """The GLOBAL path keeps its canonical dominant reason only
    (the mixed-blocker law targets GROUP historical candidate
    rows, not the frontier summary)."""
    record = _path_record(
        CurrentnessStatus.CONTENT_CONFLICT,
        reasons=(CurrentnessReason.KNOWN_CONTENT_CONFLICT,),
    )
    assert record.known_digest is None and record.opaque_identity is None
    with pytest.raises(ValidationError):
        _path_record(
            CurrentnessStatus.CONTENT_CONFLICT,
            reasons=(
                CurrentnessReason.KNOWN_CONTENT_CONFLICT,
                CurrentnessReason.OWNERSHIP_AMBIGUITY,
            ),
        )
    with pytest.raises(ValidationError):
        _path_record(
            CurrentnessStatus.OWNERSHIP_AMBIGUITY,
            reasons=(CurrentnessReason.KNOWN_CONTENT_CONFLICT,),
        )
    with pytest.raises(ValidationError):
        _path_record(
            CurrentnessStatus.CURRENT_KNOWN,
            known_digest=_hex64("d"),
            reasons=(CurrentnessReason.OWNERSHIP_AMBIGUITY,),
        )
    with pytest.raises(ValidationError):
        _path_record(
            CurrentnessStatus.CURRENT_OPAQUE,
            opaque_identity=_hex64("i"),
            known_digest=_hex64("d"),
        )


# --- Overlay and result invariants --------------------------------------


def test_overlay_scope_key_and_emitted_reasons() -> None:
    bounds = CurrentnessBounds()
    history_key = _hex64("history")
    overlay = CurrentnessOverlay(
        history_key=history_key,
        revision=1,
        workspace="/work",
        scope_key=currentness_scope_key(history_key, "/work", CURRENTNESS_POLICY_VERSION, bounds),
        emitted_reasons=0,
    )
    assert overlay.scope_key == currentness_scope_key(
        history_key, "/work", CURRENTNESS_POLICY_VERSION, bounds
    )
    with pytest.raises(ValidationError):
        CurrentnessOverlay(
            history_key=history_key,
            revision=1,
            workspace="/work",
            scope_key=_hex64("forged"),
            emitted_reasons=0,
        )
    # A different bound set is a different scope identity.
    stricter = CurrentnessBounds(max_paths=bounds.max_paths - 1)
    assert (
        currentness_scope_key(history_key, "/work", CURRENTNESS_POLICY_VERSION, stricter)
        != overlay.scope_key
    )


def test_result_ok_and_refusal_shapes() -> None:
    ns = make_ns(MODES[0], lineage="result-shape")
    state = empty_state(ns)
    with pytest.raises(ValidationError):
        CurrentnessResult(outcome=CurrentnessOutcome.OK, state=state)
    refusal = CurrentnessResult(
        outcome=CurrentnessOutcome.REFUSED_FOREIGN_SCOPE,
        state=state,
        diagnostics=(CurrentnessLimitation.FOREIGN_SCOPE,),
    )
    assert refusal.state is state and refusal.overlay is None
    with pytest.raises(ValidationError):
        CurrentnessResult(
            outcome=CurrentnessOutcome.REFUSED_FOREIGN_SCOPE,
            state=state,
        )
    with pytest.raises(ValidationError):
        CurrentnessResult(
            outcome=CurrentnessOutcome.OK,
            state=state,
            overlay=CurrentnessOverlay(
                history_key=state.history_key,
                revision=0,
                workspace=ns.workspace,
                scope_key=currentness_scope_key(
                    state.history_key,
                    ns.workspace,
                    CURRENTNESS_POLICY_VERSION,
                    CurrentnessBounds(),
                ),
                emitted_reasons=0,
            ),
            diagnostics=(CurrentnessLimitation.FOREIGN_SCOPE,),
        )


# --- Currentness bounds ---------------------------------------------------


_BOUND_FIELDS = (
    "max_paths",
    "max_groups",
    "max_witness_memberships",
    "max_relation_pairs",
    "max_work_units",
    "max_diagnostics",
)


def test_bounds_stricter_supported_wider_refused() -> None:
    defaults = CurrentnessBounds()
    for field in _BOUND_FIELDS:
        default = getattr(defaults, field)
        # Strict positive values are supported.
        stricter = CurrentnessBounds.model_validate({**defaults.model_dump(), field: default - 1})
        assert getattr(stricter, field) == default - 1
        # Wider than the hard ceiling is refused.
        with pytest.raises(ValidationError):
            CurrentnessBounds.model_validate({**defaults.model_dump(), field: default + 1})
        with pytest.raises(ValidationError):
            CurrentnessBounds.model_validate({**defaults.model_dump(), field: 0})


# --- Namespace full-field revalidation (D3) ------------------------------


def _booted_ns_state(mode: AdmissionMode, lineage: str) -> tuple[CausalHistoryNamespace, Any]:
    ns = make_ns(mode, lineage=lineage)
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    return ns, boot.state


def _coherent_rekeyed_ns(
    ns: CausalHistoryNamespace, updates: dict[str, str | None]
) -> CausalHistoryNamespace:
    """A coherent DIRECT-constructed causal-history scope carrying
    the ACTUAL updated fields: every real field copied, the named
    version/lineage fields replaced, and the FULL key chain
    recomputed from the actual fields (admission namespace key,
    admission scoped key, history key, state scoped key).  The real
    constructor revalidates the whole recomputation, so a stale key
    or any shape defect would raise at construction."""
    fields: dict[str, object] = {
        name: getattr(ns, name) for name in CausalHistoryNamespace.model_fields
    }
    fields.update(updates)
    admission_canonical = {
        name: fields[name] for name in inspect.signature(_canonical_namespace_fields).parameters
    }
    admission_canonical["mode"] = str(ns.mode)
    admission_key = hashlib.sha256(
        _canonical_namespace_fields(**admission_canonical)  # type: ignore[arg-type]
    ).hexdigest()
    scoped_key = hashlib.sha256(
        (admission_key + "\0" + str(fields["workspace"])).encode()
    ).hexdigest()
    # The admission keys land in the field set BEFORE the history
    # canonical is read: for a changed base version the history key
    # depends on the RECOMPUTED admission key pair.
    fields["admission_namespace_key"] = admission_key
    fields["admission_scoped_key"] = scoped_key
    history_canonical = {
        name: fields[name] for name in inspect.signature(_canonical_history_fields).parameters
    }
    history_canonical["mode"] = str(ns.mode)
    history_key = hashlib.sha256(
        _canonical_history_fields(**history_canonical)  # type: ignore[arg-type]
    ).hexdigest()
    fields["history_key"] = history_key
    fields["state_scoped_key"] = hashlib.sha256(
        (history_key + "\0" + str(fields["workspace"])).encode()
    ).hexdigest()
    return CausalHistoryNamespace(**fields)  # type: ignore[arg-type]


def _coherent_forged_ns(
    ns: CausalHistoryNamespace, updates: dict[str, str | None]
) -> CausalHistoryNamespace:
    """Like ``_coherent_rekeyed_ns`` but via ``model_construct`` for
    shapes the REAL constructor refuses (e.g. an invalid lineage):
    the coherent recomputed keys are carried on an unvalidated
    instance so ONLY the actual-field shape can make the public
    derivation refuse."""
    fields: dict[str, object] = {
        name: getattr(ns, name) for name in CausalHistoryNamespace.model_fields
    }
    fields.update(updates)
    history_canonical = {
        name: fields[name] for name in inspect.signature(_canonical_history_fields).parameters
    }
    history_canonical["mode"] = str(ns.mode)
    history_key = hashlib.sha256(
        _canonical_history_fields(**history_canonical)  # type: ignore[arg-type]
    ).hexdigest()
    fields["history_key"] = history_key
    fields["state_scoped_key"] = hashlib.sha256(
        (history_key + "\0" + str(fields["workspace"])).encode()
    ).hexdigest()
    return CausalHistoryNamespace.model_construct(**fields)  # type: ignore[arg-type]


@pytest.mark.parametrize("mode", MODES)
def test_ns_invalid_lineage_refused_despite_coherent_keys(mode: AdmissionMode) -> None:
    """Coherent RECOMPUTED keys cannot rescue an invalid ACTUAL
    lineage (empty / over-long / None): the fresh real constructor
    refuses the shape itself, and the public derivation refuses with
    a fixed typed result over the EXACT re-keyed negative state
    (the early foreign guard cannot mask: the negative state's
    history key MATCHES the forged namespace).  No source
    authentication claim is made from this negative fixture."""
    ns, state = _booted_ns_state(mode, f"lineage-{mode.value}")
    for bad in ("", "x" * 129, None):
        updates = {"lineage_id": bad}
        # The fresh REAL namespace constructor refuses the shape,
        # even with the fully coherent recomputed key chain.
        with pytest.raises(ValidationError):
            _coherent_rekeyed_ns(ns, updates)
        forged = _coherent_forged_ns(ns, updates)
        assert forged.lineage_id == bad
        assert forged.history_key != ns.history_key  # the bad lineage moved the scope
        negative_state = state.model_copy(update={"history_key": forged.history_key})
        assert negative_state.history_key == forged.history_key
        result = derive_currentness_overlay(negative_state, forged)
        assert result.outcome is CurrentnessOutcome.REFUSED_VERSION_CONFLICT
        assert result.state is negative_state
        assert result.overlay is None
        assert result.diagnostics == (CurrentnessLimitation.VERSION_UNSUPPORTED,)


@pytest.mark.parametrize("mode", MODES)
def test_ns_unsupported_actual_versions_refused(mode: AdmissionMode) -> None:
    """EVERY one of the SEVEN actual version identities, when
    unsupported, is refused by the supported-version fence BEFORE
    positive interpretation -- with a FULLY coherent namespace
    (all actual fields, the whole admission-scoped and history key
    chain recomputed) and a matching negative state, so neither the
    foreign guard nor any key/shape defect can mask the fence.  The
    fresh real constructor ACCEPTS the coherent typed shape, proving
    the refusal is the version fence and not construction."""
    ns, state = _booted_ns_state(mode, f"versions-{mode.value}")
    for field in (
        "admission_version",
        "observation_version",
        "graph_version",
        "reference_version",
        "proof_version",
        "history_version",
        "arguments_version",
    ):
        coherent = _coherent_rekeyed_ns(ns, {field: "unsupported-synthetic/v99"})
        assert getattr(coherent, field) == "unsupported-synthetic/v99"
        assert coherent.history_key != ns.history_key
        negative_state = state.model_copy(update={"history_key": coherent.history_key})
        assert negative_state.history_key == coherent.history_key
        result = derive_currentness_overlay(negative_state, coherent)
        assert result.outcome is CurrentnessOutcome.REFUSED_VERSION_CONFLICT, field
        assert result.state is negative_state
        assert result.overlay is None
        assert result.diagnostics == (CurrentnessLimitation.VERSION_UNSUPPORTED,), field


@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_ns_foreign_scope_refused(endpoint: str) -> None:
    ns, state = _booted_ns_state(MODES[0], f"foreign-{endpoint}")
    other_ns = make_ns(MODES[0], lineage=f"other-{endpoint}")
    assert other_ns.history_key != ns.history_key
    result = derive_currentness_overlay(state, other_ns)
    assert result.outcome is CurrentnessOutcome.REFUSED_FOREIGN_SCOPE
    assert result.state is state and result.overlay is None
    assert result.diagnostics == (CurrentnessLimitation.FOREIGN_SCOPE,)
