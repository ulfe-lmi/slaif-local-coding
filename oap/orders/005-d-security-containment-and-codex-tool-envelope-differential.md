# OAP Work Order — 005-d

## Objective

Amend Objective-005 PR #7 with a no-live security-containment record and a
bounded no-model Codex 0.149 tool-envelope differential against the unchanged
pinned gateway policy. Determine whether supported disposable Codex feature/
configuration flags can remove the gateway-rejected `tool_search`/`web_search`
declarations while preserving ordinary local shell/function tools. Do not run
Docker, PostgreSQL, gateway/adapter services, Qwen calls, or modify the gateway.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`.
- Numeric objective / round: `005` / `005-d`.
- PR mode: `AMEND_EXISTING_PR`; **NO NEW PR**.
- Existing PR #7:
  `https://github.com/ulfe-lmi/slaif-local-coding/pull/7`.
- Base/head: `main` / `oap/005-gateway-ingress-integration`.
- Current verified remote head / failed 005-c SELF:
  `b38ba39a2f0ab63f03a25504487b96f4f29e5538`.
- 005-c implementation parent:
  `45f712aff53e8f71669ba51314cce790838d8e0a`.
- PR OPEN/non-draft/MERGEABLE/CLEAN; report-head `test` SUCCESS.
- Same PR only; coding never merges or enables auto-merge.

## Accepted 005-c partial evidence

Accept only the directly proven portions: disposable unchanged gateway service,
PostgreSQL migrations/seed, public model visibility, standard text, typed SSE,
one inline image, finalized reservations/ledger rows for successful standard
requests, invalid-key and over-quota pre-adapter rejection, credential
boundaries, and complete Docker/gateway/candidate/image/temp cleanup. Do not
claim Codex, full accounting, cutover, or production acceptance.

## A. Security incident record and containment audit

005-c diagnosis executed this prohibited broad command twice:

```text
rg -n "web_search_tool_type|supports_search_tool|experimental_supported_tools"
  . <CODEX_HOME> 2>/dev/null | sed -n '1,260p'
```

It traversed host Codex session-cache JSONL and placed cached session prose into
the coding agent's local tool output/provider context. No raw content may be
reopened, quoted, copied, committed, or reported.

Strategic containment already performed:

- exact affected coding rollout identified by metadata;
- file mode changed from `0644` to `0600` without deleting/rewriting it;
- pattern-only scan over that affected rollout found:
  - GitHub-token matches: 0;
  - private-key blocks: 0;
  - two unique OpenAI-style `sk-*` shapes / eight occurrences, not safely
    attributable from content-free evidence;
  - one unique long Bearer shape / four occurrences;
  - temporary/synthetic database/secret/token-shaped matches;
- disposable gateway DB/key/service/container no longer exists, postgres image
  is absent, and generated rehearsal credentials are unusable;
- no evidence proves that the protected Qwen credential or any persistent
  GitHub/OpenAI credential value was printed; absence is not overclaimed as a
  formal secret-forensics guarantee.

Requirements:

1. Add a concise sanitized incident record under `docs/` or `oap/` with fixed
   facts above, impact boundary, containment, residual uncertainty, and explicit
   statement that repository/GitHub artifacts contain no raw exposed content.
2. Do not include the real session filename/UUID, host username/home path,
   matches, hashes of credentials, raw command output, or session prose.
3. Add a repository-only path-safety helper/test used by rehearsal/capture
   scripts that rejects:
   - `$HOME`, `~`, `CODEX_HOME` outside the driver-owned disposable directory;
   - host `.codex`/session/history/cache/state paths;
   - `/`, workspace parents, unresolved traversal, and broad recursive search
     roots;
   - any diagnostic subprocess not explicitly allowlisted by argv/path.
4. Rehearsal docs/scripts must state diagnostics operate only on exact repo-
   owned files, pinned disposable gateway clone, or driver-owned temp roots.
5. Add tests/scans proving no script contains or constructs a host Codex-cache
   search and that rejected paths fail before subprocess execution.
6. Do not delete sessions, rotate credentials, modify Codex profiles, or change
   global file permissions further. Report whether human rotation/action is
   recommended from bounded evidence.

## B. Exact gateway rejection localization — no services

Use pinned unchanged gateway source at
`8f2813bf745b90221da33a7cfaf40726c5b1b480` in a disposable read-only clone and
its actual Responses request-policy/capability code. Do not start its ASGI app or
database.

Using a temporary loopback fake Responses provider that captures one request in
memory and returns a fixed error, execute at most four Codex 0.149 global-yolo
no-model captures. Each uses a fresh disposable CODEX_HOME/catalog and no
protected key/model.

Variants must be predetermined and differ only in supported, explicit Codex
configuration/feature flags plausibly governing client tools, such as:

1. accepted current disposable baseline;
2. `--ignore-user-config` plus disabled `apps`/browser/computer features;
3. additionally disabled supported standalone/web-search features;
4. one minimal documented catalog/config variant if still needed.

Do not pass unknown flags blindly. Check `codex features list`/CLI help first and
record only fixed flag names/statuses, never config content.

For each captured first request:

- retain only bounded top-level `tools[].type` counts from validated ASCII
  labels, whether ordinary `function|custom` remains, and whether
  `tool_search|web_search` remains;
- feed the transient request body directly to the pinned gateway's actual
  Responses policy/capability validation with the same synthetic route
  capabilities used by 005-c;
- retain only accepted/rejected, fixed gateway error code/field/type, and
  whether rejection occurs before reservation by source control-flow evidence;
- discard body, prompt, image, tool names/schemas, instructions, headers,
  session ID, and error prose immediately;
- no raw request logging or persistent capture.

Determine the minimal variant, if any, that:

- gateway accepts;
- retains ordinary local function/custom shell tooling needed by Codex;
- removes hosted/provider tool declarations not supported by the route;
- does not enable sandbox bypass beyond already approved global yolo;
- needs no gateway code change.

If none exists, report the exact immutable compatibility gap and stop. Do not
weaken gateway policy, strip tools inside Local Coding, alter the captured body,
or claim configuration-only compatibility.

## C. Rehearsal support correction

Update repository-only 005-c driver/support only to:

- use the proven minimal Codex flags/catalog when one exists;
- emit a fixed tool-envelope preflight result before any Docker/Qwen stage;
- refuse full rehearsal when preflight is gateway-rejected;
- eliminate debug monkeypatch/print hooks and broad search guidance;
- ensure exactly one full execution flag/path can be invoked after preflight in
  a future order;
- keep raw/private fields out of facts.

Do **not** rerun the full rehearsal in 005-d.

## D. Documentation and completeness

Update gateway integration/runbook/security documentation with:

- exact fixed incident classification and containment;
- tool-envelope differential results;
- whether unchanged-gateway configuration-only compatibility is possible;
- no gateway modification authorization;
- no live/cutover acceptance.

Completeness remains unchanged from the accepted partial Objective-005 state;
do not advance from the failed 005-c run.

## Verification and protected safety

Run incident/path-guard tests, no-model capture/policy differential once,
driver preflight tests, full frozen Ruff/format/mypy/pytest/build/wheel/
compileall/shell/diff/secret/raw-log scans, and current CI.

No Docker command except read-only `docker ps/image inspect` final verification;
no container/image pull/run/remove; no Postgres; no gateway/adapter listener; no
Qwen API/model call. Vision remains active, text inactive, 18020 unchanged,
18021/18031 absent.

## Publication contract

Amend only PR #7; never create another PR or merge. Push all non-report work,
record literal implementation SHA, then publish exactly one immutable
`oap/reports/005-d-security-containment-and-codex-tool-envelope-differential.md`
with literal SHA and `Report publication commit: SELF`. SELF changes only
report, parent equals implementation SHA, and is remote head before FIFO `OK`.
