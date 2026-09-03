from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence, TypeVar

from .contracts import MarketRecord, ProviderAdapter, ProviderHealth

T = TypeVar("T")


@dataclass(frozen=True)
class ReliabilityResult:
    records: tuple[MarketRecord, ...]
    provider_health: ProviderHealth
    attempts: int
    degraded: bool
    error: str | None = None


class BoundedProviderRunner:
    """Runs an adapter with an explicit, finite retry budget."""

    def __init__(self, max_attempts: int = 2):
        if max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        self.max_attempts = max_attempts

    def fetch(self, adapter: ProviderAdapter, symbols: Sequence[str]) -> ReliabilityResult:
        last_error: Exception | None = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                records = tuple(adapter.fetch(symbols))
                health = adapter.health()
                degraded = health.status != "HEALTHY"
                return ReliabilityResult(records, health, attempt, degraded)
            except Exception as exc:  # adapter boundary: preserve failure, do not hide it
                last_error = exc
        health = adapter.health()
        return ReliabilityResult(
            records=(),
            provider_health=ProviderHealth(
                provider_id=health.provider_id,
                status="DEGRADED",
                observed_at=health.observed_at,
                message=str(last_error) if last_error else health.message,
            ),
            attempts=self.max_attempts,
            degraded=True,
            error=str(last_error) if last_error else "provider fetch failed",
        )
