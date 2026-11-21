"""The v1 runtime composition (objective 022-c, the startup slice).

The typed startup composition of the ``dependency-bundles-v1``
profile over the accepted 019/020/021/022 components: the ACTUAL
protected recovery store over the operator-prepared root, the
ACTUAL pinned tokenizer loaded and verified ONCE, the ACTUAL
process RAM owner registry with the closed single-flight work
plane, the ACTUAL validated budget plan and the ACTUAL bounded
direct tool-free compiler bound through the RAM work plane.

Law (objective 022-c section 2):
- the construction ORDER is closed: the recovery capability and
  the pinned tokenizer are verified BEFORE any HTTP client exists,
  so a fixed typed startup failure leaves no network component
  behind and never constructs the legacy pipeline;
- the failure vocabulary is closed (one reason per capability),
  sanitized (no raw store / asset / OS detail, no paths, no
  credential references) and fixed; the app maps each reason to
  its fixed startup message at the entry point;
- the runtime is process-owned: ONE registry, ONE store root
  descriptor, ONE tokenizer instance and ONE compiler client for
  the whole process lifetime (closed in the app lifespan);
- nothing here touches a request payload, a workspace or the
  adapter filesystem beyond the operator-prepared recovery root
  (workspace is the legitimate observed scope or verified resumed
  scope at request time, never adapter filesystem access).
"""

from __future__ import annotations

import asyncio
import os
from collections.abc import Coroutine, Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any

import httpx

from .bundle_budget import BundleBudgetConfig, BundleBudgetPlan
from .bundle_compile_work import BundleCompileWork
from .bundle_compiler import BundleCompiler
from .bundle_tokenizer import (
    BundleTokenizer,
    BundleTokenizerError,
    get_bundle_tokenizer,
)
from .ram_state import RamStateOwnerRegistry
from .ram_work_models import RamWorkBounds
from .recovery_store import RecoveryStore, RecoveryStoreError

if TYPE_CHECKING:
    from ...config import ContextCacheRouteContract


class V1RuntimeReason(StrEnum):
    """The closed v1 startup capability vocabulary."""

    NOT_SELECTED = "not_selected"
    RECOVERY_ROOT = "recovery_root"
    TOKENIZER = "tokenizer"
    MARKER_KEY = "marker_key"
    RAM = "ram"
    COMPILER = "compiler"


#: The fixed sanitized startup message per reason (never a raw
#: store / asset / OS error, never a path or credential reference).
V1_RUNTIME_MESSAGES: Mapping[V1RuntimeReason, str] = {
    V1RuntimeReason.NOT_SELECTED: (
        "the v1 runtime composition requires the dependency-bundles-v1 profile"
    ),
    V1RuntimeReason.RECOVERY_ROOT: (
        "the v1 protected recovery store root is unavailable in this build"
    ),
    V1RuntimeReason.TOKENIZER: ("the v1 pinned tokenizer is unavailable in this build"),
    V1RuntimeReason.MARKER_KEY: (
        "the v1 application-owned marker key reference is unavailable in this build"
    ),
    V1RuntimeReason.RAM: ("the v1 RAM ownership bounds are unavailable in this build"),
    V1RuntimeReason.COMPILER: ("the v1 bounded compiler policy is unavailable in this build"),
}


class V1RuntimeUnavailableError(RuntimeError):
    """Fixed typed startup/readiness failure for the v1 profile.

    Raised by ``create_app`` when the selected v1 profile cannot
    establish its runnable runtime for a capability that is fixed
    at startup (the operator-prepared recovery root, the pinned
    tokenizer assets, the RAM ownership bounds, the compiler
    policy).  A refused app does not establish v1 readiness,
    source replacement, native-format, streaming or recovery
    qualification.  Invalid CONFIGURATION already fails closed in
    the settings model before any runtime construction."""

    def __init__(self, reason: V1RuntimeReason) -> None:
        super().__init__(V1_RUNTIME_MESSAGES[reason])
        self.reason = reason


@dataclass(frozen=True, slots=True)
class V1Runtime:
    """The process-owned v1 runtime (one per app).

    Every component is the ACTUAL accepted component object (not a
    factory or a promise): the registry owns the process RAM
    occupancy ceiling, the store holds the owned root descriptor,
    the tokenizer is the load-and-validate-once pinned instance
    and the compiler is the direct authenticated tool-free
    channel bound into the RAM work plane through
    ``compile_work``.  ``governed_routes`` is the closed
    route-name-to-contract mapping exactly as validated by the
    settings law (every governed route carries its explicit model
    contract; no other route is governed).

    ``marker_key`` is the distinct application-owned private marker
    key material (objective 022-c section 2): resolved ONCE from the
    configured protected environment reference at construction,
    repr-suppressed, never echoed in any error or diagnostic, never
    a gateway / service credential and never a public digest.  The
    stable authenticated session binding is the MAC-bound trusted
    namespace key, which is stable across recovery; the raw key
    bytes are the per-process secret that authenticates the two
    versioned opaque markers."""

    ram_registry: RamStateOwnerRegistry
    recovery_store: RecoveryStore
    tokenizer: BundleTokenizer
    budget: BundleBudgetConfig
    budget_plan: BundleBudgetPlan
    marker_key: bytes = field(repr=False, compare=False)
    compiler: BundleCompiler
    compile_work: BundleCompileWork
    admission_mode: str = field(compare=False)
    governed_routes: Mapping[str, ContextCacheRouteContract] = field(compare=False)

    async def aclose(self) -> None:
        """Close the process-owned network components (the recovery
        store root descriptor is process-owned and closed with the
        process; the RAM registry is pure memory)."""
        await self.compiler.aclose()


def _close_async(coro: Coroutine[Any, Any, None]) -> None:
    """Close one async cleanup coroutine from a sync construction
    context: drive it with a fresh loop when no loop is running,
    schedule it on the running loop otherwise, and abandon (closing)
    the coroutine only as the last bounded fallback."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        try:
            asyncio.run(coro)
        except (OSError, RuntimeError):
            coro.close()
    else:
        try:
            loop.create_task(coro)
        except RuntimeError:
            coro.close()


def build_v1_runtime(
    settings: object,
    *,
    compiler_transport: httpx.AsyncBaseTransport | None = None,
) -> V1Runtime:
    """Compose the v1 runtime for a SELECTED v1 profile.

    The closed construction order (capability BEFORE network):
    1. the profile selector (a non-selected profile is a fixed
       typed refusal, never a silent legacy fall-through);
    2. the operator-prepared protected recovery root (the store
       verifies the existing 0700 current-owner non-symlink root
       on the same descriptor and refuses with the closed typed
       limitation -- it never creates the root or any ancestor);
    3. the pinned tokenizer (load-and-validate-once over the
       packaged digest-verified assets; a refused asset is the
       fixed typed tokenizer failure, never a byte estimation);
    4. the application-owned marker key (resolved ONCE from the
       configured protected environment reference; a missing or
       out-of-range value is the fixed typed marker-key failure,
       never echoed);
    5. the process RAM owner registry with the closed single-
       flight work plane over the configured ownership bounds;
    6. the direct authenticated tool-free compiler bound through
       the RAM work plane (its HTTP client is the FIRST network
       component constructed, after every capability check).
    """
    from ...config import V1_PROFILE, ContextCacheConfig

    cc: ContextCacheConfig | None = getattr(settings, "context_cache", None)
    if cc is None or cc.profile != V1_PROFILE:
        raise V1RuntimeUnavailableError(V1RuntimeReason.NOT_SELECTED)
    if not cc.recovery.enabled or cc.recovery.root is None:
        # The settings closure already refuses this; keep the
        # typed capability vocabulary closed at this boundary too.
        raise V1RuntimeUnavailableError(V1RuntimeReason.RECOVERY_ROOT)
    try:
        store = RecoveryStore(cc.recovery.root)
    except RecoveryStoreError:
        raise V1RuntimeUnavailableError(V1RuntimeReason.RECOVERY_ROOT) from None
    try:
        tokenizer = get_bundle_tokenizer()
    except (BundleTokenizerError, OSError, ValueError):
        raise V1RuntimeUnavailableError(V1RuntimeReason.TOKENIZER) from None
    if cc.budget is None:
        raise V1RuntimeUnavailableError(V1RuntimeReason.TOKENIZER)
    try:
        plan = BundleBudgetPlan(tokenizer, cc.budget)
    except (ValueError, OSError):
        raise V1RuntimeUnavailableError(V1RuntimeReason.TOKENIZER) from None
    if cc.marker_key_env is None:
        # The settings closure already refuses this; keep the
        # typed capability vocabulary closed at this boundary too.
        raise V1RuntimeUnavailableError(V1RuntimeReason.MARKER_KEY)
    marker_key = os.environ.get(cc.marker_key_env, "").encode("utf-8")
    if not 16 <= len(marker_key) <= 256:
        # A missing, empty or out-of-range protected environment
        # value is the fixed typed capability failure; the value
        # itself never crosses this boundary.
        raise V1RuntimeUnavailableError(V1RuntimeReason.MARKER_KEY)
    if cc.compiler is None:
        raise V1RuntimeUnavailableError(V1RuntimeReason.COMPILER)
    try:
        registry = RamStateOwnerRegistry(bounds=cc.ram, work_bounds=RamWorkBounds())
    except (ValueError, TypeError):
        raise V1RuntimeUnavailableError(V1RuntimeReason.RAM) from None
    compiler_client = httpx.AsyncClient(
        base_url=cc.compiler.base_url,
        timeout=httpx.Timeout(cc.compiler.timeout_seconds),
        transport=compiler_transport,
    )
    compiler = BundleCompiler(cc.compiler, client=compiler_client)
    try:
        compile_work = BundleCompileWork(registry, compiler=compiler, tokenizer=tokenizer)
    except (ValueError, TypeError):
        # Unreachable defense (the components above are the actual
        # accepted types); the just-built client is never leaked.
        _close_async(compiler.aclose())
        raise V1RuntimeUnavailableError(V1RuntimeReason.COMPILER) from None
    return V1Runtime(
        ram_registry=registry,
        recovery_store=store,
        tokenizer=tokenizer,
        budget=cc.budget,
        budget_plan=plan,
        marker_key=marker_key,
        compiler=compiler,
        compile_work=compile_work,
        admission_mode=cc.admission_mode,
        governed_routes=dict(cc.route_contracts),
    )


__all__ = [
    "V1Runtime",
    "V1RuntimeReason",
    "V1RuntimeUnavailableError",
    "V1_RUNTIME_MESSAGES",
    "build_v1_runtime",
]
