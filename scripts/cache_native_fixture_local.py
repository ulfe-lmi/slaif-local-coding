#!/usr/bin/env python3
"""Order-bound local fixture preparation and Python rehearsal (017-s).

A DISTINCT, explicit local entry: ONE bounded serial Python-only
fixture rehearsal on THIS host, using ONLY the already available
Docker daemon and exact freshly owned fixture resources.  It reuses
R's validated image build, model, controller, exporter, stand-in,
guarded executor, measured confinement, deadline/ledger, artifact
acquisition and ownership helpers (narrow shared seams only); it
never runs the hosted CI path locally (it refuses a hosted
environment and never sets/spoofs GITHUB_ACTIONS or RUNNER_ENVIRONMENT).

ARCHITECTURE (017-s owner design): ONE long-lived Python
fixture-owner process IS the supervisor — independent of the coding
worker W, with ONE RAM run context.  The CLI caller is a thin
client that drives the owner's bounded protected lifecycle:

    prepare   -> preflight, collision, artifact, build, sentinels,
                then the EXACT target CID: registered in the
                protected state BEFORE start, confinement-inspected
                and 21002-measured there, PTY/env-handoff verified
                (zero wire), and observed NON-CONSUMING (closed
                actual controller state: scenario, wire request
                count, one-shot diagnostic state).  No semantic
                POST happens in prepare; the target is HELD.
    observe   -> the bounded trusted non-consuming status command
                (closed /state record; it makes no model POST,
                consumes nothing, advances no state).
    rehearse  -> the S Python consume on THAT SAME prepared
                instance: the closed controller auth-binding proof
                (valid admitted / wrong refused / missing refused);
                the first valid POST CONSUMES the one-shot
                no-tools diagnostic at causal position 0 and must
                answer the fixed assistant final text.
    finish    -> quiesce/freeze/export WHILE THE CONTAINER STILL
                EXISTS (21001) on the HELD instance — with or
                without the S Python consume: an ACTUAL
                non-consuming /state observation right before the
                export is the identity baseline (monotonic
                controller ledger, diagnostic-state identity), and
                the S rehearsal's exact Python-specific assertions
                (position 0, fixed no-tools metadata, the exact
                3+2 controller ledger) apply only when the Python
                consume actually ran on this run.  Exact teardown
                verified (positive-before / negative-after, exact
                CID/image/descendants, sentinel survival), owner
                convergence, then protected 0700/0600 publication.
    abort     -> caller or exact-run-id abort file: the SAME
                exact-owned cleanup on the SAME remaining budgets.

ONE non-resettable monotonic END anchor and ONE cumulative host
ledger cover every phase and every actor (total lifetime 1800 s
plus ONE bounded 600 s cleanup grace, never larger than R); there
is no second watchdog process, no second fresh budget, and no
UID-only or PID-reuse-prone host signalling (the owner handles its
own SIGTERM/KeyboardInterrupt and converges; the rehearsal driver
launches the owner in its own session, verifies that independence,
and never signals it).  The protected control root (fresh 0700,
outside the disposable work root) carries the bounded command
socket (private 0600 — the ONE declared producer/consumer
permission contract, verified with no-link/ownership checks) and
the protected closed state file (0600 under 0700) publishing the
run id, the single END anchor, the exact resource registry (CIDs
registered BEFORE start, image id, build intent, env file) and the
cumulative ledger at every phase boundary — the protected
intent/ledger a later separately-authorized recovery may read when
cleanup remains unverified (the control root is destroyed only on
fully verified cleanup); S itself performs no recovery experiment.

Order-bound opt-in: the rehearsal runs only when explicitly bound
to order ``017-s`` AND a literal source head (current git HEAD
equals the bound head, clean worktree, committed order bytes match
disk, ``oap/active`` selects 017-s).  A STABLE one-attempt
admission record — independent of any caller-selected output or
work directory, keyed by the order, not reset by a source-head
change inside the same activated S — refuses a second admitted
attempt (pass, fail, aborted or still-running); a read-only
opt-in refusal before admission records no attempt.  The retained
evidence destination must additionally not pre-exist.

NO native Codex is launched anywhere (not even --help/--version):
the attach plan is a PURE validated inert argv document
(``codex --yolo --profile early-beta`` under
``docker exec -it --user 21002:21002`` with the subject workspace
workdir and the two env-file keys) that S never executes.  The
rehearsal records native_started=false, worker_stopped=false and
codex_invoked=false throughout.  No secrets are forwarded to the
fixture; the synthetic credential is generated per run,
transferred only through the protected env file, and never
printed, exported or retained.  This local Python-only rehearsal
is NOT native-client qualification (D09 remains NOT RUN).
"""

from __future__ import annotations

import argparse
import base64
import errno
import hashlib
import json
import math
import os
import platform
import re
import select
import signal
import socket
import stat
import subprocess
import sys
import threading
import time
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cache_native_fixture_binding as oap_binding  # noqa: E402
import cache_native_fixture_ci as ci  # noqa: E402
import cache_native_fixture_export_client as fixture_export  # noqa: E402
import cache_native_fixture_identity as fidentity  # noqa: E402
import cache_native_fixture_model as model  # noqa: E402
import cache_native_fixture_native_prep as fixture_prep  # noqa: E402
import cache_native_fixture_runtime_profile as rprofile  # noqa: E402
import cache_native_fixture_standin as fixture_standin  # noqa: E402

FixtureError = ci.FixtureError

SCHEMA = "slaif-017s-local-evidence-v1"
# The DISTINCT native-scope owner terminal record for NEW-ORDER
# (017-v onward) bound runs: the same measured owner state,
# cleanup and publication as the S record, but WITHOUT the
# historical S whole-run false assertions (a native run never
# asserts them) and a distinct scope — the S rehearsal record
# keeps its S meaning and is never relabeled or doubled.
NATIVE_OWNER_RUN_EVIDENCE_SCHEMA = "slaif-native-owner-run-evidence-v1"
NATIVE_OWNER_RUN_SCOPE = "native-owner-run"
STATE_SCHEMA = "slaif-017s-owner-state-v1"
# The DISTINCT identity-bearing owner-state tag of the canonical
# 017-ab entry (the AB owner publishes ONLY this form; the
# historical v1 tag stays the strict 12-key original and rejects
# it — explicit new versions for the new physical identity).
AB_STATE_SCHEMA = "slaif-017ab-owner-state-v1"
ADMISSION_SCHEMA = "slaif-017s-admission-v1"
ORDER_ID = "017-s"
ORDER_PATH = "oap/orders/017-s-local-fixture-preparation-and-supervision.md"
ACTIVE_EXPECTED = b"017-s\n"
# The 017-x capability order: the ONE other order id this CLI's
# owner subcommand admits (the detached capability start; its
# SEALED child owns resolve+admit ONCE before any external work —
# the module-minted run identity is admitted in THIS process, and
# a constructor failure AFTER the won admission closes the SAME
# attempt honestly).
X_ORDER_ID = "017-x"
# The 017-y capability order: the SECOND explicit sealed entry
# (order 017-y readiness diagnosis and one separately bound
# Python-only capability attempt).  Its SEALED child owns
# resolve+admit ONCE in the DISTINCT 017-y namespace before any
# external work; the historical S rehearsal and the CONSUMED 017-x
# entry/namespace/records are unchanged and never adopted.  The
# owner mechanism, ledger, END and publication law are the SAME
# reviewed ones (no second orchestration stack).
Y_ORDER_ID = "017-y"
# The canonical FUTURE 017-ab sealed entry (INACTIVE under any
# other active order): the ONE owner-UID capability entry.  Its
# SEALED child owns resolve+admit ONCE in the DISTINCT 017-ab
# namespace before any external work; the historical S/X/Y entries,
# namespaces and records are unchanged and never adopted.  The
# owner mechanism, ledger, END and publication law are the SAME
# reviewed ones (no second orchestration stack).  This constant
# names the entry; it grants NO authority — actual
# repository-context validation refuses it before fixture work or
# admission under any other active order.
AB_ORDER_ID = rprofile.AB_ORDER_ID
# The DISTINCT closed owner-UID AB terminal record (017-aa): the
# SAME measured owner state, cleanup and publication as the
# native-scope record, PLUS the frozen owner identity
# substructure (the canonical profile description's measured
# context) and the AB-only exact-CID teardown proof.  The S and
# native-scope records keep their original meaning byte-for-byte.
AB_OWNER_RUN_EVIDENCE_SCHEMA = rprofile.AB_OWNER_RUN_EVIDENCE_SCHEMA
AB_OWNER_RUN_SCOPE = rprofile.AB_OWNER_RUN_SCOPE
# The canonical FUTURE 017-ad native-order entry (INERT in
# 017-ac: input-gated, unqualified — never created, activated,
# admitted or launched in this round).  It selects ONLY the
# owner-UID profile and carries the DISTINCT versioned
# identity-bearing record tags of the native handoff; this
# constant names the entry and grants NO authority — actual
# repository-context validation refuses it before fixture work
# or admission under any other active order.
AD_ORDER_ID = rprofile.AD_ORDER_ID
# The DISTINCT identity-bearing owner-state tag of the 017-ad
# entry (the AD owner publishes ONLY this form; the historical
# v1 tag stays the strict 12-key original and rejects it).
AD_STATE_SCHEMA = rprofile.AD_OWNER_STATE_SCHEMA
# The DISTINCT closed owner-UID AD native terminal record
# (017-ac): the SAME measured owner state, cleanup and
# publication as the native-scope record, PLUS the frozen owner
# identity substructure and the exact-CID teardown proof.  The
# S and native-scope records keep their original meaning
# byte-for-byte (the two tags are separate closed records, never
# a widened grammar).
AD_OWNER_RUN_EVIDENCE_SCHEMA = rprofile.AD_NATIVE_RUN_EVIDENCE_SCHEMA
AD_OWNER_RUN_SCOPE = rprofile.AD_OWNER_RUN_SCOPE
# The canonical FUTURE 017-af native-PTY qualification entry
# (INERT in 017-ae: software-only — never activated, admitted
# or launched in this round).  It selects ONLY the owner-UID
# profile through the closed entry mapping and carries the
# DISTINCT versioned identity-bearing record tags of the
# native attach-binding phase (devpts baseline, owned
# allocation, derived expected proc tty_nr); this constant
# names the entry and grants NO authority — actual
# repository-context validation refuses it before fixture work
# or admission under any other active order.
AF_ORDER_ID = rprofile.AF_ORDER_ID
# The DISTINCT identity-bearing owner-state tag of the 017-af
# entry (the AF owner publishes ONLY this form; the historical
# v1 tag stays the strict 12-key original and rejects it).
AF_STATE_SCHEMA = rprofile.AF_OWNER_STATE_SCHEMA
# The DISTINCT closed owner-UID AF native terminal record
# (017-ae software): the SAME measured owner state, cleanup
# and publication as the native-scope record, PLUS the frozen
# owner identity substructure and the exact-CID teardown
# proof.  The S, native-scope, AB and AD records keep their
# original meaning byte-for-byte (the tags are separate closed
# records, never a widened grammar).
AF_OWNER_RUN_EVIDENCE_SCHEMA = rprofile.AF_NATIVE_RUN_EVIDENCE_SCHEMA
AF_OWNER_RUN_SCOPE = rprofile.AF_OWNER_RUN_SCOPE
# The canonical FUTURE 017-ah native-PTY REQUALIFICATION entry
# (INERT in 017-ag: software-only — never activated, admitted
# or launched in this round).  It selects ONLY the owner-UID
# profile through the closed entry mapping and composes the
# EXISTING owner/guarded exact-CID/NativeOwnerRun and
# independent devpts producer APIs; it carries the DISTINCT
# versioned identity-bearing record tags of the 017-ah
# requalification; this constant names the entry and grants NO
# authority — actual repository-context validation refuses it
# before fixture work or admission under any other active
# order.
AH_ORDER_ID = rprofile.AH_ORDER_ID
# The DISTINCT identity-bearing owner-state tag of the 017-ah
# entry (the AH owner publishes ONLY this form; the historical
# v1 tag stays the strict 12-key original and rejects it; the
# AF tag stays AF-only, even for equal-numeric identities).
AH_STATE_SCHEMA = rprofile.AH_OWNER_STATE_SCHEMA
# The DISTINCT closed owner-UID AH native terminal record
# (017-ag software): the SAME measured owner state, cleanup
# and publication as the AF native-scope record, PLUS the
# frozen owner identity substructure and the exact-CID
# teardown proof.  The S, native-scope, AB, AD and AF records
# keep their original meaning byte-for-byte (the tags are
# separate closed records, never a widened grammar).
AH_OWNER_RUN_EVIDENCE_SCHEMA = rprofile.AH_NATIVE_RUN_EVIDENCE_SCHEMA
AH_OWNER_RUN_SCOPE = rprofile.AH_OWNER_RUN_SCOPE
# The canonical FUTURE 017-aj native-process format
# QUALIFICATION entry (INERT in 017-ai: software-only — never
# activated, admitted or launched in this round).  It selects
# ONLY the owner-UID profile through the closed entry mapping
# and composes the EXISTING owner/guarded exact-CID/NativeOwnerRun
# and independent devpts producer APIs; the canonical entry
# selects the CLOSED native format-capture scenario before
# startup; it carries the DISTINCT versioned identity-bearing
# record tags of the 017-aj qualification; this constant names
# the entry and grants NO authority — actual repository-context
# validation refuses it before fixture work or admission under
# any other active order.
AJ_ORDER_ID = rprofile.AJ_ORDER_ID
# The DISTINCT identity-bearing owner-state tag of the 017-aj
# entry (the AJ owner publishes ONLY this form; the historical
# v1 tag stays the strict 12-key original and rejects it; the
# AH tag stays AH-only, even for equal-numeric identities).
AJ_STATE_SCHEMA = rprofile.AJ_OWNER_STATE_SCHEMA
# The DISTINCT closed owner-UID AJ native terminal record
# (017-ai software): the SAME measured owner state, cleanup
# and publication as the AH native-scope record, PLUS the
# frozen owner identity substructure and the exact-CID
# teardown proof.  The S, native-scope, AB, AD, AF and AH
# records keep their original meaning byte-for-byte (the tags
# are separate closed records, never a widened grammar).
AJ_OWNER_RUN_EVIDENCE_SCHEMA = rprofile.AJ_NATIVE_RUN_EVIDENCE_SCHEMA
AJ_OWNER_RUN_SCOPE = rprofile.AJ_OWNER_RUN_SCOPE


def _entry_scenario(order_id: str | None) -> str:
    """The CLOSED scenario selected BEFORE startup by the owner's
    OWN frozen entry: the verified binding / frozen owner context
    is the sole selection authority — ambient environment values,
    HTTP flags and caller-ready records never select or redefine
    it.  Only the canonical 017-aj entry declares the closed
    ``format-capture`` scenario; every historical entry and the
    original default (``None``) keep ``diagnostic``
    byte-for-byte.  A foreign or unknown entry id is a closed
    refusal at the selection seam — the SAME closed entry set the
    observer-seam helper enforces, never a silent fallback."""
    if order_id is None:
        return "diagnostic"
    if order_id == AJ_ORDER_ID:
        return rprofile.AJ_FORMAT_SCENARIO
    if order_id in (
        AB_ORDER_ID,
        AD_ORDER_ID,
        AF_ORDER_ID,
        AH_ORDER_ID,
    ):
        return "diagnostic"
    raise FixtureError("local-entry-scenario-invalid")


def _entry_scenario_set(order_id: str | None) -> tuple[str, ...]:
    """The closed set of declared scenarios a host observer may
    accept for the owner's OWN frozen entry: the historical
    two-scenario set for every non-AJ entry (the hosted CI path
    included) and the AJ entry's own closed ``format-capture``
    declaration for the AJ entry ONLY: the AJ observer expects the
    closed format-capture scenario and NOTHING else (legacy
    scenario drift is a closed refusal).  A foreign or unknown
    entry id is a closed refusal at the observer seam, never a
    silent acceptance."""
    if order_id is None or order_id in (
        AB_ORDER_ID,
        AD_ORDER_ID,
        AF_ORDER_ID,
        AH_ORDER_ID,
    ):
        return ("diagnostic", "tool-cycle")
    if order_id == AJ_ORDER_ID:
        return (rprofile.AJ_FORMAT_SCENARIO,)
    raise FixtureError("local-entry-scenario-invalid")


# The R CI-measured built-image identity (immutable R report fact at
# 2ce9dcd): the local rebuild records whether it matches.
R_CI_IMAGE_ID = "sha256:331e1a70ec585f6fb1494c8486faf77fb1e624cf5f0f5765f7c5bab83a92de94"
# Finite ceilings no larger than R: the same 1800 s END anchor plus
# ONE bounded 600 s cleanup grace.
CLEANUP_GRACE_SECONDS = 600.0
ENV_FILE_NAME = "slaif-017s-env"
ENV_FILE_KEYS = ("CODEX_HOME", "SLAIF_SYNTHETIC_API_KEY")
# The PURE validated inert attach plan (the exact future native
# attachment document).  S NEVER executes it (not even help/version).
ATTACH_PLAN: dict[str, object] = {
    "argv": ("codex", "--yolo", "--profile", "early-beta"),
    "workdir": ci.fixture_standin.SUBJ_WORKDIR,
    "env_file_keys": ENV_FILE_KEYS,
    "executed": False,
}
_PHASES = (
    "start",
    "work-root",
    "preflight",
    "collision",
    "artifact",
    "build-context",
    "pull",
    "build",
    "sentinels",
    "prepare-target",
    "prepared",
    "consume",
    "finish",
    "teardown",
    "publish",
)
# The failure record's stage vocabulary: the closed phases plus the
# convergence stage (cleanup failures attributed to the umbrella).
_FAILURE_STAGES = _PHASES + ("cleanup",)
_STATE_STATUSES = ("running", "finished", "failed")
_CLEANUP_FAILURE_TOKENS = (
    "container-cleanup-unverified",
    "image-rmi-failed",
    "image-still-present",
    "image-absence-unverified",
    "image-cleanup-unverified",
    "env-file-remove-failed",
    "sentinel-died",
    "listener-cleanup-failed",
    "sentinel-cleanup-failed",
    "work-cleanup-failed",
    "control-cleanup-unverified",
    "internal",
)
_ADMISSION_DIR = ".oap-local"
_ADMISSION_EXCLUDE_LINE = ".oap-local/"
_ADMISSION_STATUSES = ("running", "pass", "fail", "aborted")

# -- closed failure-reason vocabulary -----------------------------------------
# The fail record's ``reason`` is a measured fixture token, never
# raw exception text.  The closed set below is the complete finite
# universe of tokens this module can record: every local fixed
# token, the exact ci runner tokens reachable through the local
# path (including the interpolated closed-key forms), the stand-in
# closed fail vocabulary, and the model's fixed-format mapped
# validation tokens.  Anything else is a bug, not a recordable fact.
_LOCAL_REASONS = frozenset(
    {
        "local-hosted-env",
        "local-binding-invalid",
        "local-ad-order-path-mismatch",
        "local-af-order-path-mismatch",
        "local-ah-order-path-mismatch",
        "local-aj-order-path-mismatch",
        "local-bounded-admission-missing",
        "local-deadline-offset-invalid",
        "local-bind-head-invalid",
        "local-head-mismatch",
        "local-worktree-dirty",
        "local-order-missing",
        "local-order-bytes",
        "local-active-mismatch",
        "local-git-argv",
        "local-git-timeout",
        "local-git-output-overbound",
        "local-git-failed",
        "local-admission-untrusted",
        "local-admission-malformed",
        "local-admission-env",
        "local-attempt-exhausted",
        "local-rehearsal-exists",
        "local-run-token-invalid",
        "native-owner-run-evidence-invalid",
        "local-env-untrusted",
        "local-env-exists",
        "local-env-remove-failed",
        "local-attach-plan-invalid",
        "local-state-malformed",
        "local-state-missing",
        "local-state-untrusted",
        "local-state-write-failed",
        "local-env-handoff-unverified",
        "local-prepared-wire-charged",
        "local-prepared-state",
        "local-image-state",
        "local-hold-unavailable",
        "local-hold-already-started",
        "local-hold-start-failed",
        "local-top-unavailable",
        "local-cleanup-unverified",
        "local-observe-unavailable",
        # The owner-UID (AB) identity collection/derivation: the Z
        # production reason vocabulary, prefixed, plus the
        # same-context at-use revalidation drift token.
        "local-identity-unsupported-platform",
        "local-identity-id-getter-failure",
        "local-identity-invalid-id-type",
        "local-identity-root-id",
        "local-identity-invalid-id-range",
        "local-identity-uid-triple-mismatch",
        "local-identity-gid-triple-mismatch",
        "local-identity-controller-id-collision",
        "local-identity-invalid-profile",
        "local-identity-controller-mismatch",
        "local-identity-invalid-group-vector",
        "local-identity-invalid-subject-for-profile",
        "local-identity-drift",
        "local-entry-scenario-invalid",
        "local-aj-context-unmeasured",
        "local-control-protocol",
        "local-control-socket-untrusted",
        "local-control-unbound",
        "local-lifecycle-state",
        "local-converged",
        "local-driver-startup",
        "local-driver-independence",
        "local-driver-patience",
        "local-driver-output",
        "local-driver-evidence",
        "local-driver-exit",
        "local-docker-endpoint",
        "pull-failed",
        "build-failed",
        "image-collision",
        "image-collision-unverified",
        "auth-binding-failed",
        "auth-binding-record-state",
        "finish-export-failed",
        "sentinel-process-died",
        "descendant-leftover",
        "descendant-unverified",
        "export-shape",
        "export-quiesce-state",
        "export-sha-mismatch",
        "export-overbound",
        "export-invalid",
        "export-identity-mismatch",
        "controller-ledger-mismatch",
        "cleanup-incomplete",
        "deadline-expired",
        "work-cleanup-failed",
        "cancelled",
        "internal",
    }
)
_CONF_KEY = (
    "NetworkMode",
    "ReadonlyRootfs",
    "CapDrop",
    "Memory",
    "MemorySwap",
    "PidsLimit",
    "NanoCpus",
    "Privileged",
    "UsernsMode",
    "IpcMode",
    "PidMode",
    "ShmSize",
    "Binds",
    "Devices",
    "VolumesFrom",
    "DeviceRequests",
    "NoNewPrivileges",
    "SeccompProfileName",
)
_CI_REASONS = frozenset(
    {
        "argv-untrusted",
        "deadline-expired",
        "deadline-grace-invalid",
        "deadline-grace-repeat",
        "ledger-admission-cap",
        "ledger-attempt-cap",
        "ledger-attempt-identity",
        "ledger-attempt-reserve",
        "ledger-outcome-identity",
        "ledger-output-cap",
        "ledger-output-invalid",
        "ledger-request-cap",
        "ledger-request-reserve",
        "ledger-reserve-identity",
        "ledger-healthz-invalid",
        "ledger-reserve-requests-invalid",
        "ledger-reserve-attempts-invalid",
        "ledger-requests-invalid",
        "ledger-attempts-invalid",
        "ledger-admitted-invalid",
        "ledger-refused-invalid",
        "engine-version-invalid",
        "seccomp-unavailable",
        "runtime-invalid",
        "runtime-version-invalid",
        "query-failed",
        "archive-digest",
        "archive-extract-failed",
        "archive-fetch-failed",
        "archive-oversize",
        "archive-shape",
        "archive-size",
        "binary-identity",
        "binary-oversize",
        "license-fetch-failed",
        "license-identity",
        "license-oversize",
        "license-shape",
        "notice-fetch-failed",
        "notice-identity",
        "notice-oversize",
        "notice-shape",
        "dockerfile-base-mismatch",
        "dockerfile-base-unpinned",
        "dockerfile-missing",
        "context-mismatch",
        "name-collision",
        "create-failed",
        "container-namespace-untrusted",
        "start-failed",
        "controller-not-ready",
        # 017-y closed readiness-diagnosis REFINEMENTS of the
        # controller-not-ready category: the ONLY closed facts the
        # fixed in-container readiness probe can measure on a
        # nonzero bounded readiness exec.  A missing/malformed/
        # duplicate/foreign/over-bound/contradictory probe output
        # keeps the original generic token (the fixed unknown);
        # these never widen the success schema or the confinement
        # law, and the original token keeps its original meaning.
        "controller-not-ready:uid-not-21001",
        "controller-not-ready:pid1-uid",
        "controller-not-ready:health-unreachable",
        # 017-y closed readiness-diagnosis lifecycle REFINEMENT:
        # a nonzero readiness exec without the probe's closed
        # record is followed by the ONE conditional bounded
        # allowlisted query of the SAME registered CID
        # (.State.Status only); exactly the closed ``exited``
        # line refines the category.  Any other status, any
        # other shape and every query failure (query failure is
        # NOT absence) keep the original generic token.
        "controller-not-ready:container-exited",
        "controller-measurement-mismatch",
        "inspect-mismatch:{{.HostConfig.LogConfig.Type}}",
        "inspect-mismatch:{{.Config.User}}",
        "confinement-shape",
        "confinement-user",
        "confinement-image",
        "confinement-mounts",
        "confinement-securityopt",
        "confinement-no-new-privileges",
        "confinement-seccomp",
        "confinement-logconfig",
        "confinement-tmpfs-set",
        "confinement-tmpfs-spec",
        "confinement-tmpfs-size",
        "confinement-tmpfs-identity",
        "confinement-tmpfs-mode",
        "cleanup-failed",
        "cleanup-query-failed",
        "leftover-container",
        "leftover-query-failed",
        "top-query-failed",
        "top-count-untrusted",
        "image-rmi-failed",
        "image-still-present",
        "image-absence-unverified",
        "exec-measurement-failed",
        "pty-attach-failed",
        "pty-record-state",
        "pty-workspace-state",
        "pty-term-mismatch",
        "profile-record-state",
        "standin-record-keys",
        "standin-record-state",
        "standin-record-identity",
        "observe-failed",
        "observe-record-state",
        "observe-entry-invalid",
        "observe-profile-invalid",
        "env-file-unbound",
        "output-read-failed",
        "work-root-exists",
        "work-root-untrusted",
    }
    | {f"confinement-missing:{key}" for key in _CONF_KEY}
    | {f"confinement-value:{key}" for key in _CONF_KEY}
)


def _model_mapped_reasons() -> frozenset[str]:
    """The model's fixed-format validation tokens, reconstructed
    from the model's own closed field universe (finite, explicit)."""
    universe = model.VALIDATION_FIELD_UNIVERSE
    out: set[str] = set(ci._MODEL_VALIDATION_FIXED) | {"record-validation"}
    for category in ci._MODEL_FIELD_CATEGORIES:
        for field in universe:
            out.add(f"closed record field {category} invalid: {field}")
    for field in universe:
        out.add(f"closed record digest invalid: {field}")
    return frozenset(out)


_FAILURE_REASONS = _LOCAL_REASONS | _CI_REASONS | ci._STANDIN_FAIL_REASONS | _model_mapped_reasons()


# -- bounded read-only git opt-in -------------------------------------------------
# These queries run BEFORE the shared runtime deadline/ledger exist,
# so they carry their OWN finite bounds (exact read-only grammar, a
# bounded output read and a bounded wait) and never call the fully
# bounded shared accounting.  No shell; ``--end-of-options`` is NOT
# a supported global option on this host's git and is never used.
_GIT_OUTPUT_MAX = 1 << 20
_GIT_TIMEOUT_SECONDS = 60.0


def _git_query(git: Callable[[list[str], Path], bytes], repo: Path, args: tuple[str, ...]) -> bytes:
    """Closed argv grammar for the opt-in gate: only the three exact
    read-only forms this gate needs, with the bound head embedded in
    the show ref (40-hex, validated by the caller)."""
    if args in (("rev-parse", "HEAD"), ("status", "--porcelain")):
        return git(list(args), repo)
    if (
        len(args) == 2
        and args[0] == "show"
        and re.fullmatch(r"[0-9a-f]{40}:" + re.escape(ORDER_PATH), args[1]) is not None
    ):
        return git(list(args), repo)
    raise FixtureError("local-git-argv")


def _git_default(args: list[str], repo: Path, _binary: bool = False) -> bytes:
    """Bounded read-only git query: exact argv, a capped AND
    time-bounded output read (select-gated on Linux; a longer or a
    HUNG response is killed — never hashed truncated, never waited
    on forever) and a bounded wait.  The child is reaped and its
    stream closed on EVERY exit (success, timeout, cap or read
    error) — no zombie, no held pipe — and any failure is a fixed
    closed token."""
    proc = subprocess.Popen(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    stream = proc.stdout
    data = b""
    try:
        if stream is not None:
            budget_end = time.monotonic() + _GIT_TIMEOUT_SECONDS
            while True:
                remaining = budget_end - time.monotonic()
                if remaining <= 0:
                    raise FixtureError("local-git-timeout")
                ready, _, _ = select.select([stream], [], [], min(remaining, 5.0))
                if not ready:
                    continue
                chunk = os.read(stream.fileno(), min(65536, _GIT_OUTPUT_MAX + 1 - len(data)))
                if not chunk:
                    break
                data += chunk
                if len(data) > _GIT_OUTPUT_MAX:
                    raise FixtureError("local-git-output-overbound")
        try:
            proc.wait(timeout=max(1.0, budget_end - time.monotonic()))
        except subprocess.TimeoutExpired:
            raise FixtureError("local-git-timeout") from None
    except FixtureError:
        raise
    except (OSError, subprocess.TimeoutExpired):
        raise FixtureError("local-git-failed") from None
    finally:
        # Bounded child reap + stream close on every exit: kill is
        # a no-op when the query already completed, and the reap
        # itself is bounded (a wedged child is left to the kernel's
        # own bounds, never waited on here forever).
        try:
            proc.kill()
        except OSError:
            pass
        try:
            proc.wait(timeout=5.0)
        except (OSError, subprocess.TimeoutExpired):
            pass
        if stream is not None:
            try:
                stream.close()
            except OSError:
                pass
    if proc.returncode != 0:
        raise FixtureError("local-git-failed")
    return data


def verify_local_optin(
    repo, bind_head: str, git_runner: Callable[[list[str]], bytes] | None = None
) -> dict[str, str]:
    """The order-bound opt-in gate: order 017-s, a literal 40-hex
    source head that equals the current HEAD, a clean worktree, the
    committed order bytes matching disk, and ``oap/active``
    selecting 017-s.  Any mismatch is a fixed closed failure — the
    rehearsal never runs against an unbound or drifted source, and
    a read-only refusal here admits no attempt (nothing is
    recorded until the experiment is actually admitted)."""
    repo = Path(repo)
    git = git_runner if git_runner is not None else _git_default
    if not re.fullmatch(r"[0-9a-f]{40}", bind_head):
        raise FixtureError("local-bind-head-invalid")
    head = _git_query(git, repo, ("rev-parse", "HEAD")).decode("ascii", "replace").strip()
    if head != bind_head:
        raise FixtureError("local-head-mismatch")
    status = _git_query(git, repo, ("status", "--porcelain")).decode("ascii", "replace")
    if status.strip() != "":
        raise FixtureError("local-worktree-dirty")
    try:
        order_disk = (repo / ORDER_PATH).read_bytes()
        order_head = _git_query(git, repo, ("show", f"{bind_head}:{ORDER_PATH}"))
        active = (repo / "oap" / "active").read_bytes()
    except OSError:
        raise FixtureError("local-order-missing") from None
    if hashlib.sha256(order_disk).hexdigest() != hashlib.sha256(order_head).hexdigest():
        raise FixtureError("local-order-bytes")
    if active != ACTIVE_EXPECTED:
        raise FixtureError("local-active-mismatch")
    return {
        "order": ORDER_ID,
        "bind_head": bind_head,
        "head": head,
        "order_sha256": hashlib.sha256(order_disk).hexdigest(),
    }


# -- stable one-attempt admission record ------------------------------------------
# The order's ONE actual rehearsal attempt is recorded in a stable
# protected file derived from the REPOSITORY and the ORDER (never
# from a caller-selected output/work directory, never keyed by the
# source head): a head change inside the same activated S does not
# reset it.  The directory is kept out of git status via the
# checkout's LOCAL-only .git/info/exclude (no tracked file, no
# worktree content).  Admission is an ATOMIC EXCLUSIVE CLAIM (an
# O_EXCL claim file, not a read-empty-then-replace race): two
# concurrent owners can never both admit.
_ADMISSION_READ_CAP = 8192
_ABORT_READ_CAP = 256


def _admission_dir_path(repo: Path) -> Path:
    return repo / _ADMISSION_DIR / "017-s"


def _admission_path(repo: Path) -> Path:
    return _admission_dir_path(repo) / "admission.json"


def _admission_claim_path(repo: Path) -> Path:
    return _admission_dir_path(repo) / "admission.claim"


def _admission_ancestor_ok(path: Path) -> None:
    """Protect the exact owned components this invocation creates
    (and only those): each must be a 0700 regular directory owned
    by this uid; a missing component is created fresh 0700.  A
    pre-existing foreign or group/other-writable component is
    refused — it is never adopted and never chmod'd."""
    base = path.parent.parent.parent  # the repository root
    cursor = base
    for component in (_ADMISSION_DIR, "017-s"):
        cursor = cursor / component
        if cursor.is_symlink():
            raise FixtureError("local-admission-env")
        if cursor.exists():
            st = os.lstat(cursor)
            if (
                not stat.S_ISDIR(st.st_mode)
                or stat.S_IMODE(st.st_mode) != stat.S_IRWXU
                or st.st_uid != os.getuid()
            ):
                raise FixtureError("local-admission-env")
        else:
            try:
                os.mkdir(cursor, 0o700)
            except OSError:
                raise FixtureError("local-admission-env") from None
            st = os.lstat(cursor)
            if (
                not stat.S_ISDIR(st.st_mode)
                or stat.S_IMODE(st.st_mode) != stat.S_IRWXU
                or st.st_uid != os.getuid()
            ):
                raise FixtureError("local-admission-env")


def _ensure_git_exclude(repo: Path) -> None:
    git_dir = repo / ".git"
    try:
        gst = os.lstat(git_dir)
    except OSError:
        raise FixtureError("local-admission-env") from None
    if not stat.S_ISDIR(gst.st_mode) or gst.st_uid != os.getuid():
        raise FixtureError("local-admission-env")
    info_dir = git_dir / "info"
    # Validate the info PARENT as a real (non-symlink) owned
    # directory — an unknown link is never followed.
    try:
        ist = os.lstat(info_dir)
    except OSError:
        raise FixtureError("local-admission-env") from None
    if not stat.S_ISDIR(ist.st_mode) or ist.st_uid != os.getuid():
        raise FixtureError("local-admission-env")
    exclude = info_dir / "exclude"
    try:
        if exclude.is_symlink() or (exclude.exists() and not exclude.is_file()):
            raise FixtureError("local-admission-env")
        data = _read_bounded(exclude, _ADMISSION_READ_CAP) if exclude.exists() else b""
    except FixtureError:
        raise
    except OSError:
        raise FixtureError("local-admission-env") from None
    lines = data.decode("utf-8", "replace").splitlines()
    if any(line.strip() == _ADMISSION_EXCLUDE_LINE for line in lines):
        return
    try:
        fd = os.open(exclude, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        with os.fdopen(fd, "a", encoding="utf-8") as handle:
            # Preserve the existing exclude bytes exactly; insert a
            # newline when the pre-existing last line has none, so
            # the entry never concatenates onto a foreign line.
            if data and not data.endswith(b"\n"):
                handle.write("\n" + _ADMISSION_EXCLUDE_LINE)
            else:
                handle.write(_ADMISSION_EXCLUDE_LINE)
    except OSError:
        raise FixtureError("local-admission-env") from None


def _read_bounded(path: Path, cap: int) -> bytes:
    """Bounded descriptor read of an exact owned regular file:
    lstat-checked (regular, not a link, size within the cap) and
    opened NO-FOLLOW, then read in chunks capped at ``cap + 1`` —
    a longer file is REJECTED, never silently truncated into a
    shorter accepted object."""
    try:
        st = os.lstat(path)
    except OSError:
        raise FixtureError("local-admission-malformed") from None
    if not stat.S_ISREG(st.st_mode) or st.st_size > cap:
        raise FixtureError("local-admission-malformed")
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    except OSError:
        raise FixtureError("local-admission-malformed") from None
    data = b""
    try:
        while len(data) <= cap:
            chunk = os.read(fd, min(65536, cap + 1 - len(data)))
            if not chunk:
                break
            data += chunk
    except OSError:
        raise FixtureError("local-admission-malformed") from None
    finally:
        try:
            os.close(fd)
        except OSError:
            pass
    if len(data) > cap:
        raise FixtureError("local-admission-malformed")
    return data


def _claim_owned_file(path: Path, expected_content: bytes) -> bool:
    """Verify a pre-existing claim file is OUR exact 0600 owned
    regular file with the expected content; True when it is."""
    try:
        st = os.lstat(path)
    except OSError:
        return False
    if (
        not stat.S_ISREG(st.st_mode)
        or stat.S_IMODE(st.st_mode) != 0o600
        or st.st_uid != os.getuid()
    ):
        return False
    try:
        return path.read_bytes() == expected_content
    except OSError:
        return False


def _read_admission(path: Path) -> dict:
    try:
        st = os.lstat(path)
    except FileNotFoundError:
        return {"record": ADMISSION_SCHEMA, "order": ORDER_ID, "attempts": []}
    if (
        not stat.S_ISREG(st.st_mode)
        or stat.S_IMODE(st.st_mode) != 0o600
        or st.st_uid != os.getuid()
    ):
        raise FixtureError("local-admission-untrusted")
    parent = path.parent
    pst = os.lstat(parent)
    if (
        not stat.S_ISDIR(pst.st_mode)
        or stat.S_IMODE(pst.st_mode) != stat.S_IRWXU
        or pst.st_uid != os.getuid()
    ):
        raise FixtureError("local-admission-untrusted")
    try:
        raw = _read_bounded(path, _ADMISSION_READ_CAP)
        record = json.loads(raw.decode("ascii"))
    except (ValueError, UnicodeDecodeError, OSError):
        raise FixtureError("local-admission-malformed") from None
    if (
        not isinstance(record, dict)
        or set(record) != {"record", "order", "attempts"}
        or record["record"] != ADMISSION_SCHEMA
        or record["order"] != ORDER_ID
        or not isinstance(record["attempts"], list)
        or len(record["attempts"]) > 8
        or any(
            not isinstance(entry, dict)
            or set(entry) != {"head", "run_id", "status"}
            or not re.fullmatch(r"[0-9a-f]{40}", entry["head"])
            or not re.fullmatch(r"[0-9a-f]{32}", entry["run_id"])
            or entry["status"] not in _ADMISSION_STATUSES
            for entry in record["attempts"]
        )
    ):
        raise FixtureError("local-admission-malformed")
    return record


def _write_admission(path: Path, record: dict) -> None:
    _admission_ancestor_ok(path)
    payload = (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
    tmp = path.with_name(path.name + ".tmp")
    if tmp.exists() or tmp.is_symlink():
        tmp.unlink()
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
        os.replace(tmp, path)
    except BaseException:
        try:
            tmp.unlink()
        except OSError:
            pass
        raise FixtureError("local-admission-malformed") from None
    st = path.lstat()
    if (
        not stat.S_ISREG(st.st_mode)
        or stat.S_IMODE(st.st_mode) != 0o600
        or st.st_uid != os.getuid()
    ):
        raise FixtureError("local-admission-untrusted")


def _release_admission_claim(repo: Path, run_id: str) -> None:
    """Release the exclusive claim ONLY when it is still our exact
    owned 0600 file carrying our run id (never a foreign object)."""
    claim = _admission_claim_path(repo)
    if _claim_owned_file(claim, run_id.encode("ascii")):
        try:
            os.unlink(claim)
        except OSError:
            pass


def _admit_attempt(repo: Path, bind_head: str, run_id: str) -> None:
    """ATOMICALLY ADMIT the one authorized attempt (the experiment
    boundary): an O_EXCL claim is won before the admission record is
    read, so two concurrent owners can never both admit.  A claim
    left by a run that already reached a TERMINAL record is stale
    (crash between the terminal record and the release) and is
    re-claimed exactly once; any other pre-existing claim or any
    previously admitted attempt — pass, fail, aborted or still
    running — exhausts the order's one rehearsal."""
    path = _admission_path(repo)
    _admission_ancestor_ok(path)
    claim = _admission_claim_path(repo)
    for attempt in (1, 2):
        try:
            fd = os.open(claim, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            if attempt == 2:
                raise FixtureError("local-attempt-exhausted") from None
            # Stale-claim recovery: a terminal record for the
            # claimed run id means the claim was never released
            # after convergence — reclaim it exactly once.
            try:
                claim_raw = _read_bounded(claim, _ABORT_READ_CAP)
                claimed_run_id = claim_raw.decode("ascii").strip()
            except (OSError, ValueError, UnicodeDecodeError):
                raise FixtureError("local-attempt-exhausted") from None
            if not re.fullmatch(r"[0-9a-f]{32}", claimed_run_id):
                raise FixtureError("local-attempt-exhausted") from None
            record = _read_admission(path)
            terminal = any(
                entry["run_id"] == claimed_run_id and entry["status"] in ("pass", "fail", "aborted")
                for entry in record["attempts"]
            )
            if not terminal or not _claim_owned_file(claim, claimed_run_id.encode("ascii")):
                raise FixtureError("local-attempt-exhausted") from None
            try:
                os.unlink(claim)
            except OSError:
                raise FixtureError("local-attempt-exhausted") from None
            continue
        with os.fdopen(fd, "wb") as handle:
            handle.write(run_id.encode("ascii"))
        break
    else:
        raise FixtureError("local-attempt-exhausted")
    try:
        record = _read_admission(path)
        if record["attempts"]:
            raise FixtureError("local-attempt-exhausted")
        _ensure_git_exclude(repo)
        _write_admission(
            path,
            {
                "record": ADMISSION_SCHEMA,
                "order": ORDER_ID,
                "attempts": [{"head": bind_head, "run_id": run_id, "status": "running"}],
            },
        )
    except BaseException:
        # The claim was won but the experiment was not admitted:
        # release it so a later invocation can claim cleanly.
        _release_admission_claim(repo, run_id)
        raise


def _record_attempt(repo: Path, run_id: str, status: str) -> None:
    """Record the terminal outcome of the admitted attempt (honest
    preservation: a failed or aborted attempt stays recorded), then
    release the exclusive claim (terminal record first, release
    second — a crash between them leaves a reclaimable stale
    claim, never a double-admission)."""
    try:
        path = _admission_path(repo)
        record = _read_admission(path)
        changed = False
        for entry in record["attempts"]:
            if entry["run_id"] == run_id:
                entry["status"] = status
                changed = True
        if changed:
            _write_admission(path, record)
        _release_admission_claim(repo, run_id)
    except FixtureError:
        # The journal is evidence, not a gate on cleanup: a journal
        # write failure after the run converged must not mask the
        # primary outcome or block the umbrella.
        pass


def _abort_requested(path: Path, run_id: str) -> bool:
    """The exact run-id abort file (strategy-side termination): a
    bounded read (the content must be exactly the run id, stripped;
    anything larger or anything else is not this run's abort)."""
    try:
        data = _read_bounded(path, _ABORT_READ_CAP)
    except (FileNotFoundError, OSError):
        return False
    except FixtureError:
        return False
    return data.strip() == run_id.encode("ascii")


# -- closed owner state file (0600 under 0700) -------------------------------------
def _identity_substructure_law(
    identity: object,
) -> tuple[int, int, tuple[int, ...], fidentity.FixtureIdentityDescription] | None:
    """The shared closed structural law of the AB frozen owner
    identity substructure (the identity-bearing owner STATE, the
    AB owner-run EVIDENCE and the AB driver RECORD all carry this
    ONE closed six-key substructure): the exact key set, the
    canonical owner-UID profile name, the strict nonroot finite
    Linux IDs distinct from the controller 21001, the
    one-element primary-GID group vector, and the 64-hex
    canonical fingerprint and profile-DATA digest — with the
    production codec re-deriving the canonical record from the
    retained IDs (controller fixed 21001/21001) and both digests
    verified against it.  Returns the frozen ``(uid, gid,
    groups, description)`` — the re-derived canonical
    description is included so the strict PUBLIC wrappers derive
    their runtime profile expectations from the SAME validated
    identity (production codec, no caller input) — or ``None``:
    ONE shared structural core; each
    public wrapper keeps its OWN fixed refusal token.  This is
    closed data integrity — never a measured-authority claim
    (a caller-authored valid substructure is still only data)."""
    if not isinstance(identity, dict) or set(identity) != {
        "profile",
        "fingerprint",
        "subject_uid",
        "subject_gid",
        "subject_groups",
        "profile_data_sha256",
    }:
        return None
    profile = identity["profile"]
    fingerprint = identity["fingerprint"]
    subject_uid = identity["subject_uid"]
    subject_gid = identity["subject_gid"]
    subject_groups = identity["subject_groups"]
    profile_data_sha256 = identity["profile_data_sha256"]
    if (
        profile != fidentity.PROFILE_OWNER_UID
        or not isinstance(fingerprint, str)
        or re.fullmatch(r"[0-9a-f]{64}", fingerprint) is None
        or isinstance(subject_uid, bool)
        or not isinstance(subject_uid, int)
        or isinstance(subject_gid, bool)
        or not isinstance(subject_gid, int)
        or not (fidentity.LINUX_ID_MIN <= subject_uid <= fidentity.LINUX_ID_MAX)
        or not (fidentity.LINUX_ID_MIN <= subject_gid <= fidentity.LINUX_ID_MAX)
        or not isinstance(subject_groups, list)
        or len(subject_groups) != 1
        or isinstance(subject_groups[0], bool)
        or not isinstance(subject_groups[0], int)
        or subject_groups[0] != subject_gid
        or not isinstance(profile_data_sha256, str)
        or re.fullmatch(r"[0-9a-f]{64}", profile_data_sha256) is None
    ):
        return None
    try:
        description = fidentity.FixtureIdentityDescription(
            profile=profile,
            controller_uid=fidentity.CONTROLLER_UID,
            controller_gid=fidentity.CONTROLLER_GID,
            subject_uid=subject_uid,
            subject_gid=subject_gid,
            subject_groups=(subject_gid,),
        )
    except fidentity.FixtureIdentityError:
        return None
    if (
        fidentity.fingerprint_description(description) != fingerprint
        or hashlib.sha256(fidentity.encode_description(description)).hexdigest()
        != profile_data_sha256
    ):
        return None
    return (subject_uid, subject_gid, (subject_gid,), description)


# The shared closed 12-key base of BOTH state grammars (the
# historical v1 form is exactly these keys; the DISTINCT
# identity-bearing AB form adds its own closed keys).
_STATE_BASE_KEYS = frozenset(
    {
        "record",
        "run_id",
        "pid",
        "end_anchor",
        "phase",
        "status",
        "containers",
        "create_intent",
        "image_id",
        "build_attempted",
        "env_file",
        "ledger",
    }
)


def _validate_state_common_fields(state: dict, token: str) -> None:
    """The private structural core shared by BOTH state
    validators: the exact field laws of the shared keys (pid, END
    anchor, phase, status, containers, create intent, image id,
    build attempt, env file, ledger).  Each PUBLIC wrapper first
    enforces its own tag, key set and binding/identity law with
    its own fixed refusal token, then delegates the shared field
    checks here (the v1 law is byte-for-byte the historical one)."""
    pid = state["pid"]
    if not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0:
        raise FixtureError(token)
    anchor = state["end_anchor"]
    if (
        not isinstance(anchor, (int, float))
        or isinstance(anchor, bool)
        or not (0 < float(anchor) < 1e15)
    ):
        raise FixtureError(token)
    if state["phase"] not in _PHASES:
        raise FixtureError(token)
    if state["status"] not in _STATE_STATUSES:
        raise FixtureError(token)
    containers = state["containers"]
    if (
        not isinstance(containers, list)
        or len(containers) > 16
        or not all(ci._is_cid(c) for c in containers)
    ):
        raise FixtureError(token)
    create_intent = state["create_intent"]
    if create_intent is not None and not ci._LOCAL_NAME_RE.fullmatch(str(create_intent)):
        raise FixtureError(token)
    image_id = state["image_id"]
    if image_id is not None and not ci._IMAGE_ID_RE.fullmatch(str(image_id)):
        raise FixtureError(token)
    if not isinstance(state["build_attempted"], bool):
        raise FixtureError(token)
    env_file = state["env_file"]
    if env_file is not None and (
        not isinstance(env_file, str)
        or not env_file.startswith("/")
        or len(env_file) > 4096
        or "\x00" in env_file
    ):
        raise FixtureError(token)
    ledger = state["ledger"]
    if (
        not isinstance(ledger, dict)
        or set(ledger) != set(_ledger_facts(ci._RunLedger(model.FixtureBudgets())))
        or any(not isinstance(v, int) or isinstance(v, bool) or v < 0 for v in ledger.values())
    ):
        raise FixtureError(token)


def _validate_state_object(state: object, run_id: str) -> None:
    """The ORIGINAL closed owner-state grammar
    (``slaif-017s-owner-state-v1``): the STRICT 12-key v1 form,
    byte-for-byte the historical law.  The identity-bearing AB
    state carries its OWN explicit tag (``_validate_ab_state_
    object``): the v1 consumer rejects the new profile record —
    a tag plus a valid data fingerprint is integrity, never
    owner-ID origin or a widened v1 grammar."""
    if not isinstance(state, dict) or set(state) != _STATE_BASE_KEYS:
        raise FixtureError("local-state-malformed")
    if state["record"] != STATE_SCHEMA or state["run_id"] != run_id:
        raise FixtureError("local-state-malformed")
    if not re.fullmatch(r"[0-9a-f]{32}", str(state["run_id"])):
        raise FixtureError("local-state-malformed")
    _validate_state_common_fields(state, "local-state-malformed")


def _validate_identity_state_core(
    state: dict,
    run_id: str,
    *,
    tag: str,
    entry_order: str,
    token: str,
) -> None:
    """The shared private structural core of the DISTINCT
    identity-bearing owner-state grammars (the AB and AD
    wrappers): the shared 12 keys PLUS the closed identity
    substructure — the frozen owner identity (the shared
    structural law) and the full ORIGINAL verified order/head/
    run binding (the entry's own order id, the literal bound
    head and the admitted run id).  The tag and the data
    fingerprint are integrity only — the binding ties this state
    to the owner's OWN admitted attempt, and the sealed
    composition's admission verification is what proves it;
    nothing here is a measured-authority claim.  Each PUBLIC
    wrapper keeps its own fixed refusal token, its own tag and
    its own entry-order binding (the strict wrappers are
    separate closed grammars — a tag is never widened across
    entries, including for equal-numeric identities)."""
    if not isinstance(state, dict) or set(state) != _STATE_BASE_KEYS | {
        "identity",
        "order",
        "bind_head",
    }:
        raise FixtureError(token)
    if state["record"] != tag or state["run_id"] != run_id:
        raise FixtureError(token)
    if not re.fullmatch(r"[0-9a-f]{32}", str(state["run_id"])):
        raise FixtureError(token)
    if state["order"] != entry_order:
        raise FixtureError(token)
    if not re.fullmatch(r"[0-9a-f]{40}", str(state["bind_head"])):
        raise FixtureError(token)
    if _identity_substructure_law(state["identity"]) is None:
        raise FixtureError(token)
    _validate_state_common_fields(state, token)


def _validate_ab_state_object(state: object, run_id: str) -> None:
    """The DISTINCT identity-bearing AB owner-state grammar
    (``slaif-017ab-owner-state-v1``): the shared 12 keys PLUS the
    closed AB substructure — the frozen owner identity (the
    shared structural law) and the full ORIGINAL verified
    order/head/run binding (the canonical AB entry, the literal
    bound head and the admitted run id).  The tag and the data
    fingerprint are integrity only — the binding ties this state
    to the owner's OWN admitted attempt, and the sealed driver's
    admission verification is what proves it; nothing here is a
    measured-authority claim.  The old v1 tag is never widened to
    this record, and this tag is refused by the v1 consumer."""
    _validate_identity_state_core(
        state,
        run_id,
        tag=AB_STATE_SCHEMA,
        entry_order=AB_ORDER_ID,
        token="local-ab-state-malformed",
    )


def _validate_ad_state_object(state: object, run_id: str) -> None:
    """The DISTINCT identity-bearing AD owner-state grammar
    (``slaif-017ad-owner-state-v1``): the SAME shared structural
    law as the AB wrapper, under the canonical 017-ad entry's
    OWN tag and order binding (the future native entry, INERT in
    017-ac).  The AB tag is refused here and the v1 tag never
    widened — explicit separate closed grammars for the new
    physical identity, including for equal-numeric identities."""
    _validate_identity_state_core(
        state,
        run_id,
        tag=AD_STATE_SCHEMA,
        entry_order=AD_ORDER_ID,
        token="local-ad-state-malformed",
    )


def _validate_af_state_object(state: object, run_id: str) -> None:
    """The DISTINCT identity-bearing AF owner-state grammar
    (``slaif-017af-owner-state-v1``): the SAME shared structural
    law as the AB wrapper, under the canonical 017-af entry's
    OWN tag and order binding (the future native-PTY
    qualification entry, INERT in 017-ae).  The AB and AD tags
    are refused here and the v1 tag never widened — explicit
    separate closed grammars for the new physical identity,
    including for equal-numeric identities."""
    _validate_identity_state_core(
        state,
        run_id,
        tag=AF_STATE_SCHEMA,
        entry_order=AF_ORDER_ID,
        token="local-af-state-malformed",
    )


def _validate_ah_state_object(state: object, run_id: str) -> None:
    """The DISTINCT identity-bearing AH owner-state grammar
    (``slaif-017ah-owner-state-v1``): the SAME shared structural
    law as the AB wrapper, under the canonical 017-ah entry's
    OWN tag and order binding (the future native-PTY
    REQUALIFICATION entry, INERT in 017-ag).  The AB, AD and
    AF tags are refused here and the v1 tag never widened —
    explicit separate closed grammars for the new physical
    identity, including for equal-numeric identities."""
    _validate_identity_state_core(
        state,
        run_id,
        tag=AH_STATE_SCHEMA,
        entry_order=AH_ORDER_ID,
        token="local-ah-state-malformed",
    )


def _validate_aj_state_object(state: object, run_id: str) -> None:
    """The DISTINCT identity-bearing AJ owner-state grammar
    (``slaif-017aj-owner-state-v1``): the SAME shared structural
    law as the AB wrapper, under the canonical 017-aj entry's
    OWN tag and order binding (the future native-process
    format QUALIFICATION entry, INERT in 017-ai).  The AB,
    AD, AF and AH tags are refused here and the v1 tag never
    widened — explicit separate closed grammars for the new
    physical identity, including for equal-numeric
    identities."""
    _validate_identity_state_core(
        state,
        run_id,
        tag=AJ_STATE_SCHEMA,
        entry_order=AJ_ORDER_ID,
        token="local-aj-state-malformed",
    )


def _write_state(path: Path, state: dict, *, ab: bool = False) -> None:
    """Atomic (same-directory tmp + rename) 0600 state publish.
    The validator follows the published FORM: the DISTINCT
    identity-bearing state (``ab=True`` — the AB or AD owner's
    own form) is validated by its OWN tag's grammar (the tag
    selects the strict wrapper); the original v1 form keeps the
    strict 12-key law (the owner publishes exactly one form,
    chosen by its OWN frozen context, never the caller's)."""
    tag = state["record"] if isinstance(state, dict) else None
    if tag == AB_STATE_SCHEMA:
        validator = _validate_ab_state_object
    elif tag == AD_STATE_SCHEMA:
        validator = _validate_ad_state_object
    elif tag == AF_STATE_SCHEMA:
        validator = _validate_af_state_object
    elif tag == AH_STATE_SCHEMA:
        validator = _validate_ah_state_object
    elif tag == AJ_STATE_SCHEMA:
        validator = _validate_aj_state_object
    else:
        validator = _validate_state_object
    validator(state, str(state["run_id"]))
    payload = (json.dumps(state, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
    tmp = path.with_name(path.name + ".tmp")
    if tmp.exists() or tmp.is_symlink():
        tmp.unlink()
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
        os.replace(tmp, path)
    except BaseException:
        try:
            tmp.unlink()
        except OSError:
            pass
        raise FixtureError("local-state-write-failed") from None
    st = path.lstat()
    if (
        not stat.S_ISREG(st.st_mode)
        or stat.S_IMODE(st.st_mode) != 0o600
        or st.st_uid != os.getuid()
    ):
        raise FixtureError("local-state-write-failed")


# -- protected bounded owner control protocol (017-s lifecycle) ----------------------
# ONE independently running Python owner serves thin clients over a
# protected Unix socket inside its fresh 0700 control root: one
# closed JSON line per connection, ONE closed request, ONE closed
# response.  The SAME RAM run context (ledger, attempt, END anchor,
# registry) answers every command; a client disappearance cannot
# stop or reset ownership, and the owner converges independently at
# its own finite deadline.  No raw content crosses the protocol.
CONTROL_RECORD = "slaif-017s-control-v1"
# ``hold`` is the 017-x detached capability start (ONE closed
# detached stand-in hold exec on the held prepared exact CID; a
# second start — including a failed one — is refused for the run).
# ``top`` is the 017-x bounded exact-CID process inventory (the
# authoritative member list the host-side capability discovery
# cross-checks; every query charges the SAME owner ledger/deadline).
_CONTROL_COMMANDS = ("prepare", "observe", "rehearse", "finish", "abort", "hold", "top")
_CONTROL_REQUEST_CAP = 4096
_CONTROL_RESPONSE_CAP = 16384
_CONTROL_ACCEPT_TIMEOUT = 5.0
_CONTROL_READ_TIMEOUT = 30.0
_CONTROL_STARTUP_TIMEOUT = 60.0
_CLIENT_TIMEOUT = 3600.0
_DRIVER_STARTUP_REAP_SECONDS = 30.0
_DRIVER_CAPTURE_MAX = 1 << 20
_CONTROL_STATE_NAME = "owner-state.json"
_CONTROL_SOCK_NAME = "control.sock"
_CONTROL_DETAIL_KEYS = {
    "prepare": ("cid", "state", "observed", "end_anchor"),
    "observe": ("scenario", "wire_requests", "diagnostic_state", "raw_content_retained"),
    "rehearse": (
        "cid",
        "valid_admitted",
        "wrong_refused",
        "missing_refused",
        "diagnostic_response",
        "admitted",
        "refused",
    ),
    "finish": ("outcome", "stage", "evidence_sha256", "control_dir_retained"),
    "abort": ("outcome", "stage", "evidence_sha256", "control_dir_retained"),
    "hold": ("hold_token",),
    "top": ("pids", "rows"),
}


def _validate_control_response(
    response: object, command: str, entry_order: str | None = None
) -> None:
    """Closed validation of the owner's control response: exact key
    set, fixed record tag, run-id identity, the closed failure
    vocabulary for ``reason``, and the exact per-command ``detail``
    key set with closed value grammar — no raw content, env value or
    exception text can be reflected back to a client."""
    if (
        not isinstance(response, dict)
        or set(response) != {"record", "ok", "command", "run_id", "reason", "detail"}
        or response["record"] != CONTROL_RECORD
        or response["command"] != command
        or not isinstance(response["ok"], bool)
        or not re.fullmatch(r"[0-9a-f]{32}", str(response["run_id"]))
    ):
        raise FixtureError("local-control-protocol")
    if response["reason"] is not None and response["reason"] not in _FAILURE_REASONS:
        raise FixtureError("local-control-protocol")
    detail = response["detail"]
    if response["ok"] and command in _CONTROL_DETAIL_KEYS:
        if not isinstance(detail, dict) or set(detail) != set(_CONTROL_DETAIL_KEYS[command]):
            raise FixtureError("local-control-protocol")
        if command == "prepare":
            observed = detail["observed"]
            ok = (
                ci._is_cid(detail["cid"])
                and detail["state"] == "prepared-unconsumed"
                and isinstance(observed, dict)
                and set(observed) == {"scenario", "wire_requests", "diagnostic_state"}
                and observed["scenario"] == _entry_scenario(entry_order)
                and observed["wire_requests"] == 0
                and observed["diagnostic_state"] == "unobserved"
                and isinstance(detail["end_anchor"], (int, float))
                and not isinstance(detail["end_anchor"], bool)
                and math.isfinite(detail["end_anchor"])
                and 0 < detail["end_anchor"] < 1e15
            )
        elif command == "observe":
            ok = (
                detail["scenario"] in _entry_scenario_set(entry_order)
                and isinstance(detail["wire_requests"], int)
                and not isinstance(detail["wire_requests"], bool)
                and detail["wire_requests"] >= 0
                and detail["diagnostic_state"] in ("unobserved", "observed")
                and detail["raw_content_retained"] is False
            )
        elif command == "rehearse":
            ok = (
                ci._is_cid(detail["cid"])
                and detail["valid_admitted"] is True
                and detail["wrong_refused"] is True
                and detail["missing_refused"] is True
                and detail["diagnostic_response"] == "fixed-final-text-no-tools"
                and detail["admitted"] == 1
                and detail["refused"] == 2
            )
        elif command == "hold":
            # The detached capability start returns ONLY the issued
            # 32-hex marker (the kernel-cmdline correlation
            # identity); nothing else crosses the protocol.  The
            # closed marker grammar is an ACTUAL string: a numeric
            # (or any non-string) value is refused, never coerced
            # by ``str()``.
            ok = (
                isinstance(detail["hold_token"], str)
                and re.fullmatch(r"[0-9a-f]{32}", detail["hold_token"]) is not None
            )
        elif command == "top":
            # The bounded exact-CID inventory: distinct positive
            # PIDs, at most the fixture pids limit of rows, and a
            # row count agreeing with the list — no raw content.
            pids = detail["pids"]
            rows = detail["rows"]
            ok = (
                isinstance(pids, list)
                and isinstance(rows, int)
                and not isinstance(rows, bool)
                and rows == len(pids)
                and 1 <= rows <= model.PIDS_LIMIT
                and all(isinstance(p, int) and not isinstance(p, bool) and p > 0 for p in pids)
                and len(set(pids)) == len(pids)
            )
        else:  # finish / abort: the converged closed outcome
            ok = (
                detail["outcome"] in ("pass", "fail", "aborted")
                and detail["stage"] in _FAILURE_STAGES
                and (detail["evidence_sha256"] is None or _is_sha256(detail["evidence_sha256"]))
                and isinstance(detail["control_dir_retained"], bool)
            )
        if not ok:
            raise FixtureError("local-control-protocol")
    if not response["ok"] and detail is not None:
        raise FixtureError("local-control-protocol")


def _state_record(control_dir, *, entry_order: str | None = None) -> dict | None:
    """Protected read of the owner's published state (0600 under the
    owned 0700 control root): a CLOSED full check under the
    entry's OWN strict grammar (record tag, then the complete
    validator for that tag — exact key set, run id, END anchor,
    phase/status, every shared field law, and for the AB form the
    full binding/identity substructures); None when not yet
    published or not this uid's file — the client never trusts a
    foreign, oversized or malformed state.

    The entry-aware tag law: the historical v1 tag for the original
    entries (``entry_order`` None or a non-owner-UID sealed entry —
    byte-for-byte the historical meaning) and the DISTINCT
    identity-bearing AB/AD/AF/AH/AJ tags for the canonical 017-ab
    / 017-ad / 017-af / 017-ah / 017-aj entries (which
    additionally require the full closed binding and identity
    substructures of their OWN entry).  Each entry reads ONLY
    its own tag: a foreign tag is not this entry's state, and
    the v1 grammar rejects an identity-bearing record (the old
    tag is never widened)."""
    if entry_order == AB_ORDER_ID:
        tag = AB_STATE_SCHEMA
    elif entry_order == AD_ORDER_ID:
        tag = AD_STATE_SCHEMA
    elif entry_order == AF_ORDER_ID:
        tag = AF_STATE_SCHEMA
    elif entry_order == AH_ORDER_ID:
        tag = AH_STATE_SCHEMA
    elif entry_order == AJ_ORDER_ID:
        tag = AJ_STATE_SCHEMA
    else:
        tag = STATE_SCHEMA
    root = Path(control_dir)
    try:
        rstat = os.lstat(root)
        if (
            not stat.S_ISDIR(rstat.st_mode)
            or stat.S_IMODE(rstat.st_mode) != stat.S_IRWXU
            or rstat.st_uid != os.getuid()
        ):
            return None
        path = root / _CONTROL_STATE_NAME
        st = os.lstat(path)
        if (
            not stat.S_ISREG(st.st_mode)
            or stat.S_IMODE(st.st_mode) != 0o600
            or st.st_uid != os.getuid()
        ):
            return None
        state = json.loads(_read_bounded(path, 8192).decode("ascii"))
    except (OSError, ValueError, UnicodeDecodeError, FixtureError):
        return None
    if not isinstance(state, dict) or state.get("record") != tag:
        return None
    # the FULL closed grammar of this entry's tag (the minimal
    # pre-checks are subsumed): extra keys, an invalid pid or
    # ledger, a broken AB binding or identity substructure all
    # refuse the state — the reader is a closed consumer, not a
    # convenience parser
    try:
        if tag == AB_STATE_SCHEMA:
            _validate_ab_state_object(state, str(state["run_id"]))
        elif tag == AD_STATE_SCHEMA:
            _validate_ad_state_object(state, str(state["run_id"]))
        elif tag == AF_STATE_SCHEMA:
            _validate_af_state_object(state, str(state["run_id"]))
        elif tag == AH_STATE_SCHEMA:
            _validate_ah_state_object(state, str(state["run_id"]))
        elif tag == AJ_STATE_SCHEMA:
            _validate_aj_state_object(state, str(state["run_id"]))
        else:
            _validate_state_object(state, str(state["run_id"]))
    except (FixtureError, KeyError, TypeError, ValueError):
        return None
    return state


def _accept_bounded(listener, timeout: float):
    ready, _, _ = select.select([listener], [], [], timeout)
    if not ready:
        return None
    try:
        conn, _addr = listener.accept()
    except OSError:
        return None
    conn.settimeout(_CONTROL_READ_TIMEOUT)
    return conn


def _reject_closed_constant(name: str) -> float:
    """Strict JSON: the closed control grammar admits no NaN or
    Infinity constants — a non-finite value can never be a valid
    anchor, budget, count or identity, and parsing one is a
    malformed closed record, not a representable number."""
    raise ValueError("closed json constant")


def _read_control_request(conn) -> dict | None:
    """ONE bounded closed request line from a client: malformed,
    overbound or blocked input is dropped (None) — never reflected,
    never able to wedge the owner."""
    try:
        deadline = time.monotonic() + _CONTROL_READ_TIMEOUT
        data = b""
        while b"\n" not in data:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return None
            conn.settimeout(min(remaining, 5.0))
            chunk = conn.recv(65536)
            if not chunk:
                return None
            data += chunk
            if len(data) > _CONTROL_REQUEST_CAP:
                return None
        line = data.split(b"\n", 1)[0]
        request = json.loads(line.decode("ascii"), parse_constant=_reject_closed_constant)
    except (OSError, ValueError, UnicodeDecodeError):
        return None
    if (
        not isinstance(request, dict)
        or set(request) != {"record", "command", "run_id"}
        or request["record"] != CONTROL_RECORD
        or request["command"] not in _CONTROL_COMMANDS
        or not re.fullmatch(r"[0-9a-f]{32}", str(request["run_id"]))
    ):
        return None
    return request


def _control_client(
    control_dir,
    command: str,
    run_id: str,
    timeout: float,
    entry_order: str | None = None,
) -> dict:
    """ONE bounded thin-client command against the running owner.

    Protected socket verification is the ONE declared permission
    contract the actual producer publishes: the socket lives in the
    owner's fresh owned 0700 control root and is a private 0600
    socket of the same uid (the same 0700-root / 0600-file rule as
    the protected state and the retained evidence — never a
    write-only or world-reachable mode, never a link).  The request
    and the response are closed single lines with their bounds; the
    response must bind the EXACT requested run id, and ONE absolute
    remaining budget (finite, never extended) covers connect, send
    and every read — a slow-drip peer cannot stretch the command
    beyond it.  The client's own disappearance cannot reach the
    owner (the owner keeps serving)."""
    root = Path(control_dir)
    try:
        rstat = os.lstat(root)
    except OSError:
        raise FixtureError("local-control-socket-untrusted") from None
    if (
        not stat.S_ISDIR(rstat.st_mode)
        or stat.S_IMODE(rstat.st_mode) != stat.S_IRWXU
        or rstat.st_uid != os.getuid()
    ):
        raise FixtureError("local-control-socket-untrusted")
    path = root / _CONTROL_SOCK_NAME
    try:
        sstat = os.lstat(path)
    except OSError:
        raise FixtureError("local-control-socket-untrusted") from None
    if (
        not stat.S_ISSOCK(sstat.st_mode)
        or stat.S_IMODE(sstat.st_mode) != 0o600
        or sstat.st_uid != os.getuid()
    ):
        raise FixtureError("local-control-socket-untrusted")
    if command not in _CONTROL_COMMANDS or not re.fullmatch(r"[0-9a-f]{32}", run_id):
        raise FixtureError("local-control-protocol")
    if (
        not isinstance(timeout, (int, float))
        or isinstance(timeout, bool)
        or not math.isfinite(float(timeout))
        or float(timeout) <= 0
    ):
        raise FixtureError("local-control-protocol")
    request = (
        json.dumps(
            {"record": CONTROL_RECORD, "command": command, "run_id": run_id},
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("ascii")
    if len(request) > _CONTROL_REQUEST_CAP:
        raise FixtureError("local-control-protocol")
    # ONE absolute remaining budget across connect, send and EVERY
    # read (recomputed from the same deadline before each blocking
    # call): a slow-drip peer that stays under any single-operation
    # timeout cannot stretch the command past the bound.
    deadline = time.monotonic() + float(timeout)

    def _remaining() -> float:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise FixtureError("local-control-protocol")
        return remaining

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        sock.settimeout(_remaining())
        sock.connect(str(path))
        sock.settimeout(_remaining())
        sock.sendall(request)
        data = b""
        while b"\n" not in data:
            sock.settimeout(_remaining())
            chunk = sock.recv(65536)
            if not chunk:
                raise FixtureError("local-control-protocol")
            data += chunk
            if len(data) > _CONTROL_RESPONSE_CAP:
                raise FixtureError("local-control-protocol")
        line = data.split(b"\n", 1)[0]
        response = json.loads(line.decode("ascii"), parse_constant=_reject_closed_constant)
    except (OSError, ValueError, UnicodeDecodeError):
        raise FixtureError("local-control-protocol") from None
    finally:
        sock.close()
    _validate_control_response(response, command, entry_order)
    # The response must bind the EXACT requested identity before the
    # result is exposed (a different valid 32-hex run id is a
    # protocol violation, not a valid answer to this command).
    if response["run_id"] != run_id:
        raise FixtureError("local-control-protocol")
    return response


# -- protected generated env file ---------------------------------------------------
def _synthetic_credential(run_token: str) -> str:
    return "slaif-synthetic-" + hashlib.sha256(run_token.encode("ascii")).hexdigest()[:32]


def create_env_file(env_dir: Path, run_token: str) -> tuple[Path, str]:
    """Create the protected generated env file: exactly the two
    synthetic variables (CODEX_HOME + the generated fake-provider
    value derived from the run token), 0600 under the owned 0700 env
    directory, O_EXCL (never adopted/overwritten), no links.  The
    VALUES are never printed or placed on any argv — the file PATH
    alone is bound for the single docker exec --env-file use."""
    if not re.fullmatch(r"[0-9a-f]{32}", run_token):
        raise FixtureError("local-run-token-invalid")
    st = os.lstat(env_dir)
    if (
        not stat.S_ISDIR(st.st_mode)
        or stat.S_IMODE(st.st_mode) != stat.S_IRWXU
        or st.st_uid != os.getuid()
    ):
        raise FixtureError("local-env-untrusted")
    path = env_dir / ENV_FILE_NAME
    if path.exists() or path.is_symlink():
        raise FixtureError("local-env-exists")
    content = (
        f"CODEX_HOME={ci.fixture_standin.SUBJ_CODEX_HOME}\n"
        f"{ENV_FILE_KEYS[1]}={_synthetic_credential(run_token)}\n"
    ).encode("ascii")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as handle:
        handle.write(content)
    st = path.lstat()
    if (
        not stat.S_ISREG(st.st_mode)
        or stat.S_IMODE(st.st_mode) != 0o600
        or st.st_uid != os.getuid()
    ):
        raise FixtureError("local-env-untrusted")
    return path, hashlib.sha256(content).hexdigest()


def remove_env_file(path: Path | None) -> None:
    """Idempotent exact env-file removal on EVERY success/failure/
    cancel path: the exact path must be a 0600 regular file owned by
    this uid before unlink; a vanished file is a successful no-op,
    anything else is a fixed failure (never a blind unlink)."""
    if path is None:
        return
    try:
        st = os.lstat(path)
    except FileNotFoundError:
        return
    if (
        not stat.S_ISREG(st.st_mode)
        or stat.S_IMODE(st.st_mode) != 0o600
        or st.st_uid != os.getuid()
    ):
        raise FixtureError("local-env-untrusted")
    os.unlink(path)
    if os.path.lexists(str(path)):
        raise FixtureError("local-env-remove-failed")


def validate_attach_plan(plan: dict) -> None:
    """Closed validation of the PURE inert attach plan: the Codex
    argv is EXACTLY ``codex --yolo --profile early-beta`` (no
    additional flags/wrapper/resume/exec), the subject workspace
    workdir and the two env-file keys are exact, and the plan is
    recorded as never executed."""
    if set(plan) != {"argv", "workdir", "env_file_keys", "executed"}:
        raise FixtureError("local-attach-plan-invalid")
    if tuple(plan["argv"]) != ("codex", "--yolo", "--profile", "early-beta"):
        raise FixtureError("local-attach-plan-invalid")
    if plan["workdir"] != ci.fixture_standin.SUBJ_WORKDIR:
        raise FixtureError("local-attach-plan-invalid")
    if tuple(plan["env_file_keys"]) != ENV_FILE_KEYS:
        raise FixtureError("local-attach-plan-invalid")
    if plan["executed"] is not False:
        raise FixtureError("local-attach-plan-invalid")


# -- closed ledger facts -------------------------------------------------------------
def _ledger_facts(ledger) -> dict[str, int]:
    return {
        "docker_admissions": ledger.admissions,
        "docker_refusals": ledger.refusals,
        "bytes_drained": ledger.bytes_drained,
        "bytes_retained": ledger.bytes_retained,
        "api_requests": ledger.api_requests,
        "api_attempts": ledger.api_attempts,
        "requests_admitted": ledger.requests_admitted,
        "requests_refused": ledger.requests_refused,
        "healthz_attempts": ledger.healthz_attempts,
    }


def _runner_facts() -> dict[str, str]:
    uname = platform.uname()
    return {
        "runner_kernel": uname.release,
        "runner_arch": uname.machine,
        "runner_python": platform.python_version(),
    }


def _require_absent(executor, container_id: str) -> None:
    """Positive-before / negative-after: the exact registered CID
    must be verified absent (a failed query is never absence)."""
    if ci._ps_filter(executor, f"id={container_id}") != "absent":
        raise FixtureError("local-cleanup-unverified")


# -- section 2: verified local Docker endpoint binding -------------------------
# The local rehearsal may reach ONLY this host's Docker daemon.  The
# narrow supported local endpoint is the documented default unix
# socket, verified read-only (lstat: it must exist as a socket file,
# never connected).  EVERY run Docker child inherits a FROZEN
# once-per-owner environment in which DOCKER_HOST is pinned to that
# verified socket and the overriding context selection is removed:
# a stored currentContext, or later HOME/DOCKER_CONFIG/DOCKER_CONTEXT
# drift, cannot redirect a later action.  An explicit remote
# selection refuses BEFORE any mutation, and no endpoint value (URL,
# credential, or context name) is ever echoed.
_LOCAL_ENDPOINT_SELECTION_VARS = ("DOCKER_HOST", "DOCKER_CONTEXT")
_LOCAL_DOCKER_SOCKET = "/var/run/docker.sock"
_LOCAL_DOCKER_ENDPOINT_PIN = "unix://" + _LOCAL_DOCKER_SOCKET


def _assert_local_endpoint_selection(env: Mapping[str, str]) -> None:
    """Refuse a caller-selected remote endpoint before any mutation.

    A non-blank ``DOCKER_HOST`` selects some endpoint this module
    must not silently override; a ``DOCKER_CONTEXT`` other than the
    daemon's own ``default`` (blank counts as unset) selects a
    foreign context.  The selected value is never echoed into the
    closed failure reason."""
    if env.get("DOCKER_HOST", "").strip():
        raise FixtureError("local-docker-endpoint")
    if env.get("DOCKER_CONTEXT", "") not in ("", "default"):
        raise FixtureError("local-docker-endpoint")


def _verify_local_socket(path: str) -> None:
    """Read-only proof that the narrow local unix socket EXISTS as a
    socket file: lstat only (no connect, no Docker call, no global
    config or daemon change).  A missing, foreign, or non-socket
    state is a closed refusal."""
    try:
        st = os.lstat(path)
    except OSError:
        raise FixtureError("local-docker-endpoint") from None
    if not stat.S_ISSOCK(st.st_mode):
        raise FixtureError("local-docker-endpoint")


def _local_bound_executor() -> Callable[[list[str], float], ci.ExecResult]:
    """The owner's default executor: the reviewed real executor with
    a child environment snapshotted ONCE when the factory runs (once
    per owner): the overriding context selection is removed and
    DOCKER_HOST is pinned to the verified local socket, so a later
    environment/config/context change cannot reach a later child.
    Every child inherits the SAME frozen mapping (values never
    printed)."""
    env = {k: v for k, v in os.environ.items() if k != "DOCKER_CONTEXT"}
    env["DOCKER_HOST"] = _LOCAL_DOCKER_ENDPOINT_PIN

    def bound(argv: list[str], timeout: float) -> ci.ExecResult:
        return ci._real_execute(argv, timeout, env=env)

    return bound


@dataclass(frozen=True)
class OwnerIdentityContext:
    """The ONE immutable owner-UID run context (017-aa).

    Frozen at construction AFTER the bound run identity is adopted
    and BEFORE any external fixture work, from the owner's OWN
    collection/derivation through the Z production collector and
    closed codec (a caller-supplied description, fingerprint or
    ready flag can never mint it).  It carries the canonical
    profile description's fingerprint, the frozen INDEPENDENT
    subject identity, the closed runtime profile view, and the
    ORIGINAL verified order/head/run/admission binding.  It is
    revalidated at actual use (bounded current-ID coherence read)
    and may be COMPARED, never rebased or silently re-frozen after
    drift.
    """

    profile: rprofile.RuntimeProfile
    fingerprint: str
    subject_uid: int
    subject_gid: int
    subject_groups: tuple[int, ...]
    exec_user: str
    order_id: str
    bind_head: str
    run_id: str
    profile_data_sha256: str


class LocalFixtureOwner:
    """The ONE long-lived Python fixture owner (the supervisor): a
    single non-Codex owning actor with ONE RAM run context.  It owns
    every Docker operation (through the closed guarded executor),
    the exact resource registry (CIDs registered BEFORE start, image
    id, build intent, env file), the single absolute END anchor, the
    cumulative ledger, the one cleanup grace and the final evidence.
    The thin CLI caller drives the bounded protected lifecycle
    prepare / observe / rehearse / finish / abort; a caller death
    cannot kill or reset the owner (the owner converges its own
    exact-owned cleanup on its own remaining budgets, and its own
    SIGTERM/KeyboardInterrupt converge through the same path).

    There is deliberately NO second watchdog process, NO second
    fresh deadline or ledger, and NO host PID signalling at all
    (UID equality or filename resemblance is never an ownership
    proof, and a recycled PID must never be reachable from this
    code): termination of fixture resources is by docker on the
    exact registered CID only."""

    def __init__(
        self,
        repo,
        work,
        evidence_out,
        bind_head: str,
        control_dir,
        *,
        git_runner: Callable[[list[str]], bytes] | None = None,
        executor=None,
        deadline_offset: float = 0.0,
        binding: object = None,
        identity_reader: fidentity.IdentityReader | None = None,
        proc_root: Path | None = None,
    ) -> None:
        if os.environ.get("GITHUB_ACTIONS") == "true":
            raise FixtureError("local-hosted-env")
        if (
            not isinstance(deadline_offset, (int, float))
            or isinstance(deadline_offset, bool)
            or deadline_offset < 0
            or deadline_offset >= ci.TOTAL_ANCHOR_SECONDS
        ):
            raise FixtureError("local-deadline-offset-invalid")
        self.repo = Path(repo)
        self.work = Path(work)
        self.evidence_out = Path(evidence_out)
        # The protected control root (fresh 0700, created by the
        # owner at serve start, OUTSIDE the disposable work root):
        # the bounded command socket, the protected state/abort
        # files — the exact recovery registry/ledger that survives
        # the destroyed scratch when cleanup remains unverified.
        self.control_dir = Path(control_dir)
        self.control_dir_owned = False
        # The /proc root for the owned-lifetime frame reads
        # (production: the real /proc; the faithful narrow fake
        # seam for tests — the SAME bounded reader law applies
        # to both).
        self._proc_root = Path(proc_root) if proc_root is not None else Path("/proc")
        self._control_socket: socket.socket | None = None
        self._converged = False
        self._exit_code = 1
        self._outcome: str | None = None
        self._evidence_sha: str | None = None
        # The SAME-owner protected-writer retention receipt
        # (RAM only): initialized false and set only after
        # the protected owner writer returns verified
        # success — independent of the pass/cleanup
        # outcome (the native composition's owner-FIRST
        # publication gate reads this measured fact, never
        # a precomputed digest or a merely existing file).
        self._evidence_retained: bool = False
        self._recovery_state_retained = False
        # Own-process termination handling from the first bounded
        # query: SIGTERM and SIGINT both converge through the same
        # exact-owned cleanup (never a new experiment).
        signal.signal(signal.SIGTERM, self._termination_handler)
        # Authority selection: the S default (no binding) keeps
        # the historical order-bound opt-in UNCHANGED.  A
        # verified OrderRunBinding selects the authority of its
        # OWN order: the 017-s binding keeps the historical S
        # opt-in unchanged, and a NEW-order binding selects the
        # distinct native authority path — the complete
        # frozen-context revalidation re-verifies the ACTUAL
        # repository context READ-ONLY against the ORIGINAL
        # immutable binding (literal head, clean worktree,
        # committed and disk active, repository identity,
        # unique committed order file and its bytes): nothing
        # is written, no authority is minted, no second run
        # identity is minted or adopted, no active/S constant
        # changes, no runtime-global monkeypatch, no second
        # owner — a context that drifted between admission and
        # construction is a closed refusal before adoption.  A
        # bound run must carry a LIVE bound admission in that
        # order's stable namespace BEFORE adoption — a bare
        # caller run id can never skip or bypass the order's
        # one-attempt law (an exhausted, missing or foreign
        # admission is a closed refusal).
        self._native_binding: oap_binding.OrderRunBinding | None = None
        if binding is None:
            self.optin = verify_local_optin(self.repo, bind_head, git_runner)
        elif isinstance(binding, oap_binding.OrderRunBinding):
            # The frozen binding is the source of truth: a
            # contradictory bind_head argument is a closed
            # refusal BEFORE any adoption (the revalidation
            # compares the actual context to the ORIGINAL
            # binding, never to the argument).
            if bind_head != binding.source_head:
                raise FixtureError("local-binding-invalid")
            record = oap_binding.read_admission_record(self.repo, binding.order_id)
            live = any(
                entry["run_id"] == binding.run_id and entry["status"] == "running"
                for entry in record["attempts"]
            )
            if not live:
                raise FixtureError("local-bounded-admission-missing")
            if binding.order_id == oap_binding._S_ORDER_ID:
                self.optin = verify_local_optin(self.repo, bind_head, git_runner)
            else:
                # order 017-w section 2: the complete
                # frozen-context revalidation compares the
                # ACTUAL repository context READ-ONLY with
                # the ORIGINAL immutable binding (literal
                # head, clean worktree, disk and committed
                # active, repository identity, the unique
                # committed order file and its bytes) — not
                # a fresh resolution whose result would be
                # discarded.  A drifted context between
                # admission and owner construction is a
                # closed refusal before any owner adoption
                # (the composition closes the already-won
                # attempt honestly; no second run identity
                # is minted or adopted).
                oap_binding._revalidate_repo_context(
                    git_runner if git_runner is not None else oap_binding._git_default,
                    self.repo,
                    binding.order_id,
                    binding,
                )
                self.optin = {
                    "order": binding.order_id,
                    "bind_head": bind_head,
                    "head": bind_head,
                    "order_sha256": binding.order_sha256,
                }
                self._native_binding = binding
        else:
            raise FixtureError("local-binding-invalid")
        # Second layer of the one-attempt law (defense in depth):
        # the retained evidence destination must not pre-exist.
        if self.evidence_out.exists() or self.evidence_out.is_symlink():
            raise FixtureError("local-rehearsal-exists")
        validate_attach_plan(ATTACH_PLAN)
        if executor is None:
            executor = _local_bound_executor()
        self._executor = executor
        # Run identity: the historical S default mints a fresh
        # 32-hex run id HERE and admits in the stable 017-s
        # namespace before any external mutation.  A BOUNDED
        # composition (order 017-v) passes the verified
        # immutable OrderRunBinding instead: the owner adopts
        # the binding's minted run identity (the ONE shared
        # identity with the public native workflow) — the live
        # bound admission was verified above, before any
        # mutation.  No second mint, no second admission.
        if binding is None:
            self.run_id = uuid.uuid4().hex
            # The experiment boundary: the STABLE admission
            # record is written here, before any external
            # mutation.  A read-only opt-in refusal (above)
            # admitted nothing.
            _admit_attempt(self.repo, self.optin["bind_head"], self.run_id)
        else:
            self.run_id = binding.run_id
        # owner-UID branch (the canonical future sealed entries;
        # 017-aa AB and 017-ac AD): AFTER the bound run identity is adopted and
        # BEFORE any external fixture work, the owner collects the
        # host owner IDs through the ONE raw read seam (the
        # faithful narrow fake seam for tests; production is the
        # direct bounded OS read), derives the inert description
        # with Z production code, and freezes the immutable owner
        # context.  A caller-supplied description, fingerprint or
        # ready flag is NEVER accepted — only this own
        # collection/derivation feeds the context.  No process is
        # started merely to collect host IDs.  Any failure here is
        # a closed refusal BEFORE any mutation; the caller/serve
        # composition closes the SAME already-won attempt
        # honestly (no second mint, no adopted journal, no
        # re-resolution).
        self.identity_reader: fidentity.IdentityReader | None = identity_reader
        self._owner_context: OwnerIdentityContext | None = None
        # ALL canonical owner-UID sealed entries (AB, the
        # future AD, the future AF and the future AH) select
        # ONLY the owner-UID profile through the closed entry
        # mapping; the original entries never collect (their
        # owner context stays None and every original
        # record/meaning stays byte-for-byte)
        if binding is not None and binding.order_id in (
            rprofile.AB_ORDER_ID,
            rprofile.AD_ORDER_ID,
            rprofile.AF_ORDER_ID,
            rprofile.AH_ORDER_ID,
            rprofile.AJ_ORDER_ID,
        ):
            # The fixed canonical 017-ad and 017-af entries
            # resolve ONLY at their unique committed order paths
            # (the resolver applies the same closed law): a
            # directly-constructed binding carrying the entry's
            # order id at a foreign path can never adopt the
            # frozen owner context — a closed refusal BEFORE any
            # collection (the generic original orders keep the
            # exact historical law).
            if (
                binding.order_id == rprofile.AD_ORDER_ID
                and binding.order_path != rprofile.AD_ORDER_PATH
            ):
                raise FixtureError("local-ad-order-path-mismatch")
            if (
                binding.order_id == rprofile.AF_ORDER_ID
                and binding.order_path != rprofile.AF_ORDER_PATH
            ):
                raise FixtureError("local-af-order-path-mismatch")
            if (
                binding.order_id == rprofile.AH_ORDER_ID
                and binding.order_path != rprofile.AH_ORDER_PATH
            ):
                raise FixtureError("local-ah-order-path-mismatch")
            if (
                binding.order_id == rprofile.AJ_ORDER_ID
                and binding.order_path != rprofile.AJ_ORDER_PATH
            ):
                raise FixtureError("local-aj-order-path-mismatch")
            reader = (
                identity_reader
                if identity_reader is not None
                else fidentity._default_identity_reader
            )
            outcome = fidentity.collect_host_owner_ids(reader)
            if not outcome.ok:
                raise FixtureError(f"local-identity-{outcome.reason}")
            try:
                description = fidentity.derive_owner_uid_identity(outcome.ids)
            except fidentity.FixtureIdentityError as exc:
                raise FixtureError(f"local-identity-{exc.reason}") from None
            profile = rprofile.owner_runtime_profile(description)
            self._owner_context = OwnerIdentityContext(
                profile=profile,
                fingerprint=fidentity.fingerprint_description(description),
                subject_uid=description.subject_uid,
                subject_gid=description.subject_gid,
                subject_groups=description.subject_groups,
                exec_user=profile.exec_user,
                order_id=binding.order_id,
                bind_head=bind_head,
                run_id=self.run_id,
                profile_data_sha256=hashlib.sha256(profile.profile_data).hexdigest(),
            )
        self.run_token = uuid.uuid4().hex
        # ONE absolute END anchor (start + 1800 s) and ONE
        # cumulative host ledger over every phase and error.
        self.budgets = model.FixtureBudgets()
        self.deadline = ci._RunDeadline(
            time.monotonic() + ci.TOTAL_ANCHOR_SECONDS - deadline_offset
        )
        self.ledger = ci._RunLedger(self.budgets)
        if self._owner_context is None:
            self.guarded = ci._guarded_execute(self._executor, self.deadline, self.ledger)
        else:
            # The OWNER-SCOPED guarded allowlist: the SAME closed
            # factories bound to the frozen profile (its exact
            # independent exec user, the closed build-arg form and
            # the owner tmpfs spec set); the ONE new native-
            # specific operation (the AF devpts probe) is admitted
            # for the canonical 017-af entry ONLY, selected from
            # this owner's OWN bound order id; the original
            # callers keep the byte-for-byte original matcher
            # tuple.  No global mutable identity binding.
            self.guarded = ci._guarded_execute(
                self._executor,
                self.deadline,
                self.ledger,
                matchers=ci._owner_argv_matchers(
                    self._owner_context.profile, self._owner_context.order_id
                ),
            )
        # -- run context (one RAM context) --
        self.phase = "start"
        self.status = "running"
        self.created: list[str] = []
        self.target_cid: str | None = None
        # The 017-x detached capability start: ONE subject start in
        # this run INCLUDING failed starts (the attempt latch is set
        # BEFORE the dispatch, so a failed start consumes the one
        # start and refuses any retry); the issued marker is the
        # run's own 32-hex token (never a caller value).
        self.hold_start_attempted = False
        self.hold_token: str | None = None
        # The exact fresh create name/ownership intent, persisted
        # in the protected state BEFORE docker create (the create/
        # response gap is recoverable data, never an adopted
        # foreign resource).
        self.create_intent: str | None = None
        self.image_id: str | None = None
        self.image_removed = False
        self.build_attempted = False
        self.env_file: Path | None = None
        self.env_file_digest: str | None = None
        self.cleanup_failures: list[str] = []
        self.sentinel: subprocess.Popen[bytes] | None = None
        self.sentinel_reaped = False
        self.sentinel_file: Path | None = None
        self.sentinel_file_digest: str | None = None
        self.sentinel_survived = False
        self.listener: socket.socket | None = None
        self.parent_pid: int | None = None
        self.parent_port: int | None = None
        self.parent_ns: dict[str, str] | None = None
        self.engine_version = ""
        self.runtime_name = ""
        self.runtime_version = ""
        self.artifact: dict[str, object] | None = None
        self.env_base: dict[str, str] = {}
        self.confinement_facts: dict[str, str] | None = None
        self.subject_facts: dict[str, object] | None = None
        self.pty_facts: dict[str, object] | None = None
        self.prepared: dict[str, object] | None = None
        self.consumed: dict[str, object] | None = None
        # The ACTUAL non-consuming controller observation taken at
        # finish (measured, never invented): the held-instance
        # finish path revalidates the export against THIS closed
        # observation instead of hard-coded Python-consume facts.
        self.finish_observed: dict[str, object] | None = None
        self.finish_position: int | None = None
        self.finish_ledger_requests: int | None = None
        self.export_payload: bytes | None = None
        self.export_sha = ""
        self.descendants_before = 0
        # The SEPARATELY STORED measured teardown facts (the
        # verification itself is unchanged): the 017-t
        # native-owner preparation adapter reads these
        # measured values — it never re-queries the
        # platform.
        self.teardown_container_absent: bool | None = None
        self.teardown_descendants_after: int | None = None
        # The owner-UID (AB) owned-lifetime registry: the exact
        # registered CID's member PID + birth(start_time) + uid
        # measured BEFORE removal (the same exact-CID top
        # channel, read-only), and the tri-stated post-removal
        # verification result.  This is the exact-CID + owned
        # PID/birth lifetime proof the order requires for the
        # new profile — NOT a UID scan and NOT a count inference.
        # The original 21002 path never populates it.
        self.owned_members_before: tuple[tuple[int, int, int], ...] | None = None
        self.owned_members_after: tuple[tuple[int, str], ...] | None = None
        # NOTE (017-t): the run's native_started/native_ready
        # facts are NOT owner state — the owner never launches
        # or measures a native subject.  They are measured by
        # the PUBLIC native-handoff workflow's subject
        # collector (the retained pre-teardown identity) and
        # reach the native-owner producer through that
        # measured receipt, never through a caller flag write.
        # The historical S scope's closed whole-run
        # native_started/native_ready flags live in its own
        # evidence record and keep their original meaning.
        self.phases_completed: set[str] = set()
        self.work_root_owned = False
        self.state_path: Path | None = None
        self.abort_path: Path | None = None
        self._context_dir: Path | None = None
        self._artifact_dir: Path | None = None
        self._env_dir: Path | None = None
        self._abort_by_caller = False
        self.failure_reason = ""
        self.failure_stage = "start"

    def _revalidate_identity_context(self) -> None:
        """Re-measure the CURRENT host owner identity through the
        SAME read seam and compare it to the FROZEN owner context
        (the bounded current-ID coherence read at actual use): it
        may COMPARE, but never rebase or silently re-freeze after
        drift.  An unreadable, failed or drifted context is a
        closed refusal — the composition closes the SAME already-
        won attempt honestly (no fresh collection is adopted)."""
        # Strict read: the real constructor ALWAYS initializes
        # ``_owner_context`` (``None`` for the original form), so
        # a missing attribute is a defective object, not a
        # no-owner signal — the partial-object test seam must set
        # the faithful original default explicitly.
        ctx = self._owner_context
        if ctx is None:
            # The closed fail-closed law at every identity-bound
            # use site: a canonical 017-aj bound owner whose
            # frozen context is missing is a closed refusal —
            # never a fall-through to the original profile
            # (the original form, no owner context, keeps its
            # legitimate historical default byte-for-byte).
            if self.optin["order"] == AJ_ORDER_ID:
                raise FixtureError("local-aj-context-unmeasured")
            return
        reader = (
            self.identity_reader
            if self.identity_reader is not None
            else fidentity._default_identity_reader
        )
        outcome = fidentity.collect_host_owner_ids(reader)
        if not outcome.ok:
            raise FixtureError(f"local-identity-{outcome.reason}")
        try:
            current = fidentity.derive_owner_uid_identity(outcome.ids)
        except fidentity.FixtureIdentityError:
            raise FixtureError("local-identity-drift") from None
        if fidentity.fingerprint_description(current) != ctx.fingerprint:
            raise FixtureError("local-identity-drift")

    @staticmethod
    def _termination_handler(signum: int, frame) -> None:
        raise KeyboardInterrupt("slaif-017s-owner-terminated")

    # -- protected workspace ---------------------------------------------------
    def _init_workspace(self) -> None:
        self.phase = "work-root"
        ci._create_work_root(self.work)
        self.work_root_owned = True
        self._context_dir = ci._owned_subdir(self.work, "context")
        self._artifact_dir = ci._owned_subdir(self.work, "artifact")
        # The protected state/abort files live in the CONTROL root
        # (created by _init_control, outside this disposable root):
        # the recovery registry/ledger must survive the destroyed
        # scratch when cleanup remains unverified.
        self._env_dir = ci._owned_subdir(self.work, "env")
        sentinels = ci._owned_subdir(self.work, "sentinels")
        self.sentinel_file = sentinels / "parent-sentinel-file"
        self._publish_state()

    def _state_dict(self) -> dict:
        state = {
            "record": STATE_SCHEMA,
            "run_id": self.run_id,
            "pid": os.getpid(),
            "end_anchor": self.deadline.anchor,
            "phase": self.phase,
            "status": self.status,
            "containers": list(self.created),
            "create_intent": self.create_intent,
            "image_id": self.image_id,
            "build_attempted": self.build_attempted,
            "env_file": str(self.env_file) if self.env_file is not None else None,
            "ledger": _ledger_facts(self.ledger),
        }
        # The AB-only frozen owner identity (017-aa): the SAME
        # closed substructure the AB owner-run evidence and the
        # AB driver record carry — collected and derived by THIS
        # owner (never caller-authored), published so the sealed
        # driver can adopt the frozen subject expectation from
        # the owner's own protected state.  The original form
        # (no owner context) keeps the 12-key state byte-for-byte.
        if self._owner_context is not None:
            ctx = self._owner_context
            # The DISTINCT identity-bearing state tag of THIS
            # entry's OWN canonical form (the AB, AD or AF tag —
            # the v1 tag is never widened to the new profile
            # record) and the full ORIGINAL verified order/head/
            # run binding frozen with the context (tag/
            # fingerprint alone are integrity, never owner-ID
            # origin).  Each entry names its OWN tag explicitly:
            # an unexpected order id in a frozen context is an
            # internal invariant violation, never a silent
            # relabel to another entry's form.
            if ctx.order_id == AB_ORDER_ID:
                state["record"] = AB_STATE_SCHEMA
            elif ctx.order_id == AD_ORDER_ID:
                state["record"] = AD_STATE_SCHEMA
            elif ctx.order_id == AF_ORDER_ID:
                state["record"] = AF_STATE_SCHEMA
            elif ctx.order_id == AH_ORDER_ID:
                state["record"] = AH_STATE_SCHEMA
            elif ctx.order_id == AJ_ORDER_ID:
                state["record"] = AJ_STATE_SCHEMA
            else:
                raise FixtureError("internal")
            state["order"] = ctx.order_id
            state["bind_head"] = ctx.bind_head
            state["identity"] = {
                "profile": ctx.profile.profile,
                "fingerprint": ctx.fingerprint,
                "subject_uid": ctx.subject_uid,
                "subject_gid": ctx.subject_gid,
                "subject_groups": list(ctx.subject_groups),
                "profile_data_sha256": ctx.profile_data_sha256,
            }
        return state

    def _publish_state(self, status: str | None = None) -> None:
        """Best-effort phase-boundary publication (monitoring
        surface): a write failure after the mutation already
        happened must never mask the in-flight primary; the
        registry in RAM remains the authoritative cleanup source
        for this owner.  Pre-mutation registry publication is
        REQUIRED and gates the external mutation (see
        ``_publish_state_required``)."""
        if self.state_path is None:
            return
        if status is not None:
            self.status = status
        try:
            _write_state(self.state_path, self._state_dict(), ab=self._owner_context is not None)
        except FixtureError:
            pass

    def _publish_state_required(self, status: str | None = None) -> None:
        """REQUIRED registry publication BEFORE an external
        mutation (build intent, CID before start): the protected
        state must demonstrably carry the exact ownership, or the
        mutation is refused fail-closed.  A failure here becomes
        the primary (preserved through the cleanup umbrella, which
        also removes any container created before the failure)."""
        if self.state_path is None:
            raise FixtureError("local-state-missing")
        if status is not None:
            self.status = status
        _write_state(self.state_path, self._state_dict(), ab=self._owner_context is not None)

    def _cid_registered(self, cid: str) -> None:
        """The shared helper's registration callback: the exact
        fresh CID is ALREADY registered in the owner registry
        (before this callback and before any start).  This performs
        the REQUIRED protected-state publication with the lifecycle
        status UNCHANGED (the callback argument is the CID, never a
        status); a failure here propagates through the shared
        helper and forbids the start, with the container already
        registered for the umbrella."""
        if not self.created or self.created[-1] != cid:
            raise FixtureError("local-state-missing")
        self._publish_state_required()

    def _abort_check(self) -> None:
        if self._abort_by_caller:
            raise FixtureError("local-abort-requested")
        if self.abort_path is not None and _abort_requested(self.abort_path, self.run_id):
            raise FixtureError("local-abort-requested")

    def _check_sentinel(self) -> None:
        """Fail-fast containment fact: the unrelated parent sentinel
        must still be alive at every phase boundary."""
        if self.sentinel is not None and self.sentinel.poll() is not None:
            raise FixtureError("sentinel-process-died")

    def _verify_local_daemon_host(self) -> None:
        """Read-only section-2 proof BEFORE any mutation: the narrow
        local unix socket exists (lstat only, never connected) and
        the daemon reachable through the PINNED bound executor
        declares a Name equal to this host's hostname — corroboration
        of the pin (the explicit DOCKER_HOST pin, not the name, is
        the endpoint binding).  A failed query or a foreign or blank
        name is a closed refusal; the comparison is in memory only
        and the daemon name is never recorded or printed."""
        _verify_local_socket(_LOCAL_DOCKER_SOCKET)
        result = self.guarded(["docker", "info", "--format", "{{.Name}}"], ci._QUERY_TIMEOUT)
        if result.returncode != 0 or not result.output:
            raise FixtureError("local-docker-endpoint")
        if result.output.decode("ascii", "replace").strip() != socket.gethostname():
            raise FixtureError("local-docker-endpoint")

    def _phase_done(self, phase: str) -> None:
        self._check_sentinel()
        self.phases_completed.add(phase)
        self._publish_state()

    # -- lifecycle: prepare ------------------------------------------------------
    def prepare(self) -> None:
        """PREPARE the exact target CID (held, unconsumed): read-only
        discovery, pre-existing tag collision probe (never adopt or
        delete), public pinned artifact, allowlisted build context,
        pull/build with the exact fresh intent persisted BEFORE the
        build, owned parent sentinels, then the target: registered
        in the protected state BEFORE start, inspected and measured
        THERE, PTY/env-handoff verified with zero wire, and observed
        non-consuming (closed actual controller state)."""
        self._abort_check()
        # Section 2, BEFORE any external mutation (the workspace
        # root is created after this): refuse a caller-selected
        # remote endpoint and prove the effective daemon is THIS
        # host with the read-only daemon-name query.
        _assert_local_endpoint_selection(os.environ)
        self._verify_local_daemon_host()
        # The disposable scratch root is created HERE, inside the
        # lifecycle boundary: a partial workspace failure converges
        # through the same exact-owned cleanup (work root destroyed
        # when owned, registry published before any mutation).
        self._init_workspace()
        self.phase = "preflight"
        self.engine_version, self.runtime_name, self.runtime_version = ci._engine_preflight(
            self.guarded
        )
        self._phase_done("preflight")

        self.phase = "collision"
        probe = self.guarded(
            ["docker", "inspect", "--format", "{{.Id}}", ci.IMAGE_NAME], ci._QUERY_TIMEOUT
        )
        if probe.returncode == 0:
            raise FixtureError("image-collision")
        if not ci._NO_SUCH_OBJECT_RE.search(probe.output.decode("ascii", "replace")):
            raise FixtureError("image-collision-unverified")
        self._phase_done("collision")

        self.phase = "artifact"
        self.artifact = ci.fetch_public_artifact(self._artifact_dir, self.deadline)
        self._phase_done("artifact")

        self.phase = "build-context"
        self._revalidate_identity_context()
        if self._owner_context is None:
            dockerfile_bytes = ci.verify_dockerfile_base(self.repo)
            ci.prepare_build_context(
                self.repo,
                self._artifact_dir,
                self._context_dir,
                dockerfile_bytes,
                self.artifact,
            )
        else:
            # The owner-UID variant: the EXPLICIT owner Dockerfile
            # (the original stays byte-for-byte the original) and
            # the frozen profile DATA bytes (the closed canonical
            # Z record) plus the inert identity module in the
            # build context; every copy re-hashed AFTER writing.
            dockerfile_bytes = ci.verify_dockerfile_base(self.repo, rprofile.OWNER_DOCKERFILE_NAME)
            ci.prepare_build_context(
                self.repo,
                self._artifact_dir,
                self._context_dir,
                dockerfile_bytes,
                self.artifact,
                profile_data=self._owner_context.profile.profile_data,
            )
        self._phase_done("build-context")

        self.phase = "pull"
        result = self.guarded(["docker", "pull", ci.PINNED_BASE], ci.PULL_TIMEOUT)
        if result.returncode != 0:
            raise FixtureError("pull-failed")
        self._phase_done("pull")

        self.phase = "build"
        self.build_attempted = True
        # Persist the exact fresh create/build intent BEFORE the
        # external mutation (an interrupted build is recoverable
        # ownership data, never an adopted foreign resource); the
        # publication is REQUIRED and gates the build.
        self._publish_state_required()
        if self._context_dir is None:
            raise FixtureError("internal")
        result = self.guarded(
            self._build_argv(),
            ci.BUILD_TIMEOUT,
        )
        if result.returncode != 0:
            raise FixtureError("build-failed")
        self.image_id = self._discover_image_id()
        self._phase_done("build")

        self.phase = "sentinels"
        self._spawn_sentinels()
        self._phase_done("sentinels")

        self.phase = "prepare-target"
        self._prepare_target()
        self._phase_done("prepare-target")

        self.phase = "prepared"
        self._publish_state()

    def _build_argv(self) -> list[str]:
        """The closed build argv: the historical byte-for-byte
        original for the original profile, and the owner-scoped
        closed form (the SAME base/tag plus the EXACT frozen
        profile build-arg tuple) for the owner-UID variant."""
        argv = ["docker", "build", "-t", ci.IMAGE_NAME]
        if self._owner_context is not None:
            argv += list(self._owner_context.profile.build_args)
        argv.append(str(self._context_dir))
        return argv

    def _discover_image_id(self) -> str:
        image_id = (
            ci._query(self.guarded, ["docker", "inspect", "--format", "{{.Id}}", ci.IMAGE_NAME])
            .decode("ascii", "replace")
            .strip()
        )
        if not ci._IMAGE_ID_RE.fullmatch(image_id):
            raise FixtureError("build-failed")
        return image_id

    def _spawn_sentinels(self) -> None:
        sentinel_file = self.sentinel_file
        if sentinel_file is None:
            raise FixtureError("internal")
        sentinel_fd = os.open(sentinel_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(sentinel_fd, "wb") as handle:
            handle.write(b"slaif-synthetic-parent-sentinel-017s\n")
        self.sentinel_file_digest = ci.sha256_file(sentinel_file)
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.bind(("127.0.0.1", 0))
        self.listener.listen(1)
        self.parent_port = self.listener.getsockname()[1]
        self.parent_pid = os.getpid()
        self.parent_ns = ci.parent_namespace_ids()
        self.sentinel = ci._spawn_parent_sentinel()

    def _prepare_target(self) -> None:
        env_base = {
            "SLAIF_FIXTURE_DEADLINE_ABS": repr(self.deadline.anchor),
            "SLAIF_FIXTURE_DEADLINE": str(int(ci.TOTAL_ANCHOR_SECONDS)),
            "SLAIF_FIXTURE_PORT": str(ci.CONTROLLER_PORT),
        }
        self.env_base = env_base
        ctx = self._owner_context
        # The closed fail-closed law at the scenario SELECTION
        # site: a canonical 017-aj bound owner whose frozen
        # context is missing is a closed refusal BEFORE the
        # fixture create — never a fall-through to the legacy
        # diagnostic scenario or the original profile (the
        # original form keeps its legitimate historical
        # default byte-for-byte).
        if ctx is None and self.optin["order"] == AJ_ORDER_ID:
            raise FixtureError("local-aj-context-unmeasured")
        env = dict(env_base)
        env["SLAIF_FIXTURE_MODE"] = "main"
        # The CLOSED scenario is selected BEFORE startup by the
        # owner's OWN frozen entry (the verified binding is the
        # sole authority; ambient env / HTTP / caller-ready values
        # never select or redefine it).
        env["SLAIF_FIXTURE_SCENARIO"] = _entry_scenario(ctx.order_id if ctx is not None else None)
        env["SLAIF_FIXTURE_AUTH_TOKEN"] = self.run_token
        # The protected generated env file (0600 under the owned
        # 0700 env directory): the values never appear on argv.
        if self._env_dir is None:
            raise FixtureError("internal")
        self.env_file, self.env_file_digest = create_env_file(self._env_dir, self.run_token)
        ci.bind_env_files({str(self.env_file)})
        self._publish_state_required()
        # The exact fresh create NAME intent is persisted in the
        # protected state BEFORE docker create, and the exact fresh
        # CID registration is persisted BEFORE any start (the shared
        # helper calls the callbacks at those exact points; both
        # publish required state with the lifecycle status
        # unchanged, and a failure forbids the mutation).
        cid = ci.prepare_container(
            self.guarded,
            0,
            "prepared",
            env,
            self.created,
            self.ledger,
            prefix="017s",
            on_registered=self._cid_registered,
            on_intent=self._create_intent_published,
            tmpfs_specs=ci.owner_tmpfs_specs(ctx.profile) if ctx is not None else None,
        )
        self.target_cid = cid
        self._publish_state()
        # NON-CONSUMING confinement inspection of THIS exact CID.
        self.confinement_facts = ci.measure_controller_confinement_on(
            self.guarded,
            cid,
            tmpfs_budgets=ci.owner_tmpfs_budgets(ctx.profile) if ctx is not None else None,
        )
        # The subject exec boundary measured on THIS exact CID (no
        # wire): the original fixed-21002 law byte-for-byte, or the
        # frozen profile's exact independent uid:gid with the
        # explicit v2 closed record (v1/v2 refuse each other); the
        # model's closed-record validation failures map to fixed
        # tokens (no raw record content).
        assert self.parent_pid is not None and self.parent_port is not None
        assert self.sentinel_file is not None and self.parent_ns is not None
        try:
            if ctx is None:
                self.subject_facts = ci.measure_subject_on(
                    self.guarded,
                    cid,
                    env,
                    (self.parent_pid, self.parent_port, self.sentinel_file, self.parent_ns),
                    self.ledger,
                )
            else:
                self.subject_facts = ci.measure_subject_on_profile(
                    self.guarded,
                    cid,
                    env,
                    (self.parent_pid, self.parent_port, self.sentinel_file, self.parent_ns),
                    self.ledger,
                    ctx.profile,
                )
        except ValueError as exc:
            raise FixtureError(ci._model_validation_reason(exc)) from None
        # The reviewed Python PTY rehearsal with the protected
        # env-file handoff: ZERO wire POSTs.
        api_before = self.ledger.api_requests
        try:
            self.pty_facts = ci.pty_attach_on(
                self.guarded,
                cid,
                env_base,
                self.run_token,
                self.ledger,
                env_file=str(self.env_file),
                profile=ctx.profile if ctx is not None else None,
            )
        except ValueError as exc:
            raise FixtureError(ci._model_validation_reason(exc)) from None
        if self.pty_facts["env_handoff_verified"] is not True:
            raise FixtureError("local-env-handoff-unverified")
        # The generated protected env file is HELD through the
        # prepared-unconsumed state: the later exact foreground
        # attachment (a separately activated native run) needs the
        # same protected synthetic handoff, and a prior PTY's
        # environment or a file digest is not a substitute.  Only
        # the owner's TERMINAL cleanup (the exact-owned umbrella on
        # every success/failure/cancel path) removes it.
        self._publish_state()
        if self.ledger.api_requests != api_before:
            raise FixtureError("local-prepared-wire-charged")
        # Closed NON-CONSUMING actual controller state on the exact
        # CID: the prepared-unconsumed claim is OBSERVED, never
        # inferred from a host charge delta.
        observed = ci.observe_controller_on(
            self.guarded,
            cid,
            env_base,
            self.ledger,
            profile=ctx.profile if ctx is not None else None,
            entry_order=ctx.order_id if ctx is not None else None,
        )
        if (
            observed["wire_requests"] != 0
            or observed["diagnostic_state"] != "unobserved"
            or observed["scenario"] != _entry_scenario(ctx.order_id if ctx is not None else None)
        ):
            raise FixtureError("local-prepared-state")
        self.prepared = {
            "cid": cid,
            "state": "prepared-unconsumed",
            "observed": observed,
            "env_file_sha256": self.env_file_digest,
            "env_file_keys": list(ENV_FILE_KEYS),
        }

    # -- lifecycle: observe ------------------------------------------------------
    def observe(self) -> dict[str, object]:
        """The bounded trusted NON-CONSUMING observe command on the
        held prepared target: a closed /state record read under
        21002 (declared scenario, the controller's own cumulative
        request count, the one-shot diagnostic state).  It makes no
        model POST and consumes nothing, so it may be repeated
        without changing the fixture.  Valid only while the target
        is held (prepared, not yet finished)."""
        if self.target_cid is None or self.phase in ("teardown", "publish", "start"):
            raise FixtureError("local-observe-unavailable")
        ctx = self._owner_context
        return ci.observe_controller_on(
            self.guarded,
            self.target_cid,
            self.env_base,
            self.ledger,
            profile=ctx.profile if ctx is not None else None,
            entry_order=ctx.order_id if ctx is not None else None,
        )

    def hold_start(self) -> str:
        """The 017-x detached capability start: ONE closed detached
        exec (``docker exec -d``) of the reviewed stand-in hold mode
        as 21002 on the held prepared exact CID, carrying the issued
        32-hex run marker on argv — the kernel-cmdline correlation
        identity the host-side capability driver uses (no -e
        arguments, no PTY, no env file, no output capture: the
        subject's own finite hold and natural exit run without a
        host capture).  Valid only while the target is held
        (prepared).  ONE subject start in this run INCLUDING failed
        starts: the attempt latch is set BEFORE the dispatch, so a
        failed start consumes the one start and refuses any retry
        (the run then converges through the existing finish/abort
        path; the exact-CID cleanup is the subject's removal path on
        every outcome)."""
        self._abort_check()
        if self.hold_start_attempted:
            raise FixtureError("local-hold-already-started")
        if self.target_cid is None or self.phase != "prepared":
            raise FixtureError("local-hold-unavailable")
        self.hold_start_attempted = True
        cid = self.target_cid
        self.hold_token = self.run_token
        self._revalidate_identity_context()
        if self._owner_context is None:
            exec_user = f"{ci.SUBJECT_UID}:{ci.SUBJECT_UID}"
        else:
            # The frozen profile's exact independent uid:gid (never
            # uid:uid): the same identity law the stand-in enforces
            # at every in-image check site.
            exec_user = self._owner_context.exec_user
        result = self.guarded(
            [
                "docker",
                "exec",
                "-d",
                "--user",
                exec_user,
                cid,
                "python3",
                ci.STANDIN_PATH,
                "--mode",
                "hold",
                "--hold-token",
                self.hold_token,
            ],
            ci._QUERY_TIMEOUT,
        )
        if result.returncode != 0:
            raise FixtureError("local-hold-start-failed")
        self._publish_state()
        return self.hold_token

    #: The FINITE verified ``docker top`` header forms the daemon
    #: may emit for the closed 2-argument query: the default ``-ef``
    #: listing and the existing fixture's closed form (each with
    #: exactly one PID column).
    _TOP_HEADER_FORMS: tuple[tuple[str, ...], ...] = (
        ("UID", "PID", "PPID", "C", "STIME", "TTY", "TIME", "CMD"),
        ("UID", "PID", "COMMAND"),
    )

    def top_pids(self) -> list[int]:
        """The 017-x bounded exact-CID process inventory: ONE
        guarded ``docker top`` for the held prepared exact CID
        (closed 2-argument form; the query charges the SAME owner
        deadline/ledger as every other operation — the SAME closed
        command the existing CI descendant count uses; no ``ps``
        argument or column selection is widened).  The response is
        the authoritative member list of the exact owned CID,
        parsed under FINITE verified header forms: the daemon's
        default ``-ef`` listing (``UID PID PPID C STIME TTY TIME
        CMD``) and the existing fixture's closed form (``UID PID
        COMMAND``).  The PID column is LOCATED in the header (each
        closed form carries exactly one), every row must carry
        exactly the header's columns with a positive integer in
        the PID column, rows are distinct, and the member count is
        inside the closed fixture pids bound — an unknown,
        duplicate-column, malformed, duplicate, overbound or
        unreadable inventory is a closed refusal, never a silent
        truncation.  The host-side capability discovery
        cross-checks its bounded scan against this attestation: a
        member the attestation cannot account for is never
        silently filtered."""
        self._abort_check()
        if self.target_cid is None or self.phase in ("teardown", "publish", "start"):
            raise FixtureError("local-top-unavailable")
        cid = self.target_cid
        return self._exact_cid_top_pids(cid)

    def _exact_cid_top_pids(self, cid: str) -> list[int]:
        """The bounded exact-CID top attestation core (the shared
        measurement of ``top_pids`` and the owner-UID teardown
        lifetime registry): ONE guarded ``docker top`` on the exact
        registered CID, parsed under the FINITE verified header
        forms with the closed row/bound/duplicate law.  No ``ps``
        argument or column selection is widened; the host /proc is
        NEVER enumerated from this channel.  The phase guard of the
        public ``top_pids`` is the caller's concern; this core is
        charged to the SAME owner deadline/ledger as every other
        operation."""
        result = self.guarded(["docker", "top", cid], ci._QUERY_TIMEOUT)
        if result.returncode != 0:
            raise FixtureError("top-query-failed")
        lines = [
            line for line in result.output.decode("ascii", "replace").splitlines() if line.strip()
        ]
        header = tuple(lines[0].split()) if lines else ()
        if header not in self._TOP_HEADER_FORMS or header.count("PID") != 1:
            raise FixtureError("top-query-failed")
        pid_idx = header.index("PID")
        pids: list[int] = []
        for line in lines[1:]:
            # The trailing CMD/COMMAND column is ONE field: a bounded
            # split keeps its full remainder (command arguments with
            # spaces are legal), the leading columns stay fixed.
            fields = line.split(None, len(header) - 1)
            if (
                len(fields) != len(header)
                or not fields[pid_idx].isdigit()
                or int(fields[pid_idx]) <= 0
            ):
                raise FixtureError("top-count-untrusted")
            pids.append(int(fields[pid_idx]))
        if not 1 <= len(pids) <= model.PIDS_LIMIT:
            raise FixtureError("top-count-untrusted")
        if len(set(pids)) != len(pids):
            raise FixtureError("top-count-untrusted")
        return pids

    # -- lifecycle: rehearse (the S Python consume) --------------------------------
    def rehearse(self) -> None:
        """The S PYTHON REHEARSAL consumes THAT SAME prepared
        instance: the closed controller auth-binding proof on the
        live wire — the valid synthetic bearer is admitted (200) and
        its no-tools POST CONSUMES the one-shot diagnostic at causal
        position 0, answering the fixed assistant final text; the
        same-length WRONG bearer and the MISSING header are refused
        (401) before any semantic step.  The wire facts are
        reserved pre-work and charged at scenario end."""
        self._abort_check()
        if self.target_cid is None:
            raise FixtureError("internal")
        self.phase = "consume"
        cid = self.target_cid
        env = dict(self.env_base)
        env["SLAIF_RUN_TOKEN"] = self.run_token
        self.ledger.reserve_http(3, 3)
        result = ci._exec(
            self.guarded,
            cid,
            ci.SUBJECT_UID,
            ["python3", ci.STANDIN_PATH, "--mode", "auth-binding"],
            env,
        )
        if result.returncode != 0:
            ci._note_standin_detail(result)
            raise FixtureError("auth-binding-failed")
        record = ci._standin_record(
            result.output,
            "auth-binding",
            frozenset(
                {
                    "valid_admitted",
                    "wrong_refused",
                    "missing_refused",
                    "diagnostic_response",
                    "requests",
                    "attempts",
                }
            ),
        )
        if (
            record["valid_admitted"] is not True
            or record["wrong_refused"] is not True
            or record["missing_refused"] is not True
            or record["diagnostic_response"] != "fixed-final-text-no-tools"
            or record["requests"] != 3
            or record["attempts"] != 3
        ):
            raise FixtureError("auth-binding-record-state")
        self.ledger.charge_http(3, 3, 1, 2)
        self.consumed = {
            "cid": cid,
            "valid_admitted": True,
            "wrong_refused": True,
            "missing_refused": True,
            "diagnostic_response": "fixed-final-text-no-tools",
            "requests": 3,
            "attempts": 3,
            "admitted": 1,
            "refused": 2,
        }
        self._phase_done("consume")

    # -- lifecycle: finish -----------------------------------------------------------
    def finish(self) -> None:
        """FINISH the held prepared instance (usable with OR without
        the S Python consume): quiesce/freeze/export as 21001 WHILE
        THE CONTAINER STILL EXISTS, an ACTUAL non-consuming /state
        observation right before the export, host closed-object
        revalidation of the DECODED selected payload against THAT
        closed observation (the controller ledger is monotonic and
        the one-shot diagnostic state must match), then the exact
        verified teardown and owner convergence.  The S rehearsal's
        Python-specific assertions (fixed no-tools diagnostic
        metadata, causal position 0, empty issued calls, the exact
        3+2 controller ledger) are applied only when the Python
        consume actually happened on this run; no metadata is
        invented, no caller-ready boolean is promoted, and the
        diagnostic/ledger are never reset."""
        self._abort_check()
        if self.target_cid is None:
            raise FixtureError("internal")
        self.phase = "finish"
        # The FROZEN owner context is revalidated at THIS
        # identity-bound use site as well (the bounded current-ID
        # coherence read through the SAME seam, compared to the
        # frozen fingerprint): it may compare, never rebase — the
        # subject measurement, PTY and export all run as the
        # frozen identity, so a changed host identity after the
        # run began is a drift fact and a closed refusal (the
        # exact-owned cleanup still converges; no ID keeps it
        # alive or gates it).
        self._revalidate_identity_context()
        cid = self.target_cid
        # ACTUAL closed controller state right before the export
        # (non-consuming: no model POST, no charge, no state change)
        # — the identity baseline for this finish, whatever the
        # held instance's wire history is (S Python consume, an
        # external subject, or none at all).
        ctx = self._owner_context
        self.finish_observed = ci.observe_controller_on(
            self.guarded,
            cid,
            self.env_base,
            self.ledger,
            profile=ctx.profile if ctx is not None else None,
            entry_order=ctx.order_id if ctx is not None else None,
        )
        self.ledger.reserve_http(2, 2)
        export_result = ci._exec(
            self.guarded,
            cid,
            ci.CONTROLLER_UID,
            ["python3", ci.EXPORT_CLIENT_PATH],
            dict(self.env_base),
        )
        if export_result.returncode != 0:
            raise FixtureError("finish-export-failed")
        data = export_result.output
        i1 = data.find(b"\n")
        i2 = data.find(b"\n", i1 + 1)
        if i1 < 0 or i2 < 0:
            raise FixtureError("export-shape")
        line1, line2, payload = data[:i1], data[i1 + 1 : i2], data[i2 + 1 :]
        if not line1.startswith(b"quiesce-ok "):
            raise FixtureError("export-quiesce-state")
        quiesce_record = ci._parse_prefixed_record(line1, ci._QUIESCE_PREFIX)
        try:
            model.validate_quiesce_record(quiesce_record)
        except ValueError:
            raise FixtureError("export-quiesce-state") from None
        if not line2.startswith(b"export-sha256 "):
            raise FixtureError("export-shape")
        declared = line2[len(b"export-sha256 ") :].decode("ascii", "replace")
        if (
            not re.fullmatch(r"[0-9a-f]{64}", declared)
            or declared != hashlib.sha256(payload).hexdigest()
        ):
            raise FixtureError("export-sha-mismatch")
        if len(payload) > self.budgets.max_export_bytes:
            raise FixtureError("export-overbound")
        # HOST INDEPENDENT closed-object revalidation: the DECODED
        # selected payload itself must be a valid closed record (the
        # client's proof is not the host's proof).  The canonical
        # 017-aj entry's closed format-capture scenario carries the
        # DISTINCT three-field format payload (the closed record tag
        # selects the full or the safe partial format law); the
        # untagged six-field legacy form is drift under AJ and is
        # refused, never relabelled.
        ctx_is_aj = ctx is not None and ctx.order_id == AJ_ORDER_ID
        try:
            if ctx_is_aj:
                selected = fixture_export.validate_selected_payload(payload)
                if selected.get("record") not in (
                    model.SCHEMA_FORMAT_EXPORT,
                    model.SCHEMA_FORMAT_EXPORT_PARTIAL,
                ):
                    raise ValueError("format-payload-tag")
            else:
                selected = fixture_export.validate_payload(payload)
        except ValueError:
            raise FixtureError("export-invalid") from None
        snapshot = selected["snapshot"]
        # Identity against the ACTUAL closed observation taken
        # above (measured, never invented): the export's own
        # snapshot is coherent with the controller's state iff the
        # ledger is monotonic across the observe->export window and
        # the one-shot diagnostic state in the payload matches the
        # observed state (closed-object validation of the payload's
        # internal position/diagnostic grammar already holds).
        ledger_requests = snapshot["controller_ledger"]["requests"]
        if ledger_requests < self.finish_observed["wire_requests"]:
            raise FixtureError("export-identity-mismatch")
        if ctx_is_aj:
            # The AJ format scenario carries NO legacy one-shot
            # diagnostic position: the truthful format coordinates
            # (issued calls, case/result positions, the model POST
            # truth) live inside the validated snapshot, and the
            # observed diagnostic state is a measured fact, never
            # interpreted as format consumption or absence.
            self.finish_position = None
        else:
            position = selected["observed_at_position"]
            if self.finish_observed["diagnostic_state"] == "unobserved":
                if selected["diagnostic"] != {"state": "unobserved"} or position is not None:
                    raise FixtureError("export-identity-mismatch")
            else:
                if (
                    selected["diagnostic"] == {"state": "unobserved"}
                    or not isinstance(position, int)
                    or isinstance(position, bool)
                    or position < 0
                ):
                    raise FixtureError("export-identity-mismatch")
            if self.consumed is not None:
                # The S PYTHON REHEARSAL keeps its exact Python-specific
                # qualification: the first admitted auth-binding POST
                # consumed the one-shot no-tools diagnostic at causal
                # position 0 against the fixed single-source metadata,
                # the diagnostic scenario issued nothing, and the
                # controller's own ledger counts exactly the three auth
                # POSTs plus the two exporter commands.
                if selected["diagnostic"] != model.bounds_diagnostic(
                    fixture_standin._fixed_request([])
                ):
                    raise FixtureError("export-identity-mismatch")
                if position != 0 or snapshot["issued_calls"] != []:
                    raise FixtureError("export-identity-mismatch")
                if ledger_requests != 5:
                    raise FixtureError("controller-ledger-mismatch")
            self.finish_position = position
        self.finish_ledger_requests = ledger_requests
        self.ledger.charge_http(2, 2, 2, 0)
        self.export_payload = payload
        self.export_sha = declared
        self._phase_done("finish")
        self._teardown_verified()

    def _member_lifetime(self, pid: int) -> tuple[int, int] | str | None:
        """The POST-removal bounded host read of the exact owned
        PID's lifetime frame (the reviewed /proc parsers reused
        READ-ONLY on a single exact PID — no enumeration, no
        signal, no privilege, no new channel): ``(birth, uid)``
        for a complete frame, the literal ``"gone"`` ONLY for
        verified ENOENT, and ``None`` for unreadable/unknown
        (a present-but-degraded frame, a vanished-between-reads
        file, or an OVER-BOUND frame: each file is read cap+1
        and refused at cap+1, so a growing/over-bound frame is
        never silently truncated and never misread).  An
        unreadable listed PID is never conflated with
        verified-gone.
        """
        root = self._proc_root
        try:
            with open(root / str(pid) / "stat", "rb") as handle:
                raw_stat = handle.read(fixture_prep._PROC_STAT_MAX + 1)
        except OSError as exc:
            if exc.errno == errno.ENOENT:
                return "gone"
            return None
        if len(raw_stat) > fixture_prep._PROC_STAT_MAX:
            return None
        try:
            with open(root / str(pid) / "status", "rb") as handle:
                raw_status = handle.read(fixture_prep._STATUS_MAX + 1)
        except OSError:
            return None
        if len(raw_status) > fixture_prep._STATUS_MAX:
            return None
        try:
            parsed = fixture_prep.parse_proc_stat(raw_stat.decode("ascii", "replace"))
            uid, _gid, _groups = fixture_prep.parse_proc_status(raw_status)
        except (FixtureError, ValueError, UnicodeDecodeError):
            return None
        # LIFETIME AUTHORITY: the parser now accepts a well-formed
        # ZERO pgrp/session row as observation data, but a
        # lifetime frame can never be one — the old parser's
        # positive prerequisite is preserved at this consumer
        # boundary (unknown, never a frame)
        if not fixture_prep._is_pid(parsed.pgrp) or not fixture_prep._is_pid(parsed.session):
            return None
        if parsed.pid != pid:
            return None
        return (parsed.start_time, uid)

    def _owned_member_frame(
        self, pid: int, table: fixture_prep.RealCidScopedTable
    ) -> tuple[int, int] | None:
        """The PRE-removal CID-ATTESTED, STABLE lifetime frame of
        one listed PID: the registered-CID channel reads the
        exact PID's stat frame, then its status frame, then its
        stat frame AGAIN — every single read gated on the PID's
        CURRENT cgroup scope for the EXACT registered CID (the
        over-bound/unsafe read refusal included).  The two stat
        frames must agree on ``(pid, start_time)``: the same
        live process observed before AND after the status read,
        with the CID scope still holding at each instant — a
        raced PID (exit/reuse in any read window), an exited
        member, an out-of-scope or over-bound/unreadable frame
        is refused, never adopted: list membership without a
        stable combined birth/UID/CID frame is not ownership.
        Returns ``(birth, uid)`` or ``None`` (unverified)."""
        first_stat = table.stat(pid)
        raw_status = table.status(pid)
        second_stat = table.stat(pid)
        if first_stat is None or raw_status is None or second_stat is None:
            return None
        try:
            first = fixture_prep.parse_proc_stat(first_stat.decode("ascii", "replace"))
            second = fixture_prep.parse_proc_stat(second_stat.decode("ascii", "replace"))
            uid, _gid, _groups = fixture_prep.parse_proc_status(raw_status)
        except (FixtureError, ValueError, UnicodeDecodeError):
            return None
        # LIFETIME AUTHORITY: both stable frames must carry the
        # old parser's positive group/session prerequisite — a
        # well-formed ZERO pgrp/session observation is never an
        # owned lifetime frame (unknown, never adopted)
        if (
            not fixture_prep._is_pid(first.pgrp)
            or not fixture_prep._is_pid(first.session)
            or not fixture_prep._is_pid(second.pgrp)
            or not fixture_prep._is_pid(second.session)
        ):
            return None
        if first.pid != pid or second.pid != pid:
            return None
        # Stable combined frame: the same (pid, birth) live
        # across the status read — an exit/reuse in the window
        # changes the birth (or drops the scope) and is refused.
        if first.start_time != second.start_time:
            return None
        return (second.start_time, uid)

    def _teardown_verified(self) -> None:
        self.phase = "teardown"
        if self.target_cid is None:
            raise FixtureError("internal")
        cid = self.target_cid
        # Positive-before: the exact owned container still has
        # processes; negative-after: verified absent after removal.
        self.descendants_before = ci._descendant_count(self.guarded, cid)
        if self._owner_context is not None:
            # The owner-UID variant (017-aa): the subject UID is
            # the HOST OWNER's own UID (the worker/owner/unrelated
            # host processes share it), so a global owner-UID scan
            # is FORBIDDEN.  The owned-lifetime registry is
            # measured instead: the ACTUAL member PID +
            # birth(start_time) + uid of the EXACT registered CID
            # (the SAME bounded exact-CID top channel, read-only
            # reuse, charged to the same deadline/ledger),
            # cross-checked against that channel's count.  An
            # unreadable or raced listed member is a closed
            # refusal — unverified members are never silently
            # ignored; the post-removal proof below verifies
            # THESE owned identities tri-stated.
            pids = self._exact_cid_top_pids(cid)
            # The registered-CID channel attests each listed PID
            # CURRENTLY: the per-PID cgroup scope for the exact
            # registered CID gates the frame read, so a raced or
            # exited PID is never adopted from list position
            # alone (the scoped table's over-bound/unsafe read
            # refusal is inherited by the frame read).
            table = fixture_prep.RealCidScopedTable(cid, root=self._proc_root)
            members: list[tuple[int, int, int]] = []
            for pid in pids:
                frame = self._owned_member_frame(pid, table)
                if frame is None:
                    raise FixtureError("descendant-unverified")
                birth, uid = frame
                members.append((pid, birth, uid))
            if len(members) != self.descendants_before:
                raise FixtureError("descendant-leftover")
            self.owned_members_before = tuple(members)
        ci.cleanup_container(self.guarded, cid)
        _require_absent(self.guarded, cid)
        self.teardown_container_absent = True
        ci.verify_no_leftovers(self.guarded, ci.IMAGE_NAME)
        if self.image_id is None and self.build_attempted:
            # The collision probe proved the exact tag ABSENT before
            # our build: whatever id resolves that exact tag now is
            # ours (we never adopt arbitrary names or ids).
            self.image_id = self._discover_image_id()
        if self.image_id is not None and not self.image_removed:
            outcome = ci.remove_owned_image_exact(
                self.guarded, self.image_id, self.cleanup_failures
            )
            if outcome == "absent-verified":
                self.image_removed = True
        if not self.image_removed:
            raise FixtureError("local-image-state")
        # The unrelated parent sentinel MUST have survived the whole
        # run (measured BEFORE the intentional reap).
        if self.sentinel is None or self.sentinel.poll() is not None:
            raise FixtureError("sentinel-process-died")
        self.sentinel_survived = True
        if ci._count_fixture_uid_processes(ci.CONTROLLER_UID) != 0:
            raise FixtureError("descendant-leftover")
        if self._owner_context is None:
            # The historical original law: the fixed subject UID
            # (21002) is a fixture-owned host UID, so the global
            # host scan is the closed subject proof.
            if ci._count_fixture_uid_processes(ci.SUBJECT_UID) != 0:
                raise FixtureError("descendant-leftover")
            self.teardown_descendants_after = 0
        else:
            # Tri-stated post-removal verification of the OWNED
            # lifetime registry, per exact owned PID (bounded host
            # /proc read of the exact PID only — no enumeration,
            # no UID membership, no signal), each frame compared
            # against its CID-attested pre-removal birth frame:
            #   verified-gone  — the proc frame is absent (verified
            #                    ENOENT): the member is gone;
            #   recycled       — a frame is present with a
            #                    DIFFERENT birth: ONLY a changed
            #                    birth proves PID reuse; the owned
            #                    member is gone (the exact CID is
            #                    verified absent) and the PID was
            #                    reused; the occupant is a
            #                    different process, never
            #                    mislabeled as the old member,
            #                    signalled, or counted as one;
            #   still-existing — a frame is present with the SAME
            #                    birth AND uid: the owned member
            #                    is a real leftover, a closed
            #                    refusal;
            #   unverified     — present but unreadable/degraded/
            #                    over-bound frame, OR the same
            #                    birth with a CHANGED uid (a
            #                    contradictory frame: neither the
            #                    owned member nor a proven reuse):
            #                    a closed refusal (never silently
            #                    ignored, never inferred gone,
            #                    never classified).
            after: list[tuple[int, str]] = []
            still_existing = 0
            for pid, birth, uid in self.owned_members_before or ():
                state = self._member_lifetime(pid)
                if state == "gone":
                    after.append((pid, "verified-gone"))
                elif state is None:
                    raise FixtureError("descendant-unverified")
                else:
                    cur_birth, cur_uid = state
                    if cur_birth != birth:
                        # Only a changed birth proves PID reuse:
                        # the occupant is a different process —
                        # never signalled, mislabeled or counted
                        # as the old member.
                        after.append((pid, "recycled"))
                    elif cur_uid != uid:
                        # Same birth, changed UID: a contradictory
                        # frame — refused, never classified as
                        # reuse (no birth change) and never as
                        # the owned member (frame mismatch).
                        raise FixtureError("descendant-unverified")
                    else:
                        still_existing += 1
                        after.append((pid, "still-existing"))
            self.owned_members_after = tuple(after)
            if still_existing:
                raise FixtureError("descendant-leftover")
            # Measured: zero owned members still existing (every
            # owned identity verified gone or recycled).
            self.teardown_descendants_after = 0
        self._phase_done("teardown")

    # -- the single exact-owned cleanup umbrella ---------------------------------------
    def _cleanup_umbrella(self) -> None:
        """ONE exact-owned cleanup path on the SAME remaining
        budgets, run on EVERY path (success, phase failure,
        cancellation): an earlier failure never skips the rest, and
        each resource is touched exactly once (idempotence: an
        already-verified-removed image is never rmi'd twice, a
        vanished env file is a no-op).  Fixture resources are
        cleaned FIRST (containers, then the exact fresh build
        intent — recovered through the OWN tag when the id was
        never learned, then env file, then listener); the unrelated
        sentinel survival is MEASURED after the fixture cleanup and
        only then reaped intentionally (the containment fact stays
        separate from the reap, on every path).  Daemon/query
        failures stay recorded unverified states — never claimed
        clean."""
        try:
            self.deadline.add_grace(CLEANUP_GRACE_SECONDS, "cleanup")
        except FixtureError:
            pass  # the single grace was already reserved
        for container_id in self.created:
            try:
                ci.cleanup_container(self.guarded, container_id)
            except (FixtureError, ci._OwnedTimeout, OSError):
                if "container-cleanup-unverified" not in self.cleanup_failures:
                    self.cleanup_failures.append("container-cleanup-unverified")
        # The create/response gap: when the exact fresh create
        # intent was persisted but NO CID was ever returned (create
        # failed or was interrupted), a ps discovery under the
        # exact fresh name is a QUERY, not an image/run/ownership
        # attestation: it cannot prove which object a failed create
        # left behind.  The closed, honest disposition is
        # fail-closed: any non-empty or ambiguous discovery result
        # (or a failed query) is recorded
        # container-cleanup-unverified and the exact intent is
        # RETAINED in the fail record for the separately authorized
        # recovery — no unattested CID is ever removed here (the
        # exact registered-CID cleanup above stays intact).
        if self.create_intent is not None and self.target_cid is None:
            try:
                result = self.guarded(
                    ["docker", "ps", "-aq", "--filter", f"name={self.create_intent}"],
                    ci._QUERY_TIMEOUT,
                )
                if result.returncode != 0:
                    raise FixtureError("query-failed")
                found = [line for line in result.output.decode("ascii", "replace").split() if line]
                if found:
                    if "container-cleanup-unverified" not in self.cleanup_failures:
                        self.cleanup_failures.append("container-cleanup-unverified")
            except (FixtureError, ci._OwnedTimeout, OSError):
                if "container-cleanup-unverified" not in self.cleanup_failures:
                    self.cleanup_failures.append("container-cleanup-unverified")
        # The exact fresh build intent: when the build was attempted
        # but the image id was never learned (failed build or failed
        # id query), recover it ONLY through the exact own tag —
        # the collision probe proved that exact tag ABSENT before
        # the build, so whatever resolves it now is this run's
        # (never arbitrary names or ids are adopted).
        if self.build_attempted and not self.image_removed:
            if self.image_id is None:
                try:
                    self.image_id = self._discover_image_id()
                except (FixtureError, ci._OwnedTimeout, OSError):
                    if "image-cleanup-unverified" not in self.cleanup_failures:
                        self.cleanup_failures.append("image-cleanup-unverified")
            if self.image_id is not None:
                try:
                    outcome = ci.remove_owned_image_exact(
                        self.guarded, self.image_id, self.cleanup_failures
                    )
                    if outcome == "absent-verified":
                        self.image_removed = True
                except (FixtureError, ci._OwnedTimeout, OSError):
                    if "image-cleanup-unverified" not in self.cleanup_failures:
                        self.cleanup_failures.append("image-cleanup-unverified")
        if self.env_file is not None:
            try:
                remove_env_file(self.env_file)
                self.env_file = None
            except FixtureError:
                if "env-file-remove-failed" not in self.cleanup_failures:
                    self.cleanup_failures.append("env-file-remove-failed")
        if self.listener is not None:
            try:
                self.listener.close()
            except OSError:
                if "listener-cleanup-failed" not in self.cleanup_failures:
                    self.cleanup_failures.append("listener-cleanup-failed")
        # The unrelated parent sentinel: survival is MEASURED now —
        # after the fixture cleanup, before the intentional reap —
        # and the reap follows (a failed reap is a separate cleanup
        # fact; an actually-dead sentinel is the containment fact).
        if self.sentinel is not None and not self.sentinel_reaped:
            if self.sentinel.poll() is not None:
                if "sentinel-died" not in self.cleanup_failures:
                    self.cleanup_failures.append("sentinel-died")
            try:
                self.sentinel.kill()
                self.sentinel.wait(timeout=ci._LEADER_REAP_SECONDS)
                self.sentinel_reaped = True
            except (OSError, subprocess.TimeoutExpired):
                if "sentinel-cleanup-failed" not in self.cleanup_failures:
                    self.cleanup_failures.append("sentinel-cleanup-failed")
            if self.sentinel.poll() is None:
                if "sentinel-cleanup-failed" not in self.cleanup_failures:
                    self.cleanup_failures.append("sentinel-cleanup-failed")

    def _deadline_expired(self) -> bool:
        try:
            self.deadline.remaining()
        except FixtureError:
            return True
        return False

    # -- abort ---------------------------------------------------------------------
    def abort(self) -> None:
        """Caller-side abort: the SAME exact-owned convergence at the
        next phase boundary (or immediately when called from a
        terminal phase).  Never a new experiment."""
        self._abort_by_caller = True

    # -- the protected control surface -------------------------------------------------
    def _create_intent_published(self, name: str) -> None:
        """The shared helper's create-intent callback: the exact
        fresh create name is persisted in the protected state
        BEFORE docker create (the create/response gap is then
        recoverable ownership data, never an adopted foreign
        resource); a failure forbids the create."""
        if not ci._LOCAL_NAME_RE.fullmatch(name):
            raise FixtureError("local-state-malformed")
        self.create_intent = name
        self._publish_state_required()

    def _init_control(self) -> None:
        """Create the FRESH protected control root (0700, owned,
        never adopted — the same fresh-root law as the work root)
        with the bounded command socket (0600), BEFORE accepting
        any client or external mutation.  The protected state/abort
        files live here, OUTSIDE the disposable work root: the
        exact recovery registry/ledger survives the destroyed
        scratch when cleanup remains unverified."""
        ci._create_work_root(self.control_dir)
        self.control_dir_owned = True
        self.state_path = self.control_dir / _CONTROL_STATE_NAME
        self.abort_path = self.control_dir / "abort"
        sock_path = self.control_dir / _CONTROL_SOCK_NAME
        listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            listener.bind(str(sock_path))
            os.chmod(str(sock_path), 0o600)
            listener.listen(1)
        except BaseException:
            listener.close()
            raise FixtureError("local-control-unbound") from None
        self._control_socket = listener

    def _finalize_control(self) -> None:
        """Terminal control-surface disposition (called BEFORE the
        final pass gate and attempt record): the listener is closed
        and the socket unlinked on EVERY path; the control root
        (state + abort) is destroyed only when the cleanup fully
        converged.  An unverified close/unlink/destruction is a
        MEASURED cleanup failure (it can never disappear after a
        published pass) and RETAINS the protected registry/ledger
        for the later separately-authorized recovery — a failed
        destruction keeps ownership recorded, never cleared."""
        failures = 0
        if self._control_socket is not None:
            try:
                self._control_socket.close()
            except OSError:
                failures += 1
            self._control_socket = None
        sock = self.control_dir / _CONTROL_SOCK_NAME
        try:
            if sock.exists() or sock.is_symlink():
                os.unlink(str(sock))
        except OSError:
            failures += 1
        if self.control_dir_owned:
            if failures or self.cleanup_failures:
                # Unverified cleanup: the registry/ledger survive
                # in the retained protected control root.
                pass
            elif not ci._destroy_owned_work_root(self.control_dir):
                failures += 1
                # The destruction did not verify: ownership stays
                # recorded (the root is retained, not adopted as
                # gone).
            else:
                self.control_dir_owned = False
        if failures:
            if "control-cleanup-unverified" not in self.cleanup_failures:
                self.cleanup_failures.append("control-cleanup-unverified")

    def _response(self, command: str, ok: bool, reason: str | None, detail: dict | None) -> dict:
        return {
            "record": CONTROL_RECORD,
            "ok": ok,
            "command": command,
            "run_id": self.run_id,
            "reason": reason,
            "detail": detail,
        }

    def _converge(self, primary: BaseException | None) -> None:
        """The SINGLE exact-owned convergence used by EVERY terminal
        path (success, phase failure, cancellation, deadline
        expiry): the umbrella on the SAME remaining budgets, the
        disposable work-root destruction, the terminal control-
        surface disposition (a cleanup FACT measured BEFORE the
        final gate and the attempt record), the honest pass gate,
        protected evidence publication, the stable one-attempt
        outcome, and the final protected state (only in the
        retained control root).  A publication failure after a
        computed pass is never recorded as an admitted pass (the
        retained record IS the pass; if it cannot be retained the
        outcome is a truthful fail)."""
        if self._converged:
            return
        if primary is not None:
            if isinstance(primary, FixtureError):
                self.failure_reason = (
                    "cancelled" if str(primary) == "local-abort-requested" else str(primary)
                )
            elif isinstance(primary, KeyboardInterrupt):
                self.failure_reason = "cancelled"
            else:
                self.failure_reason = "internal"
            self.failure_stage = self.phase
        self.status = "finished" if primary is None else "failed"
        self._publish_state()
        # The run-deadline fact is captured BEFORE the umbrella adds
        # the one cleanup grace: the grace authorizes the cleanup
        # WINDOW, it never retroactively makes an expired run
        # on-time.
        deadline_expired = self._deadline_expired()
        try:
            self._cleanup_umbrella()
        except BaseException:
            if "internal" not in self.cleanup_failures:
                self.cleanup_failures.append("internal")
        # Pass gate (recomputed AFTER every cleanup fact is
        # measured below): no primary failure, COMPLETE measured
        # cleanup, and the run inside its one anchor plus one grace.
        pass_ok = primary is None and not self.cleanup_failures and not deadline_expired
        self.phase = "publish"
        publish_exception: BaseException | None = None
        try:
            # Destroy the disposable root BEFORE any publication:
            # the retained evidence is the publication, and a
            # surviving scratch root can never be claimed clean.
            if self.work_root_owned and not ci._destroy_owned_work_root(self.work):
                if "work-cleanup-failed" not in self.cleanup_failures:
                    self.cleanup_failures.append("work-cleanup-failed")
                pass_ok = False
                self.failure_stage = "cleanup"
            # The terminal control-surface disposition is a CLEANUP
            # FACT measured BEFORE the final gate and the attempt
            # record: an unverified close/unlink/destruction
            # forbids the pass, retains the protected registry, and
            # can never disappear after a published pass.
            self._finalize_control()
            if self.cleanup_failures:
                pass_ok = False
            if primary is None and not pass_ok:
                self.failure_reason = (
                    "deadline-expired" if deadline_expired else "cleanup-incomplete"
                )
                self.failure_stage = "cleanup"
                self.status = "failed"
            # The recovery retention decision is final once EVERY
            # cleanup fact (scratch root, control surface) is
            # measured: the registry in the control root survives
            # iff cleanup is unverified.
            self._recovery_state_retained = bool(self.cleanup_failures)
            if pass_ok:
                if self._native_binding is not None:
                    evidence = self._build_native_pass_evidence()
                else:
                    evidence = self._build_pass_evidence()
            else:
                if not self.failure_reason:
                    self.failure_reason = "work-cleanup-failed"
                self.status = "failed"
                if self._native_binding is not None:
                    evidence = self._build_native_fail_evidence(deadline_expired)
                else:
                    evidence = self._build_fail_evidence(deadline_expired)
            payload = (json.dumps(evidence, sort_keys=True, separators=(",", ":")) + "\n").encode(
                "ascii"
            )
            if self._native_binding is not None:
                if self._owner_context is not None:
                    # The DISTINCT owner-UID terminal record of
                    # THIS entry's OWN closed grammar (the tag
                    # follows the owner's frozen context — the
                    # AB entry's tag is never the AD entry's
                    # record and vice versa; the original
                    # native-scope grammar stays the no-owner
                    # context path).  Each entry names its OWN
                    # validator explicitly: an unexpected order
                    # id in a frozen context is an internal
                    # invariant violation, never a silent
                    # relabel to another entry's grammar.
                    if self._owner_context.order_id == AB_ORDER_ID:
                        validate_ab_owner_run_evidence(evidence)
                    elif self._owner_context.order_id == AD_ORDER_ID:
                        validate_ad_owner_run_evidence(evidence)
                    elif self._owner_context.order_id == AF_ORDER_ID:
                        validate_af_owner_run_evidence(evidence)
                    elif self._owner_context.order_id == AH_ORDER_ID:
                        validate_ah_owner_run_evidence(evidence)
                    elif self._owner_context.order_id == AJ_ORDER_ID:
                        validate_aj_owner_run_evidence(evidence)
                    else:
                        raise FixtureError("internal")
                else:
                    validate_native_owner_run_evidence(evidence)
            else:
                validate_local_evidence(evidence)
            self._evidence_sha = hashlib.sha256(payload).hexdigest()
            ci._retain_evidence(self.evidence_out, payload, self._evidence_sha, self.work)
            # the protected writer returned verified success:
            # the retention receipt is earned (a failure or
            # unverified result at this seam never sets it,
            # even when bytes reached the destination)
            self._evidence_retained = True
        except BaseException as exc:
            publish_exception = exc
        if publish_exception is not None and pass_ok:
            # Publication is the pass: a failed publication is
            # never recorded as an admitted pass.
            pass_ok = False
            if not self.failure_reason:
                self.failure_reason = "internal"
            if self.failure_stage not in _FAILURE_STAGES:
                self.failure_stage = "publish"
            self.status = "failed"
        self._outcome = (
            "pass" if pass_ok else ("aborted" if self.failure_reason == "cancelled" else "fail")
        )
        if self._native_binding is not None:
            # The DISTINCT native terminal path over the SAME
            # measured owner state/cleanup/publication, in the
            # bound order's namespace: a terminal owner or
            # publication error (fail/aborted — including a
            # publication failure after a computed pass, which
            # is never an admitted pass) is finalized HONESTLY
            # now; a converged pass keeps the bound attempt
            # RUNNING until the native publication (the terminal
            # pass finalization follows the successful protected
            # retention of the native run record).
            if self._outcome != "pass":
                oap_binding.record_order_attempt(
                    self.repo, self._native_binding.order_id, self.run_id, self._outcome
                )
        else:
            _record_attempt(self.repo, self.run_id, self._outcome)
        self._exit_code = (
            0 if self._outcome == "pass" else (130 if self._outcome == "aborted" else 1)
        )
        self.status = "finished" if self._outcome == "pass" else "failed"
        if self.control_dir_owned:
            # The RETAINED control root carries the final converged
            # state for the separately-authorized recovery; a
            # verified (destroyed) root has nothing left to read.
            self._publish_state()
        self._converged = True

    def _dispatch(self, request: dict) -> dict:
        """ONE bounded command against the SAME RAM run context (no
        ledger/attempt/END/registry reinitialization).  Convergence
        rules: a failed prepare/rehearse converges immediately
        (nothing left to hold); an observe failure is a closed
        refusal WITHOUT convergence (the fixture is still held);
        finish always converges (success or failure); abort
        converges now as a truthful abort.  A command for another
        run id, or after convergence, is a closed refusal."""
        command = str(request["command"])
        if request["run_id"] != self.run_id:
            return self._response(command, False, "local-control-protocol", None)
        if self._converged:
            return self._response(command, False, "local-converged", None)
        if command == "prepare":
            if self.phase != "start":
                return self._response(command, False, "local-lifecycle-state", None)
            try:
                self.prepare()
            except BaseException as exc:
                self._converge(exc)
                return self._response(command, False, self.failure_reason, None)
            assert self.target_cid is not None and self.prepared is not None
            return self._response(
                command,
                True,
                None,
                {
                    "cid": self.target_cid,
                    "state": "prepared-unconsumed",
                    "observed": dict(self.prepared["observed"]),
                    "end_anchor": self.deadline.anchor,
                },
            )
        if command == "observe":
            if self.target_cid is None or self.phase in ("teardown", "publish", "start"):
                return self._response(command, False, "local-observe-unavailable", None)
            try:
                observed = self.observe()
            except FixtureError as exc:
                return self._response(command, False, str(exc), None)
            except BaseException as exc:
                self._converge(exc)
                return self._response(command, False, "internal", None)
            return self._response(
                command,
                True,
                None,
                {
                    "scenario": observed["scenario"],
                    "wire_requests": observed["wire_requests"],
                    "diagnostic_state": observed["diagnostic_state"],
                    "raw_content_retained": False,
                },
            )
        if command == "rehearse":
            if self.target_cid is None or self.phase in ("teardown", "publish"):
                return self._response(command, False, "local-lifecycle-state", None)
            try:
                self.rehearse()
            except BaseException as exc:
                self._converge(exc)
                return self._response(command, False, self.failure_reason, None)
            assert self.target_cid is not None
            return self._response(
                command,
                True,
                None,
                {
                    "cid": self.target_cid,
                    "valid_admitted": True,
                    "wrong_refused": True,
                    "missing_refused": True,
                    "diagnostic_response": "fixed-final-text-no-tools",
                    "admitted": 1,
                    "refused": 2,
                },
            )
        if command == "hold":
            if self.target_cid is None or self.phase in ("teardown", "publish", "start"):
                return self._response(command, False, "local-hold-unavailable", None)
            try:
                token = self.hold_start()
            except FixtureError as exc:
                # A closed start refusal (including the consumed
                # one-start latch and a failed dispatch) does NOT
                # converge the owner: the held prepared target is
                # still finishable (prep-only honest unready).
                return self._response(command, False, str(exc), None)
            except BaseException:
                self._converge(FixtureError("internal"))
                return self._response(command, False, "internal", None)
            return self._response(command, True, None, {"hold_token": token})
        if command == "top":
            if self.target_cid is None or self.phase in ("teardown", "publish", "start"):
                return self._response(command, False, "local-top-unavailable", None)
            try:
                pids = self.top_pids()
            except FixtureError as exc:
                # A closed inventory refusal does NOT converge the
                # owner: the held prepared target is still
                # finishable (prep-only honest unready).
                return self._response(command, False, str(exc), None)
            except BaseException:
                self._converge(FixtureError("internal"))
                return self._response(command, False, "internal", None)
            return self._response(command, True, None, {"pids": pids, "rows": len(pids)})
        if command == "finish":
            if self.target_cid is None or self.phase in ("teardown", "publish"):
                return self._response(command, False, "local-lifecycle-state", None)
            try:
                self.finish()
                self._converge(None)
            except BaseException as exc:
                self._converge(exc)
            return self._response(
                command,
                True,
                None,
                {
                    "outcome": self._outcome,
                    "stage": self.failure_stage if self._outcome != "pass" else "publish",
                    "evidence_sha256": self._evidence_sha,
                    "control_dir_retained": self._recovery_state_retained,
                },
            )
        if command == "abort":
            self._abort_by_caller = True
            self._converge(FixtureError("local-abort-requested"))
            return self._response(
                command,
                True,
                None,
                {
                    "outcome": self._outcome,
                    "stage": self.failure_stage,
                    "evidence_sha256": self._evidence_sha,
                    "control_dir_retained": self._recovery_state_retained,
                },
            )
        return self._response(command, False, "local-control-protocol", None)

    def serve(self) -> int:
        """The owner's long-running protected service loop (the 017-s
        lifecycle interface): ONE bounded closed command per client
        connection against the SAME RAM run context, independent
        convergence at the owner's OWN finite deadline (an idle or
        blocked client, or client disappearance, can never stop or
        reset ownership — the owner converges its exact-owned
        cleanup on its own remaining budgets and exits).

        A post-admission STARTUP refusal (control-root creation or
        the bounded socket bind) is routed through the SAME single
        owner convergence as every terminal path: the already-won
        attempt closes terminal honestly (no retry, no remint), the
        owned partial control root is disposed through the same
        exact-ownership law (a pre-existing foreign root is never
        adopted or deleted — it is not this run's to destroy), and
        the original refusal is re-raised so the thin CLI prints
        the same closed startup record and returns the same exit
        code."""
        try:
            self._init_control()
            self._publish_state()
        except BaseException as exc:
            self._converge(exc)
            raise
        try:
            while not self._converged:
                if self._deadline_expired():
                    self._converge(FixtureError("deadline-expired"))
                    break
                conn = _accept_bounded(self._control_socket, _CONTROL_ACCEPT_TIMEOUT)
                if conn is None:
                    continue
                request = _read_control_request(conn)
                if request is None:
                    try:
                        conn.close()
                    except OSError:
                        pass
                    continue
                response = self._dispatch(request)
                try:
                    line = (
                        json.dumps(response, sort_keys=True, separators=(",", ":")) + "\n"
                    ).encode("ascii")
                    if len(line) <= _CONTROL_RESPONSE_CAP:
                        conn.settimeout(5.0)
                        conn.sendall(line)
                except OSError:
                    pass  # the client is gone: the facts are in the state file
                finally:
                    try:
                        conn.close()
                    except OSError:
                        pass
        except KeyboardInterrupt as exc:
            self._converge(exc)
        finally:
            if not self._converged:
                self._converge(FixtureError("internal"))
        return self._exit_code

    # -- closed evidence ---------------------------------------------------------
    def _artifact_record(self) -> dict[str, object]:
        artifact = self.artifact
        if artifact is None:
            raise FixtureError("internal")
        return {
            "record": model.SCHEMA_ARTIFACT,
            "tag": model.ARTIFACT_TAG,
            "commit": model.ARTIFACT_COMMIT,
            "archive_sha256": model.ARTIFACT_ARCHIVE_SHA256,
            "archive_size": model.ARTIFACT_ARCHIVE_SIZE,
            "binary_name": model.ARTIFACT_BINARY_NAME,
            "binary_sha256": artifact["binary_sha256"],
            "binary_size": artifact["binary_size"],
            "license": model.ARTIFACT_LICENSE,
            "license_sha256": artifact["license_sha256"],
            "notice": model.ARTIFACT_NOTICE,
            "notice_sha256": artifact["notice_sha256"],
            "signature_verification": model.SIGNATURE_VERIFICATION,
        }

    @property
    def terminal_outcome(self) -> str | None:
        """The owner's OWN terminal outcome, once its convergence
        has completed (the same completed owner state a bounded
        composition reads; None until the owner's own
        convergence is final).  The same-order attempt journal
        is the durable record, never a prerequisite for
        deriving this outcome."""
        return self._outcome if self._converged else None

    def devpts_inventory(self) -> fixture_prep.DevptsObservation:
        """The AF / AH / AJ bounded fixture-namespace devpts
        inventory (017-ae software, extended by 017-ai):
        the ONE exact NON-PTY probe form admitted for the
        canonical 017-af, 017-ah and 017-aj entries,
        selected from this owner's OWN frozen context (a
        caller can never mint it; every other entry's guard
        refuses the form — AB and AD keep their byte-for-byte
        old closed argv sets).  The probe runs INSIDE the
        container through the owner's scoped guarded exec
        channel as the frozen owner exec user, against the
        MEASURED target CID (a failed or unreadable query is
        a closed typed refusal — a failed query is never
        absence), and the retained closed record is parsed by
        the pure consumer into typed inventory facts (the
        measured devpts policy fact included — the permitted
        node GID/mode and filesystem type, bound to the same
        measured namespace root, never assumed from the
        process identity)."""
        ctx = self._owner_context
        if ctx is None or ctx.order_id not in (AF_ORDER_ID, AH_ORDER_ID, AJ_ORDER_ID):
            raise FixtureError("local-devpts-not-admitted")
        if self.status != "running":
            # the attach-baseline window is the LIVE prepared
            # phase only: an aborting or converged owner's
            # namespace is about to be torn down, never
            # inventoried
            raise FixtureError("local-devpts-phase-invalid")
        if self.terminal_outcome is not None:
            # the owner has converged: the attach-baseline
            # window is closed (a converged owner's namespace
            # is about to be torn down, never inventoried)
            raise FixtureError("local-devpts-owner-converged")
        if not isinstance(self.target_cid, str):
            raise FixtureError("local-devpts-target-unmeasured")
        # the SAME frozen identity context is revalidated at
        # THIS actual use site (the bounded current-ID
        # coherence read — compared, never rebased): a
        # drifted host identity can never open the probe
        self._revalidate_identity_context()
        # the per-probe ABSOLUTE end: min(start + the probe's
        # own 5 s, the ORIGINAL owner END anchor) — the
        # cleanup grace is convergence, never fresh
        # measurement.  The guard's clamp uses the
        # grace-inclusive remaining budget, so the ACTUAL
        # guarded call is bounded by this end directly
        # (passing the end-relative remainder, never the
        # constant 5 s), and a late successful return is a
        # closed refusal
        start = time.monotonic()
        end = min(start + ci.DEVPTS_PROBE_TIMEOUT, self.deadline.anchor)
        now = time.monotonic()
        if now >= end:
            raise FixtureError("local-devpts-end-expired")
        argv = [
            "docker",
            "exec",
            "--user",
            ctx.exec_user,
            self.target_cid,
            "python3",
            "-I",
            "-S",
            "-c",
            ci.DEVPTS_PROBE,
        ]
        result = self.guarded(argv, end - now)
        if time.monotonic() >= end:
            # a late successful return is a closed refusal:
            # the measured result crossed the absolute end
            raise FixtureError("local-devpts-end-expired")
        if result.returncode != 0:
            raise FixtureError("local-devpts-exec-failed")
        raw = result.output
        if not isinstance(raw, (bytes, bytearray)):
            raise FixtureError("local-devpts-capture-invalid")
        # the COMPLETE capture law: the measured drained total
        # (retained + discarded) must be strict, bounded and
        # EXACTLY the retained bytes — a retained valid JSON
        # prefix with discarded extra output is not a
        # complete observation
        drained = result.drained_bytes
        if (
            isinstance(drained, bool)
            or not isinstance(drained, int)
            or drained < 0
            or drained > ci.DEVPTS_OUTPUT_MAX
            or drained != len(raw)
        ):
            raise FixtureError("local-devpts-capture-invalid")
        if len(raw) > ci.DEVPTS_OUTPUT_MAX:
            raise FixtureError("local-devpts-output-overbound")
        observation = fixture_prep.parse_devpts_inventory_record(bytes(raw))
        # the MEASURED probe uid is the frozen subject uid:
        # the probe runs as the frozen owner exec user, so a
        # record carrying any other measured uid contradicts
        # the frozen context — a closed typed refusal at the
        # owner's measurement boundary (compared, never
        # rebased or normalized to the frozen value)
        if observation.inventory.uid != ctx.subject_uid:
            raise FixtureError("local-devpts-probe-uid-mismatch")
        # and the frozen identity is revalidated at RETURN as
        # well: a host identity that drifted during the probe
        # can never carry its result into the frozen context
        self._revalidate_identity_context()
        # the end is re-checked AFTER the final identity
        # revalidation and immediately before the receipt
        # commits (the caller freezes this observation)
        if time.monotonic() >= end:
            raise FixtureError("local-devpts-end-expired")
        return observation

    def _build_pass_evidence(self) -> dict[str, object]:
        if (
            self.export_payload is None
            or self.prepared is None
            or self.confinement_facts is None
            or self.subject_facts is None
            or self.pty_facts is None
            or self.image_id is None
            or self.finish_observed is None
            or self.finish_ledger_requests is None
        ):
            raise FixtureError("internal")
        cid = self.target_cid
        assert cid is not None
        if self._owner_context is not None and self._owner_context.order_id == AJ_ORDER_ID:
            # The canonical 017-aj entry selects its OWN closed
            # format-capture scenario before startup: the fixture is
            # consumed by that scenario's workload, and the
            # truthful consumption facts are the validated format
            # snapshot's model POSTs and case qualifications (the
            # AJ format traffic does not consume the legacy
            # one-shot diagnostic; its observed diagnostic state is
            # recorded as measured, never interpreted).
            fixture_consumed_by = "format-capture"
        elif self.consumed is not None:
            fixture_consumed_by = "python-rehearsal"
        elif self.finish_observed["diagnostic_state"] == "unobserved":
            fixture_consumed_by = "unobserved"
        else:
            # Measured, never claimed: the controller's own closed
            # state says the one-shot diagnostic is observed while
            # the S Python consumer never ran on this run — a
            # separate principal consumed it.
            fixture_consumed_by = "external"
        phases: dict[str, object] = {
            "prepare": {
                "cid": cid,
                "cleanup": "absent-verified",
                "confinement": self.confinement_facts,
                "subject": self.subject_facts,
                "pty": {
                    "pty_attached": True,
                    "profile_file": self.pty_facts["profile_file"],
                    "profile_sha256": self.pty_facts["profile_sha256"],
                    "profile_table_used": False,
                    "env_handoff_verified": True,
                    "workspace": self.pty_facts["workspace"],
                },
                "observed": self.prepared["observed"],
            },
            "finish": {
                "cid": cid,
                "cleanup": "absent-verified",
                "export_sha256": self.export_sha,
                "quiesce": "closed-pass",
                "export_revalidated": True,
                # Measured facts from the ACTUAL closed observation
                # and the export snapshot (the S rehearsal's exact
                # Python-specific values are enforced by the
                # validator for the python-rehearsal variant).
                "observed_at_position": self.finish_position,
                "controller_ledger_requests": self.finish_ledger_requests,
                "observed_at_finish": dict(self.finish_observed),
                "retained_capture_bytes": len(self.export_payload),
            },
        }
        if fixture_consumed_by == "python-rehearsal":
            phases["consume"] = {
                "cid": cid,
                "cleanup": "absent-verified",
                "valid_admitted": True,
                "wrong_refused": True,
                "missing_refused": True,
                "diagnostic_response": "fixed-final-text-no-tools",
                "requests": 3,
                "attempts": 3,
                "admitted": 1,
                "refused": 2,
            }
        return {
            "record": SCHEMA,
            "status": "pass",
            "order": ORDER_ID,
            "run_id": self.run_id,
            "bind_head": self.optin["bind_head"],
            "native_started": False,
            "worker_stopped": False,
            "codex_invoked": False,
            "native_ready": False,
            "fixture_consumed_by": fixture_consumed_by,
            "deadline_expired": False,
            "prepared": {
                "cid": cid,
                "state": "prepared-unconsumed",
                "observed": self.prepared["observed"],
                "env_file_sha256": self.prepared["env_file_sha256"],
                "env_file_keys": list(ENV_FILE_KEYS),
                "disposition": _PREPARED_DISPOSITION[fixture_consumed_by],
            },
            "phases": phases,
            "engine_version": self.engine_version,
            "runtime_name": self.runtime_name,
            "runtime_version": self.runtime_version,
            "base_image": ci.PINNED_BASE,
            "image_id": self.image_id,
            "image_identity_vs_ci": self.image_id == R_CI_IMAGE_ID,
            "image_state": "absent-verified",
            "artifact": self._artifact_record(),
            "teardown": {
                "container_present_before": True,
                "container_removal": "absent-verified",
                "image_removal": "absent-verified",
                "descendants_before": self.descendants_before,
                "descendants_after": 0,
                "sentinel_survived": True,
            },
            "ledger": _ledger_facts(self.ledger),
            "attach_plan": {
                "argv": list(ATTACH_PLAN["argv"]),
                "workdir": ATTACH_PLAN["workdir"],
                "env_file_keys": list(ENV_FILE_KEYS),
                "executed": False,
            },
            "env_file": {
                "sha256": self.env_file_digest,
                "keys": list(ENV_FILE_KEYS),
                "removed": True,
            },
            "export": {
                "sha256": self.export_sha,
                "bytes": len(self.export_payload),
                "payload_b64": base64.b64encode(self.export_payload).decode("ascii"),
            },
            "supervisor": {"converged": True, "backstop": False},
            **_runner_facts(),
        }

    def _build_fail_evidence(self, deadline_expired: bool) -> dict[str, object]:
        return {
            "record": SCHEMA,
            "status": "fail",
            "order": ORDER_ID,
            "run_id": self.run_id,
            "bind_head": self.optin["bind_head"],
            "native_started": False,
            "worker_stopped": False,
            "codex_invoked": False,
            "native_ready": False,
            "deadline_expired": deadline_expired,
            "reason": self.failure_reason,
            "stage": self.failure_stage,
            "cleanup_failures": sorted(set(self.cleanup_failures)),
            "phases_completed": sorted(self.phases_completed),
            # The exact recovery registry (the protected intent a
            # later separately-authorized recovery may read): the
            # registered CIDs, the fresh create name, the image id
            # (when learned), the build intent, and the env file
            # (when not yet removed).  ``recovery_state_retained``
            # records whether the protected control-root state
            # (registry + ledger) survived outside the destroyed
            # scratch because cleanup was unverified.
            "resources": {
                "containers": list(self.created),
                "create_intent": self.create_intent,
                "image_id": self.image_id,
                "build_attempted": self.build_attempted,
                "env_file": str(self.env_file) if self.env_file is not None else None,
            },
            "recovery_state_retained": self._recovery_state_retained,
            "ledger": _ledger_facts(self.ledger),
            **_runner_facts(),
        }

    def _build_native_pass_evidence(self) -> dict[str, object]:
        """The DISTINCT native-scope terminal record for a
        new-order bound run: the SAME measured owner state and
        cleanup facts as the S pass record, minus the historical
        S whole-run false assertions (a native run that observed
        a native subject must never assert them) and the
        S-only CI-image comparison (out of scope for this
        record — the measured native-owner record carries the
        image identity)."""
        evidence = self._build_pass_evidence()
        for key in (
            "native_started",
            "worker_stopped",
            "codex_invoked",
            "native_ready",
            "image_identity_vs_ci",
        ):
            del evidence[key]
        assert self._native_binding is not None
        evidence["record"] = NATIVE_OWNER_RUN_EVIDENCE_SCHEMA
        evidence["scope"] = NATIVE_OWNER_RUN_SCOPE
        evidence["order"] = self._native_binding.order_id
        if self._owner_context is not None:
            evidence.update(self._owner_evidence_extra())
        return evidence

    def _owner_evidence_extra(self) -> dict[str, object]:
        """The DISTINCT owner-UID terminal record extras (the
        canonical 017-ab, 017-ad, 017-af and 017-ah entries;
        017-aa / 017-ac / 017-ae):
        the frozen owner identity substructure (the canonical
        profile description's measured context — collected and
        derived by THIS owner, never caller-authored) and the
        exact-CID teardown proof marker (the owner-UID subject
        removal proof is exact registered CID membership; the
        S-shaped teardown dict itself stays byte-for-byte the
        original).  The tag/scope are THIS entry's OWN distinct
        closed record form (the AB tag is never the AD entry's
        record and vice versa — separate closed grammars, never
        a widened grammar)."""
        assert self._owner_context is not None
        ctx = self._owner_context
        # Each entry names its OWN closed record form
        # explicitly: an unexpected order id in a frozen context
        # is an internal invariant violation, never a silent
        # relabel to another entry's form.
        if ctx.order_id == AB_ORDER_ID:
            record_tag, scope = AB_OWNER_RUN_EVIDENCE_SCHEMA, AB_OWNER_RUN_SCOPE
        elif ctx.order_id == AD_ORDER_ID:
            record_tag, scope = AD_OWNER_RUN_EVIDENCE_SCHEMA, AD_OWNER_RUN_SCOPE
        elif ctx.order_id == AF_ORDER_ID:
            record_tag, scope = AF_OWNER_RUN_EVIDENCE_SCHEMA, AF_OWNER_RUN_SCOPE
        elif ctx.order_id == AH_ORDER_ID:
            record_tag, scope = AH_OWNER_RUN_EVIDENCE_SCHEMA, AH_OWNER_RUN_SCOPE
        elif ctx.order_id == AJ_ORDER_ID:
            record_tag, scope = AJ_OWNER_RUN_EVIDENCE_SCHEMA, AJ_OWNER_RUN_SCOPE
        else:
            raise FixtureError("internal")
        return {
            "record": record_tag,
            "scope": scope,
            "identity": {
                "profile": ctx.profile.profile,
                "fingerprint": ctx.fingerprint,
                "subject_uid": ctx.subject_uid,
                "subject_gid": ctx.subject_gid,
                "subject_groups": list(ctx.subject_groups),
                "profile_data_sha256": ctx.profile_data_sha256,
            },
            "teardown_proof": "exact-cid-membership",
        }

    def _build_native_fail_evidence(self, deadline_expired: bool) -> dict[str, object]:
        """The DISTINCT native-scope fail record for a new-order
        bound run: the SAME measured facts as the S fail record,
        minus the historical S whole-run false assertions."""
        evidence = self._build_fail_evidence(deadline_expired)
        for key in ("native_started", "worker_stopped", "codex_invoked", "native_ready"):
            del evidence[key]
        assert self._native_binding is not None
        evidence["record"] = NATIVE_OWNER_RUN_EVIDENCE_SCHEMA
        evidence["scope"] = NATIVE_OWNER_RUN_SCOPE
        evidence["order"] = self._native_binding.order_id
        if self._owner_context is not None:
            evidence.update(self._owner_evidence_extra())
        return evidence


# -- closed evidence validation ------------------------------------------------------
def _is_int(v: object, *, minimum: int = 0) -> bool:
    return isinstance(v, int) and not isinstance(v, bool) and v >= minimum


def _is_sha256(v: object) -> bool:
    return isinstance(v, str) and re.fullmatch(r"[0-9a-f]{64}", v) is not None


_SUBJECT_FACT_KEYS = {
    "swap_source",
    "uid",
    "gid",
    "groups",
    "keyring_errno",
    "memory_limit_bytes",
    "pids_limit",
    "cpu_limit",
    "writable_mounts",
    "mounts_scanned",
    "masked_null_aliases",
}


# The truthful terminal disposition of the ONE prepared instance,
# per exact consumption variant (a held instance that was never
# consumed, or that a separate principal consumed, is never
# labelled as python-rehearsal-consumed).
_PREPARED_DISPOSITION = {
    "python-rehearsal": "consumed-by-python-rehearsal",
    "unobserved": "finished-unconsumed",
    "external": "consumed-by-external-subject",
    # The canonical 017-aj entry consumes the fixture through its
    # OWN closed format-capture workload: the truthful consumption
    # facts are the validated format snapshot's model POSTs and case
    # qualifications, never a legacy diagnostic consumption.
    "format-capture": "consumed-by-format-capture",
}


def _validate_subject_facts(
    facts: object,
    subject_uid: int = model.SUBJECT_UID,
    subject_gid: int = model.SUBJECT_UID,
    tmpfs_budgets: tuple[tuple[str, int, int, int], ...] | None = None,
) -> None:
    """Closed revalidation of the curated subject facts against the
    APPROVED R model contract (the same constants and finite laws
    ``model.validate_exec_measurement`` enforces on the full
    record): exact subject identity for uid AND gid (exact
    integers, not numeric equality — the fixed-21002 defaults for
    the historical records; the owner-UID AB record passes its
    frozen independent expectation and the owner tmpfs budget
    through these private parameters, the public v1 law stays
    byte-for-byte), the strict group variant law,
    the exact keyring denial errno for every probe, the exact
    configured memory/pids/cpu limits (exact integers — booleans
    and floats are not limits), the closed swap-source enum, the
    EXACT configured writable-mount identities (every documented
    root present exactly once, configured size/owner/mode per
    root, the SHM measured size inside its explicit bound, the
    finite reconciled data total), and the coherent finite
    scanned-table relation (data mounts + masked aliases within
    the scanned table, bounded by the scanner's closed record
    cap).  Presence or nonnegative checks alone are NOT
    revalidation: a forged final record can never pass the closed
    contract, and no raw value is reflected."""
    if not isinstance(facts, dict) or set(facts) != _SUBJECT_FACT_KEYS:
        raise FixtureError("local-evidence-invalid")
    budgets = (
        model.FixtureBudgets(tmpfs_budgets=tmpfs_budgets)
        if tmpfs_budgets is not None
        else model.FixtureBudgets()
    )
    if not _is_int(facts["uid"]) or facts["uid"] != subject_uid:
        raise FixtureError("local-evidence-invalid")
    if not _is_int(facts["gid"]) or facts["gid"] != subject_gid:
        raise FixtureError("local-evidence-invalid")
    groups = facts["groups"]
    # The strict group variant law: only [] or [the subject's own
    # primary gid] (an added group can never grant a privilege the
    # exact owned run does not already carry).
    if (
        not isinstance(groups, list)
        or not all(_is_int(g) for g in groups)
        or groups not in ([], [subject_gid])
    ):
        raise FixtureError("local-evidence-invalid")
    keyring = facts["keyring_errno"]
    if (
        not isinstance(keyring, dict)
        or set(keyring) != set(model.KEYRING_PROBES)
        or any(not _is_int(v) or v != model.KEYRING_ERRNO for v in keyring.values())
    ):
        raise FixtureError("local-evidence-invalid")
    if (
        not _is_int(facts["memory_limit_bytes"])
        or facts["memory_limit_bytes"] != budgets.memory_limit_bytes
    ):
        raise FixtureError("local-evidence-invalid")
    if not _is_int(facts["pids_limit"]) or facts["pids_limit"] != budgets.pids_limit:
        raise FixtureError("local-evidence-invalid")
    if not _is_int(facts["cpu_limit"]) or facts["cpu_limit"] != budgets.cpu_limit:
        raise FixtureError("local-evidence-invalid")
    if (
        not isinstance(facts["swap_source"], str)
        or facts["swap_source"] not in model.SWAP_SOURCE_ENUM
    ):
        raise FixtureError("local-evidence-invalid")
    # The EXACT configured writable-data surface (the R contract):
    # the configured tmpfs budgets PLUS the daemon's explicitly
    # bounded /dev/shm — every documented root present exactly
    # once, with its configured size/owner/mode (SHM measured size
    # may only stay inside its explicit bound).
    configured = {mount: (size, uid, gid) for mount, size, uid, gid in budgets.tmpfs_budgets}
    configured[model.SHM_MOUNT] = (model.SHM_SIZE_BYTES, *model.SHM_OWNER)
    mounts = facts["writable_mounts"]
    if (
        not isinstance(mounts, list)
        or len(mounts) == 0
        or len(mounts) > 64
        or any(
            not isinstance(entry, dict)
            or set(entry) != {"root", "size_bytes", "uid", "gid", "mode"}
            or not isinstance(entry["root"], str)
            or not entry["root"].startswith("/")
            or not _is_int(entry["size_bytes"], minimum=1)
            or not _is_int(entry["uid"])
            or not _is_int(entry["gid"])
            or not _is_int(entry["mode"])
            for entry in mounts
        )
    ):
        raise FixtureError("local-evidence-invalid")
    seen_roots: set[str] = set()
    data_total = 0
    for entry in mounts:
        root = entry["root"]
        if root not in configured or root in seen_roots:
            raise FixtureError("local-evidence-invalid")
        seen_roots.add(root)
        size, uid, gid = configured[root]
        measured = entry["size_bytes"]
        if root == model.SHM_MOUNT:
            if measured > size:
                raise FixtureError("local-evidence-invalid")
        elif measured != size:
            raise FixtureError("local-evidence-invalid")
        if entry["uid"] != uid or entry["gid"] != gid:
            raise FixtureError("local-evidence-invalid")
        if root == model.SHM_MOUNT:
            allowed_modes = (model.SHM_MODE,)
        elif uid == model.CONTROLLER_UID:
            allowed_modes = model.CONTROLLER_MOUNT_MODES
        else:
            allowed_modes = model.SUBJECT_MOUNT_MODES
        if entry["mode"] not in allowed_modes:
            raise FixtureError("local-evidence-invalid")
        data_total += measured
    if seen_roots != set(configured):
        raise FixtureError("local-evidence-invalid")
    if data_total > model.WRITABLE_DATA_TOTAL_MAX_BYTES:
        raise FixtureError("local-evidence-invalid")
    # The coherent finite table relation (the R contract): the
    # documented data mounts and the masked /dev/null aliases are
    # distinct records WITHIN the scanned mount table, bounded by
    # the stand-in scanner's closed record cap.
    scanned = facts["mounts_scanned"]
    aliases = facts["masked_null_aliases"]
    if (
        not _is_int(scanned, minimum=1)
        or scanned > model.MOUNTINFO_SCANNER_MAX_RECORDS
        or not _is_int(aliases)
        or len(mounts) + aliases > scanned
    ):
        raise FixtureError("local-evidence-invalid")


def _validate_prepared_entry(
    entry: object,
    consumed_by: str,
    *,
    entry_order: str | None = None,
) -> None:
    if (
        not isinstance(entry, dict)
        or set(entry)
        != {"cid", "state", "observed", "env_file_sha256", "env_file_keys", "disposition"}
        or not ci._is_cid(str(entry["cid"]))
        or entry["state"] != "prepared-unconsumed"
        or entry["disposition"] != _PREPARED_DISPOSITION[consumed_by]
        or not _is_sha256(entry["env_file_sha256"])
        or tuple(entry["env_file_keys"]) != ENV_FILE_KEYS
    ):
        raise FixtureError("local-evidence-invalid")
    observed = entry["observed"]
    # The observed PREPARE state is the ACTUAL closed measurement
    # for the entry's OWN scenario: the AJ entry's closed
    # format-capture scenario keeps the exact same closed
    # zero-traffic initial state under its own declared scenario.
    expected_scenario = rprofile.AJ_FORMAT_SCENARIO if entry_order == AJ_ORDER_ID else "diagnostic"
    if (
        not isinstance(observed, dict)
        or set(observed) != {"scenario", "wire_requests", "diagnostic_state"}
        or observed["scenario"] != expected_scenario
        or observed["wire_requests"] != 0
        or observed["diagnostic_state"] != "unobserved"
    ):
        raise FixtureError("local-evidence-invalid")


def _validate_phases(
    phases: object,
    consumed_by: str,
    *,
    subject_uid: int = ci.SUBJECT_UID,
    subject_gid: int = ci.SUBJECT_UID,
    tmpfs_budgets: tuple[tuple[str, int, int, int], ...] | None = None,
    entry_order: str | None = None,
) -> str:
    """Closed validation of the phase facts for the exact
    CONSUMPTION VARIANT: the S python-rehearsal record carries the
    consume phase with its exact Python-specific constants (causal
    position 0, empty issued calls, the exact 3+2 controller
    ledger); the unobserved and external variants have NO consume
    phase and their finish facts are the ACTUAL measured closed
    observation (monotonic controller ledger, diagnostic state
    identity) — a forged or cross-variant combination can never
    validate as pass.  The subject-identity expectations default
    to the historical fixed 21002 law (the public S/native
    wrappers pass nothing); the owner-UID AB evidence wires the
    frozen independent subject UID/GID and owner tmpfs budgets
    through these private parameters — measured facts are never
    normalized to 21002."""
    if not isinstance(phases, dict):
        raise FixtureError("local-evidence-invalid")
    if consumed_by == "python-rehearsal":
        if set(phases) != {"prepare", "consume", "finish"}:
            raise FixtureError("local-evidence-invalid")
    elif set(phases) != {"prepare", "finish"}:
        raise FixtureError("local-evidence-invalid")
    cids = set()
    prepare = phases["prepare"]
    if (
        not isinstance(prepare, dict)
        or set(prepare) != {"cid", "cleanup", "confinement", "subject", "pty", "observed"}
        or not ci._is_cid(str(prepare["cid"]))
        or prepare["cleanup"] != "absent-verified"
    ):
        raise FixtureError("local-evidence-invalid")
    cids.add(prepare["cid"])
    if not isinstance(prepare["confinement"], dict) or prepare["confinement"] != {
        "log_config": "none",
        "config_user": f"{ci.CONTROLLER_UID}:{ci.CONTROLLER_UID}",
    }:
        raise FixtureError("local-evidence-invalid")
    _validate_subject_facts(
        prepare["subject"],
        subject_uid=subject_uid,
        subject_gid=subject_gid,
        tmpfs_budgets=tmpfs_budgets,
    )
    pty = prepare["pty"]
    if (
        not isinstance(pty, dict)
        or set(pty)
        != {
            "pty_attached",
            "profile_file",
            "profile_sha256",
            "profile_table_used",
            "env_handoff_verified",
            "workspace",
        }
        or pty["pty_attached"] is not True
        or pty["profile_table_used"] is not False
        or pty["env_handoff_verified"] is not True
        or not isinstance(pty["profile_file"], str)
        or not _is_sha256(pty["profile_sha256"])
    ):
        raise FixtureError("local-evidence-invalid")
    workspace = pty["workspace"]
    if (
        not isinstance(workspace, dict)
        or set(workspace) != {"path", "mode", "uid"}
        or workspace["path"] != "/run/slaif-subj/work"
        or workspace["mode"] != 0o700
        or workspace["uid"] != subject_uid
    ):
        raise FixtureError("local-evidence-invalid")
    expected_prepare_scenario = (
        rprofile.AJ_FORMAT_SCENARIO if entry_order == AJ_ORDER_ID else "diagnostic"
    )
    if (
        not isinstance(prepare["observed"], dict)
        or set(prepare["observed"]) != {"scenario", "wire_requests", "diagnostic_state"}
        or prepare["observed"]
        != {
            "scenario": expected_prepare_scenario,
            "wire_requests": 0,
            "diagnostic_state": "unobserved",
        }
    ):
        raise FixtureError("local-evidence-invalid")
    if consumed_by == "python-rehearsal":
        consume = phases["consume"]
        if (
            not isinstance(consume, dict)
            or set(consume)
            != {
                "cid",
                "cleanup",
                "valid_admitted",
                "wrong_refused",
                "missing_refused",
                "diagnostic_response",
                "requests",
                "attempts",
                "admitted",
                "refused",
            }
            or not ci._is_cid(str(consume["cid"]))
            or consume["cleanup"] != "absent-verified"
            or consume["valid_admitted"] is not True
            or consume["wrong_refused"] is not True
            or consume["missing_refused"] is not True
            or consume["diagnostic_response"] != "fixed-final-text-no-tools"
            or consume["requests"] != 3
            or consume["attempts"] != 3
            or consume["admitted"] != 1
            or consume["refused"] != 2
        ):
            raise FixtureError("local-evidence-invalid")
        cids.add(consume["cid"])
    finish = phases["finish"]
    if (
        not isinstance(finish, dict)
        or set(finish)
        != {
            "cid",
            "cleanup",
            "export_sha256",
            "quiesce",
            "export_revalidated",
            "observed_at_position",
            "controller_ledger_requests",
            "observed_at_finish",
            "retained_capture_bytes",
        }
        or not ci._is_cid(str(finish["cid"]))
        or finish["cleanup"] != "absent-verified"
        or not _is_sha256(finish["export_sha256"])
        or finish["quiesce"] != "closed-pass"
        or finish["export_revalidated"] is not True
        or not isinstance(finish["observed_at_finish"], dict)
        or set(finish["observed_at_finish"]) != {"scenario", "wire_requests", "diagnostic_state"}
        or finish["observed_at_finish"]["scenario"]
        != (rprofile.AJ_FORMAT_SCENARIO if entry_order == AJ_ORDER_ID else "diagnostic")
        or not _is_int(finish["observed_at_finish"]["wire_requests"])
        or finish["observed_at_finish"]["diagnostic_state"] not in ("unobserved", "observed")
        or not _is_int(finish["retained_capture_bytes"], minimum=1)
    ):
        raise FixtureError("local-evidence-invalid")
    position = finish["observed_at_position"]
    ledger_requests = finish["controller_ledger_requests"]
    observed = finish["observed_at_finish"]
    # The ACTUAL closed observation coherence law (every variant):
    # the controller's own ledger is monotonic across the
    # observe->export window and always carries the two exporter
    # commands, bounded by the closed budget; the one-shot
    # diagnostic state in the payload matches the observed state.
    if (
        not _is_int(ledger_requests, minimum=2)
        or ledger_requests > model.FixtureBudgets().max_requests
        or ledger_requests < observed["wire_requests"]
    ):
        raise FixtureError("local-evidence-invalid")
    if consumed_by == "format-capture":
        # The AJ format scenario carries NO legacy one-shot
        # diagnostic position (the truthful format coordinates are
        # inside the validated snapshot); the observed diagnostic
        # state is a measured fact, never interpreted as format
        # consumption or absence of traffic.
        if position is not None:
            raise FixtureError("local-evidence-invalid")
    elif observed["diagnostic_state"] == "unobserved":
        if position is not None:
            raise FixtureError("local-evidence-invalid")
    elif not _is_int(position, minimum=0):
        raise FixtureError("local-evidence-invalid")
    if consumed_by == "python-rehearsal":
        # The S Python-specific qualification (exact measured
        # constants of the rehearsal consume).
        if (
            position != 0
            or ledger_requests != 5
            or observed
            != {"scenario": "diagnostic", "wire_requests": 3, "diagnostic_state": "observed"}
        ):
            raise FixtureError("local-evidence-invalid")
    elif consumed_by == "unobserved":
        if observed["diagnostic_state"] != "unobserved":
            raise FixtureError("local-evidence-invalid")
    elif consumed_by == "format-capture":
        # no legacy diagnostic assertion (see above): the format
        # workload's truthful facts are in the validated snapshot
        pass
    elif consumed_by != "external":
        raise FixtureError("local-evidence-invalid")
    elif observed["diagnostic_state"] != "observed":
        raise FixtureError("local-evidence-invalid")
    cids.add(finish["cid"])
    if len(cids) != 1:
        # ONE prepared instance: every phase fact is about the SAME
        # exact CID (never combined facts from unrelated CIDs).
        raise FixtureError("local-evidence-invalid")
    return str(cids.pop())


def _validate_export(
    export: object,
    consumed_by: str,
    observed_wire: int,
    *,
    entry_order: str | None = None,
) -> dict[str, object]:
    """Closed revalidation of the retained export binding for the
    EXACT CONSUMPTION VARIANT: the decoded selected payload must be
    a closed record whose one-shot diagnostic and causal position
    match the variant's measured law, and whose controller ledger
    is the measured wire history PLUS exactly the two exporter
    commands (quiesce + export) issued in the same finish
    operation — a coherent closed relation for every variant,
    never a python-rehearsal-only constant.  Returns the validated
    DECODED record so the caller can cross-bind the outer summary
    facts to the payload itself (separate range checks do not
    establish summary == payload)."""
    if (
        not isinstance(export, dict)
        or set(export) != {"sha256", "bytes", "payload_b64"}
        or not _is_sha256(export["sha256"])
        or not _is_int(export["bytes"], minimum=1)
        or export["bytes"] > model.FixtureBudgets().max_export_bytes
        or not isinstance(export["payload_b64"], str)
    ):
        raise FixtureError("local-evidence-invalid")
    try:
        decoded = base64.b64decode(export["payload_b64"], validate=True)
    except (ValueError, TypeError):
        raise FixtureError("local-evidence-invalid") from None
    if len(decoded) != export["bytes"] or hashlib.sha256(decoded).hexdigest() != export["sha256"]:
        raise FixtureError("local-evidence-invalid")
    # The DECODED selected payload is itself revalidated as a closed
    # record, including the diagnostic-state identity against the
    # closed single-source derivation (the embedded bytes can never
    # carry raw or foreign content).
    if entry_order == AJ_ORDER_ID:
        # The AJ entry's retained export is the DISTINCT closed
        # format-capture payload: the closed record tag selects the
        # full or the safe partial format law, and the untagged
        # six-field legacy form is drift under AJ, refused and never
        # relabelled.  The format snapshot's own closed law already
        # re-validates the issued calls, the case coordinates and
        # the truthful model-POST ledger count; the retained-binding
        # law here is the SAME measured wire-history relation (the
        # observed wire plus exactly the two exporter commands).
        try:
            selected = fixture_export.validate_selected_payload(decoded)
        except ValueError:
            raise FixtureError("local-evidence-invalid") from None
        if selected.get("record") not in (
            model.SCHEMA_FORMAT_EXPORT,
            model.SCHEMA_FORMAT_EXPORT_PARTIAL,
        ):
            raise FixtureError("local-evidence-invalid")
        snapshot = selected["snapshot"]
        ledger = snapshot["controller_ledger"]["requests"]
        if (
            not _is_int(ledger)
            or not _is_int(observed_wire, minimum=0)
            or ledger != observed_wire + 2
        ):
            raise FixtureError("local-evidence-invalid")
        return selected
    try:
        selected = fixture_export.validate_payload(decoded)
    except ValueError:
        raise FixtureError("local-evidence-invalid") from None
    snapshot = selected["snapshot"]
    position = selected["observed_at_position"]
    ledger = snapshot["controller_ledger"]["requests"]
    if not _is_int(ledger) or not _is_int(observed_wire, minimum=0) or ledger != observed_wire + 2:
        raise FixtureError("local-evidence-invalid")
    if snapshot["issued_calls"] != []:
        raise FixtureError("local-evidence-invalid")
    if consumed_by == "python-rehearsal":
        # The S rehearsal's exact Python-specific qualification:
        # the fixed single-source no-tools diagnostic metadata at
        # causal position 0 (the first admitted POST).
        if (
            selected["diagnostic"] != model.bounds_diagnostic(fixture_standin._fixed_request([]))
            or not isinstance(position, int)
            or isinstance(position, bool)
            or position != 0
        ):
            raise FixtureError("local-evidence-invalid")
    elif consumed_by == "unobserved":
        if selected["diagnostic"] != {"state": "unobserved"} or position is not None:
            raise FixtureError("local-evidence-invalid")
    elif consumed_by == "external":
        # A separate principal consumed the one-shot diagnostic:
        # the payload must carry a closed OBSERVED metadata
        # diagnostic (validated as a closed object above — the
        # subject's own request-derived bounds; a tool-bearing
        # external request is never assumed to equal the Python
        # rehearsal's empty-tools metadata) at a measured causal
        # position, never the unobserved marker.
        if (
            selected["diagnostic"] == {"state": "unobserved"}
            or not isinstance(position, int)
            or isinstance(position, bool)
            or position < 0
        ):
            raise FixtureError("local-evidence-invalid")
    else:
        raise FixtureError("local-evidence-invalid")
    return selected


def _validate_local_evidence_core(
    record: dict,
    *,
    subject_uid: int,
    subject_gid: int,
    tmpfs_budgets: tuple[tuple[str, int, int, int], ...] | None,
    entry_order: str | None = None,
) -> None:
    """The PRIVATE structural core of the S-shaped evidence
    validation: exact key sets at EVERY level, exact closed
    constants (the native flags are ALWAYS False in S), closed
    phase/slug vocabulary, 64-hex CIDs, sha256 digests, the strict
    group variant law, and the embedded export payload DECODED and
    revalidated as a closed object.  The subject-identity
    expectations (phase subject facts, pty workspace owner, the
    writable-mount owner law) are the ONLY parameterized surface:
    the historical fixed-21002 wrappers pass the original
    constants, and the owner-UID AB evidence passes its frozen
    independent subject UID/GID plus owner tmpfs budgets — measured
    facts are NEVER normalized to 21002.  No raw content, env
    values or exception text may enter; a supervisor/owner that
    did not fully converge, or that leaves any cleanup unverified,
    can never validate as pass."""
    if not isinstance(record, dict):
        raise FixtureError("local-evidence-invalid")
    base_keys = {
        "record",
        "status",
        "order",
        "run_id",
        "bind_head",
        "native_started",
        "worker_stopped",
        "codex_invoked",
        "native_ready",
        "deadline_expired",
        "ledger",
        "runner_kernel",
        "runner_arch",
        "runner_python",
    }
    if record.get("record") != SCHEMA or record.get("status") not in ("pass", "fail"):
        raise FixtureError("local-evidence-invalid")
    if record["status"] == "pass":
        expected = base_keys | {
            "fixture_consumed_by",
            "prepared",
            "phases",
            "engine_version",
            "runtime_name",
            "runtime_version",
            "base_image",
            "image_id",
            "image_identity_vs_ci",
            "image_state",
            "artifact",
            "teardown",
            "attach_plan",
            "env_file",
            "export",
            "supervisor",
        }
    else:
        expected = base_keys | {
            "reason",
            "stage",
            "cleanup_failures",
            "phases_completed",
            "resources",
            "recovery_state_retained",
        }
    if set(record) != expected:
        raise FixtureError("local-evidence-invalid")
    if record["order"] != ORDER_ID:
        raise FixtureError("local-evidence-invalid")
    if not re.fullmatch(r"[0-9a-f]{32}", str(record["run_id"])):
        raise FixtureError("local-evidence-invalid")
    if not re.fullmatch(r"[0-9a-f]{40}", str(record["bind_head"])):
        raise FixtureError("local-evidence-invalid")
    for constant in ("native_started", "worker_stopped", "codex_invoked", "native_ready"):
        if record[constant] is not False:
            raise FixtureError("local-evidence-invalid")
    if not isinstance(record["deadline_expired"], bool):
        raise FixtureError("local-evidence-invalid")
    ledger = record["ledger"]
    if (
        not isinstance(ledger, dict)
        or set(ledger) != set(_ledger_facts(ci._RunLedger(model.FixtureBudgets())))
        or any(not _is_int(v) for v in ledger.values())
    ):
        raise FixtureError("local-evidence-invalid")
    if ledger["requests_admitted"] + ledger["requests_refused"] != ledger["api_requests"]:
        raise FixtureError("local-evidence-invalid")
    if ledger["api_requests"] > ledger["api_attempts"]:
        raise FixtureError("local-evidence-invalid")
    for key in ("runner_kernel", "runner_arch", "runner_python"):
        if not isinstance(record[key], str) or not record[key]:
            raise FixtureError("local-evidence-invalid")
    if record["status"] == "fail":
        # The reason is a MEASURED fixture token from the closed
        # finite universe — never raw exception text.
        if record["reason"] not in _FAILURE_REASONS:
            raise FixtureError("local-evidence-invalid")
        if record["stage"] not in _FAILURE_STAGES:
            raise FixtureError("local-evidence-invalid")
        if not (
            isinstance(record["cleanup_failures"], list)
            and all(t in _CLEANUP_FAILURE_TOKENS for t in record["cleanup_failures"])
        ):
            raise FixtureError("local-evidence-invalid")
        if not (
            isinstance(record["phases_completed"], list)
            and all(p in _PHASES for p in record["phases_completed"])
        ):
            raise FixtureError("local-evidence-invalid")
        if not isinstance(record["recovery_state_retained"], bool):
            raise FixtureError("local-evidence-invalid")
        resources = record["resources"]
        env_file = resources.get("env_file") if isinstance(resources, dict) else None
        if (
            not isinstance(resources, dict)
            or set(resources)
            != {"containers", "create_intent", "image_id", "build_attempted", "env_file"}
            or not isinstance(resources["containers"], list)
            or len(resources["containers"]) > 16
            or not all(ci._is_cid(c) for c in resources["containers"])
            or (
                resources["create_intent"] is not None
                and not ci._LOCAL_NAME_RE.fullmatch(str(resources["create_intent"]))
            )
            or (
                resources["image_id"] is not None
                and not ci._IMAGE_ID_RE.fullmatch(str(resources["image_id"]))
            )
            or not isinstance(resources["build_attempted"], bool)
            or (
                env_file is not None
                and (
                    not isinstance(env_file, str)
                    or not env_file.startswith("/")
                    or len(env_file) > 4096
                    or "\x00" in env_file
                )
            )
        ):
            raise FixtureError("local-evidence-invalid")
        if record["recovery_state_retained"] and not record["cleanup_failures"]:
            # Retained registry requires unverified cleanup (a clean
            # convergence destroys the control root).
            raise FixtureError("local-evidence-invalid")
        return
    # -- pass variant --
    if entry_order == AJ_ORDER_ID:
        # The AJ entry's closed format-capture variant ONLY: the
        # canonical AJ owner binding is the selection authority
        # (passed by the AJ wrapper from its own verified record
        # tag/order), and every historical entry and default keeps
        # the strict legacy vocabulary.
        if record["fixture_consumed_by"] != "format-capture":
            raise FixtureError("local-evidence-invalid")
    elif record["fixture_consumed_by"] not in ("python-rehearsal", "unobserved", "external"):
        raise FixtureError("local-evidence-invalid")
    if record["deadline_expired"] is not False:
        raise FixtureError("local-evidence-invalid")
    target_cid = _validate_phases(
        record["phases"],
        record["fixture_consumed_by"],
        subject_uid=subject_uid,
        subject_gid=subject_gid,
        tmpfs_budgets=tmpfs_budgets,
        entry_order=entry_order,
    )
    _validate_prepared_entry(
        record["prepared"],
        record["fixture_consumed_by"],
        entry_order=entry_order,
    )
    if record["prepared"]["cid"] != target_cid:
        raise FixtureError("local-evidence-invalid")
    for key in ("engine_version", "runtime_name", "runtime_version"):
        if not isinstance(record[key], str) or not record[key]:
            raise FixtureError("local-evidence-invalid")
    if record["base_image"] != ci.PINNED_BASE:
        raise FixtureError("local-evidence-invalid")
    if not ci._IMAGE_ID_RE.fullmatch(str(record["image_id"])):
        raise FixtureError("local-evidence-invalid")
    if not isinstance(record["image_identity_vs_ci"], bool):
        raise FixtureError("local-evidence-invalid")
    if record["image_state"] != "absent-verified":
        raise FixtureError("local-evidence-invalid")
    try:
        model.validate_artifact_record(record["artifact"])
    except (ValueError, FixtureError):
        raise FixtureError("local-evidence-invalid") from None
    teardown = record["teardown"]
    if (
        not isinstance(teardown, dict)
        or set(teardown)
        != {
            "container_present_before",
            "container_removal",
            "image_removal",
            "descendants_before",
            "descendants_after",
            "sentinel_survived",
        }
        or teardown["container_present_before"] is not True
        or teardown["container_removal"] != "absent-verified"
        or teardown["image_removal"] != "absent-verified"
        or not _is_int(teardown["descendants_before"], minimum=1)
        or teardown["descendants_after"] != 0
        or teardown["sentinel_survived"] is not True
    ):
        raise FixtureError("local-evidence-invalid")
    try:
        validate_attach_plan(record["attach_plan"])
    except FixtureError:
        raise FixtureError("local-evidence-invalid") from None
    env_file = record["env_file"]
    if (
        not isinstance(env_file, dict)
        or set(env_file) != {"sha256", "keys", "removed"}
        or not _is_sha256(env_file["sha256"])
        or tuple(env_file["keys"]) != ENV_FILE_KEYS
        or env_file["removed"] is not True
        or env_file["sha256"] != record["prepared"]["env_file_sha256"]
    ):
        raise FixtureError("local-evidence-invalid")
    selected_export = _validate_export(
        record["export"],
        record["fixture_consumed_by"],
        record["phases"]["finish"]["observed_at_finish"]["wire_requests"],
        entry_order=entry_order,
    )
    # The outer FINISH SUMMARY is the measured payload itself: the
    # retained causal position and the controller ledger in the
    # summary must EQUAL the decoded snapshot/position values (the
    # two range-checked sides are one measurement, never two).
    finish_block = record["phases"]["finish"]
    if entry_order == AJ_ORDER_ID:
        # The AJ format payload carries no legacy observed_at_position:
        # the retained summary must keep the honest absent fact.
        if finish_block["observed_at_position"] is not None:
            raise FixtureError("local-evidence-invalid")
    elif finish_block["observed_at_position"] != selected_export["observed_at_position"]:
        raise FixtureError("local-evidence-invalid")
    if (
        finish_block["controller_ledger_requests"]
        != selected_export["snapshot"]["controller_ledger"]["requests"]
    ):
        raise FixtureError("local-evidence-invalid")
    if record["export"]["sha256"] != record["phases"]["finish"]["export_sha256"]:
        raise FixtureError("local-evidence-invalid")
    if record["export"]["bytes"] != record["phases"]["finish"]["retained_capture_bytes"]:
        raise FixtureError("local-evidence-invalid")
    supervisor = record["supervisor"]
    if (
        not isinstance(supervisor, dict)
        or set(supervisor) != {"converged", "backstop"}
        or supervisor["converged"] is not True
        or supervisor["backstop"] is not False
    ):
        raise FixtureError("local-evidence-invalid")


def validate_local_evidence(record: dict) -> None:
    """Closed-schema validation of the local evidence record: exact
    key sets at EVERY level, exact closed constants (the native
    flags are ALWAYS False in S), closed phase/slug vocabulary,
    64-hex CIDs, sha256 digests, the strict group variant law, and
    the embedded export payload DECODED and revalidated as a closed
    object.  No raw content, env values or exception text may
    enter; a supervisor/owner that did not fully converge, or that
    leaves any cleanup unverified, can never validate as pass.
    The historical fixed-21002 subject law is byte-for-byte the
    original: the shared structural core is called with the
    original constants and default tmpfs budgets."""
    _validate_local_evidence_core(
        record,
        subject_uid=ci.SUBJECT_UID,
        subject_gid=ci.SUBJECT_UID,
        tmpfs_budgets=None,
    )


def validate_native_owner_run_evidence(record: dict) -> None:
    """Closed-schema validation of the DISTINCT native-scope
    owner terminal record (new-order bound runs): the exact key
    set per status — the historical S whole-run false
    assertions are NOT part of this grammar (their absence is
    the point: a native run never asserts them) — the OAP
    order id (any order, not fixed to 017-s), the 32-hex run
    id, the 40-hex bound head, and the SAME closed
    ledger/runner/phase/export/teardown law as the S record.
    The shared measured substructures are validated by the
    private S-shaped structural core over an internal S-shaped
    envelope carrying the IDENTICAL sub-values (a validation
    vehicle, never a retained assertion — the retained record
    itself never carries the S whole-run false assertions or the
    S-only CI-image comparison), with the historical fixed-21002
    subject law (the native scope measures the ORIGINAL subject)."""
    if not isinstance(record, dict):
        raise FixtureError("native-owner-run-evidence-invalid")
    if (
        record.get("record") != NATIVE_OWNER_RUN_EVIDENCE_SCHEMA
        or record.get("scope") != NATIVE_OWNER_RUN_SCOPE
        or record.get("status") not in ("pass", "fail")
    ):
        raise FixtureError("native-owner-run-evidence-invalid")
    _native_key_grammar(record)
    try:
        _validate_local_evidence_core(
            _native_s_envelope(record),
            subject_uid=ci.SUBJECT_UID,
            subject_gid=ci.SUBJECT_UID,
            tmpfs_budgets=None,
        )
    except FixtureError:
        raise FixtureError("native-owner-run-evidence-invalid") from None


def _native_key_grammar(record: dict) -> None:
    """The shared native-scope KEY GRAMMAR (distinct from the
    S-shaped substructure law): the exact key set per status —
    the historical S whole-run false assertions are NOT part of
    this grammar (their absence is the point: a native run never
    asserts them) — the OAP order id (any order, not fixed to
    017-s), the 32-hex run id and the 40-hex bound head.  The
    AB wrapper re-checks this grammar over its AB extras
    stripped, but validates the substructures with its own AB
    subject expectations, never through the fixed-21002 native
    law."""
    base_keys = {
        "record",
        "status",
        "scope",
        "order",
        "run_id",
        "bind_head",
        "deadline_expired",
        "ledger",
        "runner_kernel",
        "runner_arch",
        "runner_python",
    }
    if record["status"] == "pass":
        expected = base_keys | {
            "fixture_consumed_by",
            "prepared",
            "phases",
            "engine_version",
            "runtime_name",
            "runtime_version",
            "base_image",
            "image_id",
            "image_state",
            "artifact",
            "teardown",
            "attach_plan",
            "env_file",
            "export",
            "supervisor",
        }
    else:
        expected = base_keys | {
            "reason",
            "stage",
            "cleanup_failures",
            "phases_completed",
            "resources",
            "recovery_state_retained",
        }
    if (
        set(record) != expected
        or not isinstance(record["order"], str)
        or re.fullmatch(r"^[0-9]{3}-[a-z]{1,2}$", record["order"]) is None
        or not re.fullmatch(r"[0-9a-f]{32}", str(record["run_id"]))
        or not re.fullmatch(r"[0-9a-f]{40}", str(record["bind_head"]))
    ):
        raise FixtureError("native-owner-run-evidence-invalid")


def _native_s_envelope(record: dict) -> dict:
    """The internal S-shaped validation vehicle for the DISTINCT
    native-scope record: the IDENTICAL sub-values under the S
    record/order literals plus the S whole-run false assertions
    (a validation vehicle, never a retained assertion — the
    retained record itself never carries the S whole-run false
    assertions or the S-only CI-image comparison)."""
    envelope = {key: value for key, value in record.items() if key != "scope"}
    envelope["record"] = SCHEMA
    envelope["order"] = ORDER_ID
    envelope["native_started"] = False
    envelope["worker_stopped"] = False
    envelope["codex_invoked"] = False
    envelope["native_ready"] = False
    if record["status"] == "pass":
        envelope["image_identity_vs_ci"] = False
    return envelope


def validate_ab_owner_run_evidence(record: dict) -> None:
    """Closed-schema validation of the DISTINCT owner-UID AB terminal
    record (017-aa): the native-scope grammar (the SAME measured
    owner state, cleanup and publication law) PLUS exactly two
    closed AB-only substructures under the AB record/scope tags:

    * ``identity`` — the frozen owner identity substructure THIS
      owner collected and derived (never caller-authored): the
      canonical owner-UID profile name, the canonical description
      fingerprint, the frozen INDEPENDENT subject UID/GID, the
      exact one-element primary-GID group vector and the profile
      DATA sha256.  The production codec re-derives the canonical
      record from the retained IDs (the controller identity fixed
      21001/21001) and must hash to the retained digest, and the
      retained fingerprint must be its canonical fingerprint: the
      retained identity is closed data integrity — never a
      measured-authority claim.
    * ``teardown_proof`` — the literal exact-CID-membership marker:
      the owner-UID subject removal proof is EXACT registered-CID
      lifetime membership (the owned PID/birth registry), and the
      S-shaped teardown dict itself stays byte-for-byte the
      original.

    The order is the CANONICAL AB entry (``017-ab``) — the generic
    new-order grammar of the native-scope record does NOT apply
    here: an AB-tagged record of any other order id is refused.

    Every shared measured substructure is then validated through
    the SAME private S-shaped structural core over the AB extras
    stripped — with the frozen AB subject UID/GID and the derived
    owner tmpfs budgets wired through (the measured 1001-class
    facts are validated as-is, NEVER normalized to 21002; the
    public v1 S/native wrappers keep the fixed-21002 law
    byte-for-byte)."""
    if not isinstance(record, dict):
        raise FixtureError("ab-owner-run-evidence-invalid")
    if (
        record.get("record") != AB_OWNER_RUN_EVIDENCE_SCHEMA
        or record.get("scope") != AB_OWNER_RUN_SCOPE
        or record.get("status") not in ("pass", "fail")
    ):
        raise FixtureError("ab-owner-run-evidence-invalid")
    # The canonical AB entry ONLY: the AB-tagged grammar is the
    # distinct owner-UID record of 017-ab, and no other order id
    # may carry it (the native-scope generic order law is
    # unchanged and remains the native validator's own).
    if record.get("order") != AB_ORDER_ID:
        raise FixtureError("ab-owner-run-evidence-invalid")
    if record.get("teardown_proof") != "exact-cid-membership":
        raise FixtureError("ab-owner-run-evidence-invalid")
    identity = record.get("identity")
    # the ONE shared structural core (state/evidence/record):
    # the canonical profile name, the strict ID laws, the
    # one-element primary-GID group vector and the production
    # codec re-derivation of both digests — the public wrapper
    # keeps its own fixed refusal token
    law = _identity_substructure_law(identity)
    if law is None:
        raise FixtureError("ab-owner-run-evidence-invalid")
    subject_uid, subject_gid, _expected_groups, description = law
    # The shared measured substructures: the SAME native-scope
    # key grammar (re-checked over the AB extras stripped) plus
    # the S-shaped structural core with the AB subject
    # expectations wired through — the owner profile view is
    # re-derived from the retained identity (production codec, no
    # caller input), and its owner tmpfs budgets are the closed
    # writable-mount expectation.
    reduced = {
        key: value for key, value in record.items() if key not in ("identity", "teardown_proof")
    }
    reduced["record"] = NATIVE_OWNER_RUN_EVIDENCE_SCHEMA
    reduced["scope"] = NATIVE_OWNER_RUN_SCOPE
    try:
        _native_key_grammar(reduced)
    except FixtureError:
        raise FixtureError("ab-owner-run-evidence-invalid") from None
    try:
        profile_view = rprofile.owner_runtime_profile(description)
        _validate_local_evidence_core(
            _native_s_envelope(reduced),
            subject_uid=subject_uid,
            subject_gid=subject_gid,
            tmpfs_budgets=ci.owner_tmpfs_budgets(profile_view),
        )
    except FixtureError:
        raise FixtureError("ab-owner-run-evidence-invalid") from None


def validate_ad_owner_run_evidence(record: dict) -> None:
    """Closed-schema validation of the DISTINCT owner-UID AD
    terminal record (017-ac): the SAME closed measured owner
    state, cleanup and publication law as the AB wrapper, under
    the canonical 017-ad native entry's OWN distinct record/
    scope tags and order binding:

    * ``identity`` — the frozen owner identity substructure
      THIS owner collected and derived (never caller-authored),
      through the SAME shared structural core (canonical
      profile name, strict ID laws, one-element primary-GID
      group vector, production codec re-derivation of both
      digests) — closed data integrity, never a measured-
      authority claim;
    * ``teardown_proof`` — the literal exact-CID-membership
      marker (the owner-UID subject removal proof is exact
      registered-CID lifetime membership; the S-shaped teardown
      dict stays byte-for-byte the original).

    The order is the CANONICAL 017-ad entry ONLY: an AD-tagged
    record of any other order id is refused, and the AB tag is
    a separate closed grammar (never widened to the AD entry,
    including for equal-numeric identities).  Every shared
    measured substructure is validated through the SAME private
    S-shaped structural core over the AD extras stripped — with
    the frozen AD subject UID/GID and the derived owner tmpfs
    budgets wired through (the measured owner facts are
    validated as-is, NEVER normalized to 21002; the public v1
    S/native/AB wrappers keep their closed laws byte-for-byte).
    """
    if not isinstance(record, dict):
        raise FixtureError("ad-owner-run-evidence-invalid")
    if (
        record.get("record") != AD_OWNER_RUN_EVIDENCE_SCHEMA
        or record.get("scope") != AD_OWNER_RUN_SCOPE
        or record.get("status") not in ("pass", "fail")
    ):
        raise FixtureError("ad-owner-run-evidence-invalid")
    # The canonical 017-ad entry ONLY: the AD-tagged grammar is
    # the distinct owner-UID record of 017-ad, and no other
    # order id may carry it (the AB tag and the native-scope
    # generic order law are separate closed grammars).
    if record.get("order") != AD_ORDER_ID:
        raise FixtureError("ad-owner-run-evidence-invalid")
    if record.get("teardown_proof") != "exact-cid-membership":
        raise FixtureError("ad-owner-run-evidence-invalid")
    identity = record.get("identity")
    law = _identity_substructure_law(identity)
    if law is None:
        raise FixtureError("ad-owner-run-evidence-invalid")
    subject_uid, subject_gid, _expected_groups, description = law
    reduced = {
        key: value for key, value in record.items() if key not in ("identity", "teardown_proof")
    }
    reduced["record"] = NATIVE_OWNER_RUN_EVIDENCE_SCHEMA
    reduced["scope"] = NATIVE_OWNER_RUN_SCOPE
    try:
        _native_key_grammar(reduced)
    except FixtureError:
        raise FixtureError("ad-owner-run-evidence-invalid") from None
    try:
        profile_view = rprofile.owner_runtime_profile(description)
        _validate_local_evidence_core(
            _native_s_envelope(reduced),
            subject_uid=subject_uid,
            subject_gid=subject_gid,
            tmpfs_budgets=ci.owner_tmpfs_budgets(profile_view),
        )
    except FixtureError:
        raise FixtureError("ad-owner-run-evidence-invalid") from None


def validate_af_owner_run_evidence(record: dict) -> None:
    """Closed-schema validation of the DISTINCT owner-UID AF
    terminal record (017-ae software): the SAME closed measured
    owner state, cleanup and publication law as the AB wrapper,
    under the canonical 017-af native-PTY qualification
    entry's OWN distinct record/scope tags and order binding:

    * ``identity`` — the frozen owner identity substructure
      THIS owner collected and derived (never caller-authored),
      through the SAME shared structural core (canonical
      profile name, strict ID laws, one-element primary-GID
      group vector, production codec re-derivation of both
      digests) — closed data integrity, never a measured-
      authority claim;
    * ``teardown_proof`` — the literal exact-CID-membership
      marker (the owner-UID subject removal proof is exact
      registered-CID lifetime membership; the S-shaped teardown
      dict stays byte-for-byte the original).

    The order is the CANONICAL 017-af entry ONLY: an AF-tagged
    record of any other order id is refused, and the AB and AD
    tags are separate closed grammars (never widened to the AF
    entry, including for equal-numeric identities).  Every
    shared measured substructure is validated through the SAME
    private S-shaped structural core over the AF extras
    stripped — with the frozen AF subject UID/GID and the
    derived owner tmpfs budgets wired through (the measured
    owner facts are validated as-is, NEVER normalized to 21002;
    the public v1 S/native/AB/AD wrappers keep their closed
    laws byte-for-byte).
    """
    if not isinstance(record, dict):
        raise FixtureError("af-owner-run-evidence-invalid")
    if (
        record.get("record") != AF_OWNER_RUN_EVIDENCE_SCHEMA
        or record.get("scope") != AF_OWNER_RUN_SCOPE
        or record.get("status") not in ("pass", "fail")
    ):
        raise FixtureError("af-owner-run-evidence-invalid")
    # The canonical 017-af entry ONLY: the AF-tagged grammar is
    # the distinct owner-UID record of 017-af, and no other
    # order id may carry it (the AB/AD tags and the native-
    # scope generic order law are separate closed grammars).
    if record.get("order") != AF_ORDER_ID:
        raise FixtureError("af-owner-run-evidence-invalid")
    if record.get("teardown_proof") != "exact-cid-membership":
        raise FixtureError("af-owner-run-evidence-invalid")
    identity = record.get("identity")
    law = _identity_substructure_law(identity)
    if law is None:
        raise FixtureError("af-owner-run-evidence-invalid")
    subject_uid, subject_gid, _expected_groups, description = law
    reduced = {
        key: value for key, value in record.items() if key not in ("identity", "teardown_proof")
    }
    reduced["record"] = NATIVE_OWNER_RUN_EVIDENCE_SCHEMA
    reduced["scope"] = NATIVE_OWNER_RUN_SCOPE
    try:
        _native_key_grammar(reduced)
    except FixtureError:
        raise FixtureError("af-owner-run-evidence-invalid") from None
    try:
        profile_view = rprofile.owner_runtime_profile(description)
        _validate_local_evidence_core(
            _native_s_envelope(reduced),
            subject_uid=subject_uid,
            subject_gid=subject_gid,
            tmpfs_budgets=ci.owner_tmpfs_budgets(profile_view),
        )
    except FixtureError:
        raise FixtureError("af-owner-run-evidence-invalid") from None


def validate_ah_owner_run_evidence(record: dict) -> None:
    """Closed-schema validation of the DISTINCT owner-UID AH
    terminal record (017-ag sealed INERT entry): the SAME closed
    measured owner state, cleanup and publication law as the AB
    wrapper, under the canonical 017-ah native-PTY
    requalification entry's OWN distinct record/scope tags and
    order binding:

    * ``identity`` — the frozen owner identity substructure
      THIS owner collected and derived (never caller-authored),
      through the SAME shared structural core (canonical
      profile name, strict ID laws, one-element primary-GID
      group vector, production codec re-derivation of both
      digests) — closed data integrity, never a measured-
      authority claim;
    * ``teardown_proof`` — the literal exact-CID-membership
      marker (the owner-UID subject removal proof is exact
      registered-CID lifetime membership; the S-shaped teardown
      dict stays byte-for-byte the original).

    The order is the CANONICAL 017-ah entry ONLY: an AH-tagged
    record of any other order id is refused, and the AB, AD and
    AF tags are separate closed grammars (never widened to the
    AH entry, including for equal-numeric identities).  Every
    shared measured substructure is validated through the SAME
    private S-shaped structural core over the AH extras
    stripped — with the frozen AH subject UID/GID and the
    derived owner tmpfs budgets wired through (the measured
    owner facts are validated as-is, NEVER normalized to 21002;
    the public v1 S/native/AB/AD/AF wrappers keep their closed
    laws byte-for-byte).
    """
    if not isinstance(record, dict):
        raise FixtureError("ah-owner-run-evidence-invalid")
    if (
        record.get("record") != AH_OWNER_RUN_EVIDENCE_SCHEMA
        or record.get("scope") != AH_OWNER_RUN_SCOPE
        or record.get("status") not in ("pass", "fail")
    ):
        raise FixtureError("ah-owner-run-evidence-invalid")
    # The canonical 017-ah entry ONLY: the AH-tagged grammar is
    # the distinct owner-UID record of 017-ah, and no other
    # order id may carry it (the AB/AD/AF tags and the
    # native-scope generic order law are separate closed
    # grammars).
    if record.get("order") != AH_ORDER_ID:
        raise FixtureError("ah-owner-run-evidence-invalid")
    if record.get("teardown_proof") != "exact-cid-membership":
        raise FixtureError("ah-owner-run-evidence-invalid")
    identity = record.get("identity")
    law = _identity_substructure_law(identity)
    if law is None:
        raise FixtureError("ah-owner-run-evidence-invalid")
    subject_uid, subject_gid, _expected_groups, description = law
    reduced = {
        key: value for key, value in record.items() if key not in ("identity", "teardown_proof")
    }
    reduced["record"] = NATIVE_OWNER_RUN_EVIDENCE_SCHEMA
    reduced["scope"] = NATIVE_OWNER_RUN_SCOPE
    try:
        _native_key_grammar(reduced)
    except FixtureError:
        raise FixtureError("ah-owner-run-evidence-invalid") from None
    try:
        profile_view = rprofile.owner_runtime_profile(description)
        _validate_local_evidence_core(
            _native_s_envelope(reduced),
            subject_uid=subject_uid,
            subject_gid=subject_gid,
            tmpfs_budgets=ci.owner_tmpfs_budgets(profile_view),
        )
    except FixtureError:
        raise FixtureError("ah-owner-run-evidence-invalid") from None


def validate_aj_owner_run_evidence(record: dict) -> None:
    """Closed-schema validation of the DISTINCT owner-UID AJ
    terminal record (017-ai sealed INERT entry): the SAME closed
    measured owner state, cleanup and publication law as the AB
    wrapper, under the canonical 017-aj native-process format
    qualification entry's OWN distinct record/scope tags and
    order binding:

    * ``identity`` — the frozen owner identity substructure
      THIS owner collected and derived (never caller-authored),
      through the SAME shared structural core (canonical
      profile name, strict ID laws, one-element primary-GID
      group vector, production codec re-derivation of both
      digests) — closed data integrity, never a measured-
      authority claim;
    * ``teardown_proof`` — the literal exact-CID-membership
      marker (the owner-UID subject removal proof is exact
      registered-CID lifetime membership; the S-shaped teardown
      dict stays byte-for-byte the original).

    The order is the CANONICAL 017-aj entry ONLY: an AJ-tagged
    record of any other order id is refused, and the AB, AD, AF
    and AH tags are separate closed grammars (never widened to
    the AJ entry, including for equal-numeric identities).
    Every shared measured substructure is validated through the
    SAME private S-shaped structural core over the AJ extras
    stripped — with the frozen AJ subject UID/GID and the
    derived owner tmpfs budgets wired through (the measured
    owner facts are validated as-is, NEVER normalized to 21002;
    the public v1 S/native/AB/AD/AF/AH wrappers keep their
    closed laws byte-for-byte).
    """
    if not isinstance(record, dict):
        raise FixtureError("aj-owner-run-evidence-invalid")
    if (
        record.get("record") != AJ_OWNER_RUN_EVIDENCE_SCHEMA
        or record.get("scope") != AJ_OWNER_RUN_SCOPE
        or record.get("status") not in ("pass", "fail")
    ):
        raise FixtureError("aj-owner-run-evidence-invalid")
    # The canonical 017-aj entry ONLY: the AJ-tagged grammar is
    # the distinct owner-UID record of 017-aj, and no other
    # order id may carry it (the AB/AD/AF/AH tags and the
    # native-scope generic order law are separate closed
    # grammars).
    if record.get("order") != AJ_ORDER_ID:
        raise FixtureError("aj-owner-run-evidence-invalid")
    if record.get("teardown_proof") != "exact-cid-membership":
        raise FixtureError("aj-owner-run-evidence-invalid")
    identity = record.get("identity")
    law = _identity_substructure_law(identity)
    if law is None:
        raise FixtureError("aj-owner-run-evidence-invalid")
    subject_uid, subject_gid, _expected_groups, description = law
    reduced = {
        key: value for key, value in record.items() if key not in ("identity", "teardown_proof")
    }
    reduced["record"] = NATIVE_OWNER_RUN_EVIDENCE_SCHEMA
    reduced["scope"] = NATIVE_OWNER_RUN_SCOPE
    try:
        _native_key_grammar(reduced)
    except FixtureError:
        raise FixtureError("aj-owner-run-evidence-invalid") from None
    try:
        profile_view = rprofile.owner_runtime_profile(description)
        _validate_local_evidence_core(
            _native_s_envelope(reduced),
            subject_uid=subject_uid,
            subject_gid=subject_gid,
            tmpfs_budgets=ci.owner_tmpfs_budgets(profile_view),
            entry_order=AJ_ORDER_ID,
        )
    except FixtureError:
        raise FixtureError("aj-owner-run-evidence-invalid") from None


# -- the sealed owner launch + the thin rehearsal driver ----------------------------
def _owner_argv(
    module_path: str,
    bind_head: str,
    repo,
    work,
    control_dir,
    evidence_out,
    order: str = ORDER_ID,
) -> list[str]:
    """The SEALED owner launch: the exact closed argv form (this
    module, the owner subcommand, the order-bound arguments only —
    no caller-supplied launch argv, no shell, no wrapper, no
    arbitrary supervisor argv or bypass)."""
    return [
        sys.executable,
        module_path,
        "owner",
        "--order",
        order,
        "--bind-head",
        bind_head,
        "--repo",
        str(repo),
        "--work",
        str(work),
        "--control-dir",
        str(control_dir),
        "--evidence-out",
        str(evidence_out),
    ]


def _driver_record(
    status: str,
    run_id: str | None,
    owner_exit: int | None,
    evidence_sha256: str | None,
    reason: str | None = None,
) -> dict[str, object]:
    return {
        "record": "slaif-017s-local-driver-v1",
        "status": status,
        "reason": reason,
        "run_id": run_id,
        "owner_exit": owner_exit,
        "evidence_sha256": evidence_sha256,
    }


def run_local_rehearsal(repo, bind_head, work, control_dir, evidence_out) -> dict[str, object]:
    """The ONE bounded S rehearsal: SEALED-launch the Python owner
    (exact closed argv; the owner IS the supervisor — no second
    watchdog, no caller launch argv) and drive ITS protected
    interface prepare -> observe -> rehearse -> finish in order —
    the SAME run, ledger, attempt and END (no direct-call
    simulation) — then verify the retained closed evidence against
    the owner's exit.  The driver's patience is bounded by the
    owner's OWN published END anchor plus the owner's own single
    allowed cleanup grace — the approved ONE END+grace anchor
    (no extra margin, no hidden reset, no second fixture
    budget).  The owner child is launched in its OWN session, and
    that independence is VERIFIED, never assumed: a driver death
    can
    never kill or reset the independently running owner, and the
    driver NEVER signals the owner (a bounded wait that expires
    leaves the owner to its own finite END).  A driver failure is
    a closed record; it never mutates the owner."""
    argv = _owner_argv(
        str(Path(__file__).resolve()), bind_head, repo, work, control_dir, evidence_out
    )
    captured: bytearray = bytearray()
    captured_total = 0
    capture_faulted = False
    proc = subprocess.Popen(
        argv,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        # INDEPENDENCE: the owner runs in its own session/process
        # group; the driver's own death (or its terminal cleanup)
        # can never propagate to the independently running owner.
        start_new_session=True,
    )

    def _capture() -> None:
        nonlocal captured_total, capture_faulted
        assert proc.stdout is not None
        try:
            # Bounded drain: a TOTAL byte cap on top of the retained
            # 16KiB (the owner emits only small closed lines; a
            # pathological stream cannot hold the reader forever).
            # Hitting the cap, or any read error, is a FAULT: the
            # stream was not drained to EOF, so the driver gates
            # the result as a closed failure, never a pass.
            try:
                while captured_total < _DRIVER_CAPTURE_MAX:
                    chunk = proc.stdout.read(min(65536, _DRIVER_CAPTURE_MAX - captured_total))
                    if not chunk:
                        break
                    captured_total += len(chunk)
                    if len(captured) < 16384:
                        captured.extend(chunk[: 16384 - len(captured)])
                else:
                    capture_faulted = True
            except OSError:
                capture_faulted = True
        finally:
            try:
                proc.stdout.close()
            except OSError:
                pass

    reader = threading.Thread(target=_capture, daemon=True)
    reader.start()

    def _settled() -> bool:
        reader.join(5.0)
        return not reader.is_alive()

    def _reap_bounded() -> int | None:
        """Bounded reap: wait at most the closed startup-reap
        budget.  A still-running owner is NEVER signalled or killed
        (independence: it converges its own exact-owned cleanup on
        its own finite END) — the bounded wait simply gives up and
        the driver records what it measured."""
        try:
            return proc.wait(timeout=_DRIVER_STARTUP_REAP_SECONDS)
        except subprocess.TimeoutExpired:
            return proc.returncode

    run_id: str | None = None
    end = time.monotonic() + _CONTROL_STARTUP_TIMEOUT
    while time.monotonic() < end:
        if proc.poll() is not None:
            break
        state = _state_record(control_dir)
        if state is not None:
            run_id = str(state["run_id"])
            break
        time.sleep(0.2)
    if run_id is None:
        owner_exit = _reap_bounded()
        _settled()
        reason = "local-driver-startup"
        try:
            lines_ = bytes(captured).decode("ascii", "replace").strip().splitlines()
            startup = json.loads(lines_[-1])
            if (
                isinstance(startup, dict)
                and startup.get("record") == CONTROL_RECORD
                and startup.get("stage") == "startup"
                and isinstance(startup.get("reason"), str)
                and startup["reason"] in _FAILURE_REASONS
            ):
                reason = startup["reason"]
        except (ValueError, IndexError):
            pass
        return _driver_record("fail", None, owner_exit, None, reason)
    state = _state_record(control_dir)
    if state is None:
        owner_exit = _reap_bounded()
        _settled()
        return _driver_record("fail", run_id, owner_exit, None, "local-driver-startup")
    # VERIFY (never assume) the sealed independence: the owner's
    # own session must differ from the driver's session; a mismatch
    # or unreadable identity is a closed driver failure (the owner
    # keeps running and converges on its own END — the driver never
    # signals it).
    if proc.poll() is None:
        try:
            independent = os.getsid(proc.pid) != os.getsid(os.getpid())
        except (OSError, ValueError, TypeError):
            independent = False
        if not independent:
            _settled()
            return _driver_record("fail", run_id, proc.poll(), None, "local-driver-independence")
    # The driver's WHOLE command/wait budget is the owner's OWN
    # published END anchor plus the owner's own single allowed
    # cleanup grace — the approved ONE END+grace anchor (no extra
    # margin, no hidden reset, no second fixture budget).
    patience_abs = float(state["end_anchor"]) + CLEANUP_GRACE_SECONDS
    for command in ("prepare", "observe", "rehearse", "finish"):
        remaining = patience_abs - time.monotonic()
        if remaining <= 0:
            return _driver_record("fail", run_id, proc.poll(), None, "local-driver-patience")
        try:
            # ONE absolute remaining budget per command (the same
            # owner END/grace anchor — no separate per-operation
            # budget and no hidden reset); the client enforces it
            # across its whole connect/send/read sequence.
            response = _control_client(control_dir, command, run_id, remaining)
        except FixtureError as exc:
            return _driver_record("fail", run_id, proc.poll(), None, str(exc))
        if not response["ok"] and command != "finish":
            return _driver_record(
                "fail", run_id, proc.poll(), None, response["reason"] or "internal"
            )
    # The final reap uses the SAME one END+grace anchor: an EXPIRED
    # remaining budget refuses BEFORE the blocking wait (no fresh
    # positive floor, no post-window pass); only an ALREADY-EXITED
    # owner is distinguished (a non-blocking poll, never a renewed
    # wait).
    remaining = patience_abs - time.monotonic()
    if remaining <= 0:
        if proc.poll() is not None:
            owner_exit = proc.poll()
        else:
            _settled()
            return _driver_record("fail", run_id, None, None, "local-driver-patience")
    else:
        try:
            owner_exit = proc.wait(timeout=remaining)
        except subprocess.TimeoutExpired:
            # The owner still holds its own budget: the driver gives
            # up (closed failure) and never signals the owner.
            _settled()
            return _driver_record("fail", run_id, None, None, "local-driver-patience")
    # The capture must have settled BEFORE a pass is published: the
    # owner exited, the pipe hit EOF and the bounded drain is
    # complete WITHOUT a cap/read fault (an unsettled reader or a
    # faulted drain is a closed driver failure).
    if not _settled() or capture_faulted:
        return _driver_record("fail", run_id, owner_exit, None, "local-driver-output")
    try:
        est = os.lstat(evidence_out)
        if not (
            stat.S_ISREG(est.st_mode)
            and stat.S_IMODE(est.st_mode) == 0o600
            and est.st_uid == os.getuid()
        ):
            return _driver_record("fail", run_id, owner_exit, None, "local-driver-evidence")
        raw = _read_bounded(Path(evidence_out), 33 * 1024 * 1024)
        evidence = json.loads(raw.decode("ascii"))
        validate_local_evidence(evidence)
    except (OSError, ValueError, UnicodeDecodeError, FixtureError):
        return _driver_record("fail", run_id, owner_exit, None, "local-driver-evidence")
    if evidence["run_id"] != run_id:
        return _driver_record("fail", run_id, owner_exit, None, "local-driver-evidence")
    expected_exit = 0
    if evidence["status"] != "pass":
        expected_exit = 130 if evidence["reason"] == "cancelled" else 1
    if owner_exit != expected_exit:
        return _driver_record("fail", run_id, owner_exit, None, "local-driver-exit")
    digest = hashlib.sha256(raw).hexdigest()
    return _driver_record(
        "pass" if evidence["status"] == "pass" else "fail",
        run_id,
        owner_exit,
        digest,
        None if evidence["status"] == "pass" else evidence["reason"],
    )


def main(argv: list[str] | None = None) -> int:
    """The THIN local CLI: closed subcommand grammar.  ``owner``
    runs the one owning fixture actor (the supervisor — no second
    watchdog process and no caller-supplied launch argv);
    ``client`` sends ONE bounded command to a running owner;
    ``rehearsal`` sealed-launches the owner and drives the
    interface prepare -> observe -> rehearse -> finish (the ONE
    bounded S rehearsal)."""
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("owner", "rehearsal"):
        p = sub.add_parser(name)
        p.add_argument("--order", help=f"the bound order id (must be {ORDER_ID})")
        p.add_argument("--bind-head", help="literal 40-hex source head")
        p.add_argument("--repo", help="repository checkout root")
        p.add_argument("--work", help="fresh owned disposable work root")
        p.add_argument("--control-dir", help="fresh protected control root")
        p.add_argument("--evidence-out", help="protected evidence destination")
    pc = sub.add_parser("client")
    pc.add_argument("--control-dir", help="the running owner's protected control root")
    pc.add_argument("--command", choices=_CONTROL_COMMANDS, help="the one bounded command")
    args = parser.parse_args(argv)
    if args.command in ("owner", "rehearsal"):
        if (
            args.order not in (ORDER_ID, X_ORDER_ID, Y_ORDER_ID, AB_ORDER_ID)
            or not args.bind_head
            or not args.repo
            or not args.work
            or not args.control_dir
            or not args.evidence_out
        ):
            print(json.dumps({"schema": SCHEMA, "status": "fail", "reason": "local-args-invalid"}))
            return 1
        repo, work = Path(args.repo), Path(args.work)
        control_dir, evidence_out = Path(args.control_dir), Path(args.evidence_out)
        if args.command == "rehearsal":
            # The S sealed rehearsal is the 017-s path only: the
            # 017-x driver sealed-launches the owner itself with
            # the capability command sequence.
            if args.order != ORDER_ID:
                print(
                    json.dumps({"schema": SCHEMA, "status": "fail", "reason": "local-args-invalid"})
                )
                return 1
            # The OUTER catch: any unexpected driver-side failure
            # still returns a closed truthful driver record (never
            # a traceback, never a bare exit).
            try:
                summary = run_local_rehearsal(repo, args.bind_head, work, control_dir, evidence_out)
            except FixtureError as exc:
                summary = _driver_record("fail", None, None, None, str(exc))
            except KeyboardInterrupt:
                summary = _driver_record("fail", None, None, None, "cancelled")
            except Exception:
                summary = _driver_record("fail", None, None, None, "internal")
            print(json.dumps(summary, sort_keys=True))
            return 0 if summary["status"] == "pass" else 1
        try:
            if args.order == ORDER_ID:
                owner = LocalFixtureOwner(repo, work, evidence_out, args.bind_head, control_dir)
            else:
                # 017-x / 017-y / 017-ab: the SEALED CHILD owns
                # resolve+admit ONCE before any external work — the
                # module-minted run identity is admitted in THIS
                # process, so ONE identity/admission survives the
                # process boundary.
                # Exhaustion is a closed REFUSAL: the one-attempt
                # law is never bypassed by reconstructing identity
                # from the journal, and a running attempt can never
                # be served by a second owner.  A constructor
                # failure closes the SAME already-won attempt as
                # fail (the one-attempt law is never left dangling
                # by a startup fault).
                binding = oap_binding.resolve_order_binding(repo, args.order, args.bind_head)
                oap_binding.admit_order_attempt(repo, args.order, binding)
                try:
                    owner = LocalFixtureOwner(
                        repo, work, evidence_out, args.bind_head, control_dir, binding=binding
                    )
                except FixtureError:
                    oap_binding.record_order_attempt(repo, args.order, binding.run_id, "fail")
                    raise
            return owner.serve()
        except FixtureError as exc:
            print(json.dumps({"record": CONTROL_RECORD, "stage": "startup", "reason": str(exc)}))
            return 1
        except KeyboardInterrupt:
            print(json.dumps({"record": CONTROL_RECORD, "stage": "startup", "reason": "cancelled"}))
            return 130
        except Exception:
            print(json.dumps({"record": CONTROL_RECORD, "stage": "startup", "reason": "internal"}))
            return 1
    # -- client: ONE bounded command against the running owner --
    if not args.control_dir:
        print(
            json.dumps(
                {
                    "record": CONTROL_RECORD,
                    "ok": False,
                    "command": args.command,
                    "run_id": "0" * 32,
                    "reason": "local-args-invalid",
                    "detail": None,
                }
            )
        )
        return 1
    # ONE protected state snapshot (the same bounded, ownership-
    # checked reader the owner publishes through): a single read,
    # so a state that disappears after the read cannot race into
    # an uncaught assert or a second divergent read.
    state = _state_record(Path(args.control_dir))
    if state is None:
        print(
            json.dumps(
                {
                    "record": CONTROL_RECORD,
                    "ok": False,
                    "command": args.command,
                    "run_id": "0" * 32,
                    "reason": "local-state-missing",
                    "detail": None,
                }
            )
        )
        return 1
    run_id = str(state["run_id"])
    # The client's budget is bounded by the EXISTING owner END
    # anchor plus the owner's own single allowed cleanup grace
    # (capped by the closed client ceiling): no separate fixture
    # lifetime of the caller's own.
    anchor = float(state["end_anchor"])
    remaining = anchor + CLEANUP_GRACE_SECONDS - time.monotonic()
    if remaining <= 0:
        # The owner's OWN END+grace anchor has already elapsed:
        # refuse BEFORE any IO with a closed record — the budget
        # is never refreshed for a dead anchor.
        print(
            json.dumps(
                {
                    "record": CONTROL_RECORD,
                    "ok": False,
                    "command": args.command,
                    "run_id": run_id,
                    "reason": "local-driver-patience",
                    "detail": None,
                }
            )
        )
        return 1
    budget = min(_CLIENT_TIMEOUT, remaining)
    try:
        response = _control_client(Path(args.control_dir), args.command, run_id, budget)
    except FixtureError as exc:
        print(
            json.dumps(
                {
                    "record": CONTROL_RECORD,
                    "ok": False,
                    "command": args.command,
                    "run_id": run_id,
                    "reason": str(exc),
                    "detail": None,
                }
            )
        )
        return 1
    print(json.dumps(response, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
