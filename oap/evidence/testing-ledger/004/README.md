# Testing ledger 004 — real Codex RC5 qualification (PASS)

## Purpose

This append-only ledger entry records the bounded standalone real-Codex
qualification of `slaif-local-coding` 0.1.0-rc5 performed by the
opt-in, fail-closed, privacy-bounded repository gate
(`scripts/real_codex_rc_qualification.py`, facts schema v2). It is
documentation and sanitized evidence, not an accepted fix, release
acceptance, benchmark result, or authorization to modify a deployed
service.

Ledger 003 remains the scoped RC4 real-Codex PASS evidence it is; this
entry supersedes nothing and re-runs the qualification against the RC5
candidate after RC4 was rejected for the source-reference binding
defect (work order 014-c, workstream E). The gate is the harness
corrected in 014-b, carrying the 014-c RC5 identity binding (RC5
sentinel, credential environment key, and per-arm provider identity);
no gate semantics changed.

## Qualified identities

- Product source (image build commit `S5`):
  `e04b4a99afa6268c98f28ed7abfc1db506107523`
- Product wheel `W5` (byte-identical across the two observed CPython
  3.12 patch builds; bound equal in the gate facts):
  `897ef60568e9521dbb4ea563f297608e4409e02d54109471e789d43ff57dd10d`
  (identical to the RC3/RC4 wheels: this round changed no wheel input —
  `src/` and package metadata are untouched; the changes live in the RC
  record machinery, the record-present rehearsal, workflows, and docs)
- Published image digest `D5`
  `sha256:70b450f5eaf885a38015838b30198d02072bf0f9ae30258bdc4e68d5c957642f`
  under the tags `0.1.0-rc5` and
  `sha-e04b4a99afa6268c98f28ed7abfc1db506107523` (publication run
  36410676600, 2026-09-28T10:36:08Z → 2026-09-28T10:36:38Z)
- Subject client: Codex CLI 0.149.0
  (`bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`)
- Responses model name: `qwen3.8-27b`
- Topology: disposable Codex home/repository → `127.0.0.1:18031` Local
  Coding → existing protected backend endpoint (loopback fixture);
  **no SLAIF API Gateway** (gateway ingress disabled, no signed Gateway
  headers)
- Gate schema: `slaif-real-codex-rc-qualification-v2`
- Run date: 2026-09-28 UTC

## Result

Overall verdict: **PASS** (all three required product arms pass;
protected state unchanged; disposable state removed).

- **VISION**: verdict `PASS` — attempts 1, exit 0, sentinel present
  (3 bytes), 1 genuine tool interaction, adapter 200/500/422 = 2/0/0,
  upstream failures 0, compiler cache entries 0, duration 4 s, failure
  class `none`.
- **CACHE**: verdict `PASS` — attempts 1, exit 0, sentinel present
  (3 bytes), 1 genuine tool interaction, adapter 200/500/422 = 2/0/0,
  upstream failures 0, compiler calls 1, compiler cache entries 1,
  duration 38 s, failure class `none`.
- **BOTH**: verdict `PASS` — attempts 1, exit 0, sentinel present
  (3 bytes), 1 genuine tool interaction, adapter 200/500/422 = 2/0/0,
  upstream failures 0, compiler calls 1, compiler cache entries 1,
  duration 35 s, failure class `none`.
- **DIRECT**: verdict `PASS` — attempts 1, exit 0, sentinel present
  (3 bytes), 1 genuine tool interaction, adapter 200/500/422 = 0/0/0
  (bypassed by construction), upstream failures 0, compiler cache
  entries 0, duration 8 s, failure class `none`.

The CACHE and BOTH arms demonstrate the full constitutional path end to
end (deterministic AGENTS.md observation from a genuine Codex project
envelope → compiler over the direct authenticated upstream channel →
one derived-cache entry each) while the VISION arm demonstrates the
one-image `retain_newest` route policy. DIRECT is a contextual backend
control and never substitutes for a product arm.

Every mechanical ceiling was enforced and stayed below its limit: arms
4 ≤ 4, tool interactions 1/arm ≤ 8, adapter requests ≤ 64, compiler
calls ≤ 4, per-attempt output cap 1 MiB, per-attempt 600 s, total
5400 s.

## Protected state

13 protected files checked, 0 changed; units
`qwen-serving-vision.service` (active) and `qwen-serving.service`
(inactive) unchanged; port 18020 held exactly one listener and 18031
was free before and after. No protected model, vLLM, network, or
service state was altered; the long-lived vLLM fixture process (PID
23961, no restart) was untouched.

## Environment note

The protected host forbids the unprivileged user-namespace network setup
that bubblewrap requires, so the genuine client runs with its
client-side sandbox set to `danger-full-access`. The gate's own
boundary is the control: fresh disposable workspace and Codex home,
loopback-only adapter on 18031, fixed synthetic prompt over stdin, no
credentials or private URLs in argv, bounded attempts and timeouts,
enforced byte ceilings, sanitized facts only.

## Evidence

[real-codex-rc5-qualification.json](real-codex-rc5-qualification.json)
is the gate's closed-schema sanitized facts record. It contains only
fixed categories, counts, statuses, version/hash, timings, and boolean
verdicts — no prompt, source, tool argument or output, request/response
body, image, credential, private URL, or session ID.

`MANIFEST.sha256` covers exactly this ledger directory (the manifest
itself excepted, per the ledger 001/002 convention) in sha256sum
format.
