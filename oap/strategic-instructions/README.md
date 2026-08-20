# Strategic workspace bootstrap source

These files are copied by `../bin/bootstrap-two-codex-oap.sh` to:

```text
/synology/homes/janezp/codex-supervision/slaif-local-coding
```

The strategic Codex runs there. Root repository `AGENTS.md` governs the coding
Codex; this directory does not override it. `initial-orders/` contains inert
editable seed drafts. An order becomes executable only after the strategic agent
finalizes a separate strategic-workspace copy, atomically publishes it into
`oap/orders/`, writes `oap/active`, and sends exact FIFO `OK`.
