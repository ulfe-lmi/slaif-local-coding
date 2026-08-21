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

To refresh safely, create a disposable repository containing only synthetic data,
start a loopback fake endpoint which returns a minimal successful Responses JSON
object (`id`, `object`, `status`, and an empty `output`), then run the target CLI
with this command skeleton (placeholders are not credential literals):

```text
CODEX_HOME=<temporary-home> CODEX_API_KEY=<throwaway-value> codex exec \
  --ephemeral --ignore-user-config -c model_provider=<temporary-provider> \
  -c model_providers.<temporary-provider>.base_url=http://127.0.0.1:<port>/v1 \
  <synthetic-request>
```

Minimize the received JSON in memory to the matching developer/`input_text`
project-instruction item. Never commit the raw capture. The direct `input_file`
and Responses `function_call`/`function_call_output` fixtures are synthetic
supplements, not shapes observed in that CLI capture.
