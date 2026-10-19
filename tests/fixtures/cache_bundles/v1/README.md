# Synthetic cache-bundle observation fixtures (v1)

Every JSON file in this directory is **synthetic**. Provenance is per shape
family and is stated in each fixture's `observed_format_authority`:

- `root_*` fixtures model the project-instructions **root envelope** shapes;
  their observed-format authority is the sanitized Codex 0.149.0
  API-boundary capture record
  ([`tests/fixtures/codex/0.149.0/README.md`](../../codex/0.149.0/README.md)).
  That capture is **root-only**: it contains no read call/result or exec
  wrapper content, so it is not authority for the read wrapper shape.
- `read_*` fixtures model the Responses `function_call` /
  `function_call_output` (and Chat `tool_calls` / `tool`) pairing plus the
  **exec wrapper text form**; their observed-format authority is the human
  handoff section 6.2 documented real format
  ([`docs/CACHE-REWORK.md`](../../../docs/CACHE-REWORK.md)), with synthetic
  supplemental values (chunk IDs, timings, content). The real-format
  `Chunk ID:` header and the explicitly earned compatible `Chunk Id:`
  variant are both exercised.

No fixture here is a fresh actual-client trace, and no private audit history,
task answer, credential, or customer/source content enters these files.

Each fixture self-identifies in its top-level `_fixture` object:

- `synthetic: true`;
- `observed_format_authority`: the observed-format record it models;
- `parser_versions`: the observer/envelope/read-grammar/tool-wrapper versions
  the fixtures were authored against (they must match the constants in
  `src/slaif_local_coding/constitution/bundles/observation_models.py`);
- `note`: what the file exercises.

The `_fixture` key is out-of-band annotation: the observation code reads only
the recognized payload keys (`input`, `messages`, `tools`) and ignores
unknown top-level keys; tests assert that behavior explicitly.

## File families

- `root_*`: versioned project-instructions envelope shapes — adjacent,
  newline-separated and separate-item environment tails, CRLF terminators,
  repeated identical roots, same-scope version candidates, competing scopes,
  assistant negatives and malformed-Unicode rejection.
- `read_*`: supported call/result pairs — single and two-member `cat`,
  reversed and repeated operands, Unicode/CRLF content, empty-file, nonzero
  exit, truncation, missing body, duplicate/mismatched call IDs, namespace
  names with and without envelope evidence, process-running and write_stdin
  deferrals, Chat equivalent, substitution and fragment negatives, and the
  human-handoff 6.2 real-format wrapper (`read_handoff_wrapper_format_*`).

Content strings are minimal synthetic placeholders (they look like
instructions or file content but are not). Exact byte digests asserted by
tests are computed from these exact bytes at test time; the fixtures never
carry asserted digest values, so a byte change is caught by every span and
reconstruction assertion rather than by a stale constant.
