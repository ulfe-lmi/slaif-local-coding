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
run the target CLI with `--ephemeral --ignore-user-config` and command-line provider
overrides against a temporary loopback fake endpoint, and minimize the received
JSON in memory to only the matching project-instruction item. Use a throwaway
credential environment variable and never commit the raw capture.
