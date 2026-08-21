# Sanitized Codex 0.149.0 fixtures

`project_instructions_responses.json` is a synthetic supplemental developer-item
shape. It is retained as a conservative compatibility test, but it has no current
capture-provenance claim. The immutable `001-a` report's earlier captured-shape
claim was not reproduced in `001-c` and must not be treated as current wire truth.

The input-file and paired-tool fixtures are synthetic supplemental supported
shapes; the capture did not exercise them. These fixtures document tested shapes,
not universal or future Codex wire stability.

Two fresh disposable validations on 2026-08-21 with `codex-cli 0.149.0` failed to
establish a stable replacement contract. The `001-c` run reported a marker in
top-level instructions plus a user/`input_text` item. The new `001-d` run found one
marker only, at a top-level user/`input_text` item; top-level instructions contained
no AGENTS label, project phrase, delimiter, or synthetic rule. The helper failed
closed and wrote no fixture in both cases. No detector support is inferred from
either unreproduced shape.

To refresh safely, use the executable helper from the repository root. It creates a
new temporary `CODEX_HOME` and Git repository, writes only a synthetic `AGENTS.md`,
starts an ephemeral loopback fake Responses endpoint, and invokes the requested
Codex binary. It never reads or modifies the real Codex home, login, catalog,
profiles, sessions, compaction settings, or a non-disposable repository:

```bash
python3 tests/helpers/capture_codex_project_envelope.py \
  --codex-bin codex --output /tmp/project_instructions_responses.json
```

The helper's fully quoted invocation uses synthetic model
`synthetic-capture-model`, provider `synthetic_capture`, loopback
`base_url=http://127.0.0.1:<ephemeral-port>/v1`, `wire_api="responses"`, and
`env_key="SLAIF_CAPTURE_KEY"`. It sets that variable to the throwaway value
`synthetic-only`. A one-model temporary `model_catalog_json`, derived from the
CLI's bundled `gpt-5.4` entry with a synthetic slug/name/description, makes the
selected synthetic model behavior explicit. The command passes `--ephemeral`,
`--ignore-user-config`, and `-C` with the disposable repository. The fake endpoint
requires `POST /v1/responses` and
`stream: true`, then terminates the CLI with one `response.completed` SSE event
containing a synthetic completed Response with empty `output`.

The raw request exists only in the helper process. Its minimizer requires exactly
one top-level instructions envelope corroborated by one top-level user/`input_text`
envelope with the same logical label and exact inner bytes. It replaces the random
disposable directory with `repo`, permits only the captured environment-context
tail boundary, and emits a synthetic two-position fixture plus safe counts/hash/
length facts. It rejects a missing, relocated, duplicate, mismatched, or unsupported
pair rather than rewriting evidence. It discards authorization and all headers,
IDs, loopback/host paths, internal prompts, tools, unrelated input, user/session/
account values, and response content before writing. Review the minimized output;
never commit a raw capture. The direct `input_file` and Responses
`function_call`/`function_call_output` fixtures are synthetic supplements, not
shapes observed in that CLI capture or claims of universal compatibility.
