# Public archive redactions and exclusions

The source snapshot is intentionally not byte-identical to the private VM copy.
This file lists every transformation class.

## Excluded paths

- `.local/`
- `runs/`, `state/`, and `secrets/`
- `.venv/`, `.pytest_cache/`, `__pycache__/`, `*.pyc`, and `dist/`
- private backend environment files and all authentication stores
- raw Codex/native rollout artifacts, subject workspaces, screenshots, adapter
  logs, and host telemetry
- all invalid-harness qualification outcomes, task/judge scores, per-condition
  statuses, token totals, wall times, and attempt-result tables
- delivered/current result artifacts `VALIDATION.md`, `VALIDATION.json`, and
  `validation/offline-tests.xml`

## Replacements in the public `harness/` copy

| Private class | Public replacement |
|---|---|
| benchmark host address | `192.0.2.195` (RFC 5737 documentation address) |
| benchmark VM address | `192.0.2.112` (RFC 5737 documentation address) |
| physical GPU UUID | `GPU-REDACTED-BENCHMARK-LANE` |
| VM private root | `/ABSOLUTE/PRIVATE/slaif-benchmark` |

The historical delivery manifest was renamed to
`harness/MANIFEST.pre-redaction.sha256`; its hashes describe the pre-redaction
delivery and are not expected to validate this public copy. The archive-level
`MANIFEST.sha256` authenticates the committed sanitized copy.

No product source, model weights, customer data, real credential, private URL,
raw subject response body, or tool output is included. At explicit human
direction, the post-invalidation model catalog is included verbatim; its
`instructions_template` is therefore intentionally public.
