# Synthetic cache-bundle observation fixtures (v1)

Every JSON file in this directory is **synthetic**. It is constructed to the
exact observed API-boundary shapes recorded for Codex 0.149.0 (Responses
`input` items, `function_call`/`function_call_output` pairs, the Chat
`tool_calls`/`tool` equivalent, and the exec wrapper text form). The sanitized
authority record for those shapes is
[`tests/fixtures/codex/0.149.0/README.md`](../../codex/0.149.0/README.md).
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
  deferrals, Chat equivalent, substitution and fragment negatives.

Content strings are minimal synthetic placeholders (they look like
instructions or file content but are not). Exact byte digests asserted by
tests are computed from these exact bytes at test time; the fixtures never
carry asserted digest values, so a byte change is caught by every span and
reconstruction assertion rather than by a stale constant.
