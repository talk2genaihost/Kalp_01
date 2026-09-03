from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal
from uuid import uuid4

from .persistence.sqlite import SQLiteStore

RouteStatus = Literal["DISCOVERED", "VALIDATED", "REGISTERED", "AVAILABLE", "DEPRECATED", "RETIRED"]


@dataclass(frozen=True)
class RoutingEntry:
    request_class: str
    version: str
    selection_conditions: dict[str, Any]
    capability_id: str | None = None
    department_ref: str | None = None
    agent_ref: str | None = None
    authority_scope: list[str] = field(default_factory=list)
    escalation_conditions: list[str] = field(default_factory=list)
    status: RouteStatus = "DISCOVERED"
    provenance: list[str] = field(default_factory=list)
    route_id: str = field(default_factory=lambda: f"route_{uuid4().hex}")


class RoutingRegistry:
    """Declarative candidate routing only; it does not authorize or execute."""

    def __init__(self, store: SQLiteStore):
        self.store = store

    def register(self, entry: RoutingEntry) -> str:
        self._validate(entry)
        if self.store.get("routing_entries", entry.route_id) is not None:
            raise ValueError(f"duplicate route_id: {entry.route_id}")
        record = asdict(entry)
        record["id"] = entry.route_id
        self.store.insert("routing_entries", record)
        return entry.route_id

    def get(self, route_id: str) -> dict[str, Any] | None:
        return self.store.get("routing_entries", route_id)

    def list(self, request_class: str | None = None, capability_id: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM routing_entries"
        clauses: list[str] = []
        params: list[str] = []
        if request_class is not None:
            clauses.append("request_class = ?")
            params.append(request_class)
        if capability_id is not None:
            clauses.append("capability_id = ?")
            params.append(capability_id)
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY route_id"
        cursor = self.store.connection.execute(query, params)
        columns = [d[0] for d in cursor.description]
        rows = []
        import json
        json_fields = {"selection_conditions", "authority_scope", "escalation_conditions", "provenance"}
        for row in cursor.fetchall():
            record = dict(zip(columns, row))
            for field in json_fields:
                record[field] = json.loads(record[field])
            rows.append(record)
        return rows

    @staticmethod
    def _validate(entry: RoutingEntry) -> None:
        if not entry.route_id.strip():
            raise ValueError("route_id is required")
        if not entry.request_class.strip():
            raise ValueError("request_class is required")
        if not entry.version.strip():
            raise ValueError("version is required")
        if not isinstance(entry.selection_conditions, dict):
            raise ValueError("selection_conditions must be a dict")
        if not (entry.capability_id or entry.department_ref or entry.agent_ref):
            raise ValueError("at least one governed capability, department, or agent reference is required")
        if not entry.provenance:
            raise ValueError("provenance is required")
