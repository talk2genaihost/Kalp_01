from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import Any, Literal
from uuid import uuid4

from .persistence.sqlite import SQLiteStore

ProviderType = Literal["AGENT", "TOOL"]


def new_id() -> str:
    return f"cap_{uuid4().hex}"


@dataclass(frozen=True)
class Capability:
    capability_id: str = field(default_factory=new_id)
    name: str = ""
    version: str = ""
    description: str = ""
    provider_type: ProviderType = "AGENT"
    provider_ref: str = ""
    required_inputs: dict[str, Any] = field(default_factory=dict)
    expected_outputs: dict[str, Any] = field(default_factory=dict)
    constraints: list[str] = field(default_factory=list)
    authority_scope: list[str] = field(default_factory=list)
    escalation_conditions: list[str] = field(default_factory=list)
    status: str = "DISCOVERED"
    provenance: list[str] = field(default_factory=list)


class CapabilityRegistry:
    """Persist discoverable capability metadata without granting execution authority."""

    def __init__(self, store: SQLiteStore):
        self.store = store

    def register(self, capability: Capability) -> None:
        self._validate(capability)
        if self.store.get("capabilities", capability.capability_id) is not None:
            raise ValueError(f"capability already exists: {capability.capability_id}")
        data = asdict(capability)
        for field_name in (
            "required_inputs",
            "expected_outputs",
            "constraints",
            "authority_scope",
            "escalation_conditions",
            "provenance",
        ):
            data[field_name] = json.dumps(data[field_name], separators=(",", ":"), sort_keys=True)
        self.store.insert("capabilities", data)

    def get(self, capability_id: str) -> dict[str, Any] | None:
        return self.store.get("capabilities", capability_id)

    def list(self, status: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM capabilities"
        params: tuple[Any, ...] = ()
        if status is not None:
            query += " WHERE status = ?"
            params = (status,)
        query += " ORDER BY capability_id"
        cursor = self.store.connection.execute(query, params)
        rows = cursor.fetchall()
        columns = [item[0] for item in cursor.description]
        results = [dict(zip(columns, row)) for row in rows]
        for result in results:
            for field_name in (
                "required_inputs",
                "expected_outputs",
                "constraints",
                "authority_scope",
                "escalation_conditions",
                "provenance",
            ):
                result[field_name] = json.loads(result[field_name])
        return results

    @staticmethod
    def _validate(capability: Capability) -> None:
        required = {
            "capability_id": capability.capability_id,
            "name": capability.name,
            "version": capability.version,
            "description": capability.description,
            "provider_ref": capability.provider_ref,
            "status": capability.status,
        }
        missing = [name for name, value in required.items() if not str(value).strip()]
        if missing:
            raise ValueError(f"capability fields required: {', '.join(missing)}")
        if capability.provider_type not in ("AGENT", "TOOL"):
            raise ValueError("provider_type must be AGENT or TOOL")
        if not isinstance(capability.required_inputs, dict):
            raise ValueError("required_inputs must be an object")
        if not isinstance(capability.expected_outputs, dict):
            raise ValueError("expected_outputs must be an object")
        for name in ("constraints", "authority_scope", "escalation_conditions", "provenance"):
            if not isinstance(getattr(capability, name), list):
                raise ValueError(f"{name} must be a list")
