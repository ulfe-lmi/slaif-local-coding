# Testing ledger 003 — real Codex RC4 qualification (PASS)

## Purpose

This append-only ledger entry records the bounded standalone real-Codex
qualification of `slaif-local-coding` 0.1.0-rc4 performed by the
opt-in, fail-closed, privacy-bounded repository gate
(`scripts/real_codex_rc_qualification.py`, facts schema v2). It is
documentation and sanitized evidence, not an accepted fix, release
acceptance, benchmark result, or authorization to modify a deployed
service.

Ledger 002 remains the scoped RC3 real-Codex PASS evidence it is; this
entry supersedes nothing and re-runs the qualification on the corrected
harness after the 014-b repair round.

## Qualified identities

- Product source (image build commit `S4`):
  `601a7f9fae19869ad8e09f10fa994550368fd87c`
- Product wheel `W4` (byte-identical across the two observed CPython
  3.12 patch builds; bound equal in the gate facts):
  `897ef60568e9521dbb4ea563f297608e4409e02d54109471e789d43ff57dd10d`
  (identical to the RC3 wheel: this round changed no wheel input —
  `src/` and package metadata are untouched; the repair lives in the
  qualification harness, RC record machinery, workflows, and docs)
- Subject client: Codex CLI 0.149.0
  (`bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`)
- Responses model name: `qwen3.8-27b`
- Topology: disposable Codex home/repository → `127.0.0.1:18031` Local
  Coding → existing protected backend endpoint (loopback fixture);
  **no SLAIF API Gateway** (gateway ingress disabled, no signed Gateway
  headers)
- Gate schema: `slaif-real-codex-rc-qualification-v2`
- Run date: 2026-09-28 UTC

## Harness corrections verified by this run (order 014-b, WS-A)

- The fixed synthetic prompt is delivered over **stdin** (Codex 0.149
  documented stdin mode); the client argv is exactly
  `[codex, exec, --ephemeral, -s, danger-full-access, --json]` — no
  prompt, no model flag, no provider, no URL, no credential.
- Provider/model/catalog settings live in the **disposable Codex home**
  `config.toml` (mode 0600, deleted with the home); the upstream
  credential is referenced only by an environment variable name; the
  backend URL arrives through a protected mode-0600 file reference,
  never through any process argv.
- A **live** stdout+stderr byte ceiling (1 MiB default) terminates the
  whole session on exceedance; byte COUNTS are the only recorded
  output facts.
- Tool interactions are counted **content-free** from the closed
  `--json` event stream (`item.completed` with tool item types only);
  any non-JSON line fails the event stream closed.
- Explicit mechanical ceilings (all enforced, all below their limits in
  this run): attempts ≤ 2, attempt timeout 600 s, total timeout 5400 s,
  adapter requests ≤ 64 (all statuses), compiler calls ≤ 4, tool
  interactions 1..8, arms ≤ 4.

## Result

Overall verdict: **PASS** (all three required product arms pass;
protected state unchanged; disposable state removed).

- **VISION**: verdict `PASS` — attempts 1, exit 0, sentinel present
  (3 bytes), 1 genuine tool interaction, adapter 200/500/422 = 2/0/0,
  upstream failures 0, compiler cache entries 0, duration 8 s, failure
  class `none`.
- **CACHE**: verdict `PASS` — attempts 1, exit 0, sentinel present
  (3 bytes), 1 genuine tool interaction, adapter 200/500/422 = 2/0/0,
  upstream failures 0, compiler calls 1, compiler cache entries 1,
  duration 31 s, failure class `none`.
- **BOTH**: verdict `PASS` — attempts 1, exit 0, sentinel present
  (3 bytes), 1 genuine tool interaction, adapter 200/500/422 = 2/0/0,
  upstream failures 0, compiler calls 1, compiler cache entries 1,
  duration 31 s, failure class `none`.
- **DIRECT**: verdict `PASS` — attempts 1, exit 0, sentinel present
  (3 bytes), 1 genuine tool interaction, adapter 200/500/422 = 0/0/0
  (bypassed by construction), upstream failures 0, compiler cache
  entries 0, duration 6 s, failure class `none`.

The CACHE and BOTH arms demonstrate the full constitutional path end to
end (deterministic AGENTS.md observation from a genuine Codex project
envelope → compiler over the direct authenticated upstream channel →
one derived-cache entry each) while the VISION arm demonstrates the
one-image `retain_newest` route policy with the compatibility repair in
place. DIRECT is a contextual backend control and never substitutes for
a product arm.

## Protected state

13 protected files checked, 0 changed; units
`qwen-serving-vision.service` (active) and `qwen-serving.service`
(inactive) unchanged; port 18020 held exactly one listener and 18031
was free before and after. No protected model, vLLM, network, or
service state was altered.

## Environment note

The protected host forbids the unprivileged user-namespace network setup
that bubblewrap requires, so the genuine client runs with its
client-side sandbox set to `danger-full-access`. The gate's own
boundary is the control: fresh disposable workspace and Codex home,
loopback-only adapter on 18031, fixed synthetic prompt over stdin, no
credentials or private URLs in argv, bounded attempts and timeouts,
enforced byte ceilings, sanitized facts only.

## Evidence

[real-codex-rc4-qualification.json](real-codex-rc4-qualification.json)
is the gate's closed-schema sanitized facts record. It contains only
fixed categories, counts, statuses, version/hash, timings, and boolean
verdicts — no prompt, source, tool argument or output, request/response
body, image, credential, private URL, or session ID.

`MANIFEST.sha256` covers exactly this ledger directory (the manifest
itself excepted, per the ledger 001/002 convention) in sha256sum
format.
