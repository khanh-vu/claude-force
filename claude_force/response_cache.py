"""
Response caching system for Claude API calls.

All critical and high-priority fixes from expert review applied:
- ✅ Cache key length increased to 32 chars (reduced collision risk)
- ✅ HMAC integrity verification for security
- ✅ Optimized LRU eviction with heapq (O(k log n) instead of O(n log n))
- ✅ Cache path validation to prevent directory traversal
- ✅ Improved error handling for file operations
- ✅ Structured logging
"""

import hashlib
import hmac
import json
import time
import heapq
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """
    Cached response entry with integrity verification.

    ✅ Added signature field for HMAC verification
    """

    key: str
    agent_name: str
    task: str
    model: str
    response: str
    input_tokens: int
    output_tokens: int
    estimated_cost: float
    timestamp: float
    hit_count: int = 0
    signature: str = ""  # HMAC signature for integrity


class ResponseCache:
    """
    Intelligent response cache for Claude API calls.

    Features:
    - TTL-based expiration
    - LRU eviction (optimized with heapq)
    - Size limits
    - Cache statistics
    - Exclusion lists (non-deterministic agents)
    - HMAC integrity verification
    - Path traversal protection

    Performance characteristics:
    - Cache hit: O(1) average
    - Cache miss: O(1) average
    - Eviction: O(k log n) where k is eviction count
    """

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        ttl_hours: int = 24,
        max_size_mb: int = 100,
        enabled: bool = True,
        cache_secret: Optional[str] = None,
        exclude_agents: Optional[list] = None,
    ):
        """
        Initialize response cache.

        Args:
            cache_dir: Cache directory (default: ~/.claude/cache)
            ttl_hours: Time to live in hours
            max_size_mb: Maximum cache size in MB
            enabled: Whether caching is enabled
            cache_secret: Secret for HMAC signatures
            exclude_agents: List of agents to exclude from caching
        """
        # ✅ Validate cache directory to prevent path traversal (SECURITY FIX)
        if cache_dir:
            cache_dir = cache_dir.resolve()
            base = Path.home() / ".claude"
            # Allow /tmp and current directory for testing
            allowed_bases = [base, Path("/tmp"), Path.cwd()]

            # Use proper path comparison to prevent bypasses like /tmp_evil or /tmp/../etc
            is_allowed = False
            for allowed_base in allowed_bases:
                try:
                    # Check if cache_dir is relative to allowed_base
                    cache_dir.relative_to(allowed_base.resolve())
                    is_allowed = True
                    break
                except ValueError:
                    # Not relative to this base, try next
                    continue

            if not is_allowed:
                raise ValueError(
                    f"Cache directory must be under {base}, /tmp, or current directory. "
                    f"Got: {cache_dir}"
                )

        self.cache_dir = cache_dir or Path.home() / ".claude" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.ttl_seconds = ttl_hours * 3600
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.enabled = enabled
        self.exclude_agents = set(exclude_agents or [])

        # ✅ HMAC secret for integrity verification
        self.cache_secret = cache_secret or os.getenv(
            "CLAUDE_CACHE_SECRET", "default_secret_change_in_production"
        )

        # ✅ FIXED: Security warning for default secret
        if self.cache_secret == "default_secret_change_in_production":
            logger.warning(
                "⚠️  SECURITY WARNING: Using default HMAC secret! "
                "Cache integrity is NOT protected. "
                "Set CLAUDE_CACHE_SECRET environment variable or pass cache_secret parameter. "
                "Attackers can forge cache entries with the default secret.",
                extra={"security_risk": "HIGH", "cvss_score": 8.1},
            )

        # In-memory cache for fast access
        self._memory_cache: Dict[str, CacheEntry] = {}

        # Statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "size_bytes": 0,
            "integrity_failures": 0,  # ✅ Track integrity check failures
        }

        # Load existing cache index
        self._load_cache_index()

        logger.info(
            "Response cache initialized",
            extra={
                "cache_dir": str(self.cache_dir),
                "ttl_hours": ttl_hours,
                "max_size_mb": max_size_mb,
                "enabled": enabled,
                "entries_loaded": len(self._memory_cache),
            },
        )

    def _cache_key(self, agent_name: str, task: str, model: str) -> str:
        """
        Generate cache key.

        ✅ FIXED: Use 32 chars instead of 16 to reduce collision risk
        """
        content = f"{agent_name}:{task}:{model}"
        # Use 32 characters for 128-bit hash (negligible collision probability)
        return hashlib.sha256(content.encode()).hexdigest()[:32]

    def _compute_signature(self, entry_dict: Dict[str, Any]) -> str:
        """
        Compute HMAC signature for cache entry.

        ✅ NEW: HMAC integrity verification

        Note: Excludes hit_count and signature from verification since
        hit_count is a mutable stat that changes on cache hits.
        """
        # Remove mutable fields that shouldn't affect signature
        entry_copy = entry_dict.copy()
        entry_copy.pop("signature", None)
        entry_copy.pop("hit_count", None)  # Exclude mutable stat

        # Create canonical JSON representation (sorted keys for consistency)
        canonical = json.dumps(entry_copy, sort_keys=True)

        # Compute HMAC-SHA256
        signature = hmac.new(
            key=self.cache_secret.encode(), msg=canonical.encode(), digestmod=hashlib.sha256
        ).hexdigest()

        return signature

    def _verify_signature(self, entry: CacheEntry) -> bool:
        """
        Verify HMAC signature of cache entry.

        ✅ NEW: Integrity verification
        """
        if not entry.signature:
            # Old cache entries without signature - consider invalid
            logger.warning("Cache entry missing signature", extra={"key": entry.key[:8]})
            return False

        expected_sig = entry.signature
        entry_dict = asdict(entry)
        actual_sig = self._compute_signature(entry_dict)

        if expected_sig != actual_sig:
            logger.warning("Cache integrity check failed", extra={"key": entry.key[:8]})
            self.stats["integrity_failures"] += 1
            return False

        return True

    def get(self, agent_name: str, task: str, model: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached response.

        Returns cached response if found and valid, None otherwise.
        """
        if not self.enabled or agent_name in self.exclude_agents:
            return None

        key = self._cache_key(agent_name, task, model)

        # Check memory cache
        if key in self._memory_cache:
            entry = self._memory_cache[key]

            # ✅ Verify integrity
            if not self._verify_signature(entry):
                self._evict(key)
                self.stats["misses"] += 1
                return None

            # Check TTL
            age = time.time() - entry.timestamp
            if age > self.ttl_seconds:
                # Expired
                self._evict(key)
                self.stats["misses"] += 1
                logger.debug("Cache entry expired", extra={"key": key[:8], "age_seconds": age})
                return None

            # Cache hit
            entry.hit_count += 1
            self.stats["hits"] += 1

            logger.debug(
                "Cache hit",
                extra={
                    "key": key[:8],
                    "agent": agent_name,
                    "age_seconds": age,
                    "hit_count": entry.hit_count,
                },
            )

            return {
                "response": entry.response,
                "input_tokens": entry.input_tokens,
                "output_tokens": entry.output_tokens,
                "estimated_cost": entry.estimated_cost,
                "cached": True,
                "cache_age_seconds": age,
                "hit_count": entry.hit_count,
            }

        # Check disk cache
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                # Check file age for TTL
                age = time.time() - cache_file.stat().st_mtime
                if age > self.ttl_seconds:
                    cache_file.unlink()
                    self.stats["misses"] += 1
                    return None

                # Load from disk
                with open(cache_file, "r") as f:
                    entry_dict = json.load(f)
                    entry = CacheEntry(**entry_dict)

                # ✅ Verify integrity
                if not self._verify_signature(entry):
                    self._evict(key)
                    self.stats["misses"] += 1
                    return None

                # Load into memory cache
                self._memory_cache[key] = entry
                entry.hit_count += 1
                self.stats["hits"] += 1

                logger.debug("Cache hit (from disk)", extra={"key": key[:8], "age_seconds": age})

                return {
                    "response": entry.response,
                    "input_tokens": entry.input_tokens,
                    "output_tokens": entry.output_tokens,
                    "estimated_cost": entry.estimated_cost,
                    "cached": True,
                    "cache_age_seconds": age,
                    "hit_count": entry.hit_count,
                }

            except Exception as e:
                logger.warning("Failed to load cache file", extra={"key": key[:8], "error": str(e)})
                # ✅ Clean up corrupt file
                try:
                    cache_file.unlink()
                except OSError:
                    pass

        # Cache miss
        self.stats["misses"] += 1
        logger.debug("Cache miss", extra={"key": key[:8], "agent": agent_name})
        return None

    def set(
        self,
        agent_name: str,
        task: str,
        model: str,
        response: str,
        input_tokens: int,
        output_tokens: int,
        estimated_cost: float,
    ):
        """
        Cache a response.

        Stores response in both memory and disk cache.
        """
        if not self.enabled or agent_name in self.exclude_agents:
            return

        key = self._cache_key(agent_name, task, model)

        entry = CacheEntry(
            key=key,
            agent_name=agent_name,
            task=task,
            model=model,
            response=response,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            estimated_cost=estimated_cost,
            timestamp=time.time(),
        )

        # ✅ Compute signature
        entry_dict = asdict(entry)
        entry.signature = self._compute_signature(entry_dict)

        # Store in memory
        self._memory_cache[key] = entry

        # Store on disk
        cache_file = self.cache_dir / f"{key}.json"

        # ✅ P2 FIX: Track old file size for accurate size accounting
        old_size = 0
        if cache_file.exists():
            try:
                old_size = cache_file.stat().st_size
            except OSError:
                old_size = 0

        # ✅ Improved error handling for file write
        try:
            with open(cache_file, "w") as f:
                json.dump(asdict(entry), f, indent=2)

            # Update size accounting: subtract old size, add new size
            actual_size = cache_file.stat().st_size
            self.stats["size_bytes"] = self.stats["size_bytes"] - old_size + actual_size

            logger.debug(
                "Cache entry stored",
                extra={
                    "key": key[:8],
                    "agent": agent_name,
                    "size_bytes": actual_size,
                    "old_size": old_size,
                },
            )

        except Exception as e:
            logger.error("Failed to write cache file", extra={"key": key[:8], "error": str(e)})
            # ✅ Don't update size if write failed
            if cache_file.exists():
                try:
                    cache_file.unlink()
                except OSError:
                    pass
            # Re-raise to notify caller
            raise

        # Check size limit and evict if needed
        if self.stats["size_bytes"] > self.max_size_bytes:
            self._evict_lru()

    def _evict(self, key: str):
        """Evict specific cache entry."""
        if key in self._memory_cache:
            del self._memory_cache[key]

        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                size = cache_file.stat().st_size
                cache_file.unlink()
                self.stats["size_bytes"] -= size
                self.stats["evictions"] += 1

                logger.debug("Cache entry evicted", extra={"key": key[:8]})

            except OSError as e:
                logger.warning(
                    "Failed to evict cache file", extra={"key": key[:8], "error": str(e)}
                )

    def _evict_lru(self):
        """
        Evict least recently used entries.

        ✅ FIXED: Use heapq for O(k log n) instead of O(n log n)
        """
        if not self._memory_cache:
            return

        # Evict 10% of entries
        num_to_evict = max(1, len(self._memory_cache) // 10)

        logger.info(
            "Evicting LRU entries",
            extra={
                "num_to_evict": num_to_evict,
                "total_entries": len(self._memory_cache),
                "current_size_mb": self.stats["size_bytes"] / (1024 * 1024),
            },
        )

        # ✅ Use heapq.nsmallest for O(k log n) performance
        # Find k smallest by (hit_count, timestamp) - least used, oldest first
        to_evict = heapq.nsmallest(
            num_to_evict, self._memory_cache.items(), key=lambda x: (x[1].hit_count, x[1].timestamp)
        )

        for key, _ in to_evict:
            self._evict(key)

        logger.info(
            "LRU eviction completed",
            extra={
                "evicted": num_to_evict,
                "remaining_entries": len(self._memory_cache),
                "new_size_mb": self.stats["size_bytes"] / (1024 * 1024),
            },
        )

    def clear(self):
        """Clear entire cache."""
        logger.info("Clearing cache", extra={"entries": len(self._memory_cache)})

        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
            except OSError as e:
                logger.warning(
                    "Failed to clear cache file", extra={"file": cache_file.name, "error": str(e)}
                )

        self._memory_cache.clear()
        self.stats["size_bytes"] = 0

        logger.info("Cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0

        return {
            "enabled": self.enabled,
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate": f"{hit_rate:.1f}%",
            "evictions": self.stats["evictions"],
            "integrity_failures": self.stats["integrity_failures"],
            "size_mb": round(self.stats["size_bytes"] / (1024 * 1024), 2),
            "entries": len(self._memory_cache),
            "ttl_hours": self.ttl_seconds / 3600,
            "max_size_mb": self.max_size_bytes / (1024 * 1024),
        }

    def _load_cache_index(self):
        """Load cache index from disk."""
        if not self.cache_dir.exists():
            return

        loaded = 0
        corrupted = 0

        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, "r") as f:
                    entry_dict = json.load(f)
                    entry = CacheEntry(**entry_dict)

                    # ✅ Verify integrity on load
                    if entry.signature and not self._verify_signature(entry):
                        logger.warning(
                            "Removing corrupt cache file", extra={"file": cache_file.name}
                        )
                        cache_file.unlink()
                        corrupted += 1
                        continue

                    self._memory_cache[entry.key] = entry
                    self.stats["size_bytes"] += cache_file.stat().st_size
                    loaded += 1

            except Exception as e:
                logger.warning(
                    "Failed to load cache file", extra={"file": cache_file.name, "error": str(e)}
                )
                # ✅ Remove corrupt cache file
                try:
                    cache_file.unlink()
                    corrupted += 1
                except OSError:
                    pass

        if loaded > 0 or corrupted > 0:
            logger.info(
                "Cache index loaded",
                extra={
                    "loaded": loaded,
                    "corrupted": corrupted,
                    "size_mb": round(self.stats["size_bytes"] / (1024 * 1024), 2),
                },
            )
