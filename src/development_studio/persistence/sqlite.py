from __future__ import annotations
import json, sqlite3
from pathlib import Path
from typing import Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (id TEXT PRIMARY KEY, intent TEXT NOT NULL, platform TEXT NOT NULL, deployment_mode TEXT NOT NULL, state TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS requirements (id TEXT PRIMARY KEY, project_id TEXT NOT NULL, description TEXT NOT NULL, source TEXT NOT NULL, status TEXT NOT NULL, approved INTEGER NOT NULL, FOREIGN KEY(project_id) REFERENCES projects(id));
CREATE TABLE IF NOT EXISTS tasks (id TEXT PRIMARY KEY, project_id TEXT NOT NULL, capability_id TEXT NOT NULL, state TEXT NOT NULL, inputs TEXT NOT NULL, outputs TEXT NOT NULL, FOREIGN KEY(project_id) REFERENCES projects(id));
CREATE TABLE IF NOT EXISTS agent_assignments (id TEXT PRIMARY KEY, task_id TEXT NOT NULL, agent_ref TEXT NOT NULL, capability_id TEXT NOT NULL, status TEXT NOT NULL, provenance TEXT NOT NULL, FOREIGN KEY(task_id) REFERENCES tasks(id));
CREATE TABLE IF NOT EXISTS dependencies (id TEXT PRIMARY KEY, source_id TEXT NOT NULL, target_id TEXT NOT NULL, dependency_type TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS artifacts (id TEXT PRIMARY KEY, project_id TEXT NOT NULL, type TEXT NOT NULL, version TEXT NOT NULL, created_by TEXT NOT NULL, created_at TEXT NOT NULL, parent_artifact TEXT, status TEXT NOT NULL, integrity TEXT, source_references TEXT NOT NULL, validation_status TEXT NOT NULL, FOREIGN KEY(project_id) REFERENCES projects(id));
CREATE TABLE IF NOT EXISTS builds (id TEXT PRIMARY KEY, project_id TEXT NOT NULL, status TEXT NOT NULL, input_refs TEXT NOT NULL, output_refs TEXT NOT NULL, FOREIGN KEY(project_id) REFERENCES projects(id));
CREATE TABLE IF NOT EXISTS test_runs (id TEXT PRIMARY KEY, project_id TEXT NOT NULL, test_type TEXT NOT NULL, target_ref TEXT NOT NULL, status TEXT NOT NULL, result TEXT NOT NULL, evidence TEXT NOT NULL, FOREIGN KEY(project_id) REFERENCES projects(id));
CREATE TABLE IF NOT EXISTS approvals (id TEXT PRIMARY KEY, project_id TEXT NOT NULL, approval_type TEXT NOT NULL, required INTEGER NOT NULL, decision TEXT NOT NULL, actor TEXT NOT NULL, reason TEXT NOT NULL, timestamp TEXT NOT NULL, FOREIGN KEY(project_id) REFERENCES projects(id));
CREATE TABLE IF NOT EXISTS retries (id TEXT PRIMARY KEY, target_id TEXT NOT NULL, failure_class TEXT NOT NULL, attempt INTEGER NOT NULL, outcome TEXT NOT NULL, reason TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS checkpoints (id TEXT PRIMARY KEY, project_id TEXT NOT NULL, milestone TEXT NOT NULL, snapshot_ref TEXT NOT NULL, timestamp TEXT NOT NULL, FOREIGN KEY(project_id) REFERENCES projects(id));
CREATE TABLE IF NOT EXISTS releases (id TEXT PRIMARY KEY, project_id TEXT NOT NULL, version TEXT NOT NULL, artifact_refs TEXT NOT NULL, validation_state TEXT NOT NULL, approval_state TEXT NOT NULL, state TEXT NOT NULL, FOREIGN KEY(project_id) REFERENCES projects(id));
CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, project_id TEXT NOT NULL, task_id TEXT, timestamp TEXT NOT NULL, previous_state TEXT, new_state TEXT, actor TEXT NOT NULL, reason TEXT NOT NULL, inputs TEXT NOT NULL, outputs TEXT NOT NULL, source_references TEXT NOT NULL, FOREIGN KEY(project_id) REFERENCES projects(id));
CREATE TABLE IF NOT EXISTS capabilities (id TEXT PRIMARY KEY, capability_id TEXT NOT NULL UNIQUE, name TEXT NOT NULL, version TEXT NOT NULL, description TEXT NOT NULL, provider_type TEXT NOT NULL, provider_ref TEXT NOT NULL, required_inputs TEXT NOT NULL, expected_outputs TEXT NOT NULL, constraints TEXT NOT NULL, authority_scope TEXT NOT NULL, escalation_conditions TEXT NOT NULL, status TEXT NOT NULL, provenance TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS routing_entries (id TEXT PRIMARY KEY, route_id TEXT NOT NULL UNIQUE, version TEXT NOT NULL, request_class TEXT NOT NULL, capability_id TEXT, department_ref TEXT, agent_ref TEXT, selection_conditions TEXT NOT NULL, authority_scope TEXT NOT NULL, escalation_conditions TEXT NOT NULL, status TEXT NOT NULL, provenance TEXT NOT NULL);
"""
JSON_FIELDS = {"tasks": ("inputs", "outputs"), "artifacts": ("source_references",), "builds": ("input_refs", "output_refs"), "test_runs": ("evidence",), "releases": ("artifact_refs",), "events": ("inputs", "outputs", "source_references"), "capabilities": ("required_inputs", "expected_outputs", "constraints", "authority_scope", "escalation_conditions", "provenance"), "routing_entries": ("selection_conditions", "authority_scope", "escalation_conditions", "provenance")}
TABLES = {"projects","requirements","tasks","agent_assignments","dependencies","artifacts","builds","test_runs","approvals","retries","checkpoints","releases","events","capabilities","routing_entries"}

class SQLiteStore:
    def __init__(self, path: str | Path = ":memory:"):
        self.connection = sqlite3.connect(str(path))
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.executescript(SCHEMA)
        self.connection.commit()

    def insert(self, table: str, record: dict[str, Any]) -> None:
        if table not in TABLES: raise ValueError(f"unsupported table: {table}")
        data = dict(record)
        for field in JSON_FIELDS.get(table, ()): data[field] = json.dumps(data[field], separators=(",", ":"), sort_keys=True)
        for field in ("approved", "required"):
            if field in data: data[field] = int(bool(data[field]))
        cols = list(data)
        self.connection.execute(f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join('?' for _ in cols)})", [data[c] for c in cols])
        self.connection.commit()

    def get(self, table: str, entity_id: str) -> dict[str, Any] | None:
        if table not in TABLES: raise ValueError(f"unsupported table: {table}")
        cursor = self.connection.execute(f"SELECT * FROM {table} WHERE id = ?", (entity_id,))
        row = cursor.fetchone()
        if row is None: return None
        cols = [d[0] for d in cursor.description]
        data = dict(zip(cols, row))
        for field in JSON_FIELDS.get(table, ()): data[field] = json.loads(data[field])
        for field in ("approved", "required"):
            if field in data: data[field] = bool(data[field])
        return data

    def close(self) -> None: self.connection.close()
