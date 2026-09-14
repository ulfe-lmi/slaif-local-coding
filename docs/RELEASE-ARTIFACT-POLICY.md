# Release-artifact policy

Order 009-a, workstream B. This is the deliberate, documented artifact policy
for the `slaif-local-coding` package. It replaces the accidental build-backend
defaults that previously produced a wheel containing only the runtime package
and an sdist containing the entire working tree (including OAP transcripts).

## Supported artifacts

- **Wheel (`slaif-local-coding-<version>-py3-none-any.whl`): the single supported distributable.** It is the only artifact used for deployment,
  upgrade, and rollback (see [deployment](DEPLOYMENT.md)). Its verified-clean
  property is that it contains exactly the `slaif_local_coding/` runtime
  package plus `*.dist-info/` metadata and license files
  (`LICENSE`, `NOTICE` under `licenses/`).
- **sdist (`slaif-local-coding-<version>.tar.gz`): developer-only source
  archive, not a supported release artifact.** It must never be
  treated as one. It carries a deliberate whitelist (code, tests, fixtures,
  config and packaging templates, current docs, CI workflow, project
  metadata) so that a developer can inspect or rebuild the package source
  without receiving orchestration transcripts or host-specific material.

The policy is implemented explicitly in `pyproject.toml`
(`[tool.hatch.build]` top-level exclusions plus per-target
`[tool.hatch.build.targets.wheel]` and `[tool.hatch.build.targets.sdist]`
include/exclude lists). It is not a backend default.

## What no artifact may contain

Both the wheel and the sdist must be free of:

- orchestration transcripts and OAP state: everything under `oap/`
  (orders, reports, `active`, evidence, `bin`, strategic/coding runtime state,
  `runtime.env`);
- temporary/placeholder files (including the untracked `Local`, `clean`,
  `unchanged` repository-root placeholders);
- caches and virtual environments (`__pycache__`, `*.pyc`, `.venv`,
  `.mypy_cache`, `.pytest_cache`, `.ruff_cache`, `build/`, `dist/`,
  `*.egg-info`);
- host-specific artifacts: paths under `/synology`, hostnames, private LAN
  endpoint addresses, and any file that embeds protected-host deployment
  paths (which is why selected docs, test files, and OAP harness scripts are
  excluded from the sdist; they remain in the git repository, and CI runs from
  the git checkout);
- credentials or key material (upstream API keys, gateway service tokens,
  signing secrets, `*.key`, `*.pem`, `*.env` runtime files), and any file
  whose content embeds them as scanner pattern definitions
  (`tests/test_packaging.py` is excluded for this reason; it remains in the
  git repository and runs in CI);
- model weights, or any Gateway code vendored from the separate
  `slaif-api-gateway` repository.

## Mechanical proof

`scripts/artifact_policy_check.py` is the machine-executable policy check:

```bash
uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect
```

It fails on any forbidden entry, any missing required entry (wheel runtime
package + metadata + licenses; sdist whitelist), or any forbidden byte pattern
in any artifact file (host paths, hostnames, private LAN endpoints, key
material, credential values). It re-proves the wheel's verified-clean property
and the drift between the built runtime package and the repository source
package on every run.

The check runs:

- in the local gate (this README's "complete local gate" and the pytest gate
  `tests/test_artifact_policy.py`, which builds fresh artifacts and also
  verifies the scanner detects injected violations);
- in CI, after `uv build`, in the `test` job
  (`scripts/artifact_policy_check.py --dist dist --inspect`);
- as part of the disposable operational qualification
  (`scripts/disposable_deployment_qualification.py`) before any install step.

## Fresh-environment install proof (B4)

The wheel must install into a fresh, empty, disposable virtual environment
(venv, not an editable checkout) using only the built wheel:

```bash
uv run --frozen python scripts/artifact_policy_check.py --dist dist --install-smoke
```

The smoke proves: package import, the `slaif-local-coding` console entry point
resolves and runs (`--help`, `--version`), and runtime source provenance
(installed module and dist-info locations are inside the disposable venv, not
the repository checkout; entry point path and SHA-256 are recorded). It runs
in CI on the runner and in the local qualification.

## Publication

No artifact is published to any registry by this repository. A registry
publication, tag, or release state change is a separate human-authorized act
(see [the cutover/runbook boundary](RELEASE-CUTOVER-RUNBOOK.md)).
