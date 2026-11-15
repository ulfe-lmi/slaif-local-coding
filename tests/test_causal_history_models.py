"""018-d: causal-history scope, bounds and the strict argument
fingerprint recipe -- durable known-synthetic controls.

PUBLIC-surface tests for the inert causal-history model layer:
the NEW finite ``HistoryBounds`` (defaults AND hard ceilings; ANY
wider direct or factory construction refused), the recompute-and-
verify ``CausalHistoryNamespace`` over the ACTUAL accepted 018-c
admission namespace (the actual field constraints AND both 64-hex
scope keys revalidated; forged nested model copies refused in
factory AND direct construction), and the ONE bounded canonical
argument-fingerprint recipe (``causal-arguments-json/v1``): strict
single-walk JSON object parsing, canonical sorted-key
serialization, exact string values, closed-enum refusals, the
per-argument AND shared cumulative byte budgets enforced BEFORE
any crossing copy (input preflight without encoding allocation,
every canonical byte charged before retention), work charged
before every node/key visit, and the domain-separated sha256
fingerprint.

All payloads/inputs are inline known-synthetic; no S runtime path
dependency; no model, native, client or service facility is
started.  These controls port the reviewed independent probe
cohorts (the 27 argument cases, the 16 scope cases plus
direct-construction cases, and the allocation/accounting boundary
cases) into durable repository tests.
"""

from __future__ import annotations

import builtins
import hashlib
import json
from typing import Final

import pytest
from pydantic import ValidationError

from slaif_local_coding.constitution.bundles import (
    causal_history_models as causal_history_module,
)
from slaif_local_coding.constitution.bundles.bundle_admission_models import (
    BundleAdmissionBounds,
    BundleAdmissionNamespace,
    _canonical_namespace_fields,
    make_bundle_admission_namespace,
)
from slaif_local_coding.constitution.bundles.bundle_proof_models import (
    BundlePiece,
    BundleProof,
    BundleProofKind,
    BundleSegment,
    BundleSurface,
)
from slaif_local_coding.constitution.bundles.causal_history_models import (
    CAUSAL_ARGUMENTS_JSON_VERSION,
    CAUSAL_HISTORY_CONTRACT_VERSION,
    CAUSAL_ROOT_FACT,
    MAX_REVISION,
    ArgumentFingerprintResult,
    CausalHistoryLimitation,
    CausalHistoryNamespace,
    CausalHistoryOutcome,
    CausalHistoryState,
    CausalHistoryTransition,
    CompletedReadOccurrence,
    HistoryBounds,
    IssuedCall,
    ParentLink,
    ResultFingerprintRecord,
    RootAnchor,
    _canonical_history_fields,
    _sha256_hex,
    canonicalize_tool_arguments,
    make_causal_history_namespace,
    validate_causal_history_state,
)
from slaif_local_coding.constitution.bundles.observation_models import (
    PRIVATE_ID_PLACEHOLDER,
    CharSpan,
    Limitation,
    NormalizedPath,
    PathForm,
)
from slaif_local_coding.constitution.cache import RequestIdentity

# --- known-synthetic scope fixtures --------------------------------------

IDENTITY = RequestIdentity(
    principal="synthetic-causal-principal",
    session="synthetic-causal-session",
    repository="synthetic-causal-repo",
    route="synthetic-causal-route",
)
MODEL_IDENTITY = "synthetic-causal-model"
CONFIG_FINGERPRINT = "abcdef0123456789" * 4
WORKSPACE = "/work"
LINEAGE = "synthetic-causal-lineage"
LINEAGE_ALT = "synthetic-causal-lineage-alt"


def make_admission() -> BundleAdmissionNamespace:
    return make_bundle_admission_namespace(
        IDENTITY,
        model_identity=MODEL_IDENTITY,
        config_fingerprint=CONFIG_FINGERPRINT,
        workspace=WORKSPACE,
    )


# --- recipe test harness ---------------------------------------------------


class _Ledger:
    """Recording shared cumulative argument-byte ledger.

    Never oversubscribes: a charge above the remaining allowance is
    refused (and recorded) instead of applied -- the test-side law
    the product must respect.
    """

    def __init__(self, budget: int) -> None:
        self.budget = budget
        self.left = budget
        self.applied: list[int] = []
        self.refused: list[int] = []
        self.attempts = 0

    def __call__(self, n: int) -> bool:
        self.attempts += 1
        if n > self.left:
            self.refused.append(n)
            return False
        self.left -= n
        self.applied.append(n)
        return True

    @property
    def applied_total(self) -> int:
        return sum(self.applied)


class _Work:
    def __init__(self, budget: int | None = None) -> None:
        self.budget = budget
        self.visits = 0

    def __call__(self) -> bool:
        self.visits += 1
        return self.budget is None or self.visits <= self.budget


def call(
    arguments: str,
    *,
    tool: str = "exec_command",
    budget: int = 4_194_304,
    work_budget: int | None = None,
    ledger: _Ledger | None = None,
    **overrides: int,
) -> tuple[ArgumentFingerprintResult, _Ledger, _Work]:
    effective_ledger = ledger if ledger is not None else _Ledger(budget)
    work = _Work(work_budget)
    kwargs: dict[str, int] = {
        "max_argument_bytes": 65_536,
        "max_total_argument_bytes": 4_194_304,
        "max_argument_nodes": 4_096,
        "max_argument_depth": 32,
    }
    kwargs.update(overrides)
    result = canonicalize_tool_arguments(
        tool,
        arguments,
        max_argument_bytes=kwargs["max_argument_bytes"],
        max_total_argument_bytes=kwargs["max_total_argument_bytes"],
        max_argument_nodes=kwargs["max_argument_nodes"],
        max_argument_depth=kwargs["max_argument_depth"],
        charge_total=effective_ledger,
        work=work,
    )
    return result, effective_ledger, work


# --- A. recipe equivalence / inequality -----------------------------------


@pytest.mark.parametrize(
    ("case", "left", "right"),
    [
        (
            "nested_key_order_and_whitespace",
            '{"cmd":"cat A.md","options":{"b":2,"a":1}}',
            ' { "options": {"a":1,"b":2}, "cmd": "cat A.md" } ',
        ),
        (
            "escaped_ascii_key_and_value",
            '{"cmd":"cat A.md"}',
            '{"\\u0063md":"cat \\u0041.md"}',
        ),
        (
            "unicode_scalar_and_surrogate_pair",
            '{"cmd":"cat \U0001f600.md"}',
            '{"cmd":"cat \\ud83d\\ude00.md"}',
        ),
        (
            "escaped_solidus",
            '{"cmd":"cat docs/A.md"}',
            '{"cmd":"cat docs\\/A.md"}',
        ),
    ],
)
def test_same_canonical_form_same_fingerprint(case: str, left: str, right: str) -> None:
    a, la = call(left)[:2]
    b, lb = call(right)[:2]
    assert a.ok and b.ok
    assert a.fingerprint == b.fingerprint
    # every successful call accounts input + canonical exactly once
    assert la.applied_total == a.input_bytes + a.canonical_bytes
    assert lb.applied_total == b.input_bytes + b.canonical_bytes


@pytest.mark.parametrize(
    ("case", "left", "right"),
    [
        (
            "exact_shell_whitespace",
            '{"cmd":"cat A.md"}',
            '{"cmd":"cat  A.md"}',
        ),
        (
            "unicode_normalization_is_not_argument_equivalence",
            '{"cmd":"cat \u00e9.md"}',
            '{"cmd":"cat e\u0301.md"}',
        ),
        (
            "exact_string_case",
            '{"cmd":"cat A.md"}',
            '{"cmd":"cat a.md"}',
        ),
    ],
)
def test_different_content_different_fingerprint(case: str, left: str, right: str) -> None:
    a, _ = call(left)[:2]
    b, _ = call(right)[:2]
    assert a.ok and b.ok
    assert a.fingerprint != b.fingerprint


def test_tool_name_binds_fingerprint() -> None:
    a, _ = call('{"cmd":"cat A.md"}', tool="exec_command")[:2]
    b, _ = call('{"cmd":"cat A.md"}', tool="other_tool")[:2]
    assert a.ok and b.ok
    assert a.fingerprint != b.fingerprint


def test_fingerprint_is_domain_separated_sha256() -> None:
    arguments = '{"cmd":"cat A.md"}'
    result, ledger = call(arguments)[:2]
    assert result.ok
    want = hashlib.sha256(
        b"causal-arguments-json/v1\x00" + b"exec_command\x00" + _canonical_json(arguments)
    ).hexdigest()
    assert result.fingerprint == want
    assert ledger.applied_total == result.input_bytes + result.canonical_bytes


# --- B. recipe refusals (closed enum) ---------------------------------------


@pytest.mark.parametrize(
    ("case", "arguments", "reason"),
    [
        (
            "duplicate_literal_key",
            '{"cmd":"cat A.md","cmd":"cat B.md"}',
            CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED,
        ),
        (
            "duplicate_decoded_key",
            '{"cmd":"cat A.md","\\u0063md":"cat B.md"}',
            CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED,
        ),
        (
            "nested_duplicate_decoded_key",
            '{"cmd":"cat A.md","x":{"a":1,"\\u0061":2}}',
            CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED,
        ),
        ("nan", '{"cmd":NaN}', CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED),
        (
            "positive_infinity",
            '{"cmd":Infinity}',
            CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED,
        ),
        (
            "negative_infinity",
            '{"cmd":-Infinity}',
            CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED,
        ),
        (
            "finite_lexeme_float_overflow",
            '{"cmd":1e99999}',
            CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED,
        ),
        (
            "lone_high_surrogate",
            '{"cmd":"\\ud800"}',
            CausalHistoryLimitation.ARGUMENTS_MALFORMED_UNICODE,
        ),
        (
            "lone_low_surrogate",
            '{"cmd":"\\udc00"}',
            CausalHistoryLimitation.ARGUMENTS_MALFORMED_UNICODE,
        ),
        (
            "unescaped_control_character",
            '{"cmd":"cat\tA.md"}',
            CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED,
        ),
        ("top_level_array", "[]", CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED),
        ("top_level_null", "null", CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED),
        (
            "trailing_json",
            '{"cmd":"cat A.md"} {}',
            CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED,
        ),
    ],
)
def test_non_strict_json_is_refused(
    case: str, arguments: str, reason: CausalHistoryLimitation
) -> None:
    result, _ = call(arguments)[:2]
    assert not result.ok
    assert result.reason is reason


@pytest.mark.parametrize(
    "arguments",
    [
        '{"cmd":"\\u+041"}',
        '{"cmd":"\\u 041"}',
        '{"cmd":"\\u0_41"}',
        '{"cmd":"\\u41zz"}',
    ],
)
def test_strict_four_hex_digits_required(arguments: str) -> None:
    result, _ = call(arguments)[:2]
    assert not result.ok
    assert result.reason is CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED


def test_finite_extreme_float_accepted() -> None:
    result, _ = call('{"cmd":1e308}')[:2]
    assert result.ok
    assert result.reason is None


def test_negative_zero_canonicalizes_like_zero() -> None:
    a, _ = call('{"cmd":-0}')[:2]
    b, _ = call('{"cmd":0}')[:2]
    assert a.ok and b.ok
    assert a.fingerprint == b.fingerprint


# --- C. node / depth / work units -------------------------------------------


def test_node_key_value_units_simple_object() -> None:
    result, _, work = call('{"cmd":"cat A.md"}')
    # node_count is EXACTLY: root object + object key + string value.
    assert result.ok
    assert result.node_count == 3
    assert result.max_depth == 1
    # every node/key visit is charged to the shared work ledger; the
    # single-walk design charges exactly the visits (a multi-pass
    # implementation may charge more, never less)
    assert work.visits >= result.node_count


def test_node_key_value_units_nested() -> None:
    result, _, work = call('{"a":{"b":0}}')
    assert result.ok
    assert result.node_count == 5
    assert result.max_depth == 2
    assert work.visits >= result.node_count


def test_input_bytes_are_utf8_bytes_not_chars() -> None:
    result, _ = call('{"cmd":"\U0001f600"}')[:2]
    assert result.ok
    assert result.input_bytes == 14  # 10 characters, one 4-byte scalar


def test_node_budget_two_refuses_three_nodes() -> None:
    result, _ = call('{"cmd":"cat A.md"}', max_argument_nodes=2)[:2]
    assert not result.ok
    assert result.reason is CausalHistoryLimitation.ARGUMENTS_OVER_BOUND


def test_shared_work_cap_refuses_at_third_visit() -> None:
    result, _, _ = call('{"cmd":"cat A.md"}', work_budget=2)
    assert not result.ok
    assert result.reason is CausalHistoryLimitation.WORK_UNITS_OVER_BOUND


def test_shared_ledger_not_reset_across_calls() -> None:
    ledger = _Ledger(100)
    r1, _ = call('{"a":1}', ledger=ledger)[:2]
    after_first = ledger.applied_total
    r2, _ = call('{"a":1}', ledger=ledger)[:2]
    assert r1.ok and r2.ok
    assert ledger.applied_total == 2 * after_first


# --- D. allocation / accounting boundaries ----------------------------------


def _canonical_json(arguments: str) -> bytes:
    """Independent stdlib oracle for the canonical form.

    ``json.loads``/``json.dumps`` (sorted keys, compact separators,
    non-ASCII kept as UTF-8, NaN/Infinity unsupported) matches the
    recipe semantics for the SELECTED positive fixtures below;
    positive canonical-byte expectations use this oracle rather than
    mirroring the walk.  It is not a universal oracle for every
    supported strict JSON object: the stdlib imposes its own limits
    (for example 4300-digit integer parsing), and strict
    duplicate-key and nonfinite-number negatives stay separate
    (the stdlib oracle accepts some of them).
    """
    return json.dumps(
        json.loads(arguments),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


class _EncodingSentinel(str):
    """str subclass recording whole-input ``encode`` attempts.

    The product must never make the whole-input encoding allocation:
    any ``encode`` call on the raw input (one-over UTF-8 byte
    refusals, lone surrogates, character-preflight refusals) is a
    crossing allocation this sentinel exposes.
    """

    def __init__(self, value: str) -> None:
        self.encode_attempts = 0

    def encode(self, encoding: str = "utf-8", errors: str = "strict") -> bytes:
        self.encode_attempts += 1
        return super().encode(encoding, errors)


class _RaiseOnEncode(str):
    """str subclass whose ``encode`` raises (numeric encode sentinel).

    Ported from the isolated allocation probe: with the product
    module's ``repr`` monkeypatched to return instances of this
    class, any ``repr(value).encode(...)`` in the numeric canonical
    path raises loudly, distinguishing before-copy charging (the
    fixed refusal returns first and ``encode`` is never reached)
    from encode-then-charge code (the canonical bytes are allocated
    before the refusal).  ``encode_attempts`` is retained for an
    explicit zero-assertion in addition to the raise.
    """

    def __init__(self, value: str) -> None:
        self.encode_attempts = 0

    def encode(self, encoding: str = "utf-8", errors: str = "strict") -> bytes:
        self.encode_attempts += 1
        raise AssertionError("canonical numeric encode attempted before fixed refusal")


def test_successful_call_accounts_input_plus_canonical_exactly() -> None:
    # Positive canonical expectations come from the independent
    # stdlib oracle; the shared ledger settles at exactly
    # input + canonical with no refused charge on success.
    for arguments in (
        "{}",
        '{"a":1}',
        '{"a":"\\"x\\""}',
        '{"a":{"b":[1,2,{"c":false}]}}',
        '{"a":[true,false,null,1e-7]}',
    ):
        result, ledger = call(arguments)[:2]
        assert result.ok
        expected = _canonical_json(arguments)
        assert result.canonical_bytes == len(expected)
        assert ledger.applied_total == result.input_bytes + len(expected)
        assert ledger.refused == []


@pytest.mark.parametrize(
    "arguments",
    [
        '{"a":true}',
        '{"a":false}',
        '{"a":null}',
        '{"a":[true,false,null]}',
        '{"a":[true,false,null,1e-7]}',
    ],
)
def test_literal_bytes_accounted_at_limit_and_one_over(arguments: str) -> None:
    total = len(arguments.encode("utf-8")) + len(_canonical_json(arguments))
    over, over_ledger = call(arguments, budget=total - 1)[:2]
    assert not over.ok
    assert over.reason is CausalHistoryLimitation.ARGUMENTS_OVER_BOUND
    assert over_ledger.applied_total == total - 1
    at, at_ledger = call(arguments, budget=total)[:2]
    assert at.ok
    assert at_ledger.applied_total == total == at.input_bytes + at.canonical_bytes


def test_comma_included_in_per_argument_cap() -> None:
    # The canonical forms (independent stdlib oracle) are exactly 17
    # bytes for the two-entry case and 23 bytes for the three-entry
    # case; the per-argument cap counts the separating commas.
    two = '{"a":1e-7,"b":0}'
    assert len(_canonical_json(two)) == 17
    over, _ = call(two, max_argument_bytes=16)[:2]
    assert not over.ok
    assert over.reason is CausalHistoryLimitation.ARGUMENTS_OVER_BOUND
    at, _ = call(two, max_argument_bytes=17)[:2]
    assert at.ok
    assert at.canonical_bytes == 17
    three = '{"a":1e-7,"b":0,"c":1}'
    assert len(_canonical_json(three)) == 23
    over2, _ = call(three, max_argument_bytes=22)[:2]
    assert not over2.ok
    assert over2.reason is CausalHistoryLimitation.ARGUMENTS_OVER_BOUND
    at2, _ = call(three, max_argument_bytes=23)[:2]
    assert at2.ok
    assert at2.canonical_bytes == 23


def test_per_argument_cap_never_pollutes_shared_ledger() -> None:
    # The canonical form (oracle) is 25 bytes; cap 22 refuses at the
    # crossing byte.  The shared ledger keeps only actually
    # constructed bytes: the walk consumes the per-argument cap
    # EXACTLY and the crossing byte is refused by the per-argument
    # cap before it is ever offered to the shared callback.
    arguments = '{"a":[1e-7,1e-7,1e-7]}'
    canonical = _canonical_json(arguments)
    assert len(canonical) == 25
    result, ledger = call(arguments, max_argument_bytes=22)[:2]
    assert not result.ok
    assert result.reason is CausalHistoryLimitation.ARGUMENTS_OVER_BOUND
    assert ledger.applied_total == result.input_bytes + 22
    assert ledger.refused == []
    at, at_ledger = call(arguments, max_argument_bytes=len(canonical))[:2]
    assert at.ok
    assert at.canonical_bytes == len(canonical)
    assert at_ledger.applied_total == at.input_bytes + len(canonical)


def test_shared_remainder_exhausted_stops_before_numeric_bytes() -> None:
    arguments = '{"a":1e-7}'
    total = len(arguments.encode("utf-8")) + len(_canonical_json(arguments))
    assert total == 21
    at, at_ledger = call(arguments, budget=total)[:2]
    assert at.ok
    assert at_ledger.applied_total == total
    over, over_ledger = call(arguments, budget=total - 1)[:2]
    assert not over.ok
    assert over.reason is CausalHistoryLimitation.ARGUMENTS_OVER_BOUND
    assert over_ledger.applied_total == total - 1
    # budget exactly the input: NO canonical byte is charged or built
    only, only_ledger = call(arguments, budget=len(arguments.encode("utf-8")))[:2]
    assert not only.ok
    assert only_ledger.applied_total == len(arguments.encode("utf-8"))
    assert only_ledger.attempts == 2  # input + one refused canonical charge


def test_empty_container_charges_both_brackets() -> None:
    arguments = "{}"
    total = len(arguments.encode("utf-8")) + len(_canonical_json(arguments))
    assert total == 4
    over, _ = call(arguments, budget=total - 1)[:2]
    assert not over.ok
    at, at_ledger = call(arguments, budget=total)[:2]
    assert at.ok
    assert at.canonical_bytes == 2
    assert at_ledger.applied_total == total


def test_numeric_bytes_refused_before_encode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # '{"a":1e-7}': input 10 + root brace 1 + key 3 = 14 applied at
    # budget 14, exactly exhausting the shared remainder; the next
    # charge attempt is the 5-byte numeric canonical piece, refused
    # before encode/retention.  The encode sentinel (ported from the
    # isolated allocation probe) monkeypatches the product module's
    # ``repr``: any ``repr(value).encode(...)`` in the numeric
    # canonical path raises and fails this test, while a before-copy
    # implementation returns the fixed refusal after the refused
    # charge and never reaches ``encode``.
    sentinels: list[_RaiseOnEncode] = []

    def fake_repr(value: object) -> str:
        sentinel = _RaiseOnEncode(builtins.repr(value))
        sentinels.append(sentinel)
        return sentinel

    monkeypatch.setattr(causal_history_module, "repr", fake_repr, raising=False)
    result, ledger = call('{"a":1e-7}', budget=14)[:2]
    assert not result.ok
    assert result.reason is CausalHistoryLimitation.ARGUMENTS_OVER_BOUND
    assert ledger.applied == [10, 1, 3]
    assert ledger.refused == [5]
    # the numeric path went through the patched repr, and the refused
    # numeric piece was never encoded/retained
    assert sentinels
    assert all(sentinel.encode_attempts == 0 for sentinel in sentinels)


def test_utf8_byte_bound_not_character_bound() -> None:
    # 9 characters, 12 UTF-8 bytes: the character preflight passes,
    # the exact UTF-8 byte refusal must fire (one-over / at-limit),
    # and no whole-input encode allocation is made (sentinel).
    sentinel = _EncodingSentinel('{"a":"\U0001f600"}')
    result, _ = call(sentinel, max_argument_bytes=9)[:2]
    assert not result.ok
    assert result.reason is CausalHistoryLimitation.ARGUMENTS_OVER_BOUND
    assert result.input_bytes == 12
    at, _ = call(sentinel, max_argument_bytes=12)[:2]
    assert at.ok
    assert at.input_bytes == 12
    assert sentinel.encode_attempts == 0


def test_overbound_input_refused_before_any_encoding() -> None:
    sentinel = _EncodingSentinel('{"cmd":"' + "x" * 70_000 + '"}')
    result, _ = call(sentinel)[:2]
    assert not result.ok
    assert result.reason is CausalHistoryLimitation.ARGUMENTS_OVER_BOUND
    assert result.input_bytes == 0  # never measured nor retained
    assert sentinel.encode_attempts == 0


def test_lone_surrogate_refused_before_any_encoding() -> None:
    sentinel = _EncodingSentinel('{"a":"\ud800"}')
    result, _ = call(sentinel)[:2]
    assert not result.ok
    assert result.reason is CausalHistoryLimitation.ARGUMENTS_MALFORMED_UNICODE
    assert result.input_bytes == 0
    assert sentinel.encode_attempts == 0


def test_canonical_cap_exceeded_within_input_cap() -> None:
    # 100 numeric lexemes '1e-7' (4 input bytes each) canonicalize to
    # '1e-07' (5 canonical bytes each): the input FITS the cap while
    # the canonical form (independent stdlib oracle) crosses it --
    # the refusal happens during canonical construction, not at the
    # input preflight (input_bytes is measured, not 0).
    arguments = '{"a":[' + ",".join(["1e-7"] * 100) + "]}"
    canonical = _canonical_json(arguments)
    input_bytes = len(arguments.encode("utf-8"))
    assert input_bytes < len(canonical)
    cap = (input_bytes + len(canonical)) // 2
    over, over_ledger = call(arguments, max_argument_bytes=cap)[:2]
    assert not over.ok
    assert over.reason is CausalHistoryLimitation.ARGUMENTS_OVER_BOUND
    assert over.input_bytes == input_bytes  # measured: preflight passed
    # the canonical prefix is charged in atomic pieces: a 5-byte
    # numeric piece may be refused with at most that many bytes of
    # remainder, so the applied prefix reaches AT MOST the cap -- it
    # never crosses it (the no-crossing bound), but exact fill-to-cap
    # is not a contract.
    assert input_bytes <= over_ledger.applied_total <= input_bytes + cap
    at, at_ledger = call(arguments, max_argument_bytes=len(canonical))[:2]
    assert at.ok
    assert at.canonical_bytes == len(canonical)
    assert at_ledger.applied_total == at.input_bytes + len(canonical)


# --- E. scope: factory + direct construction ---------------------------------


def test_factory_binds_actual_admission_scope() -> None:
    ns = make_causal_history_namespace(make_admission(), LINEAGE)
    admission = make_admission()
    assert len(ns.history_key) == 64
    assert len(ns.state_scoped_key) == 64
    want = hashlib.sha256((ns.history_key + "\0" + WORKSPACE).encode("utf-8")).hexdigest()
    assert ns.state_scoped_key == want
    assert ns.admission_namespace_key == admission.namespace_key
    assert ns.admission_scoped_key == admission.scoped_key


def test_lineage_and_bounds_change_the_history_key() -> None:
    base = make_causal_history_namespace(make_admission(), LINEAGE)
    other = make_causal_history_namespace(make_admission(), LINEAGE_ALT)
    assert base.history_key != other.history_key
    # same workspace: the state key binds history_key + workspace
    assert base.state_scoped_key != other.state_scoped_key
    tighter = make_causal_history_namespace(
        make_admission(), LINEAGE, bounds=HistoryBounds(max_issuances=1)
    )
    assert tighter.history_key != base.history_key


def test_stricter_history_bounds_permitted() -> None:
    ns = make_causal_history_namespace(
        make_admission(), LINEAGE, bounds=HistoryBounds(max_issuances=1)
    )
    assert ns.history_bounds.max_issuances == 1


@pytest.mark.parametrize("bad", ["", "x" * 129, "a b"])
def test_lineage_id_must_be_bounded_non_space(bad: str) -> None:
    with pytest.raises(ValueError):
        make_causal_history_namespace(make_admission(), bad)


@pytest.mark.parametrize("field", sorted(HistoryBounds().model_dump()))
def test_wider_history_bounds_refused_by_factory(field: str) -> None:
    ceiling = HistoryBounds().model_dump()[field]
    forged = HistoryBounds().model_copy(update={field: ceiling + 1})
    with pytest.raises(ValueError):
        make_causal_history_namespace(make_admission(), LINEAGE, bounds=forged)


def _rekeyed_forged_admission(update: dict[str, object]) -> BundleAdmissionNamespace:
    """Forge admission field values AND recompute both 64-hex keys to
    match (key consistency alone must NOT be enough)."""
    forged = make_admission().model_copy(update=update)
    canonical = _canonical_namespace_fields(
        forged.principal,
        forged.session,
        forged.repository,
        forged.route,
        forged.model_identity,
        forged.config_fingerprint,
        forged.admission_version,
        forged.graph_version,
        forged.reference_version,
        forged.proof_version,
        forged.observation_version,
        forged.mode.value,
        forged.bounds,
        forged.proof_bounds,
        forged.graph_bounds,
        forged.observation_bounds,
    )
    key = hashlib.sha256(canonical).hexdigest()
    scoped = hashlib.sha256((key + "\0" + forged.workspace).encode()).hexdigest()
    return forged.model_copy(update={"namespace_key": key, "scoped_key": scoped})


@pytest.mark.parametrize(
    "update",
    [
        {"config_fingerprint": "g" * 64},
        {"principal": "synthetic\n"},
    ],
    ids=["invalid_actual_config_fingerprint", "invalid_actual_principal_control"],
)
def test_forged_admission_fields_refused_by_factory(
    update: dict[str, object],
) -> None:
    with pytest.raises(ValueError):
        make_causal_history_namespace(_rekeyed_forged_admission(update), LINEAGE)


def _recompute_history_key(
    *,
    admission: BundleAdmissionNamespace,
    admission_namespace_key: str,
    admission_scoped_key: str,
    history_bounds: HistoryBounds,
) -> tuple[str, str]:
    payload = _canonical_history_fields(
        admission.principal,
        admission.session,
        admission.repository,
        admission.route,
        admission.model_identity,
        admission.config_fingerprint,
        admission.workspace,
        admission.mode.value,
        admission.admission_version,
        admission.observation_version,
        admission.graph_version,
        admission.reference_version,
        admission.proof_version,
        admission_namespace_key,
        admission_scoped_key,
        LINEAGE,
        CAUSAL_HISTORY_CONTRACT_VERSION,
        CAUSAL_ARGUMENTS_JSON_VERSION,
        history_bounds,
        admission.bounds,
        admission.proof_bounds,
        admission.graph_bounds,
        admission.observation_bounds,
    )
    history_key = _sha256_hex(payload)
    state_scoped_key = _sha256_hex((history_key + "\0" + admission.workspace).encode("utf-8"))
    return history_key, state_scoped_key


def test_direct_construction_roundtrip_of_valid_scope() -> None:
    base = make_causal_history_namespace(make_admission(), LINEAGE)
    rebuilt = CausalHistoryNamespace(**base.model_dump())
    assert rebuilt.history_key == base.history_key
    assert rebuilt.state_scoped_key == base.state_scoped_key


def test_direct_construction_refuses_forged_history_bounds() -> None:
    base = make_causal_history_namespace(make_admission(), LINEAGE)
    data = base.model_dump()
    forged = HistoryBounds().model_copy(update={"max_issuances": 4097})
    hk, sk = _recompute_history_key(
        admission=make_admission(),
        admission_namespace_key=base.admission_namespace_key,
        admission_scoped_key=base.admission_scoped_key,
        history_bounds=forged,
    )
    # the forged INSTANCE bypasses nested field validation; the
    # recompute-and-verify scope must still refuse it
    with pytest.raises(ValueError):
        CausalHistoryNamespace(
            **{
                **data,
                "history_bounds": forged,
                "history_key": hk,
                "state_scoped_key": sk,
            }
        )


def test_direct_construction_refuses_forged_admission_nested_bound() -> None:
    base = make_causal_history_namespace(make_admission(), LINEAGE)
    data = base.model_dump()
    forged_bound = BundleAdmissionBounds().model_copy(update={"max_entries": 129})
    forged_admission = make_admission().model_copy(update={"bounds": forged_bound})
    canonical = _canonical_namespace_fields(
        forged_admission.principal,
        forged_admission.session,
        forged_admission.repository,
        forged_admission.route,
        forged_admission.model_identity,
        forged_admission.config_fingerprint,
        forged_admission.admission_version,
        forged_admission.graph_version,
        forged_admission.reference_version,
        forged_admission.proof_version,
        forged_admission.observation_version,
        forged_admission.mode.value,
        forged_admission.bounds,
        forged_admission.proof_bounds,
        forged_admission.graph_bounds,
        forged_admission.observation_bounds,
    )
    ns_key = hashlib.sha256(canonical).hexdigest()
    scoped_key = hashlib.sha256((ns_key + "\0" + forged_admission.workspace).encode()).hexdigest()
    hk, sk = _recompute_history_key(
        admission=forged_admission,
        admission_namespace_key=ns_key,
        admission_scoped_key=scoped_key,
        history_bounds=HistoryBounds(),
    )
    with pytest.raises(ValueError):
        CausalHistoryNamespace(
            **{
                **data,
                "bounds": forged_bound,
                "admission_namespace_key": ns_key,
                "admission_scoped_key": scoped_key,
                "history_key": hk,
                "state_scoped_key": sk,
            }
        )


def test_direct_construction_refuses_forged_config_fingerprint() -> None:
    base = make_causal_history_namespace(make_admission(), LINEAGE)
    data = base.model_dump()
    forged_admission = make_admission().model_copy(update={"config_fingerprint": "g" * 64})
    canonical = _canonical_namespace_fields(
        forged_admission.principal,
        forged_admission.session,
        forged_admission.repository,
        forged_admission.route,
        forged_admission.model_identity,
        forged_admission.config_fingerprint,
        forged_admission.admission_version,
        forged_admission.graph_version,
        forged_admission.reference_version,
        forged_admission.proof_version,
        forged_admission.observation_version,
        forged_admission.mode.value,
        forged_admission.bounds,
        forged_admission.proof_bounds,
        forged_admission.graph_bounds,
        forged_admission.observation_bounds,
    )
    ns_key = hashlib.sha256(canonical).hexdigest()
    scoped_key = hashlib.sha256((ns_key + "\0" + forged_admission.workspace).encode()).hexdigest()
    hk, sk = _recompute_history_key(
        admission=forged_admission,
        admission_namespace_key=ns_key,
        admission_scoped_key=scoped_key,
        history_bounds=HistoryBounds(),
    )
    with pytest.raises(ValueError):
        CausalHistoryNamespace(
            **{
                **data,
                "config_fingerprint": "g" * 64,
                "admission_namespace_key": ns_key,
                "admission_scoped_key": scoped_key,
                "history_key": hk,
                "state_scoped_key": sk,
            }
        )


# --- F. privacy ----------------------------------------------------------------


def test_namespace_repr_suppresses_private_ids() -> None:
    ns = make_causal_history_namespace(make_admission(), LINEAGE)
    text = repr(ns)
    for private in (
        IDENTITY.principal,
        IDENTITY.session,
        IDENTITY.repository,
        IDENTITY.route,
        MODEL_IDENTITY,
        CONFIG_FINGERPRINT,
        LINEAGE,
    ):
        assert private not in text
    assert PRIVATE_ID_PLACEHOLDER in text


def test_result_repr_never_echoes_arguments() -> None:
    arguments = '{"cmd":"cat SECRET-PRIVATE-PATH.md"}'
    result, _ = call(arguments)[:2]
    assert result.ok
    assert "SECRET-PRIVATE-PATH" not in repr(result)


# --- G. immutable state records (018-d kernel) -----------------------------

ROOT_DIGEST = "a" * 64
OCC_A = "b" * 64
OCC_B = "c" * 64
OCC_C = "d" * 64
OCC_D = "e" * 64
FINGERPRINT_A = "f" * 64
FINGERPRINT_B = "1" * 64
FINGERPRINT_C = "2" * 64
FINGERPRINT_D = "3" * 64
RESULT_A = "4" * 64
SESSION_A = "7" * 64
HISTORY_KEY = "5" * 64
CALL_A = "synthetic-causal-call-a"
CALL_B = "synthetic-causal-call-b"
CALL_C = "synthetic-causal-call-c"
CALL_D = "synthetic-causal-call-d"
TOOL_NAME = "exec_command"
ROOT_TEXT = "root-anchor-body\n"
ROOT_TEXT_DIGEST = _sha256_hex(ROOT_TEXT.encode("utf-8"))


class _UnsetRoot:
    """Unique sentinel for _make_state's optional root parameter."""


_UNSET_ROOT: Final[_UnsetRoot] = _UnsetRoot()


def _root() -> RootAnchor:
    return RootAnchor(
        root_text=ROOT_TEXT,
        root_digest=ROOT_TEXT_DIGEST,
        workspace=WORKSPACE,
        first_request_index=0,
        source_byte_length=len(ROOT_TEXT.encode("utf-8")),
        location="$.input[0]",
        content_span=CharSpan(start=0, end=len(ROOT_TEXT)),
        envelope_span=CharSpan(start=0, end=len(ROOT_TEXT) + 2),
    )


def _synthetic_proof(call_id: str, source_text: str) -> BundleProof:
    """Minimal valid whole-read proof for record-level tests."""
    text_bytes = len(source_text.encode("utf-8"))
    digest = _sha256_hex(source_text.encode("utf-8"))
    return BundleProof(
        surface=BundleSurface.READ,
        kind=BundleProofKind.WHOLE,
        grammar="read-command/v1",
        command_digest=None,
        request_index=1,
        call_id=call_id,
        call_location="$.input[1]",
        call_position=1,
        result_location="$.input[2]",
        result_position=2,
        endpoint="responses",
        root_path="AGENTS.md",
        root_digest=ROOT_DIGEST,
        requested_members=(NormalizedPath(raw="A.md", form=PathForm.RELATIVE, normalized="A.md"),),
        proven_executed=("exec",),
        distinct_member_count=1,
        pieces=(
            BundlePiece(
                piece_index=0,
                carrier_location="$.input[2]",
                char_span=CharSpan(start=0, end=len(source_text)),
                char_length=len(source_text),
                byte_length=text_bytes,
                call_id=call_id,
                call_location="$.input[1]",
                call_position=1,
                result_position=2,
            ),
        ),
        segments=(
            BundleSegment(
                index=0,
                member_positions=(0,),
                char_length=len(source_text),
                byte_length=text_bytes,
                digest=digest,
                member_digest=digest,
                piece_spans=(None,),
            ),
        ),
        markers=(),
        source_text=source_text,
        source_char_length=len(source_text),
        source_byte_length=text_bytes,
        source_digest=digest,
    )


def _make_issuance(
    call_id: str = CALL_A,
    endpoint: str = "responses",
    tool_name: str = TOOL_NAME,
    fingerprint: str = FINGERPRINT_A,
    frontier: tuple[str, ...] = (CAUSAL_ROOT_FACT,),
) -> IssuedCall:
    return IssuedCall(
        call_id=call_id,
        endpoint=endpoint,
        tool_name=tool_name,
        argument_fingerprint=fingerprint,
        parent_frontier=frontier,
    )


def _make_occurrence(
    occurrence_id: str = OCC_A,
    call_id: str = CALL_A,
    endpoint: str = "responses",
    tool_name: str = TOOL_NAME,
    fingerprint: str = FINGERPRINT_A,
    source_text: str = "alpha\n",
    anchored: bool = False,
) -> CompletedReadOccurrence:
    return CompletedReadOccurrence(
        occurrence_id=occurrence_id,
        call_id=call_id,
        endpoint=endpoint,
        tool_name=tool_name,
        argument_fingerprint=fingerprint,
        proof=_synthetic_proof(call_id, source_text),
        anchored=anchored,
    )


def _make_result(
    call_id: str = CALL_A,
    endpoint: str = "responses",
    tool_name: str = TOOL_NAME,
    fingerprint: str = FINGERPRINT_A,
    result_fingerprint: str = RESULT_A,
    complete: bool = True,
    first_request_index: int = 2,
    session_digest: str = SESSION_A,
) -> ResultFingerprintRecord:
    return ResultFingerprintRecord(
        call_id=call_id,
        endpoint=endpoint,
        tool_name=tool_name,
        argument_fingerprint=fingerprint,
        result_fingerprint=result_fingerprint,
        complete=complete,
        first_request_index=first_request_index,
        session_digest=session_digest,
    )


def _make_state(
    *,
    revision: int = 0,
    history_key: str = HISTORY_KEY,
    root: RootAnchor | None | _UnsetRoot = _UNSET_ROOT,
    issuances: tuple[IssuedCall, ...] = (),
    occurrences: tuple[CompletedReadOccurrence, ...] = (),
    results: tuple[ResultFingerprintRecord, ...] = (),
    parent_links: tuple[ParentLink, ...] = (),
) -> CausalHistoryState:
    if isinstance(root, _UnsetRoot):
        effective_root: RootAnchor | None = _root()
    else:
        effective_root = root
    return CausalHistoryState(
        history_key=history_key,
        revision=revision,
        root=effective_root,
        issuances=issuances,
        occurrences=occurrences,
        results=results,
        parent_links=parent_links,
    )


def test_record_construction_positive() -> None:
    state = _make_state(
        revision=1,
        issuances=(_make_issuance(),),
        occurrences=(_make_occurrence(),),
        results=(_make_result(),),
    )
    assert state.revision == 1
    assert len(state.occurrences) == 1
    # frontier over the known completed fact; revision at the exact ceiling
    issuance_b = _make_issuance(
        call_id=CALL_B,
        fingerprint=FINGERPRINT_B,
        frontier=(OCC_A, CAUSAL_ROOT_FACT),
    )
    occurrence_b = _make_occurrence(
        occurrence_id=OCC_B,
        call_id=CALL_B,
        fingerprint=FINGERPRINT_B,
        source_text="beta\n",
        anchored=True,
    )
    linked = _make_state(
        revision=MAX_REVISION,
        issuances=(_make_issuance(), issuance_b),
        occurrences=(_make_occurrence(), occurrence_b),
        parent_links=(
            ParentLink(child=OCC_B, parent=OCC_A),
            ParentLink(child=OCC_B, parent=CAUSAL_ROOT_FACT),
        ),
    )
    assert linked.revision == MAX_REVISION
    assert linked.parent_links[0].child == OCC_B
    assert validate_causal_history_state(state) is None
    assert validate_causal_history_state(linked) is None


@pytest.mark.parametrize(
    ("root_digest", "workspace", "first_request_index", "source_byte_length"),
    [
        ("a" * 63, WORKSPACE, 0, len(ROOT_TEXT.encode("utf-8"))),
        ("A" * 64, WORKSPACE, 0, len(ROOT_TEXT.encode("utf-8"))),
        (ROOT_TEXT_DIGEST, "relative/path", 0, len(ROOT_TEXT.encode("utf-8"))),
        (ROOT_TEXT_DIGEST, "/work", -1, len(ROOT_TEXT.encode("utf-8"))),
        (ROOT_TEXT_DIGEST, "/work", 0, -1),
        (ROOT_TEXT_DIGEST, "/work", 0, len(ROOT_TEXT.encode("utf-8")) + 1),
        (ROOT_TEXT_DIGEST, "/wor k", 0, len(ROOT_TEXT.encode("utf-8"))),
        (ROOT_TEXT_DIGEST, "/work\x01", 0, len(ROOT_TEXT.encode("utf-8"))),
    ],
)
def test_root_anchor_laws(
    root_digest: str,
    workspace: str,
    first_request_index: int,
    source_byte_length: int,
) -> None:
    with pytest.raises(ValueError):
        RootAnchor(
            root_text=ROOT_TEXT,
            root_digest=root_digest,
            workspace=workspace,
            first_request_index=first_request_index,
            source_byte_length=source_byte_length,
            location="$.input[0]",
            content_span=CharSpan(start=0, end=len(ROOT_TEXT)),
        )


def test_root_anchor_provenance_laws() -> None:
    def anchor(**overrides: object) -> RootAnchor:
        base: dict[str, object] = {
            "root_text": ROOT_TEXT,
            "root_digest": ROOT_TEXT_DIGEST,
            "workspace": WORKSPACE,
            "first_request_index": 0,
            "source_byte_length": len(ROOT_TEXT.encode("utf-8")),
            "location": "$.input[0]",
            "content_span": CharSpan(start=0, end=len(ROOT_TEXT)),
        }
        base.update(overrides)
        return RootAnchor(**base)  # type: ignore[arg-type]

    # the span must cover the exact root text
    with pytest.raises(ValueError, match="content_span"):
        anchor(content_span=CharSpan(start=0, end=len(ROOT_TEXT) - 1))
    # the digest must equal the exact root text digest
    with pytest.raises(ValueError, match="exact root text digest"):
        anchor(root_digest="b" * 64)
    # the byte length must equal the exact UTF-8 length
    with pytest.raises(ValueError, match="exact root text bytes"):
        anchor(source_byte_length=len(ROOT_TEXT.encode("utf-8")) + 1)
    # the location is a bounded nonempty label
    with pytest.raises(ValueError):
        anchor(location="")
    with pytest.raises(ValueError):
        anchor(location="l" * 1025)


@pytest.mark.parametrize(
    ("call_id", "endpoint", "tool_name", "fingerprint", "frontier"),
    [
        ("", "responses", TOOL_NAME, FINGERPRINT_A, (CAUSAL_ROOT_FACT,)),
        ("c" * 257, "responses", TOOL_NAME, FINGERPRINT_A, (CAUSAL_ROOT_FACT,)),
        ("call id", "responses", TOOL_NAME, FINGERPRINT_A, (CAUSAL_ROOT_FACT,)),
        (CALL_A, "http", TOOL_NAME, FINGERPRINT_A, (CAUSAL_ROOT_FACT,)),
        (CALL_A, "responses", "exec command", FINGERPRINT_A, (CAUSAL_ROOT_FACT,)),
        (CALL_A, "responses", "t" * 257, FINGERPRINT_A, (CAUSAL_ROOT_FACT,)),
        (CALL_A, "responses", TOOL_NAME, "x" * 64, (CAUSAL_ROOT_FACT,)),
        (CALL_A, "responses", TOOL_NAME, FINGERPRINT_A, ()),
        (CALL_A, "responses", TOOL_NAME, FINGERPRINT_A, (CAUSAL_ROOT_FACT, OCC_A)),
        (CALL_A, "responses", TOOL_NAME, FINGERPRINT_A, (OCC_A, OCC_A)),
        (CALL_A, "responses", TOOL_NAME, FINGERPRINT_A, ("not-a-fact",)),
    ],
)
def test_issued_call_laws(
    call_id: str,
    endpoint: str,
    tool_name: str,
    fingerprint: str,
    frontier: tuple[str, ...],
) -> None:
    with pytest.raises(ValueError):
        IssuedCall(
            call_id=call_id,
            endpoint=endpoint,
            tool_name=tool_name,
            argument_fingerprint=fingerprint,
            parent_frontier=frontier,
        )


@pytest.mark.parametrize(
    ("occurrence_id", "call_id", "endpoint", "tool_name", "fingerprint"),
    [
        ("x" * 64, CALL_A, "responses", TOOL_NAME, FINGERPRINT_A),
        (OCC_A, "call id", "responses", TOOL_NAME, FINGERPRINT_A),
        (OCC_A, CALL_A, "http", TOOL_NAME, FINGERPRINT_A),
        (OCC_A, CALL_A, "responses", "tool name", FINGERPRINT_A),
        (OCC_A, CALL_A, "responses", TOOL_NAME, "y" * 64),
    ],
)
def test_completed_occurrence_field_laws(
    occurrence_id: str,
    call_id: str,
    endpoint: str,
    tool_name: str,
    fingerprint: str,
) -> None:
    with pytest.raises(ValueError):
        CompletedReadOccurrence(
            occurrence_id=occurrence_id,
            call_id=call_id,
            endpoint=endpoint,
            tool_name=tool_name,
            argument_fingerprint=fingerprint,
            proof=_synthetic_proof(call_id, "alpha\n"),
        )


def test_result_record_field_laws() -> None:
    with pytest.raises(ValueError):
        _make_result(fingerprint="x" * 64)
    with pytest.raises(ValueError):
        _make_result(result_fingerprint="y" * 64)
    with pytest.raises(ValueError):
        _make_result(first_request_index=-1)


def _make_result_with_pieces(
    piece_facts: tuple[tuple[int, int, int, str], ...],
    piece_call_bindings: tuple[tuple[str, str, str, str], ...],
) -> ResultFingerprintRecord:
    return ResultFingerprintRecord(
        call_id=CALL_A,
        endpoint="responses",
        tool_name=TOOL_NAME,
        argument_fingerprint=FINGERPRINT_A,
        result_fingerprint=RESULT_A,
        complete=True,
        first_request_index=1,
        session_digest=SESSION_A,
        piece_facts=piece_facts,
        piece_call_bindings=piece_call_bindings,
        # The legacy read surface carries no per-frame completion
        # fact: the aligned no-completion state.
        piece_completion=(None,) * len(piece_facts),
    )


def test_result_record_piece_call_binding_laws() -> None:
    # ONE producing-call association per retained piece, aligned by
    # piece index: the read's own call for its own piece, the observed
    # poll (canonical digest, never raw args) for a poll piece.
    record = _make_result_with_pieces(
        piece_facts=((0, 3, 3, "9" * 64), (1, 2, 2, "8" * 64)),
        piece_call_bindings=(
            (CALL_A, "responses", TOOL_NAME, FINGERPRINT_A),
            ("synthetic-poll-id", "responses", "write_stdin", FINGERPRINT_B),
        ),
    )
    assert record.piece_call_bindings[1] == (
        "synthetic-poll-id",
        "responses",
        "write_stdin",
        FINGERPRINT_B,
    )
    # The exact empty no-ID state is a legal producing-call fact (it
    # never matches anything downstream).
    _make_result_with_pieces(
        piece_facts=((0, 3, 3, "9" * 64),),
        piece_call_bindings=(("", "responses", "write_stdin", FINGERPRINT_B),),
    )
    # Misaligned lengths refuse (the bindings align with the facts).
    with pytest.raises(ValueError):
        _make_result_with_pieces(
            piece_facts=((0, 3, 3, "9" * 64),),
            piece_call_bindings=(
                (CALL_A, "responses", TOOL_NAME, FINGERPRINT_A),
                ("synthetic-poll-id", "responses", "write_stdin", FINGERPRINT_B),
            ),
        )
    # Malformed binding shapes refuse: endpoint, tool name, fingerprint.
    with pytest.raises(ValueError):
        _make_result_with_pieces(
            piece_facts=((0, 3, 3, "9" * 64),),
            piece_call_bindings=(("x", "web", TOOL_NAME, FINGERPRINT_A),),
        )
    with pytest.raises(ValueError):
        _make_result_with_pieces(
            piece_facts=((0, 3, 3, "9" * 64),),
            piece_call_bindings=(("x", "responses", "has space", FINGERPRINT_A),),
        )
    with pytest.raises(ValueError):
        _make_result_with_pieces(
            piece_facts=((0, 3, 3, "9" * 64),),
            piece_call_bindings=(("x", "responses", TOOL_NAME, "z" * 64),),
        )
    # A producing call ID keeps the bounded non-space law (non-empty).
    with pytest.raises(ValueError):
        _make_result_with_pieces(
            piece_facts=((0, 3, 3, "9" * 64),),
            piece_call_bindings=(("id with space", "responses", TOOL_NAME, FINGERPRINT_A),),
        )
    with pytest.raises(ValueError):
        _make_result_with_pieces(
            piece_facts=((0, 3, 3, "9" * 64),),
            piece_call_bindings=(("x" * 257, "responses", TOOL_NAME, FINGERPRINT_A),),
        )


def test_result_record_piece_call_binding_repr_hides_ids() -> None:
    record = _make_result_with_pieces(
        piece_facts=((0, 3, 3, "9" * 64), (1, 2, 2, "8" * 64)),
        piece_call_bindings=(
            ("private-exec-id", "responses", TOOL_NAME, FINGERPRINT_A),
            ("private-poll-id", "responses", "write_stdin", FINGERPRINT_B),
        ),
    )
    text = repr(record)
    assert "private-exec-id" not in text
    assert "private-poll-id" not in text
    assert "piece_call_bindings=2" in text


def test_parent_link_laws() -> None:
    with pytest.raises(ValueError, match="self-referential"):
        ParentLink(child=OCC_A, parent=OCC_A)
    with pytest.raises(ValueError):
        ParentLink(child="x" * 64, parent=OCC_A)


def test_state_integrity_refusals() -> None:
    issuance = _make_issuance()
    occurrence = _make_occurrence()
    result = _make_result()
    issuance_b = _make_issuance(
        call_id=CALL_B,
        fingerprint=FINGERPRINT_B,
        frontier=(OCC_A, CAUSAL_ROOT_FACT),
    )
    occurrence_b = _make_occurrence(
        occurrence_id=OCC_B,
        call_id=CALL_B,
        fingerprint=FINGERPRINT_B,
        source_text="beta\n",
    )

    # duplicate issuance call identity
    state = _make_state(revision=1, issuances=(issuance, _make_issuance()))
    assert validate_causal_history_state(state) is CausalHistoryLimitation.ISSUANCE_CONFLICT

    # a completed occurrence of an unknown (unissued) call is retained
    # evidence -- never a conflict, never a reason to invent issuance
    state = _make_state(revision=1, occurrences=(_make_occurrence(call_id="ghost-call"),))
    assert validate_causal_history_state(state) is None

    # occurrence binding deviates from the retained issuance
    state = _make_state(
        revision=1,
        issuances=(issuance,),
        occurrences=(_make_occurrence(endpoint="chat"),),
    )
    assert validate_causal_history_state(state) is CausalHistoryLimitation.ISSUANCE_CONFLICT

    # an unissued pending-result fingerprint is retained evidence
    state = _make_state(revision=1, results=(_make_result(call_id="ghost-call"),))
    assert validate_causal_history_state(state) is None

    # result binding deviates from the retained issuance
    state = _make_state(
        revision=1,
        issuances=(issuance,),
        results=(_make_result(endpoint="chat"),),
    )
    assert validate_causal_history_state(state) is CausalHistoryLimitation.RESULT_CONFLICT

    # duplicate result per call identity
    state = _make_state(revision=1, issuances=(issuance,), results=(result, _make_result()))
    assert validate_causal_history_state(state) is CausalHistoryLimitation.RESULT_CONFLICT

    # frontier member is not a known fact
    state = _make_state(
        revision=1,
        issuances=(_make_issuance(frontier=(CAUSAL_ROOT_FACT, OCC_C)),),
        occurrences=(occurrence,),
    )
    assert validate_causal_history_state(state) is CausalHistoryLimitation.FRONTIER_CONFLICT

    # the root fact without a retained anchor
    state = _make_state(revision=1, root=None, issuances=(issuance,))
    assert validate_causal_history_state(state) is CausalHistoryLimitation.FRONTIER_CONFLICT

    # parent edge to an unknown occurrence
    state = _make_state(
        revision=1,
        issuances=(issuance, issuance_b),
        occurrences=(occurrence, occurrence_b),
        parent_links=(ParentLink(child=OCC_A, parent=FINGERPRINT_A),),
    )
    assert validate_causal_history_state(state) is CausalHistoryLimitation.FRONTIER_CONFLICT

    # parent edge not in the child's exact frozen frontier
    state = _make_state(
        revision=1,
        issuances=(issuance, issuance_b),
        occurrences=(occurrence, occurrence_b),
        parent_links=(ParentLink(child=OCC_A, parent=OCC_B),),
    )
    assert validate_causal_history_state(state) is CausalHistoryLimitation.FRONTIER_CONFLICT

    # parent edge for a child without a retained issuance
    state = _make_state(
        revision=1,
        issuances=(issuance,),
        occurrences=(occurrence, occurrence_b),
        parent_links=(ParentLink(child=OCC_B, parent=OCC_A),),
    )
    assert validate_causal_history_state(state) is CausalHistoryLimitation.FRONTIER_CONFLICT

    # duplicate parent edge
    state = _make_state(
        revision=1,
        issuances=(issuance, issuance_b),
        occurrences=(occurrence, occurrence_b),
        parent_links=(
            ParentLink(child=OCC_B, parent=OCC_A),
            ParentLink(child=OCC_B, parent=OCC_A),
        ),
    )
    assert validate_causal_history_state(state) is CausalHistoryLimitation.FRONTIER_CONFLICT

    # cyclic parent edges (two-cycle; both frontiers permit the edges)
    state = _make_state(
        revision=1,
        issuances=(
            _make_issuance(frontier=(CAUSAL_ROOT_FACT, OCC_B)),
            issuance_b,
        ),
        occurrences=(
            _make_occurrence(anchored=True),
            _make_occurrence(
                occurrence_id=OCC_B,
                call_id=CALL_B,
                fingerprint=FINGERPRINT_B,
                source_text="beta\n",
                anchored=True,
            ),
        ),
        parent_links=(
            ParentLink(child=OCC_A, parent=OCC_B),
            ParentLink(child=OCC_B, parent=OCC_A),
            ParentLink(child=OCC_A, parent=CAUSAL_ROOT_FACT),
            ParentLink(child=OCC_B, parent=CAUSAL_ROOT_FACT),
        ),
    )
    assert validate_causal_history_state(state) is CausalHistoryLimitation.RECEIPT_CYCLE

    # root-parent edge is retained and legal with a retained anchor
    state = _make_state(
        revision=1,
        issuances=(issuance,),
        occurrences=(_make_occurrence(anchored=True),),
        parent_links=(ParentLink(child=OCC_A, parent=CAUSAL_ROOT_FACT),),
    )
    assert validate_causal_history_state(state) is None

    # root-parent edge without a retained anchor
    state = _make_state(
        revision=1,
        root=None,
        issuances=(issuance,),
        occurrences=(occurrence,),
        parent_links=(ParentLink(child=OCC_A, parent=CAUSAL_ROOT_FACT),),
    )
    assert validate_causal_history_state(state) is CausalHistoryLimitation.FRONTIER_CONFLICT

    # revision above the exact ceiling (field law at construction)
    with pytest.raises(ValueError):
        _make_state(revision=MAX_REVISION + 1)

    # forged anchored flag: no trusted issuance to pair
    state = _make_state(
        revision=1,
        occurrences=(_make_occurrence(anchored=True),),
    )
    assert validate_causal_history_state(state) is CausalHistoryLimitation.RECEIPT_BINDING_MISMATCH

    # an unanchored occurrence carrying a temporal edge
    state = _make_state(
        revision=1,
        issuances=(issuance, issuance_b),
        occurrences=(occurrence, occurrence_b),
        parent_links=(ParentLink(child=OCC_B, parent=OCC_A),),
    )
    assert validate_causal_history_state(state) is CausalHistoryLimitation.FRONTIER_CONFLICT

    # an anchored child omits a known-fact frontier parent (silent
    # incomparability is refused)
    state = _make_state(
        revision=1,
        issuances=(issuance_b,),
        occurrences=(
            occurrence,
            _make_occurrence(
                occurrence_id=OCC_B,
                call_id=CALL_B,
                fingerprint=FINGERPRINT_B,
                source_text="beta\n",
                anchored=True,
            ),
        ),
        parent_links=(ParentLink(child=OCC_B, parent=CAUSAL_ROOT_FACT),),
    )
    assert validate_causal_history_state(state) is CausalHistoryLimitation.FRONTIER_CONFLICT

    # an anchored child's edge beyond its exact frozen frontier
    state = _make_state(
        revision=1,
        issuances=(issuance, issuance_b),
        occurrences=(
            _make_occurrence(anchored=True),
            occurrence_b,
        ),
        parent_links=(ParentLink(child=OCC_A, parent=OCC_B),),
    )
    assert validate_causal_history_state(state) is CausalHistoryLimitation.FRONTIER_CONFLICT

    # the same unissued call identity observed with two bindings
    state = _make_state(
        revision=1,
        occurrences=(
            _make_occurrence(call_id="ghost-call"),
            _make_occurrence(occurrence_id=OCC_B, call_id="ghost-call", endpoint="chat"),
        ),
    )
    assert validate_causal_history_state(state) is CausalHistoryLimitation.ISSUANCE_CONFLICT

    # an unissued result conflicts with the same observed call binding
    state = _make_state(
        revision=1,
        occurrences=(_make_occurrence(call_id="ghost-call"),),
        results=(_make_result(call_id="ghost-call", endpoint="chat"),),
    )
    assert validate_causal_history_state(state) is CausalHistoryLimitation.RESULT_CONFLICT

    # malformed history key (field law at construction)
    with pytest.raises(ValueError):
        _make_state(history_key="z" * 64)


def test_state_represents_exact_empty_prior() -> None:
    # the typed bootstrap NO_ROOT refusal represents the EXACT empty
    # prior state: optional root None, empty record tuples, no
    # fabricated anchor.
    state = CausalHistoryState(history_key=HISTORY_KEY, revision=0, root=None)
    assert state.root is None
    assert validate_causal_history_state(state) is None
    assert "root=None" in repr(state)


def test_state_validation_work_ledger() -> None:
    state = _make_state(
        revision=1,
        issuances=(_make_issuance(),),
        occurrences=(_make_occurrence(),),
    )
    charges = {"n": 0}

    def work() -> bool:
        charges["n"] += 1
        return charges["n"] <= 2

    # the third charged visit stops with the fixed work refusal
    assert (
        validate_causal_history_state(state, work=work)
        is CausalHistoryLimitation.WORK_UNITS_OVER_BOUND
    )
    # a generous (unlimited) ledger completes the validation
    assert validate_causal_history_state(state) is None
    # the LOCAL max_work_units ceiling bounds standalone use
    one = HistoryBounds(max_work_units=1)
    assert (
        validate_causal_history_state(state, bounds=one)
        is CausalHistoryLimitation.WORK_UNITS_OVER_BOUND
    )
    # ...and applies even under a permissive shared callback
    assert (
        validate_causal_history_state(state, bounds=one, work=lambda: True)
        is CausalHistoryLimitation.WORK_UNITS_OVER_BOUND
    )


def test_state_validation_length_preflight() -> None:
    # length preflights run BEFORE any charged visit: an always-
    # refusing work ledger cannot mask a retention-bound refusal.
    def never() -> bool:
        return False

    strict = HistoryBounds(
        max_issuances=1,
        max_occurrences=1,
        max_observed_results=1,
        max_causal_links=1,
    )
    over_issuances = _make_state(
        revision=1,
        issuances=(
            _make_issuance(),
            _make_issuance(call_id=CALL_B, fingerprint=FINGERPRINT_B),
        ),
    )
    assert (
        validate_causal_history_state(over_issuances, bounds=strict, work=never)
        is CausalHistoryLimitation.ISSUANCES_OVER_BOUND
    )
    over_occurrences = _make_state(
        revision=1,
        issuances=(_make_issuance(),),
        occurrences=(
            _make_occurrence(),
            _make_occurrence(occurrence_id=OCC_B, call_id=CALL_B, fingerprint=FINGERPRINT_B),
        ),
    )
    assert (
        validate_causal_history_state(over_occurrences, bounds=strict, work=never)
        is CausalHistoryLimitation.OCCURRENCES_OVER_BOUND
    )
    over_results = _make_state(
        revision=1,
        issuances=(_make_issuance(),),
        results=(_make_result(), _make_result(result_fingerprint=FINGERPRINT_B)),
    )
    assert (
        validate_causal_history_state(over_results, bounds=strict, work=never)
        is CausalHistoryLimitation.RESULTS_OVER_BOUND
    )
    over_links = _make_state(
        revision=1,
        issuances=(
            _make_issuance(frontier=(CAUSAL_ROOT_FACT, OCC_B)),
            _make_issuance(call_id=CALL_B, fingerprint=FINGERPRINT_B),
        ),
        occurrences=(
            _make_occurrence(),
            _make_occurrence(occurrence_id=OCC_B, call_id=CALL_B, fingerprint=FINGERPRINT_B),
        ),
        parent_links=(
            ParentLink(child=OCC_A, parent=OCC_B),
            ParentLink(child=OCC_B, parent=CAUSAL_ROOT_FACT),
        ),
    )
    assert (
        validate_causal_history_state(
            over_links, bounds=HistoryBounds(max_causal_links=1), work=never
        )
        is CausalHistoryLimitation.CAUSAL_LINKS_OVER_BOUND
    )
    over_frontier = _make_state(
        revision=1,
        issuances=(_make_issuance(frontier=(CAUSAL_ROOT_FACT, OCC_B)),),
        occurrences=(
            _make_occurrence(),
            _make_occurrence(occurrence_id=OCC_B, call_id=CALL_B, fingerprint=FINGERPRINT_B),
        ),
    )
    assert (
        validate_causal_history_state(
            over_frontier, bounds=HistoryBounds(max_frontier_members=1), work=never
        )
        is CausalHistoryLimitation.FRONTIER_OVER_BOUND
    )


def test_state_diamond_is_not_a_cycle() -> None:
    # A <- B, A <- C, B <- D, C <- D: a shared ancestor (diamond) is
    # legitimate frozen evidence, not a cycle.  Every edge follows the
    # child's exact frozen issuance frontier.
    pairs = (
        (CALL_A, FINGERPRINT_A, OCC_A, "alpha\n", (CAUSAL_ROOT_FACT, OCC_B, OCC_C)),
        (CALL_B, FINGERPRINT_B, OCC_B, "beta\n", (CAUSAL_ROOT_FACT, OCC_D)),
        (CALL_C, FINGERPRINT_C, OCC_C, "gamma\n", (CAUSAL_ROOT_FACT, OCC_D)),
        (CALL_D, FINGERPRINT_D, OCC_D, "delta\n", (CAUSAL_ROOT_FACT,)),
    )
    issuances = tuple(
        _make_issuance(call_id=c, fingerprint=f, frontier=fr) for c, f, _o, _b, fr in pairs
    )
    occurrences = tuple(
        _make_occurrence(occurrence_id=o, call_id=c, fingerprint=f, source_text=b, anchored=True)
        for c, f, o, b, _fr in pairs
    )
    state = CausalHistoryState(
        history_key=HISTORY_KEY,
        revision=1,
        root=_root(),
        issuances=issuances,
        occurrences=occurrences,
        results=(),
        parent_links=(
            ParentLink(child=OCC_A, parent=OCC_B),
            ParentLink(child=OCC_A, parent=OCC_C),
            ParentLink(child=OCC_B, parent=OCC_D),
            ParentLink(child=OCC_C, parent=OCC_D),
            ParentLink(child=OCC_A, parent=CAUSAL_ROOT_FACT),
            ParentLink(child=OCC_B, parent=CAUSAL_ROOT_FACT),
            ParentLink(child=OCC_C, parent=CAUSAL_ROOT_FACT),
            ParentLink(child=OCC_D, parent=CAUSAL_ROOT_FACT),
        ),
    )
    assert len(state.parent_links) == 8
    assert validate_causal_history_state(state) is None


def test_transition_laws() -> None:
    state = _make_state(
        revision=2,
        issuances=(_make_issuance(),),
        occurrences=(_make_occurrence(),),
    )
    occurrence = state.occurrences[0]

    ok = CausalHistoryTransition(
        state=state,
        outcome=CausalHistoryOutcome.ACCEPTED,
        diagnostics=(CausalHistoryLimitation.REPLAY_POSITION_SHIFTED,),
        observation_limitations=(Limitation.MALFORMED_UNICODE,),
        new_occurrences=(occurrence,),
        revision_before=1,
        revision_after=2,
    )
    assert ok.outcome is CausalHistoryOutcome.ACCEPTED

    # accepted without a revision increment
    with pytest.raises(ValueError, match="exactly once"):
        CausalHistoryTransition(
            state=state,
            outcome=CausalHistoryOutcome.ACCEPTED,
            revision_before=2,
            revision_after=2,
        )

    # a refusal that advances the revision
    with pytest.raises(ValueError, match="never advances"):
        CausalHistoryTransition(
            state=state,
            outcome=CausalHistoryOutcome.REFUSED_CYCLE,
            revision_before=1,
            revision_after=2,
        )

    # the transition state must carry the after revision
    with pytest.raises(ValueError, match="after revision"):
        CausalHistoryTransition(
            state=state,
            outcome=CausalHistoryOutcome.ACCEPTED,
            revision_before=0,
            revision_after=1,
        )

    # unsorted diagnostics
    with pytest.raises(ValueError, match="diagnostics must be sorted"):
        CausalHistoryTransition(
            state=state,
            outcome=CausalHistoryOutcome.REPLAYED,
            revision_before=2,
            revision_after=2,
            diagnostics=(
                CausalHistoryLimitation.NO_ROOT,
                CausalHistoryLimitation.BATCH_OVER_BOUND,
            ),
        )

    # duplicated diagnostics
    with pytest.raises(ValueError, match="diagnostics must be sorted"):
        CausalHistoryTransition(
            state=state,
            outcome=CausalHistoryOutcome.REPLAYED,
            revision_before=2,
            revision_after=2,
            diagnostics=(
                CausalHistoryLimitation.NO_ROOT,
                CausalHistoryLimitation.NO_ROOT,
            ),
        )

    # unsorted observation limitations
    with pytest.raises(ValueError, match="observation limitations must be sorted"):
        CausalHistoryTransition(
            state=state,
            outcome=CausalHistoryOutcome.REPLAYED,
            revision_before=2,
            revision_after=2,
            observation_limitations=(
                Limitation.TRAVERSAL,
                Limitation.MALFORMED_UNICODE,
            ),
        )

    # a replay never retains new occurrences
    with pytest.raises(ValueError, match="a replay never retains"):
        CausalHistoryTransition(
            state=state,
            outcome=CausalHistoryOutcome.REPLAYED,
            revision_before=2,
            revision_after=2,
            new_occurrences=(occurrence,),
        )

    # Cross-state membership (every listed occurrence retained in the
    # transition state) is a CHARGED KERNEL law, not a model shape
    # check: an early CAS/scope/resource refusal must preserve the
    # exact old state without scanning an overbound old state outside
    # the shared ledger.  The model therefore does NOT refuse an
    # occurrence that is not in the transition state (the kernel
    # refuses such a construction before any transition is
    # published); its closed shape checks stay transition-local.
    other = _make_occurrence(
        occurrence_id=OCC_B,
        call_id=CALL_B,
        fingerprint=FINGERPRINT_B,
        source_text="beta\n",
    )
    not_retained = CausalHistoryTransition(
        state=state,
        outcome=CausalHistoryOutcome.ACCEPTED,
        revision_before=1,
        revision_after=2,
        new_occurrences=(other,),
    )
    assert not_retained.new_occurrences == (other,)

    # transition-local closed checks: sorted by occurrence ID
    with pytest.raises(ValueError, match="sorted and deduplicated"):
        CausalHistoryTransition(
            state=state,
            outcome=CausalHistoryOutcome.ACCEPTED,
            revision_before=1,
            revision_after=2,
            new_occurrences=(other, occurrence),
        )

    # transition-local closed checks: deduplicated
    with pytest.raises(ValueError, match="sorted and deduplicated"):
        CausalHistoryTransition(
            state=state,
            outcome=CausalHistoryOutcome.ACCEPTED,
            revision_before=1,
            revision_after=2,
            new_occurrences=(occurrence, occurrence),
        )

    # transition-local closed checks: disjoint new/replayed
    with pytest.raises(ValueError, match="both new and replayed"):
        CausalHistoryTransition(
            state=state,
            outcome=CausalHistoryOutcome.ACCEPTED,
            revision_before=1,
            revision_after=2,
            new_occurrences=(occurrence,),
            replayed_occurrences=(occurrence,),
        )


def test_transition_diagnostic_ceiling() -> None:
    state = _make_state(revision=1)
    all_history = tuple(sorted(CausalHistoryLimitation))
    all_obs = tuple(sorted(Limitation))
    assert len(all_history) + len(all_obs) >= 65
    at_limit_obs = all_obs[: 64 - len(all_history)]
    at = CausalHistoryTransition(
        state=state,
        outcome=CausalHistoryOutcome.REPLAYED,
        revision_before=1,
        revision_after=1,
        diagnostics=all_history,
        observation_limitations=at_limit_obs,
    )
    assert len(at.diagnostics) + len(at.observation_limitations) == 64
    over_obs = all_obs[: 65 - len(all_history)]
    with pytest.raises(ValueError, match="hard ceiling"):
        CausalHistoryTransition(
            state=state,
            outcome=CausalHistoryOutcome.REPLAYED,
            revision_before=1,
            revision_after=1,
            diagnostics=all_history,
            observation_limitations=over_obs,
        )


def test_record_reprs_are_privacy_safe() -> None:
    source_text = "private-canary-source-text"
    state = _make_state(
        revision=1,
        issuances=(_make_issuance(),),
        occurrences=(_make_occurrence(source_text=source_text),),
        results=(_make_result(),),
    )
    occurrence = state.occurrences[0]
    transition = CausalHistoryTransition(
        state=state,
        outcome=CausalHistoryOutcome.ACCEPTED,
        revision_before=0,
        revision_after=1,
        new_occurrences=(occurrence,),
    )
    for text in (
        repr(_root()),
        repr(state.issuances[0]),
        repr(occurrence),
        repr(state.results[0]),
        repr(state),
        str(state),
        repr(transition),
    ):
        assert CALL_A not in text
        assert WORKSPACE not in text
        assert source_text not in text
        assert ROOT_TEXT not in text
    assert PRIVATE_ID_PLACEHOLDER in repr(state.issuances[0])
    assert PRIVATE_ID_PLACEHOLDER in repr(state)
    assert str(state.issuances[0]) == repr(state.issuances[0])


def test_records_are_frozen() -> None:
    root = _root()
    with pytest.raises(ValidationError):
        root.source_byte_length = 17
    state = _make_state(revision=1, issuances=(_make_issuance(),))
    with pytest.raises(ValidationError):
        state.revision = 2
