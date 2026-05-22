"""Fetches model lists from an external agent platform API.

Reads the ``AGENT_PLATFORM_API_URL`` environment variable and calls
``GET {AGENT_PLATFORM_API_URL}/models`` to retrieve available models.
Results are cached in-memory with a configurable TTL.
"""

from __future__ import annotations

import os
import time
from typing import Any

from lfx.log.logger import logger

# Environment variable for the agent platform API base URL.
AGENT_PLATFORM_API_URL_ENV = "AGENT_PLATFORM_API_URL"

# Default cache TTL in seconds.
_DEFAULT_CACHE_TTL = 60

# ---------------------------------------------------------------------------
# Module-level in-memory cache
# ---------------------------------------------------------------------------
_cache: list[dict[str, Any]] = []
_cache_timestamp: float = 0.0


def get_agent_platform_api_url() -> str | None:
    """Return the configured agent platform API URL, or *None* if unset."""
    url = os.environ.get(AGENT_PLATFORM_API_URL_ENV, "").strip()
    return url if url else None


def fetch_models_from_agent_platform(
    api_url: str | None = None,
    *,
    cache_ttl: int = _DEFAULT_CACHE_TTL,
    force_refresh: bool = False,
) -> list[dict[str, Any]]:
    """Fetch models from the agent platform's ``/models`` endpoint.

    Args:
        api_url: Base URL of the agent platform API.  If *None*, reads from
            the ``AGENT_PLATFORM_API_URL`` environment variable.
        cache_ttl: Cache TTL in seconds.  Default: 60.
        force_refresh: Bypass cache and force a fresh fetch.

    Returns:
        List of model dicts as returned by the API (each contains at least
        ``id``, ``model_name``, ``base_url``, ``api_key``, ``is_active``).
        Returns an empty list when the API is not configured or unreachable.
    """
    import requests  # noqa: PLC0415

    global _cache, _cache_timestamp

    if api_url is None:
        api_url = get_agent_platform_api_url()

    if not api_url:
        logger.info(
            "[AgentPlatform] AGENT_PLATFORM_API_URL is not configured; "
            "using built-in providers"
        )
        return []

    url = api_url.rstrip("/") + "/models"
    now = time.time()

    # Serve from cache when valid
    if not force_refresh and _cache and (now - _cache_timestamp) < cache_ttl:
        logger.info(
            "[AgentPlatform] Using cached models (%d entries, age=%ds)",
            len(_cache),
            int(now - _cache_timestamp),
        )
        return _cache

    # ------------------------------------------------------------------
    # Fetch fresh data
    # ------------------------------------------------------------------
    logger.info("[AgentPlatform] Fetching models from %s", url)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception:
        logger.exception(
            "[AgentPlatform] Failed to fetch models from %s", url
        )
        # Fall back to stale cache if available
        if _cache:
            logger.debug("Returning stale cached agent platform models")
        return _cache

    try:
        data: dict[str, Any] = response.json()
    except ValueError:
        logger.exception("[AgentPlatform] Invalid JSON response from %s", url)
        return _cache

    models: list[dict[str, Any]] = data.get("models", [])

    # Filter out inactive models
    active_models = [m for m in models if m.get("is_active", True)]

    _cache = active_models
    _cache_timestamp = now
    logger.info(
        "[AgentPlatform] Fetched %d models (%d active) from %s",
        len(models),
        len(active_models),
        url,
    )
    for m in active_models:
        logger.info(
            "[AgentPlatform]   - %s (%s) → %s",
            m.get("id", "?"),
            m.get("model_name", "?"),
            m.get("base_url", "?"),
        )
    return active_models


def invalidate_agent_platform_cache() -> None:
    """Clear the in-memory model cache so the next fetch hits the API."""
    global _cache, _cache_timestamp
    _cache = []
    _cache_timestamp = 0.0


# ---------------------------------------------------------------------------
# Embeddings cache (separate from models cache)
# ---------------------------------------------------------------------------
_embeddings_cache: list[dict[str, Any]] = []
_embeddings_cache_timestamp: float = 0.0


def fetch_embeddings_from_agent_platform(
    api_url: str | None = None,
    *,
    cache_ttl: int = _DEFAULT_CACHE_TTL,
    force_refresh: bool = False,
) -> list[dict[str, Any]]:
    """Fetch embedding models from the agent platform's ``/embeddings`` endpoint.

    Args:
        api_url: Base URL.  Reads ``AGENT_PLATFORM_API_URL`` if *None*.
        cache_ttl: Cache TTL in seconds.
        force_refresh: Bypass cache.

    Returns:
        List of embedding model dicts.  Empty list when unavailable.
    """
    import requests  # noqa: PLC0415

    global _embeddings_cache, _embeddings_cache_timestamp

    if api_url is None:
        api_url = get_agent_platform_api_url()

    if not api_url:
        return []

    url = api_url.rstrip("/") + "/embeddings"
    now = time.time()

    if not force_refresh and _embeddings_cache and (now - _embeddings_cache_timestamp) < cache_ttl:
        logger.info(
            "[AgentPlatform] Using cached embeddings (%d entries, age=%ds)",
            len(_embeddings_cache),
            int(now - _embeddings_cache_timestamp),
        )
        return _embeddings_cache

    logger.info("[AgentPlatform] Fetching embeddings from %s", url)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception:
        logger.exception("[AgentPlatform] Failed to fetch embeddings from %s", url)
        if _embeddings_cache:
            logger.debug("Returning stale cached agent platform embeddings")
        return _embeddings_cache

    try:
        data: dict[str, Any] = response.json()
    except ValueError:
        logger.exception("[AgentPlatform] Invalid JSON response from %s", url)
        return _embeddings_cache

    models: list[dict[str, Any]] = data.get("models", [])
    active_models = [m for m in models if m.get("is_active", True)]

    _embeddings_cache = active_models
    _embeddings_cache_timestamp = now
    logger.info(
        "[AgentPlatform] Fetched %d embeddings (%d active) from %s",
        len(models),
        len(active_models),
        url,
    )
    for m in active_models:
        logger.info(
            "[AgentPlatform]   - %s (%s) → %s",
            m.get("id", "?"),
            m.get("model_name", "?"),
            m.get("base_url", "?"),
        )
    return active_models


def invalidate_agent_platform_embeddings_cache() -> None:
    """Clear the in-memory embeddings cache."""
    global _embeddings_cache, _embeddings_cache_timestamp
    _embeddings_cache = []
    _embeddings_cache_timestamp = 0.0
