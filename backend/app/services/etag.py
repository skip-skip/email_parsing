"""ETag utilities for cacheable API responses."""

from __future__ import annotations

import hashlib
from typing import Any


def compute_etag(data: Any) -> str:
    """Compute a weak ETag from serializable data."""
    raw = repr(data).encode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()[:16]
    return f'W/"{digest}"'
