# Contributing

Development is OAP-governed.

- Read `AGENTS.md`, `ARCHITECTURE-for-agents.md`, `SECURITY.md`, `TESTING.md`,
  and `OAP-COMMUNICATION-coding-agent.md` before mutation.
- No direct commits to protected `main` after bootstrap.
- One numeric OAP objective equals one PR: `NNN-a` creates it; `NNN-b..z`, then
  `NNN-aa..zz`, amend it.
- Coding agents and ordinary contributors never merge their own OAP PR.
- Scope, non-goals, tests, documentation, security, and live-host effects must
  be explicit before implementation.
- Preserve the current Qwen/vLLM installation as a protected test fixture.
- Never commit prompts, source code, images, raw request/response bodies,
  credentials, API keys, private URLs, or cache contents collected from live
  users.
- New production dependencies require purpose, version lock, license review,
  tests, and architecture compatibility.
- A passing focused test is not evidence that unrun integration/live/streaming/
  vision tests passed. Report exact states.

Required PR evidence is defined by the active OAP order and `TESTING.md`.
