"""Behavioral tests for Resource Infrastructure (Task 009).

These tests verify the expected artifacts defined in the manifest:
- LRUCache: LRU cache implementation with configurable size
- TTLCache: Time-to-live cache implementation
- ValidationCache: Specialized cache for validation results using LRU

Tests follow MAID behavioral testing pattern - they USE the artifacts
rather than just checking existence.
"""

import time


class TestLRUCache:
    """Tests for the LRUCache class."""

    def test_lru_cache_exists_and_instantiable(self):
        """Test that LRUCache class exists and can be instantiated.

        The manifest specifies:
        - type: class
        - name: LRUCache
        - description: LRU cache implementation with configurable size
        """
        from maid_runner_mcp.utils.cache import LRUCache

        # Should be able to create an instance with a size parameter
        cache = LRUCache(max_size=3)
        assert cache is not None

    def test_lru_cache_basic_operations(self):
        """Test basic LRU cache operations: get, set, delete."""
        from maid_runner_mcp.utils.cache import LRUCache

        cache = LRUCache(max_size=3)

        # Set and get operations
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        # Non-existent key returns None
        assert cache.get("nonexistent") is None

    def test_lru_cache_eviction(self):
        """Test that LRU cache evicts least recently used items."""
        from maid_runner_mcp.utils.cache import LRUCache

        cache = LRUCache(max_size=2)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # Should evict key1

        # key1 should have been evicted
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"


class TestTTLCache:
    """Tests for the TTLCache class."""

    def test_ttl_cache_exists_and_instantiable(self):
        """Test that TTLCache class exists and can be instantiated.

        The manifest specifies:
        - type: class
        - name: TTLCache
        - description: Time-to-live cache implementation
        """
        from maid_runner_mcp.utils.cache import TTLCache

        # Should be able to create an instance with a TTL parameter
        cache = TTLCache(ttl_seconds=60)
        assert cache is not None

    def test_ttl_cache_basic_operations(self):
        """Test basic TTL cache operations: get, set, delete."""
        from maid_runner_mcp.utils.cache import TTLCache

        cache = TTLCache(ttl_seconds=60)

        # Set and get operations
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        # Non-existent key returns None
        assert cache.get("nonexistent") is None

    def test_ttl_cache_expiration(self):
        """Test that TTL cache expires items after TTL."""
        from maid_runner_mcp.utils.cache import TTLCache

        cache = TTLCache(ttl_seconds=0.1)  # 100ms TTL

        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        # Wait for expiration
        time.sleep(0.2)

        # key1 should have expired
        assert cache.get("key1") is None


class TestValidationCache:
    """Tests for the ValidationCache class."""

    def test_validation_cache_exists_and_instantiable(self):
        """Test that ValidationCache class exists and can be instantiated.

        The manifest specifies:
        - type: class
        - name: ValidationCache
        - description: Specialized cache for validation results using LRU
        """
        from maid_runner_mcp.utils.cache import ValidationCache

        # Should be able to create an instance
        cache = ValidationCache(max_size=10)
        assert cache is not None

    def test_validation_cache_basic_operations(self):
        """Test basic ValidationCache operations."""
        from maid_runner_mcp.utils.cache import ValidationCache

        cache = ValidationCache(max_size=10)

        # Should be able to store validation results
        result = {"success": True, "errors": []}
        cache.set("manifest1.json", result)

        cached_result = cache.get("manifest1.json")
        assert cached_result == result

    def test_validation_cache_uses_lru_behavior(self):
        """Test that ValidationCache uses LRU eviction."""
        from maid_runner_mcp.utils.cache import ValidationCache

        cache = ValidationCache(max_size=2)

        cache.set("manifest1.json", {"success": True})
        cache.set("manifest2.json", {"success": True})
        cache.set("manifest3.json", {"success": False})  # Should evict manifest1

        # manifest1 should have been evicted
        assert cache.get("manifest1.json") is None
        assert cache.get("manifest2.json") is not None
        assert cache.get("manifest3.json") is not None


class TestResourcesModule:
    """Tests for the resources module initialization."""

    def test_resources_module_exists(self):
        """Test that resources module can be imported."""
        import maid_runner_mcp.resources

        assert maid_runner_mcp.resources is not None

    def test_resources_module_has_all_attribute(self):
        """Test that resources module has __all__ attribute."""
        import maid_runner_mcp.resources

        # The manifest specifies __all__ should exist
        assert hasattr(maid_runner_mcp.resources, "__all__")
        assert isinstance(maid_runner_mcp.resources.__all__, list)


class TestUtilsModule:
    """Tests for the utils module initialization."""

    def test_utils_module_exists(self):
        """Test that utils module can be imported."""
        import maid_runner_mcp.utils

        assert maid_runner_mcp.utils is not None

    def test_cache_module_exists(self):
        """Test that utils.cache module can be imported."""
        import maid_runner_mcp.utils.cache

        assert maid_runner_mcp.utils.cache is not None
