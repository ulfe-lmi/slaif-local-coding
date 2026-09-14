"""Mechanical release-artifact content policy (order 009-a, workstream B).

This is the machine-executable proof behind docs/RELEASE-ARTIFACT-POLICY.md.
It inspects the built wheel and sdist and fails on any forbidden entry, any
missing required entry, or any forbidden byte pattern inside an artifact file.

Policy summary
--------------
- The wheel is the single supported distributable. It must contain exactly the
  runtime package plus dist-info metadata and license files (the verified-clean
  property from the base state), and no other top-level entries.
- The sdist is a developer-only source archive, not a supported release
  artifact. It carries a deliberate whitelist (see pyproject.toml) and must
  still pass the same forbidden-entry and forbidden-content rules.
- No artifact may contain orchestration transcripts (oap/), OAP runtime state
  (runtime.env), temporary/placeholder files (Local, clean, unchanged),
  caches/venvs, host-specific paths (``/synology/``, hostnames), private LAN
  endpoints, or credential/key material.

Usage (local gates and CI):

    python scripts/artifact_policy_check.py --dist dist --inspect
    python scripts/artifact_policy_check.py --dist dist --install-smoke

The inspect mode is also exercised by tests/test_artifact_policy.py so the
gate runs inside the ordinary pytest suite.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path

PACKAGE_NAME = "slaif-local-coding"
PACKAGE_DIR = "slaif_local_coding"

# ---------------------------------------------------------------------------
# Forbidden entries and content
# ---------------------------------------------------------------------------

# Path prefixes that must never appear inside any artifact (relative to the
# artifact root; for the sdist the leading project directory is stripped).
FORBIDDEN_PATH_PREFIXES: tuple[str, ...] = (
    "oap/",
    "scripts/",
    "references/",
    "dist/",
    "build/",
    ".git/",
    ".venv/",
    ".mypy_cache/",
    ".pytest_cache/",
    ".ruff_cache/",
    ".github/",  # only the CI workflow is re-allowed for the sdist below
    "__pycache__/",
    "secrets/",
)

# Exact relative paths that must never appear inside any artifact.
FORBIDDEN_PATHS_EXACT: frozenset[str] = frozenset(
    {
        "Local",
        "clean",
        "unchanged",
        "runtime.env",
        "oap/active",
        "AGENTS.md",
        "OAP-COMMUNICATION-coding-agent.md",
        "ARCHITECTURE-for-agents.md",
        "ARCHITECTURE.md",
        "SECURITY.md",
        "TESTING.md",
        # Host-specific content that would otherwise ship in these files.
        "docs/LIVE-TEST-ENVIRONMENT.md",
        "docs/OAP-RUNBOOK.md",
        "docs/SLAIF-GATEWAY-INTEGRATION.md",
        "tests/test_packaging.py",
        "tests/test_config.py",
        "tests/test_gateway_accounting_rehearsal.py",
        "tests/test_safe_evidence.py",
    }
)

# The sdist is the only target where the CI workflow file is allowed; every
# other .github path stays excluded by FORBIDDEN_PATH_PREFIXES.
SDIST_ALLOWED_EXTRAS: frozenset[str] = frozenset({".github/workflows/ci.yml"})

FORBIDDEN_SUFFIXES: tuple[str, ...] = (".pyc", ".pyo", ".key", ".pem", ".env")

# Byte patterns that identify host-specific or credential-bearing content.
FORBIDDEN_CONTENT_PATTERNS: tuple[tuple[str, re.Pattern[bytes]], ...] = (
    ("host_path_synology", re.compile(rb"/synology/")),
    ("hostname", re.compile(rb"hinton1")),
    ("private_lan_endpoint", re.compile(rb"10\.8\.132\.\d+")),
    ("slaif_key_material", re.compile(rb"sk-slaif-[A-Za-z0-9]")),
    ("upstream_api_key_value", re.compile(rb"QWEN3090_API_KEY\s*=\s*[A-Za-z0-9._\-]{8,}")),
    ("vllm_api_key_value", re.compile(rb"VLLM_API_KEY\s*=\s*[A-Za-z0-9._\-]{8,}")),
    (
        "adapter_service_token_value",
        re.compile(rb"SLAIF_ADAPTER_SERVICE_TOKEN\s*=\s*[A-Za-z0-9._\-]{8,}"),
    ),
    (
        "adapter_signing_secret_value",
        re.compile(rb"SLAIF_ADAPTER_SIGNING_SECRET\s*=\s*[A-Za-z0-9._\-]{8,}"),
    ),
)


def _sha256(data: bytes | Path) -> str:
    digest = hashlib.sha256()
    if isinstance(data, Path):
        with data.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
    else:
        digest.update(data)
    return digest.hexdigest()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _artifact_globs(dist_dir: Path, suffix: str) -> list[Path]:
    """Match built artifacts by both the PEP 503 and raw project name."""
    patterns = (f"{PACKAGE_NAME.replace('-', '_')}-*.{suffix}", f"{PACKAGE_NAME}-*.{suffix}")
    found: set[Path] = set()
    for pattern in patterns:
        found.update(dist_dir.glob(pattern))
    return sorted(found)


def _artifact_files(artifact: Path) -> dict[str, bytes]:
    """Return {relative_path: bytes} for every regular file in an artifact."""
    files: dict[str, bytes] = {}
    if artifact.name.endswith(".whl"):
        with zipfile.ZipFile(artifact) as wheel:
            for info in wheel.infolist():
                if info.is_dir():
                    continue
                files[info.filename] = wheel.read(info)
    elif artifact.name.endswith(".tar.gz"):
        with tarfile.open(artifact, "r:gz") as sdist:
            for member in sdist.getmembers():
                if not member.isfile():
                    continue
                name = member.name
                if "/" in name:
                    name = name.split("/", 1)[1]
                handle = sdist.extractfile(member)
                if handle is None:  # pragma: no cover - defensive
                    continue
                files[name] = handle.read()
    else:
        raise ValueError(f"unsupported artifact type: {artifact.name}")
    return files


def _check_paths(kind: str, name: str, paths: list[str], violations: list[str]) -> None:
    for path in sorted(set(paths)):
        if path in SDIST_ALLOWED_EXTRAS and kind == "sdist":
            continue
        flagged = False
        for forbidden in FORBIDDEN_PATH_PREFIXES:
            if path == forbidden.rstrip("/") or path.startswith(forbidden):
                violations.append(f"{kind}:{name}: forbidden path {path!r}")
                flagged = True
                break
        if flagged:
            continue
        if path in FORBIDDEN_PATHS_EXACT:
            violations.append(f"{kind}:{name}: forbidden path {path!r}")
        if any(path.endswith(suffix) for suffix in FORBIDDEN_SUFFIXES):
            violations.append(f"{kind}:{name}: forbidden suffix in {path!r}")
        parts = path.split("/")
        if parts[-1] == "runtime.env" or (parts[-1].endswith(".env") and parts[-1] != ".gitignore"):
            violations.append(f"{kind}:{name}: forbidden runtime env file {path!r}")


def _check_content(kind: str, name: str, files: dict[str, bytes], violations: list[str]) -> None:
    for path in sorted(files):
        data = files[path]
        for label, pattern in FORBIDDEN_CONTENT_PATTERNS:
            if pattern.search(data):
                violations.append(f"{kind}:{name}: forbidden content {label} in {path!r}")


def _repo_package_files() -> set[str]:
    root = repo_root() / "src" / PACKAGE_DIR
    files = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }
    return files


def inspect_artifacts(dist_dir: Path) -> dict:
    """Inspect wheel+sdist in dist_dir; return a JSON-serializable summary."""
    violations: list[str] = []
    wheels = sorted(_artifact_globs(dist_dir, "whl"))
    sdists = sorted(_artifact_globs(dist_dir, "tar.gz"))
    if len(wheels) != 1:
        violations.append(f"dist:{dist_dir.name}: expected exactly one wheel, found {len(wheels)}")
    if len(sdists) != 1:
        violations.append(f"dist:{dist_dir.name}: expected exactly one sdist, found {len(sdists)}")
    if violations:
        return {"ok": False, "violations": violations, "facts": {}}

    wheel = wheels[0]
    sdist = sdists[0]
    facts: dict = {"wheel": wheel.name, "sdist": sdist.name}

    wheel_files = _artifact_files(wheel)
    sdist_files = _artifact_files(sdist)

    # -- wheel: verified-clean property -------------------------------------
    wheel_tops = sorted({name.split("/")[0] for name in wheel_files})
    dist_info_tops = [t for t in wheel_tops if t.endswith(".dist-info")]
    if wheel_tops != sorted({PACKAGE_DIR, *dist_info_tops}) or len(dist_info_tops) != 1:
        violations.append(f"wheel:{wheel.name}: unexpected top-level entries {wheel_tops}")
    dist_info = dist_info_tops[0] if dist_info_tops else ""

    have_dist_info = {
        name.split("/", 1)[1] for name in wheel_files if name.startswith(dist_info + "/")
    }
    for required in sorted({"METADATA", "WHEEL", "RECORD"}):
        if required not in have_dist_info:
            violations.append(f"wheel:{wheel.name}: missing dist-info entry {required!r}")
    for required in ("licenses/LICENSE", "licenses/NOTICE"):
        if required not in have_dist_info:
            violations.append(f"wheel:{wheel.name}: missing license entry {required!r}")

    wheel_package_files = {
        name.split("/", 1)[1] for name in wheel_files if name.startswith(f"{PACKAGE_DIR}/")
    }
    expected_files = _repo_package_files()
    if wheel_package_files != expected_files:
        missing = sorted(expected_files - wheel_package_files)
        extra = sorted(wheel_package_files - expected_files)
        violations.append(
            f"wheel:{wheel.name}: package contents drift; missing={missing} extra={extra}"
        )
    if "py.typed" not in wheel_package_files:
        violations.append(f"wheel:{wheel.name}: missing py.typed")

    _check_paths("wheel", wheel.name, list(wheel_files), violations)
    _check_content("wheel", wheel.name, wheel_files, violations)

    # -- sdist: developer-only archive --------------------------------------
    required_sdist = {
        "pyproject.toml",
        "uv.lock",
        "README.md",
        "LICENSE",
        "NOTICE",
        "THIRD_PARTY_NOTICES.md",
        "CONTRIBUTING.md",
        f"{PACKAGE_DIR}/__init__.py",
        "tests/test_app.py",
        "config/adapter.example.toml",
        "config/adapter.deployment.template.toml",
        "packaging/slaif-local-coding.service",
        "packaging/readyz-wait.sh",
        "packaging/release_provenance_manifest.json",
        "packaging/release_provenance_manifest.schema.json",
        ".github/workflows/ci.yml",
        "docs/DEPLOYMENT.md",
        "docs/RELEASE-ARTIFACT-POLICY.md",
        "docs/RELEASE-CUTOVER-RUNBOOK.md",
        "docs/ADAPTER-CONFIGURATION.md",
    }
    for required in sorted(required_sdist):
        if required not in sdist_files:
            violations.append(f"sdist:{sdist.name}: missing required entry {required!r}")

    _check_paths("sdist", sdist.name, list(sdist_files), violations)
    _check_content("sdist", sdist.name, sdist_files, violations)

    facts["wheel_entry_count"] = len(wheel_files)
    facts["sdist_entry_count"] = len(sdist_files)
    facts["wheel_package_file_count"] = len(wheel_package_files)
    facts["wheel_sha256"] = _sha256(wheel)
    facts["sdist_sha256"] = _sha256(sdist)
    facts["wheel_size_bytes"] = wheel.stat().st_size
    facts["sdist_size_bytes"] = sdist.stat().st_size
    facts["wheel_top_level"] = wheel_tops
    return {"ok": not violations, "violations": violations, "facts": facts}


# ---------------------------------------------------------------------------
# Fresh-environment install smoke (B4)
# ---------------------------------------------------------------------------


def install_smoke(dist_dir: Path, workdir: Path, python: str = sys.executable) -> dict:
    """Install the built wheel into a fresh empty venv and prove provenance."""
    violations: list[str] = []
    facts: dict = {"python": python}
    wheels = sorted(_artifact_globs(dist_dir, "whl"))
    if len(wheels) != 1:
        return {
            "ok": False,
            "violations": [
                f"dist:{dist_dir.name}: expected exactly one wheel, found {len(wheels)}"
            ],
            "facts": facts,
        }
    wheel = wheels[0]
    workdir.mkdir(parents=True, exist_ok=True)
    venv_dir = workdir / "venv"
    try:
        subprocess.run(
            [python, "-m", "venv", str(venv_dir)],
            check=True,
            capture_output=True,
            timeout=300,
        )
    except subprocess.SubprocessError as exc:
        return {
            "ok": False,
            "violations": [f"venv creation failed: {type(exc).__name__}"],
            "facts": facts,
        }
    venv_python = venv_dir / "bin" / "python"
    venv_pip = venv_dir / "bin" / "pip"
    if not venv_python.exists() or not venv_pip.exists():
        return {
            "ok": False,
            "violations": ["venv python/pip missing after creation"],
            "facts": facts,
        }
    try:
        subprocess.run(
            [
                str(venv_pip),
                "install",
                "--disable-pip-version-check",
                "--no-input",
                str(wheel),
            ],
            check=True,
            capture_output=True,
            timeout=900,
        )
    except subprocess.SubprocessError as exc:
        return {
            "ok": False,
            "violations": [f"fresh wheel install failed: {type(exc).__name__}"],
            "facts": facts,
        }

    probe = (
        "import importlib.metadata as m; import json, slaif_local_coding as s;"
        " print(json.dumps({'module_file': s.__file__, 'version': s.__version__,"
        " 'dist_location': str(m.distribution('slaif-local-coding')._path)}))"
    )
    try:
        probe_out = subprocess.run(
            [str(venv_python), "-c", probe],
            check=True,
            capture_output=True,
            timeout=120,
        ).stdout.decode()
        probe_facts = json.loads(probe_out.strip().splitlines()[-1])
    except (subprocess.SubprocessError, ValueError) as exc:
        return {
            "ok": False,
            "violations": [f"fresh venv import failed: {type(exc).__name__}"],
            "facts": facts,
        }

    module_file = probe_facts["module_file"]
    facts["installed_module_file"] = module_file
    facts["installed_version"] = probe_facts["version"]
    facts["installed_dist_location"] = probe_facts["dist_location"]
    venv_prefix = str(venv_dir.resolve())
    if not module_file.startswith(venv_prefix):
        violations.append(f"installed module not inside disposable venv: {module_file}")
    repo_prefix = str(repo_root().resolve())
    if module_file.startswith(repo_prefix):
        violations.append(f"installed module inside repository checkout: {module_file}")

    entrypoint = venv_dir / "bin" / "slaif-local-coding"
    if not entrypoint.exists():
        violations.append("console entry point missing in fresh venv")
    else:
        facts["entrypoint_path"] = str(entrypoint)
        facts["entrypoint_sha256"] = _sha256(entrypoint)
        help_out = subprocess.run(
            [str(entrypoint), "--help"],
            capture_output=True,
            timeout=120,
        )
        facts["entrypoint_help_exit"] = help_out.returncode
        if help_out.returncode != 0:
            violations.append("entry point --help failed")
        version_out = subprocess.run(
            [str(entrypoint), "--version"],
            capture_output=True,
            timeout=120,
        )
        facts["entrypoint_version_exit"] = version_out.returncode
        facts["entrypoint_version_line"] = version_out.stdout.decode().strip()
        if version_out.returncode != 0:
            violations.append("entry point --version failed")

    return {"ok": not violations, "violations": violations, "facts": facts}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Mechanical release-artifact content policy (order 009-a)."
    )
    parser.add_argument("--dist", type=Path, default=Path("dist"))
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--inspect", action="store_true", help="inspect artifact contents")
    mode.add_argument("--install-smoke", action="store_true", help="fresh-venv wheel install proof")
    parser.add_argument("--workdir", type=Path, default=None)
    args = parser.parse_args()

    dist_dir = args.dist.resolve()
    if not dist_dir.is_dir():
        print(
            json.dumps({"ok": False, "violations": [f"dist dir missing: {dist_dir}"], "facts": {}})
        )
        return 2

    if args.inspect:
        result = inspect_artifacts(dist_dir)
    else:
        workdir = args.workdir or Path(tempfile.mkdtemp(prefix="slaif-artifact-smoke-"))
        try:
            result = install_smoke(dist_dir, workdir)
        finally:
            if args.workdir is None:
                shutil.rmtree(workdir, ignore_errors=True)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
