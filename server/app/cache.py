from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any


@dataclass
class CacheEntry:
    expires_at: datetime
    payload: Any


class MemoryCache:
    def __init__(self, ttl_seconds: int = 300) -> None:
        self.ttl_seconds = ttl_seconds
        self._store: dict[str, CacheEntry] = {}

    def get(self, key: str) -> tuple[Any | None, bool]:
        entry = self._store.get(key)
        if not entry:
            return None, False
        if datetime.utcnow() >= entry.expires_at:
            self._store.pop(key, None)
            return None, False
        return entry.payload, True

    def set(self, key: str, payload: Any) -> Any:
        self._store[key] = CacheEntry(
            expires_at=datetime.utcnow() + timedelta(seconds=self.ttl_seconds),
            payload=payload,
        )
        return payload
