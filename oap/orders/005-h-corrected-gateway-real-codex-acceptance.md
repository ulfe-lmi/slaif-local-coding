# OAP Work Order — 005-h

## Objective

Amend Local Coding Objective-005 PR #7 with the single corrected exact-head
cross-repository acceptance run. Use the reviewed Gateway PR #291 continuation
that recognizes the exact Codex 0.149 `tool_search` declaration as an
adapter-managed candidate and explicitly pairs
`codex-0.149-responses-v1 -> local-coding-v1`. If the corrected no-live
preflight passes, proceed in the same round to the disposable real
Codex -> Gateway -> Local Coding -> protected Qwen run, signed identity,
governance, quota/accounting, isolation, and rollback evidence.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`.
- Round: `005-h`; mode `AMEND_EXISTING_PR`; **NO NEW PR**.
- PR: `https://github.com/ulfe-lmi/slaif-local-coding/pull/7`.
- Base/head: `main` / `oap/005-gateway-ingress-integration`.
- Required starting Local Coding head:
  `cd1a16cbddc4ff7e1ad2b2769fc1311479f0dc97` (005-g SELF).
- Required current Local Coding check state: `test` SUCCESS; PR OPEN,
  non-draft, MERGEABLE/CLEAN.
- Gateway repository: `ulfe-lmi/slaif-api-gateway`.
- Gateway PR: `https://github.com/ulfe-lmi/slaif-api-gateway/pull/291`.
- Required corrected Gateway 155-c report head:
  `c0094e478b83d33a52eb82a2ba9c8677e6af4a6e`.
- Gateway implementation parent:
  `02670e3275ff57850aeaa9bc8aae4ed3c8e2f124`.
- The 155-c SELF changes only
  `oap/reports/155-c-codex-0149-local-coding-preflight-deadlock-closure.md`,
  its first parent is the literal implementation SHA, and all ten report-head
  CI/CodeQL/PostgreSQL/E2E/Compose/documentation checks are SUCCESS. PR #291 is
  OPEN, non-draft, MERGEABLE/CLEAN.

Abort before setup if either exact head changes or required CI is not fully
successful. Do not substitute Gateway main, an unreported commit, a local
Gateway edit, or a different PR.

## Strategic context

005-g validly stopped before live setup at Gateway PR #291 head
`c68fa511141a0c21d420e7a94100f717e674553f`. The exact Codex 0.149 capture had
`function=5`, `custom=1`, `tool_search=1`, and `web_search=1`. That Gateway head
rejected `tool_search` in its client normalizer and lacked the exact static
Codex-0.149/Local-Coding server pair. No Local Coding defect was observed.

This continuation is valid only after the Gateway PR preserves fail-closed
security while correcting both gates. Raw byte equality between Local Coding
source vectors and Gateway provenance wrappers is not required. Exact embedded
source hashes, contract/version identity, complete semantic vector execution,
and stale/unknown provenance rejection are required.

## A. Mandatory no-live preflight

Before Docker, PostgreSQL, listeners, or Qwen traffic:

1. detach a private temporary Gateway checkout at the exact reviewed report
   head and verify its report-only commit/implementation parent;
2. verify Local Coding PR #7 exact head and clean checkout;
3. verify Gateway wrapper `source_fixture_sha256` values equal the exact Local
   Coding source fixture hashes and execute every signed-identity and tool-filter
   vector against both implementations with no omitted cases;
4. reject stale digest, unknown version, changed vector, missing case, malformed
   wrapper, and semantically divergent result;
5. capture one fresh ordinary Codex 0.149 global-yolo Responses envelope in a
   driver-owned `CODEX_HOME` without host session/cache/history access;
6. prove the selected Gateway client module accepts the exact reviewed
   `tool_search` and `web_search` declaration shapes only as adapter-managed
   candidates, preserves ordinary function/custom/namespace declarations, and
   selects the exact `local-coding-v1` server pair;
7. prove Gateway still rejects malformed/authority-bearing search declarations,
   explicit dropped/hosted search choice, unrelated server modules, and missing
   Local Coding route capability before provider/reservation;
8. prove Local Coding removes only exact disabled search declarations, preserves
   ordinary local tools/call/results, and rejects explicit selection;
9. prove service Bearer, signing, derivation, public synthetic key, database,
   and Qwen credential roles are all distinct;
10. prove path guards reject host Codex homes/sessions/history/cache and all
    roots outside the repository or driver-owned temporary tree.

Any failure stops before live setup and is reported as the first exact gate. Do
not repair Gateway in this repository and do not open another diagnostic chain.

## B. Disposable topology

If and only if A passes, start one bounded disposable topology:

```text
ordinary OpenAI client + real Codex 0.149 global-yolo
  -> exact Gateway PR #291 ASGI app on random loopback port
       temporary PostgreSQL 16 container, loopback only, tmpfs
       reviewed local-coding-v1 module
  -> Local Coding PR #7 on 127.0.0.1:18031
       service_bearer_signed_identity_v1
       responses_tool_policy=drop_disabled_codex_search
       rehydration enabled, fresh private bounded cache
  -> protected vision Qwen on 127.0.0.1:18020/v1
```

Use synthetic identities/keys/secrets/data and real repository service APIs and
migrations. No Redis/Celery/email/admin/TLS/public bind. Do not persist or
activate a Gateway route/profile/service. Use an exact unique Docker container,
official `postgres:16`, loopback bind, tmpfs, finite health timeout, no host
network/privileged mode, and complete cleanup.

## C. Required traffic and evidence

Run sequentially without retry after a product/accounting failure:

1. health/readiness and one visible synthetic public model;
2. standard client non-stream Responses text;
3. typed SSE through completion with provider usage;
4. one small inline synthetic image through the vision route;
5. real Codex 0.149 global-yolo text/tool/governance invocation that reads the
   exact delegated dependency, proves root/dependency observation,
   acquisition, compile/cache/injection, hidden binding effectiveness, Gateway
   exact-body signing, Local Coding verification, and absence of disabled search
   tools at Qwen;
6. same key/session/repository zero-root history-reduction request proving signed
   rehydration and zero additional compiler-model attempt;
7. different owner/key/session/repository zero-root request proving an isolated
   miss and no first-identity governance;
8. invalid key and over-quota rejection before Local Coding;
9. explicit dropped/hosted search choice rejection before provider with no
   leaked reservation;
10. exact replay/bad-signature request rejection without duplicate provider or
    accounting effect.

Retain only safe booleans, counts, hashes, versions, statuses, and timing. Never
record raw request/response bodies, prompts, source, tool output, model text,
images, identities, canonical signing bytes, signatures, nonces, credentials,
database URLs, or private cache names.

## D. Accounting and isolation acceptance

Prove through Gateway repository/service APIs or bounded read-only database
facts:

- exactly one reservation and one terminal ledger outcome per admitted public
  request;
- successful rows finalized using provider-reported usage relayed through Local
  Coding;
- no pending/duplicate request IDs and internally consistent request/token/cost
  counters;
- Local Coding compiler calls create zero Gateway rows/reservations;
- every rejected pre-provider case has the exact no-leak accounting outcome;
- ledger/audit metadata contains no raw content, auth, identity, signature, or
  private endpoint data.

Every identity dimension used by Local Coding cache/rehydration must derive from
the verified signed request and remain isolated. No unsigned or caller-spoofed
fallback is permitted in this production-mode run.

## E. Cleanup and protected-host proof

On every result, remove only the exact disposable Gateway, Local Coding,
PostgreSQL, temporary checkout/venv/config/cache/Codex home/workspace/log state,
and newly pulled image if absent before. Prove no temporary containers, volumes,
images, listeners, or generated credentials remain.

Leave protected vision Qwen running unchanged: same PID/start/restart/listener,
one-image fixture and context configuration. Do not start the text fixture,
change port 18020/18021, change Qwen/systemd/model/checkpoint/launch flags,
firewall/VPN/bindings/API-key files, or modify active Codex profiles. Port 18031
and all random test ports must be absent after cleanup. Do not retire the direct
vLLM rollback path.

## F. Repository completion

Add only narrowly reusable driver/test corrections supported by this run. Do
not vendor or modify Gateway. Update the Objective-005 ledger/completeness and
Gateway integration/runbook documentation to distinguish:

- fake/vector evidence;
- exact-head disposable real Codex/Qwen/Gateway evidence;
- remaining persistent deployment/cutover limitations;
- fixture-scoped claims versus production/release claims.

Run focused preflight/identity/tool/accounting/privacy tests plus the complete
frozen Ruff/format/mypy/pytest/build/wheel/compileall/shell/diff/secret/raw-log
suite and current GitHub CI. Skipped/not-run is not pass.

## Non-goals

- No Gateway code, branch, OAP artifact, PR, or merge mutation.
- No Local Coding merge by coding agent and no new PR.
- No persistent Gateway/database/container/service/profile deployment.
- No public TLS/bind/firewall/VPN change or direct-vLLM retirement.
- No sandbox/bubblewrap/workspace-write diagnosis.
- No multi-worker/restart-persistent replay, rotation overlap, certification,
  production, or generic hardware claim.
- No host Codex session/history/cache access.

## Publication contract

Amend only Local Coding PR #7. Push all non-report work, record the literal
implementation SHA, then atomically publish exactly one immutable report at
`oap/reports/005-h-corrected-gateway-real-codex-acceptance.md` with literal
implementation SHA and `Report publication commit: SELF`. SELF must change only
that report, its first parent must equal the implementation SHA, and it must be
the remote PR head before exact response FIFO `OK`.
