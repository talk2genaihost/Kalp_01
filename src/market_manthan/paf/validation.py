from __future__ import annotations

from dataclasses import dataclass

from .contracts import MarketRecord


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    errors: tuple[str, ...] = ()


def validate_record(record: MarketRecord) -> ValidationResult:
    errors: list[str] = []
    if not record.symbol.strip():
        errors.append("symbol is required")
    if not record.provider_id.strip():
        errors.append("provider_id is required")
    if record.timestamp.tzinfo is None:
        errors.append("timestamp must be timezone-aware")
    if not 0 <= _bounded(record.quality.completeness) <= 1:
        errors.append("completeness must be between 0 and 1")
    if not 0 <= _bounded(record.quality.quality_score) <= 1:
        errors.append("quality_score must be between 0 and 1")
    if not 0 <= _bounded(record.quality.confidence) <= 1:
        errors.append("confidence must be between 0 and 1")
    return ValidationResult(not errors, tuple(errors))


def _bounded(value: float | None) -> float:
    return 0.0 if value is None else value
