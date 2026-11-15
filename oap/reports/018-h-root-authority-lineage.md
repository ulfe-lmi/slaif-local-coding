# 018-h — root-authority lineage (implementation report)

Status: COMPLETE at the bounded inert scope (PENDING strategic
acceptance; no acceptance is claimed).

- Order: `oap/orders/018-h-root-authority-lineage.md` (activated bytes
  committed unchanged; `oap/active` = 018-h).
- Implementation head SHA: bbe60ba7da7b45f6bd4017d7f1674d9cf2e94d26
- Source A (implementation): 0e878444f8529bf8e8c31626d09b458d6fcff736
- Report publication commit: SELF

## What this round implemented (inert, inert-by-design)

A root-authority-lineage composition over the ACTUAL retained 018-d
causal-history state and its ACTUAL namespace
(`src/slaif_local_coding/constitution/bundles/`: `root_lineage_models`,
`root_lineage`), never active in the adapter request path:

- versioned root-lineage namespace derived from the actual D namespace;
  the NEW per-operation bounds (root facts 1024, retained root source
  bytes 16 MiB, work units 1048576, diagnostics 64; stricter positives
  allowed) on ONE outer coupled to the ACTUAL D work (D-local domains
  independent, no global min, no resets, original-batch max_requests
  domain preserved);
- bootstrap = the accepted legitimate effective AGENTS envelope (exact
  source bytes/workspace/first spans; the exact EMPTY root legal;
  rootless empty state never bootstraps); REFRESH SOURCE = an ACTUAL
  accepted complete whole singleton root read on EITHER read endpoint
  (opaque/mixed/partial/truncated/nonzero/unsupported/repeated grant
  nothing);
- SOURCE acquisition and AUTHORITY separate: matching INTERNAL trusted
  issuance/receipt with proven frozen causal ancestry to the bootstrap
  root fact; DERIVED issued/authority flags re-derived after EVERY
  accepted D transition (stored bits never trusted); UNPROVEN
  retention with the fixed ROOT_SOURCE_UNPROVEN limitation; known
  same-scope envelope replays are no-ops with FIRST provenance; an
  unknown changed envelope without independent same-batch authority
  refuses the whole transition with the exact prior state;
- current-root selection = a DISTINCT derived causal-maximal source
  fact: equal incomparable maxima ALL retained, differing maxima an
  explicit ROOT_CONTENT_CONFLICT with NO selected source, a child of
  one branch cannot causally dominate the other (equal-byte surviving
  maxima can be compatible), a genuine child of ALL can, delayed older
  receipts never override proven descendants;
- H-PRIVATE charged coherence: every retained piece producer binding
  derives from the SAME original request endpoint, and EVERY completed
  occurrence joins its complete owning result record (producer
  IDs/count/owner binding/lengths re-derived; a missing or rewritten
  owning result is refused) -- the retained proof alone cannot
  re-prove ownership; the old public D law/schemas/versions are
  UNCHANGED;
- charged closed scalar-shape prewalk fences before every nested
  revalidation (zero fallback serializer visits).

New versioned contract `docs/CACHE-ROOT-LINEAGE-CONTRACT.md`; durable
A-H original-API matrix `tests/test_root_lineage.py` (209 cases, both
read endpoints and both admission modes); human ARCH, the three
byte-equal compact mirrors, TESTING, the ledger and the append-only
018-g addendum in `oap/REPORT-CORRECTIONS.md` reconciled.

## Verification (actual results at the implementation head)

- ONE foreground managed exact-15 gate at clean B (parent umask 077;
  cmd07 pytest child process-local umask 022; live parent/child
  PID/birth/PPID/UID/umask metadata captured): all 15 commands rc 0 --
  lock/sync/ruff check/ruff format/mypy/docs; `pytest -q` = 5307
  passed, 28 skipped (657.88 s); build; artifact-policy
  inspect/install-smoke; python version; compileall; manifest verify;
  shell syntax; `git diff --check ffaabf4b..HEAD`.
- Focused module suite (actual exit 0): `tests/test_root_lineage.py` =
  209 passed (the earlier 8-failure capture preserved).
- Clean BOTH-artifact proof at exact B (one clean git-archive build on
  fresh protected paths, direct unmasked exits, no rebuild): wheel
  959b6d99… (56 entries, unique RECORD) + sdist 5813e9af… (251
  entries) byte-identical to the manifest AND to the repo gate dist;
  253/253 manifest source inputs verified against Git B and the clean
  tree; all proof assertions passed.
- GitHub: all TEN implementation-B checks SUCCESS at B
  `bbe60ba7…` (test, docker, docker-published, operator-session,
  gateway-contract, cache-native-fixture, cache-native-containment,
  CodeQL, Analyze(python), Analyze(actions)).
- ROOT-executed (not coding-executed) named original-API rechecks at
  their EXACT recorded source hashes: retained result/proof
  producer-join + ordering recheck (8/8), shape matrix (44/44),
  attribution (12/12), multibyte byte-cap encode sentinel (4/4), K5
  zero-serializer prewalk (6/6), atomic envelope binding +
  known-envelope replay (8/8), marker-index positives (20/20),
  D-local outer domain (4/4), batch-cap retention (4/4), actual
  late-ancestor (4/4), delayed-older root receipt (4/4), K2
  completeness/D-binding/source-integrity/constructor-privacy (4/4,
  8/8, 4/4, 2/2). Captures are recorded at their captured hashes, not
  as a single final-kernel result; no label-only rerun.

## Process qualifications (this round; nothing rerun for labels)

- Preliminary background full suite (setsid 077; pid 3582981 / pytest
  3582983): STOPPED by owner SIGTERM at ~37% to avoid duplicate load
  before the ordered gate; the partial summary at interrupt is "2
  failed, 2014 passed in 134.26s" (both failures umask-077 fixture
  effects); NO terminal exit was captured; it is never a final pass. A
  post-hoc STATUS NOTE is appended in the capture's .out; original
  stdout and the annotation are distinguished there.
- 00:24 wrong-basename incident: ROOT's current metadata records 13
  error pairs (empty .out + python source-not-found .err; no probe
  assertion ran). The worker audit acknowledged overwrites of prior
  capture bytes at 12 of those paths (prior bytes lost; the surviving
  files are the failed-launch bytes); for the 13th pair prior
  existence/survival is not independently established (neither
  overwrite nor survival proven). The initial no-overwrite statement
  was corrected by that audit; no old bytes were reconstructed and no
  rerun relabeled.
- `regress-post-k2.out`: a 0B background capture with no terminal
  exit -- it records an attempt only, not a pass.
- `/tmp/dummy`: observed 0B/0600 empty scratch when inspected; prior
  existence unknown; no exposure is claimed absent evidence.
- Executed-then-patched scratch sources (preserved unchanged):
  `probe-e-f-oracles-v1.py` (executed then sed -i patched at the same
  path; earlier exact bytes not proven preserved) and
  `fix-ef-durable-v1.py` (executed -> SyntaxError line 59; the repair
  is fresh v2).
- Earlier-round qualifications (018-f/018-g: the F sed -i detail, G
  batch-2 v3 multibyte oracle, 3.14 capture uncertainty,
  measure-g-thresholds/probe-k1-sites/baseline-suite log-mode items,
  the F-group 26 pre-existing mypy errors) are recorded in the 018-f
  and 018-g round reports and the append-only
  `oap/REPORT-CORRECTIONS.md`; the prewalk probe source-path erratum
  (S/probes, not S/reviews) is recorded at
  `S/reviews/018-h-prewalk-source-path-erratum-v1.json`.
- Fixture-level repairs this session (test-only, product law
  unchanged): `probe-g-owner-a-v1.py` TypeError fixture (preserved;
  fresh v2/v3 fixes); the t_rc binding fixture (the new matrix's first
  green run is v5); the native-owner (b) oracle led to the ROOT-
  directed H-private 4b kernel repair (old D unchanged, verified 8/8);
  the 4c join ordering fix kept the typed shape refusals (kernel
  b2ebea0b -> 9413c25f).

## NOT RUN (downstream, mandatory)

- The root-aware graph/admission composition consuming the 018-h
  accepted interface (recomputed root closure, withdraw/restore
  entries, canonical root/authority keys under one outer).
- C04/C05 current-version acceptance; version-owned edge/certificate
  withdrawal end-to-end; v1 runtime; RAM (019), recovery (020),
  tokenizer/compiler (021), wire (022), full stack (023), actual-model
  /genuine-Codex (024).
