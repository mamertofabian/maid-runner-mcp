"""Cache implementations for MAID Runner MCP.

Provides LRU and TTL-based caching for validation results and other data.
"""

import time
from collections import OrderedDict
from typing import Any, Generic, TypeVar


T = TypeVar("T")


class LRUCache(Generic[T]):
    """LRU cache implementation with configurable size.

    Evicts least recently used items when max_size is reached.
    Uses OrderedDict to maintain access order efficiently.

    Args:
        max_size: Maximum number of items to store in cache
    """

    def __init__(self, max_size: int) -> None:
        """Initialize LRU cache with maximum size.

        Args:
            max_size: Maximum number of items to store
        """
        self._max_size = max_size
        self._cache: OrderedDict[str, T] = OrderedDict()

    def get(self, key: str) -> T | None:
        """Get value from cache by key.

        Updates access order for LRU tracking.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if key not in self._cache:
            return None

        # Move to end to mark as recently used
        self._cache.move_to_end(key)
        return self._cache[key]

    def set(self, key: str, value: T) -> None:
        """Set value in cache.

        Evicts least recently used item if cache is full.

        Args:
            key: Cache key
            value: Value to cache
        """
        # If key exists, remove it first to update order
        if key in self._cache:
            del self._cache[key]

        # Add to end (most recently used)
        self._cache[key] = value

        # Evict oldest if over capacity
        if len(self._cache) > self._max_size:
            # Remove first item (least recently used)
            self._cache.popitem(last=False)


class TTLCache(Generic[T]):
    """Time-to-live cache implementation.

    Items expire after a specified TTL period.

    Args:
        ttl_seconds: Time to live in seconds for cached items
    """

    def __init__(self, ttl_seconds: float) -> None:
        """Initialize TTL cache with time to live.

        Args:
            ttl_seconds: Time to live in seconds
        """
        self._ttl_seconds = ttl_seconds
        self._cache: dict[str, tuple[T, float]] = {}

    def get(self, key: str) -> T | None:
        """Get value from cache by key.

        Returns None if key not found or has expired.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        if key not in self._cache:
            return None

        value, expiry_time = self._cache[key]

        # Check if expired
        if time.time() > expiry_time:
            # Remove expired entry
            del self._cache[key]
            return None

        return value

    def set(self, key: str, value: T) -> None:
        """Set value in cache with TTL expiration.

        Args:
            key: Cache key
            value: Value to cache
        """
        expiry_time = time.time() + self._ttl_seconds
        self._cache[key] = (value, expiry_time)


class ValidationCache:
    """Specialized cache for validation results using LRU.

    Wraps LRUCache to provide a domain-specific interface
    for caching MAID validation results.

    Args:
        max_size: Maximum number of validation results to cache
    """

    def __init__(self, max_size: int) -> None:
        """Initialize validation cache.

        Args:
            max_size: Maximum number of validation results to cache
        """
        self._cache: LRUCache[Any] = LRUCache(max_size=max_size)

    def get(self, manifest_path: str) -> Any | None:
        """Get cached validation result for a manifest.

        Args:
            manifest_path: Path to manifest file

        Returns:
            Cached validation result or None if not found
        """
        return self._cache.get(manifest_path)

    def set(self, manifest_path: str, result: Any) -> None:
        """Cache validation result for a manifest.

        Args:
            manifest_path: Path to manifest file
            result: Validation result to cache
        """
        self._cache.set(manifest_path, result)
