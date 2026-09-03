from datetime import datetime, timezone

from src.market_manthan.paf.contracts import MarketRecord, QualityMetadata
from src.market_manthan.paf.normalization import normalize_record
from src.market_manthan.paf.validation import validate_record


def record(**kwargs):
    values = {
        "symbol": " abc ",
        "timestamp": datetime(2026, 9, 4, tzinfo=timezone.utc),
        "values": {"price": 100},
        "provider_id": "reference",
        "quality": QualityMetadata(completeness=1, quality_score=1, confidence=1),
    }
    values.update(kwargs)
    return MarketRecord(**values)


def test_normalization_canonicalizes_symbol_and_timestamp():
    result = normalize_record(record())
    assert result.symbol == "ABC"
    assert result.timestamp.tzinfo == timezone.utc


def test_normalization_rejects_naive_timestamp():
    try:
        normalize_record(record(timestamp=datetime(2026, 9, 4)))
        assert False
    except ValueError as exc:
        assert "timezone-aware" in str(exc)


def test_validation_accepts_valid_quality_ranges():
    result = validate_record(record())
    assert result.valid
    assert result.errors == ()


def test_validation_rejects_out_of_range_quality():
    result = validate_record(
        record(quality=QualityMetadata(completeness=1.2, quality_score=0.8, confidence=-0.1))
    )
    assert not result.valid
    assert "completeness" in " ".join(result.errors)
    assert "confidence" in " ".join(result.errors)


def test_validation_rejects_missing_provider():
    result = validate_record(record(provider_id=""))
    assert not result.valid
    assert "provider_id is required" in result.errors
