from datetime import datetime, timezone

from src.market_manthan.paf.contracts import MarketRecord, ProviderHealth, QualityMetadata
from src.market_manthan.paf.reliability import BoundedProviderRunner


class FlakyAdapter:
    provider_id = "flaky"

    def __init__(self, failures=1, health_status="HEALTHY"):
        self.failures = failures
        self.calls = 0
        self.health_status = health_status

    def fetch(self, symbols):
        self.calls += 1
        if self.calls <= self.failures:
            raise RuntimeError("temporary provider failure")
        now = datetime.now(timezone.utc)
        return [MarketRecord(s, now, {"price": 100}, self.provider_id, QualityMetadata(1, 1, 1, 1)) for s in symbols]

    def health(self):
        return ProviderHealth(self.provider_id, self.health_status, datetime.now(timezone.utc))


class DeadAdapter(FlakyAdapter):
    def fetch(self, symbols):
        self.calls += 1
        raise RuntimeError("provider unavailable")


def test_bounded_retry_recovers_from_transient_failure():
    adapter = FlakyAdapter(failures=1)
    result = BoundedProviderRunner(max_attempts=2).fetch(adapter, ["ABC"])
    assert result.attempts == 2
    assert not result.degraded
    assert len(result.records) == 1


def test_retry_budget_is_finite_and_failure_is_visible():
    adapter = DeadAdapter()
    result = BoundedProviderRunner(max_attempts=2).fetch(adapter, ["ABC"])
    assert result.attempts == 2
    assert result.degraded
    assert result.records == ()
    assert result.error == "provider unavailable"
    assert result.provider_health.status == "DEGRADED"


def test_unhealthy_provider_is_marked_degraded_even_when_fetch_returns():
    adapter = FlakyAdapter(health_status="DEGRADED")
    result = BoundedProviderRunner(max_attempts=1).fetch(adapter, ["ABC"])
    assert result.degraded
    assert result.provider_health.status == "DEGRADED"
