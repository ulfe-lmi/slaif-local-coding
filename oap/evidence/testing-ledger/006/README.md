# Testing ledger 006 — real Codex RC8 qualification (PASS)

## Purpose

This append-only ledger entry records the bounded standalone real-Codex
qualification of `slaif-local-coding` 0.1.0-rc8 performed by the
opt-in, fail-closed, privacy-bounded repository gate
(`scripts/real_codex_rc_qualification.py`, facts schema v2). It is
documentation and sanitized evidence, not an accepted fix, release
acceptance, benchmark result, or authorization to modify a deployed
service.

Ledger 005 remains the scoped RC7 real-Codex PASS evidence it is; this
entry supersedes nothing and re-runs the qualification against the RC8
candidate (order 015-a). The gate is the same harness semantics as
ledger 005 with the RC8 identity binding (RC8 sentinel, wheel W8,
per-arm provider identity); no gate semantics changed in this round.

## Qualified identities

- Product source (image build commit `S`):
  `718fff301bed0a5ba93b29196cde4d0bcc5d711a`
- Product wheel `W8` (byte-identical across the observed CPython 3.12
  patch builds and the in-workflow CI rebuild; bound equal in the gate
  facts):
  `eb241dda2e079b29190868108c488edaf98261c84119bfd405070dea98b546b9`
- Published image digest `D8`
  `sha256:50450f4aa26a4da158dc457e0b80b441c69386c201491c6c0150c25d5916e126`
  under the tags `0.1.0-rc8` and
  `sha-718fff301bed0a5ba93b29196cde4d0bcc5d711a` (publication run
  36954165586, 2026-10-02T02:07:34Z → 2026-10-02T02:08:11Z)
- Subject client: Codex CLI 0.149.0
  (`bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`)
- Responses model name: `qwen3.8-27b`
- Topology: disposable Codex home/repository → `127.0.0.1:18031` Local
  Coding → existing protected backend endpoint (loopback fixture);
  **no SLAIF API Gateway** (gateway ingress disabled, no signed Gateway
  headers)
- Gate schema: `slaif-real-codex-rc-qualification-v2`
- Run date: 2026-10-02 UTC (facts created 2026-10-02T02:10:02Z)

## Result

Overall verdict: **PASS** (all three required product arms pass;
protected state unchanged; disposable state removed).

- **VISION**: verdict `PASS` — attempts 1, exit 0, sentinel present
  (3 bytes), 1 genuine tool interaction, adapter 200/500/422 = 2/0/0,
  upstream failures 0, compiler calls 0, compiler cache entries 0,
  duration 5 s, failure class `none`.
- **CACHE**: verdict `PASS` — attempts 1, exit 0, sentinel present
  (3 bytes), 1 genuine tool interaction, adapter 200/500/422 = 2/0/0,
  upstream failures 0, compiler calls 1, compiler cache entries 1,
  duration 34 s, failure class `none`.
- **BOTH**: verdict `PASS` — attempts 1, exit 0, sentinel present
  (3 bytes), 1 genuine tool interaction, adapter 200/500/422 = 2/0/0,
  upstream failures 0, compiler calls 1, compiler cache entries 1,
  duration 39 s, failure class `none`.
- **DIRECT**: verdict `PASS` — attempts 1, exit 0, sentinel present
  (3 bytes), 1 genuine tool interaction, adapter 200/500/422 = 0/0/0,
  upstream failures 0, compiler calls 0, compiler cache entries 0,
  duration 3 s, failure class `none`.

The CACHE and BOTH arms demonstrate the full constitutional path end to
end (deterministic AGENTS.md observation from a genuine Codex project
envelope → compiler over the direct authenticated upstream channel →
one derived-cache entry each) while the VISION arm demonstrates the
one-image `retain_newest` route policy. DIRECT is a contextual backend
control and never substitutes for a product arm.

Every mechanical ceiling was enforced and stayed below its limit: arms
4 <= 4, tool interactions 1/arm <= 8, adapter
requests <= 64, compiler calls <= 4, per-attempt output cap
1048576 bytes, per-attempt 600 s, total
5400 s, attempts <= 2.

## Protected state

1 protected file checked, 0 changed; user units
`qwen-serving-vision.service` (active) and `qwen-serving.service`
(inactive) unchanged; port 18020 held exactly one listener before and
after and 18031 was free before and after (teardown confirmed). No
protected model, vLLM, network, or service state was altered; the
long-lived vLLM fixture process (PID 23961, no restart) was untouched.

## Environment note

The protected host forbids the unprivileged user-namespace network setup
that bubblewrap requires, so the genuine client runs with its
client-side sandbox set to `danger-full-access`. The gate's own
boundary is the control: fresh disposable workspace and Codex home,
loopback-only adapter on 18031, fixed synthetic prompt over stdin, no
credentials or private URLs in argv, bounded attempts and timeouts,
enforced byte ceilings, sanitized facts only.

## Evidence

[real-codex-rc8-qualification.json](real-codex-rc8-qualification.json)
is the gate's closed-schema sanitized facts record. It contains only
fixed categories, counts, statuses, version/hash, timings, and boolean
verdicts — no prompt, source, tool argument or output, request/response
body, image, credential, private URL, or session ID.

`MANIFEST.sha256` covers exactly this ledger directory (the manifest
itself excepted, per the ledger 001/002 convention) in sha256sum
format.
