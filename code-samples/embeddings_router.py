# Excerpt from EnzaTrack (full source is private). Shown to illustrate the design;
# it depends on the application's models and is not runnable on its own.
# © Steve KUBENGA BANZA. All rights reserved.

from __future__ import annotations
from typing import List, Sequence, Optional
import logging
from django.conf import settings

from core.models import Organization
from core.constants import EmbeddingProviderChoice

logger = logging.getLogger(__name__)

# Ops toggles
PROVIDER_OVERRIDE: Optional[str] = getattr(settings, "EMBEDDING_PROVIDER", None)  # "local"|"openai"
ALLOW_LOCAL_FALLBACK: bool = bool(getattr(settings, "EMBEDDINGS_ALLOW_LOCAL_FALLBACK", False))

def _safe_getattr(obj, *names, default=None):
    for n in names:
        if hasattr(obj, n):
            return getattr(obj, n)
    return default

def resolve_embedding_provider_for_org(
    org: Optional[Organization],
    *,
    preferred: Optional[str] = None,   # per-call override ("local"|"openai")
) -> str:
    """
    Precedence:
      1) per-call override
      2) settings.EMBEDDING_PROVIDER override (global)
      3) org.subscription.plan: if current AND allows_remote_embeddings -> plan.default_embedding_provider
      4) default LOCAL
    """
    if preferred:
        return preferred

    if PROVIDER_OVERRIDE:
        return PROVIDER_OVERRIDE

    if org:
        sub = _safe_getattr(org, "subscription", default=None)
        is_current = callable(getattr(sub, "is_current", None)) and sub.is_current()
        if sub and is_current:
            plan = _safe_getattr(sub, "plan", "plan", default=None)
            if plan and bool(_safe_getattr(plan, "allows_remote_embeddings", default=False)):
                prov = _safe_getattr(plan, "default_embedding_provider", default=EmbeddingProviderChoice.LOCAL)
                return (prov or EmbeddingProviderChoice.LOCAL).lower()

    return EmbeddingProviderChoice.LOCAL

# Lazy imports to avoid heavy deps at import time
def _import_local():
    from core.utils.embeddings_local import (
        get_embeddings_batch as local_get_batch,
        get_embeddings_batch_for_org as local_get_batch_for_org,
        semantic_search as local_semantic_search,
    )
    return local_get_batch, local_get_batch_for_org, local_semantic_search

def _import_openai():
    from core.utils.embeddings_openai import (
        get_embeddings_batch as openai_get_batch,
        get_embeddings_batch_for_org as openai_get_batch_for_org,  # metered
        semantic_search as openai_semantic_search,
    )
    return openai_get_batch, openai_get_batch_for_org, openai_semantic_search

# -----------------------------
# Routed helpers
# -----------------------------
def get_embeddings_batch_for_org(
    org: Optional[Organization],
    texts: Sequence[str],
    *,
    batch_size: Optional[int] = None,
    model: Optional[str] = None,
    soft_fail: bool = True,            # passed to metered providers
    provider: Optional[str] = None,    # "local"|"openai"
) -> List[List[float]]:
    """
    Org-aware routing:
      - LOCAL → unmetered local implementation
      - OPENAI → metered implementation (plan caps enforced)
    IMPORTANT: If provider is OPENAI and a policy/limit error occurs (e.g., PermissionError),
               we DO NOT fall back to LOCAL (to avoid bypassing caps).
    """
    if not texts:
        return []

    prov = (provider or resolve_embedding_provider_for_org(org)).lower()

    if prov == EmbeddingProviderChoice.OPENAI:
        openai_get_batch, openai_get_batch_for_org, _ = _import_openai()
        try:
            return openai_get_batch_for_org(
                org, texts, batch_size=batch_size, model=model, soft_fail=soft_fail
            )
        except PermissionError:
            # Quota/subscription policy — do not bypass with local
            raise
        except Exception as e:
            # Non-policy failures: optionally fall back if explicitly allowed
            logger.exception("OpenAI embedding failed; fallback=%s. Err: %s", ALLOW_LOCAL_FALLBACK, e)
            if not ALLOW_LOCAL_FALLBACK:
                raise
            local_get_batch, local_get_batch_for_org, _ = _import_local()
            return local_get_batch_for_org(org, texts, batch_size=batch_size, model=model, soft_fail=True)

    # Default/local path
    local_get_batch, local_get_batch_for_org, _ = _import_local()
    return local_get_batch_for_org(org, texts, batch_size=batch_size, model=model, soft_fail=soft_fail)
