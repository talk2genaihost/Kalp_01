from datetime import datetime, timezone

import pytest

from src.market_manthan.paf.contracts import MarketRecord, ProviderHealth, ProviderRegistry, QualityMetadata
from src.market_manthan.paf.reference_adapter import ReferenceProviderAdapter


def test_reference_adapter_returns_provider_neutral_records():
    adapter = ReferenceProviderAdapter({"ABC": {"price": 123.45}})
    records = adapter.fetch(["ABC"])
    assert len(records) == 1
    assert isinstance(records[0], MarketRecord)
    assert records[0].provider_id == "reference"
    assert records[0].values["price"] == 123.45
    assert records[0].quality.completeness == 1.0


def test_provider_health_is_exposed():
    health = ReferenceProviderAdapter().health()
    assert isinstance(health, ProviderHealth)
    assert health.provider_id == "reference"
    assert health.status == "HEALTHY"


def test_registry_rejects_duplicate_provider():
    registry = ProviderRegistry()
    registry.register(ReferenceProviderAdapter())
    with pytest.raises(ValueError, match="already registered"):
        registry.register(ReferenceProviderAdapter())


def test_registry_lookup_and_listing():
    registry = ProviderRegistry()
    adapter = ReferenceProviderAdapter()
    registry.register(adapter)
    assert registry.get("reference") is adapter
    assert registry.list() == ("reference",)


def test_quality_metadata_preserves_quality_dimensions():
    metadata = QualityMetadata(
        freshness_seconds=2.5,
        completeness=0.9,
        quality_score=0.8,
        confidence=0.7,
        flags=("STALE_WARNING",),
    )
    record = MarketRecord(
        symbol="ABC",
        timestamp=datetime.now(timezone.utc),
        values={"price": 100},
        provider_id="test",
        quality=metadata,
    )
    assert record.quality.flags == ("STALE_WARNING",)
    assert record.quality.confidence == 0.7
