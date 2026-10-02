"""Order 015-b, workstream C.2: the registry-history baseline regression.

The 015-a round archived RC7 byte-identical under
``packaging/releases/0.1.0-rc7/`` but did NOT add the archived RC7 tag
pair to the read-only registry baseline's immutable historical set in
``.github/workflows/ci.yml``, so no CI round since then mechanically
asserted that ``0.1.0-rc7`` / ``sha-ae627131...`` remains resolvable at
its recorded digest. This regression closes that gap permanently:

- it derives the required historical aliases directly from EVERY archived
  strict record under ``packaging/releases/<rc>/rc_record.json`` (the
  repository convention) — self-contained, so it detects an omission even
  on a source that predates the shared helper;
- it proves the docker-published job's workflow baseline represents every
  derived pair (focused parser over the workflow's baseline step: the
  shared single source of truth when the workflow consumes it, the inline
  static tuple otherwise — the 015-a frozen shape);
- it pins the current exact archive inventory (RC1-RC5, RC7, RC8, RC9 —
  RC9 by order 015-c's archive), so any future archive forces an
  explicit baseline update in the same round;
- it handles the INTENTIONAL RC6 absence: no RC6 identity was ever
  created (the 014-d attempt was abandoned before any push, tag, or
  publication), and none may be created or reserved.

Regression anchor: the coverage assertion MUST FAIL against the 015-a
frozen source at the alias comparison — reaching the comparison and
reporting the archived aliases missing from the baseline (the exact RC7
omission named by orders 015-a/015-b, mechanically replayed in order
015-c with the corrected fallback parser — and, as the replay also
shows, the RC2 ``sha-`` alias, which no 015-a baseline tuple ever
carried) while ``packaging/releases/0.1.0-rc7/`` exists — and against
any state in which an archived pair is absent from the baseline or
unbound from its recorded digest. It MUST PASS on the current source,
where the baseline is derived from all archived strict records and
bound to their recorded digests.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import re
import types
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CI_WORKFLOW = REPO_ROOT / ".github/workflows" / "ci.yml"
SCRIPT = REPO_ROOT / "scripts" / "ghcr_tag_check.py"
RELEASES_DIR = REPO_ROOT / "packaging" / "releases"
BASELINE_STEP_NAME = "- name: Read-only registry baseline (ephemeral packages:read token)"

# The closed set of strict record schemas archived candidates may carry
# (v2: RC1/RC2, order 013-n era; v3: RC3 onward).
STRICT_RECORD_SCHEMAS = frozenset({"slaif-rc-record-v2", "slaif-rc-record-v3"})

# The pinned current exact archive inventory (order 015-c state): every
# archived strict record and the exact identity it binds. Any future
# archive must extend this map in the same round.
PINNED_ARCHIVES: dict[str, tuple[str, str]] = {
    # rc_identifier -> (image_source_commit, oci_image_digest)
    "0.1.0-rc1": (
        "4d096e404e14badb78b4f99142bf08ef17f0f8a7",
        "sha256:2dd889c2841d80651eceebb0bd22397f0b9d36c5be41ed476fa2db70510d3361",
    ),
    "0.1.0-rc2": (
        "0a2f34b6d6fc17b732a1e7570f751776dce1ae01",
        "sha256:2349400a0dd5dbcec560f6c164283f24e5a55c5f474114416af21d6f3b2cb100",
    ),
    "0.1.0-rc3": (
        "307a929ffb30f4ea41c8be4e8a5ea25802e25142",
        "sha256:41db6fcc285aecb23a9ec0acc9306e05754f8e6e9f916cae271ce00ea00cc436",
    ),
    "0.1.0-rc4": (
        "601a7f9fae19869ad8e09f10fa994550368fd87c",
        "sha256:a4f2014c7dae1e21f965f35e09b3c877c89c18bc7c8cdc0dddf7cea117584f7f",
    ),
    "0.1.0-rc5": (
        "e04b4a99afa6268c98f28ed7abfc1db506107523",
        "sha256:70b450f5eaf885a38015838b30198d02072bf0f9ae30258bdc4e68d5c957642f",
    ),
    "0.1.0-rc7": (
        "ae6271318627703785f42de57d893c9be3b980c9",
        "sha256:a3782915da58a403fd0f7991c57f9954b07bfb9377e4730715c0fb7398f901db",
    ),
    "0.1.0-rc8": (
        "718fff301bed0a5ba93b29196cde4d0bcc5d711a",
        "sha256:50450f4aa26a4da158dc457e0b80b441c69386c201491c6c0150c25d5916e126",
    ),
    "0.1.0-rc9": (
        "7f601bf153ef86a567883c0008edf4ce34e79c95",
        "sha256:54fe19483f00ef6e209b2796786fe27cddd302c6bcf5322821b2192a32884334",
    ),
}


def _load_ghcr_module() -> types.ModuleType | None:
    if not SCRIPT.is_file():
        return None
    spec = importlib.util.spec_from_file_location("ghcr_tag_check_registry_history", SCRIPT)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _archived_pairs() -> dict[str, tuple[str, str]]:
    """Derive the required historical aliases directly from every archived
    strict ``packaging/releases/<rc>/rc_record.json`` under the repository
    convention. Returns ``rc_identifier -> (sha_tag, oci_image_digest)``.
    Fails closed on an unreadable/malformed record or a tag pair that does
    not agree with its source commit."""
    out: dict[str, tuple[str, str]] = {}
    if not RELEASES_DIR.is_dir():
        return out
    for entry in sorted(RELEASES_DIR.iterdir()):
        if not entry.is_dir() or not re.fullmatch(r"0\.1\.0-rc\d+", entry.name):
            continue
        path = entry / "rc_record.json"
        if not path.is_file():
            pytest.fail(f"archived directory {entry.name}/ lacks its strict record")
        try:
            record: Any = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            pytest.fail(f"archived record for {entry.name} unreadable ({type(exc).__name__})")
        if not isinstance(record, dict) or record.get("schema") not in STRICT_RECORD_SCHEMAS:
            pytest.fail(f"archived record for {entry.name} is not a strict record")
        source = record.get("image_source_commit")
        digest = record.get("oci_image_digest")
        if not re.fullmatch(r"[0-9a-f]{40}", source if isinstance(source, str) else ""):
            pytest.fail(f"archived record for {entry.name}: malformed image_source_commit")
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest if isinstance(digest, str) else ""):
            pytest.fail(f"archived record for {entry.name}: malformed oci_image_digest")
        if not isinstance(source, str) or not isinstance(digest, str):
            pytest.fail(f"archived record for {entry.name}: non-string identity field")
        if record.get("rc_identifier") != entry.name:
            pytest.fail(f"archived record for {entry.name}: rc_identifier disagreement")
        if record.get("oci_tags") != [entry.name, f"sha-{source}"]:
            pytest.fail(f"archived record for {entry.name}: tag pair disagreement")
        out[entry.name] = (f"sha-{source}", digest)
    return out


def _baseline_step_source() -> str:
    """The Python run block of the read-only registry baseline step
    (focused parser: step located by its exact name; the ``run: |``
    literal block is the indented run that follows it)."""
    text = CI_WORKFLOW.read_text(encoding="utf-8")
    start = text.find(BASELINE_STEP_NAME)
    assert start != -1, f"baseline step not found: {BASELINE_STEP_NAME!r}"
    run_idx = text.find("run: |", start)
    assert run_idx != -1 and run_idx - start < 4000, "baseline step has no run block"
    lines = text[run_idx:].splitlines(keepends=True)
    block: list[str] = []
    for line in lines[1:]:
        if line.strip() == "" or line.startswith(" " * 10):
            block.append(line)
        else:
            break
    source = "".join(block)
    assert "python3 -" in source and "<<'PY'" in source, "baseline step is not a python run"
    body = source.split("<<'PY'", 1)[1].rsplit("\n          PY", 1)[0]
    return "\n".join(line[10:] if line.startswith(" " * 10) else line for line in body.splitlines())


class _InlineTupleError(ValueError):
    """The historical inline ``tags = (...)`` shape is malformed,
    ambiguous, or non-string (fail closed; order 015-c)."""


def _inline_static_tags(source: str) -> tuple[str, ...]:
    """Extract the static ``tags = (...)`` tuple literal from a
    record-only (015-a shape) baseline step.

    Order 015-c correction: parse the TUPLE EXPRESSION — the balanced
    ``(...)`` following the assignment — not the ``tags =`` assignment
    statement: ``ast.literal_eval`` accepts expressions only, so handing
    it ``tags = (`` raised ``SyntaxError`` before any alias could be
    compared (the defective 015-b replay evidence). The scan stays
    bounded to the exact named step's run block and never executes
    workflow text; malformed, ambiguous (non-tuple), or non-string
    content fails closed with ``_InlineTupleError``."""
    start = source.find("tags = (")
    if start == -1:
        raise _InlineTupleError("no static tags tuple in the baseline step")
    paren = source.index("(", start)
    depth = 0
    end = -1
    in_string: str | None = None
    i = paren
    while i < len(source):
        ch = source[i]
        if in_string is not None:
            if ch == in_string and source[i - 1] != "\\":
                in_string = None
        elif ch in ('"', "'"):
            in_string = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
        i += 1
    if end == -1:
        raise _InlineTupleError("unbalanced tags tuple")
    try:
        value = ast.literal_eval(source[paren:end])
    except (ValueError, SyntaxError) as exc:
        raise _InlineTupleError(f"malformed tags tuple ({type(exc).__name__})") from exc
    if not isinstance(value, tuple):
        raise _InlineTupleError("ambiguous tags literal (not a tuple)")
    if not all(isinstance(tag, str) for tag in value):
        raise _InlineTupleError("non-string tag in the static tuple")
    return tuple(value)


def _workflow_baseline_coverage() -> dict[str, str | None]:
    """What the docker-published read-only baseline asserts:
    ``tag -> expected digest`` (``None`` when the workflow shape is
    record-only), derived by the focused parser. Never touches the
    registry."""
    source = _baseline_step_source()
    module = _load_ghcr_module()
    if (
        "immutable_historical_baseline(" in source
        and module is not None
        and hasattr(module, "immutable_historical_baseline")
    ):
        baseline = module.immutable_historical_baseline(REPO_ROOT)
        return dict(baseline)
    return {tag: None for tag in _inline_static_tags(source)}


# The exact static tuple of the 015-a frozen baseline step (commit
# 78822ca8f8c58fbc959495d37bdff32e525eb945), verbatim: multiline, with
# inline comments, and WITHOUT the archived RC7 pair (the historical
# regression) or the RC2 sha alias (which no 015-a tuple ever carried).
HISTORICAL_INLINE_TUPLE = """tags = (
    "0.1.0",
    "sha-fe334e87c9f0fc65d1826cf9af7dad7e9f70a94a",
    "sha-be3c78b2016d5d40ce9155df8f94d14525c43d39",
    "0.1.0-rc1",
    "sha-4d096e404e14badb78b4f99142bf08ef17f0f8a7",
    "0.1.0-rc2",
    # Order 014-c, D.5: the rejected RC3/RC4 tag pairs are part of
    # the immutable historical set (their records are archived,
    # so the pairs are no longer picked up from
    # packaging/rc_record.json).
    "0.1.0-rc3",
    "sha-307a929ffb30f4ea41c8be4e8a5ea25802e25142",
    "0.1.0-rc4",
    "sha-601a7f9fae19869ad8e09f10fa994550368fd87c",
    # Order 014-e, workstream C.2: the rejected RC5 tag pair is part of the
    # immutable historical set (the RC5 record is archived under
    # packaging/releases/0.1.0-rc5/, so its pair is no longer
    # picked up from packaging/rc_record.json).
    "0.1.0-rc5",
    "sha-e04b4a99afa6268c98f28ed7abfc1db506107523",
)"""


def test_inline_static_tags_parses_historical_multiline_shape() -> None:
    """The 015-a frozen inline shape parses to its exact 12-tag
    sequence: the TUPLE EXPRESSION is evaluated, inline comments are
    transparent, and the assignment statement itself is never fed to
    ``ast.literal_eval`` (order 015-c: the old code failed here with
    ``SyntaxError: invalid syntax`` before any alias comparison)."""
    assert _inline_static_tags(HISTORICAL_INLINE_TUPLE) == (
        "0.1.0",
        "sha-fe334e87c9f0fc65d1826cf9af7dad7e9f70a94a",
        "sha-be3c78b2016d5d40ce9155df8f94d14525c43d39",
        "0.1.0-rc1",
        "sha-4d096e404e14badb78b4f99142bf08ef17f0f8a7",
        "0.1.0-rc2",
        "0.1.0-rc3",
        "sha-307a929ffb30f4ea41c8be4e8a5ea25802e25142",
        "0.1.0-rc4",
        "sha-601a7f9fae19869ad8e09f10fa994550368fd87c",
        "0.1.0-rc5",
        "sha-e04b4a99afa6268c98f28ed7abfc1db506107523",
    )


@pytest.mark.parametrize(
    ("source", "reason"),
    [
        (
            'tags = (\n    "0.1.0-rc1",\n',
            "unbalanced (no closing paren)",
        ),
        (
            'tags = ("0.1.0-rc1" + "x")\n',
            "malformed (non-literal expression)",
        ),
        (
            'tags = ("0.1.0-rc1", 1)\n',
            "non-string member",
        ),
        (
            'tags = ("0.1.0-rc1")\n',
            "ambiguous (parenthesized string, not a tuple)",
        ),
        (
            'repo = "x/y"\n',
            "no static tags tuple at all",
        ),
    ],
)
def test_inline_static_tags_fails_closed(source: str, reason: str) -> None:
    """Malformed, ambiguous, non-string, or absent inline shapes fail
    closed with ``_InlineTupleError`` — never a silent partial parse,
    never workflow execution."""
    with pytest.raises(_InlineTupleError):
        _inline_static_tags(source)


def test_archived_records_match_pinned_inventory() -> None:
    """The archived strict record set is EXACTLY the pinned current
    inventory (RC1-RC5, RC7, RC8) with the pinned identities — no silent
    loss and no unreviewed growth."""
    pairs = _archived_pairs()
    assert set(pairs) == set(PINNED_ARCHIVES), (
        f"archive inventory drifted: {sorted(set(pairs) ^ set(PINNED_ARCHIVES))}"
    )
    for rc_id, (sha_tag, digest) in pairs.items():
        source, pinned_digest = PINNED_ARCHIVES[rc_id]
        assert sha_tag == f"sha-{source}", rc_id
        assert digest == pinned_digest, rc_id


def test_workflow_baseline_represents_every_archived_pair() -> None:
    """Both aliases of EVERY archived strict record are represented in the
    workflow baseline. This is the assertion that FAILED on the 015-a
    frozen source (RC7 archived, pair missing from the tuple)."""
    coverage = _workflow_baseline_coverage()
    missing: list[str] = []
    for rc_id, (sha_tag, _digest) in _archived_pairs().items():
        for tag in (rc_id, sha_tag):
            if tag not in coverage:
                missing.append(tag)
    assert not missing, f"workflow baseline omits archived aliases: {missing}"


def test_workflow_baseline_binds_pairs_to_recorded_digests() -> None:
    """The workflow baseline DIGEST-ASSERTS every archived pair against the
    digest recorded in its archived record (read-only; fail closed)."""
    coverage = _workflow_baseline_coverage()
    unbound: list[str] = []
    for rc_id, (sha_tag, digest) in _archived_pairs().items():
        for tag in (rc_id, sha_tag):
            if coverage.get(tag) != digest:
                unbound.append(f"{tag} -> {coverage.get(tag)!r} (expected {digest})")
    assert not unbound, f"workflow baseline does not digest-assert: {unbound}"


def test_rc6_absence_is_intentional_and_unrepresentable() -> None:
    """The 014-d RC6 attempt was abandoned before any push, tag, or
    publication: no RC6 identity exists, none may be created or reserved,
    and the baseline must not carry any RC6 tag."""
    assert not (RELEASES_DIR / "0.1.0-rc6").exists()
    assert "0.1.0-rc6" not in _archived_pairs()
    coverage = _workflow_baseline_coverage()
    assert not any(tag.startswith("0.1.0-rc6") for tag in coverage)


def test_workflow_and_module_share_one_source_of_truth() -> None:
    """The workflow baseline step consumes the shared single source of
    truth, so it cannot drift from the archived record set; the step
    remains read-only (no tag-mutation surface in its run block)."""
    source = _baseline_step_source()
    assert "immutable_historical_baseline(" in source, (
        "baseline step must consume the shared single source of truth "
        "(scripts/ghcr_tag_check.immutable_historical_baseline)"
    )
    module = _load_ghcr_module()
    assert module is not None and hasattr(module, "immutable_historical_baseline")
    expected = dict(module.immutable_historical_baseline(REPO_ROOT))
    assert _workflow_baseline_coverage() == expected
    for forbidden in ("docker push", "registry.put", "manifests/PUT"):
        assert forbidden not in source


def test_baseline_step_records_current_pair_dynamically() -> None:
    """Order 014-a, D.2 is preserved: the CURRENT RC pair (when a record
    exists) is still picked up dynamically from
    ``packaging/rc_record.json`` and never hard-coded into the immutable
    historical set."""
    source = _baseline_step_source()
    assert "packaging/rc_record.json" in source
    for tag in re.findall(r'"(0\.1\.0-rc\d+)"', source):
        pytest.fail(f"inline candidate tag literal in the baseline step: {tag}")
    raw = CI_WORKFLOW.read_text(encoding="utf-8")
    assert "rc-candidate-0.1.0-rc10" in raw
