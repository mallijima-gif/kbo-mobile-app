from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .cache import MemoryCache
from .models import ApiEnvelope
from .provider_live import KboProvider

app = FastAPI(title="KBO Mobile API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cache = MemoryCache(ttl_seconds=300)
provider = KboProvider()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/schedules", response_model=ApiEnvelope)
def schedules() -> ApiEnvelope:
    cached_payload, hit = cache.get("schedules")
    if hit:
        return ApiEnvelope(source=cached_payload["source"], cached=True, items=cached_payload["items"])

    items, source = provider.get_schedules()
    payload = cache.set("schedules", {"source": source, "items": items})
    return ApiEnvelope(source=payload["source"], cached=False, items=payload["items"])


@app.get("/api/v1/standings", response_model=ApiEnvelope)
def standings() -> ApiEnvelope:
    cached_payload, hit = cache.get("standings")
    if hit:
        return ApiEnvelope(source=cached_payload["source"], cached=True, items=cached_payload["items"])

    items, source = provider.get_standings()
    payload = cache.set("standings", {"source": source, "items": items})
    return ApiEnvelope(source=payload["source"], cached=False, items=payload["items"])


@app.get("/api/v1/players", response_model=ApiEnvelope)
def players() -> ApiEnvelope:
    cached_payload, hit = cache.get("players")
    if hit:
        return ApiEnvelope(source=cached_payload["source"], cached=True, items=cached_payload["items"])

    items, source = provider.get_players()
    payload = cache.set("players", {"source": source, "items": items})
    return ApiEnvelope(source=payload["source"], cached=False, items=payload["items"])


@app.get("/api/v1/pitchers", response_model=ApiEnvelope)
def pitchers() -> ApiEnvelope:
    cached_payload, hit = cache.get("pitchers")
    if hit:
        return ApiEnvelope(source=cached_payload["source"], cached=True, items=cached_payload["items"])

    items, source = provider.get_pitchers()
    payload = cache.set("pitchers", {"source": source, "items": items})
    return ApiEnvelope(source=payload["source"], cached=False, items=payload["items"])
