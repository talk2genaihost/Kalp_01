from __future__ import annotations

from dataclasses import replace
from datetime import timezone

from .contracts import MarketRecord


def normalize_record(record: MarketRecord) -> MarketRecord:
    """Normalize transport-level representation without inventing market fields."""
    symbol = record.symbol.strip().upper()
    if not symbol:
        raise ValueError("symbol is required")
    timestamp = record.timestamp
    if timestamp.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    return replace(record, symbol=symbol, timestamp=timestamp.astimezone(timezone.utc))
