# Sanitized Codex 0.149.0 fixtures

`project_instructions_responses.json` is a minimized structural derivative of an
actual provider-bound `codex-cli 0.149.0` capture made from a disposable Git
repository with a synthetic `AGENTS.md`, an ephemeral CLI invocation, and a
temporary loopback fake Responses endpoint. Only the synthetic project-instruction
item and a synthetic user item remain. Authentication, IDs, host paths, internal
prompts, tool schemas, and response content were discarded during capture.

The input-file and paired-tool fixtures are synthetic supplemental supported
shapes; the capture did not exercise them. These fixtures document tested shapes,
not universal or future Codex wire stability.

Validation on 2026-08-21 with `codex-cli 0.149.0` did not reproduce that exact
parent/role shape: the synthetic project marker occurred in top-level instructions
and a user/`input_text` item, not a developer item. The helper therefore wrote no
fixture. This sanitized structural result does not change the accepted detector
contract, but means the earlier developer-item capture provenance remains
unreproduced and must not be generalized to the current custom-provider request.

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

The raw request exists only in the helper process. Its minimizer retains exactly
the synthetic model plus the developer/`input_text` project item, and rejects an
unexpected, relocated, or duplicate project item rather than rewriting its role or
claiming fixture equivalence. It discards authorization and all headers,
IDs, loopback/host paths, internal prompts, tools, unrelated input, user/session/
account values, and response content before writing. Review the minimized output;
never commit a raw capture. The direct `input_file` and Responses
`function_call`/`function_call_output` fixtures are synthetic supplements, not
shapes observed in that CLI capture or claims of universal compatibility.
