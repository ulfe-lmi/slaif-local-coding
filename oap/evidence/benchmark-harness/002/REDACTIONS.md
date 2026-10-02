# Archive 002 redactions and exclusions

## Excluded material

- credentials, authorization headers, authentication stores, and private
  environment files;
- raw Codex events, prompts, responses, reasoning, tool inputs/outputs, rollout
  databases, and SQLite state;
- subject workspaces, screenshots, browser profiles, and adapter logs;
- answer values in public result tables (the harness source itself contains the
  now-disclosed historical answer key for engineering audit);
- raw/compact host telemetry, exact timestamps, PIDs, physical GPU UUIDs, and
  private endpoint addresses;
- absolute VM-private paths;
- caches, virtual environments, bytecode, build outputs, and private controller
  state not explicitly reduced to a content-free export.

Raw recorder files were transferred privately, streamed into a compact
derivative and summary, and then deleted from the VM at human instruction after
verification. This archive therefore says "excluded," not "pending transfer."

## Replacements in `harness.tar.gz`

| Private class | Public replacement |
|---|---|
| benchmark host address | `192.0.2.195` (RFC 5737 documentation address) |
| benchmark VM address | `192.0.2.112` (RFC 5737 documentation address) |
| private benchmark root | `/ABSOLUTE/PRIVATE/slaif-benchmark` |

The historical delivery manifest inside the tarball was retained as
`MANIFEST.pre-redaction.sha256`; it describes pre-redaction bytes and is not
expected to validate the public copy. `HARNESS-CONTENTS.sha256` validates the
sanitized extracted tree, and `MANIFEST.sha256` validates this committed bundle.

The human-supplied model catalog is intentionally public and included verbatim,
including its instruction template. No bearer value appears in that file or in
the generated configuration examples.

Preliminary result exports contain identifiers, classifications, content-free
counter values, timings, and judge outcomes. Missing observations remain null,
never zero. The old human-invalidated archive-001 outcomes remain excluded.
