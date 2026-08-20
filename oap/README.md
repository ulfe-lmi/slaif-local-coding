# Versioned OAP transcript

This directory stores the repository-visible orchestration transcript. Full
coding behavior is in `../OAP-COMMUNICATION-coding-agent.md`; strategic behavior
is bootstrapped from `strategic-instructions/` into a separate workspace.

## Contract

- `active`: strategic-authored sole selector of executable order.
- `orders/`: immutable strategic-authored activated orders.
- `reports/`: immutable coding-authored execution reports.
- `templates/`: non-authoritative drafting templates.
- `bin/`: local OAP synchronization/validation helpers.
- `strategic-instructions/`: bootstrap source copied to strategic workspace;
  files here are not coding-agent instructions unless root constitution says so.

ID=`NNN-L`. `NNN-a` creates exactly one branch/PR. `NNN-b..NNN-z` amend that
same PR. One numeric objective=one PR. Strategic alone chooses IDs, accepts,
merges, advances, abandons, or escalates.

Activated order, current `active`, and matching report are committed/pushed on
the objective PR. Coding commits strategic artifacts byte-for-byte but does not
own/edit their content.

## FIFO synchronization

FIFOs live outside Git at:

```text
/synology/homes/janezp/codex-supervision/slaif-local-coding/control.fifo
/synology/homes/janezp/codex-supervision/slaif-local-coding/response.fifo
```

Strategic writes control and reads response; coding has inverse direction.
Payload is exactly ASCII `OK` (two bytes, no newline/metadata). FIFO signals do
not select work and do not mean success/acceptance.

## Report publication

Every report records:

```text
Implementation head SHA: <literal 40-hex pre-report commit>
Report publication commit: SELF
```

`SELF` is the GitHub commit containing the exact report. At coding `OK`, it is
the remote PR head, changes only the report, and its first parent equals the
literal implementation SHA. Later continuation may advance head; historical
SELF remains immutable/reachable.

## Secrets

Never place credentials, bearer values, cookies, private keys/URLs, DB URLs,
raw prompts/source/images/tool output, or customer data in OAP artifacts.
