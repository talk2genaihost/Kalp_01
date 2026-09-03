from __future__ import annotations

from datetime import datetime, timezone
from typing import Sequence

from .contracts import MarketRecord, ProviderHealth, QualityMetadata


class ReferenceProviderAdapter:
    """Deterministic reference adapter for contract and integration testing."""

    provider_id = "reference"

    def __init__(self, records: dict[str, dict[str, object]] | None = None):
        self._records = records or {}

    def fetch(self, symbols: Sequence[str]) -> list[MarketRecord]:
        now = datetime.now(timezone.utc)
        result: list[MarketRecord] = []
        for symbol in symbols:
            values = self._records.get(symbol, {})
            result.append(
                MarketRecord(
                    symbol=symbol,
                    timestamp=now,
                    values=dict(values),
                    provider_id=self.provider_id,
                    quality=QualityMetadata(
                        freshness_seconds=0,
                        completeness=1.0,
                        quality_score=1.0,
                        confidence=1.0,
                    ),
                )
            )
        return result

    def health(self) -> ProviderHealth:
        return ProviderHealth(
            provider_id=self.provider_id,
            status="HEALTHY",
            observed_at=datetime.now(timezone.utc),
        )
