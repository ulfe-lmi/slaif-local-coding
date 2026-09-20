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

ID=`NNN-L`, with one or two lowercase suffix letters. `NNN-a` creates exactly
one branch/PR. `NNN-b..NNN-z`, then `NNN-aa..NNN-zz`, amend that same PR. One
numeric objective=one PR. Strategic alone chooses IDs, accepts, merges,
advances, abandons, or escalates.

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

Field law (clarified prospectively by order 013-i A3):
`Implementation head SHA` is the literal immediate pre-report commit
(the last implementation commit pushed before the report), NOT the image
source commit. The image source commit, when an image is in scope, has its
own separate field. Historical Objective-013 image rounds recorded the
implementation head as `W6b = S` (implementation head coinciding with the
image source commit). Corrected account (order 013-j, J6): in round 013-g
the named implementation head `fe334e87...` (W6b = S) equals the first
parent of its SELF report commit `881f1f36...` — the two facts were
genuinely equal there. In round 013-h (a zero-work round blocked at the G0
entry gate, with no new implementation commits) the named implementation
head was the UNCHANGED `fe334e87...` carried over from 013-g, while the
first parent of its SELF report commit `64068209...` is the 013-g report
commit `881f1f36...` — so for 013-h the two facts were NOT equal, and the
earlier "coincidence of equal facts" explanation is inaccurate for 013-h
(this correction is recorded in the 013-j report). In 013-i the named
implementation head `317cc272...` equals the first parent of its SELF
report commit `fac7135...`. The field law removes the ambiguity
prospectively without altering any historical report or order bytes.

## Secrets

Never place credentials, bearer values, cookies, private keys/URLs, DB URLs,
raw prompts/source/images/tool output, or customer data in OAP artifacts.
