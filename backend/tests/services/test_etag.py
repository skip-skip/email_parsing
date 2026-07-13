from __future__ import annotations

from backend.app.services.etag import compute_etag


class TestComputeETag:
    def test_returns_weak_tag(self) -> None:
        etag = compute_etag({"key": "value"})
        assert etag.startswith('W/"')

    def test_deterministic(self) -> None:
        etag1 = compute_etag({"a": 1, "b": 2})
        etag2 = compute_etag({"a": 1, "b": 2})
        assert etag1 == etag2

    def test_different_data_different_tags(self) -> None:
        etag1 = compute_etag({"a": 1})
        etag2 = compute_etag({"a": 2})
        assert etag1 != etag2

    def test_empty_dict(self) -> None:
        etag = compute_etag({})
        assert etag.startswith('W/"')
