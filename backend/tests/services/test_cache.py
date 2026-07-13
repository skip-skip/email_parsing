from __future__ import annotations

import time

from backend.app.services.cache import TTLCache, cached, make_cache_key


class TestTTLCache:
    def test_set_and_get(self) -> None:
        cache = TTLCache(default_ttl=60)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_get_missing_key(self) -> None:
        cache = TTLCache()
        assert cache.get("nonexistent") is None

    def test_expiration(self) -> None:
        cache = TTLCache(default_ttl=0.01)
        cache.set("key1", "value1")
        time.sleep(0.02)
        assert cache.get("key1") is None

    def test_custom_ttl(self) -> None:
        cache = TTLCache(default_ttl=0.01)
        cache.set("key1", "value1", ttl=60)
        time.sleep(0.02)
        assert cache.get("key1") == "value1"

    def test_invalidate(self) -> None:
        cache = TTLCache()
        cache.set("key1", "value1")
        cache.invalidate("key1")
        assert cache.get("key1") is None

    def test_clear(self) -> None:
        cache = TTLCache()
        cache.set("a", 1)
        cache.set("b", 2)
        cache.clear()
        assert cache.get("a") is None
        assert cache.get("b") is None

    def test_prune(self) -> None:
        cache = TTLCache(default_ttl=0.01)
        cache.set("expired", "value")
        time.sleep(0.02)
        removed = cache.prune()
        assert removed == 1


class TestMakeCacheKey:
    def test_deterministic(self) -> None:
        key1 = make_cache_key("fn", "arg1", 42)
        key2 = make_cache_key("fn", "arg1", 42)
        assert key1 == key2

    def test_different_args_different_keys(self) -> None:
        key1 = make_cache_key("fn", "arg1")
        key2 = make_cache_key("fn", "arg2")
        assert key1 != key2


class TestCachedDecorator:
    async def test_caches_result(self) -> None:
        call_count = 0

        @cached(ttl=60)
        async def compute(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2

        result1 = await compute(5)
        result2 = await compute(5)
        assert result1 == 10
        assert result2 == 10
        assert call_count == 1

    async def test_different_args_separate_cache(self) -> None:
        call_count = 0

        @cached(ttl=60)
        async def compute(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2

        await compute(5)
        await compute(10)
        assert call_count == 2


class TestQueryCache:
    def test_global_cache_is_singleton(self) -> None:
        from backend.app.services.cache import query_cache as qc1
        from backend.app.services.cache import query_cache as qc2
        assert qc1 is qc2
