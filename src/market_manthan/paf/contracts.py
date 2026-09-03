from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol, Sequence


@dataclass(frozen=True)
class QualityMetadata:
    freshness_seconds: float | None = None
    completeness: float | None = None
    quality_score: float | None = None
    confidence: float | None = None
    flags: tuple[str, ...] = ()


@dataclass(frozen=True)
class MarketRecord:
    symbol: str
    timestamp: datetime
    values: dict[str, Any]
    provider_id: str
    quality: QualityMetadata


@dataclass(frozen=True)
class ProviderHealth:
    provider_id: str
    status: str
    observed_at: datetime
    message: str | None = None


class ProviderAdapter(Protocol):
    provider_id: str

    def fetch(self, symbols: Sequence[str]) -> list[MarketRecord]: ...
    def health(self) -> ProviderHealth: ...


@dataclass
class ProviderRegistry:
    _adapters: dict[str, ProviderAdapter] = field(default_factory=dict)

    def register(self, adapter: ProviderAdapter) -> None:
        if not getattr(adapter, "provider_id", None):
            raise ValueError("provider_id is required")
        if adapter.provider_id in self._adapters:
            raise ValueError(f"provider already registered: {adapter.provider_id}")
        self._adapters[adapter.provider_id] = adapter

    def get(self, provider_id: str) -> ProviderAdapter:
        try:
            return self._adapters[provider_id]
        except KeyError as exc:
            raise KeyError(f"provider not registered: {provider_id}") from exc

    def list(self) -> tuple[str, ...]:
        return tuple(sorted(self._adapters))
