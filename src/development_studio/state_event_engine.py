from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from .domain.state import validate_project_transition, validate_task_transition
from .persistence.sqlite import SQLiteStore

EntityKind = Literal["project", "task"]


@dataclass(frozen=True)
class TransitionResult:
    entity_kind: EntityKind
    entity_id: str
    project_id: str
    previous_state: str
    new_state: str
    event_id: str


class StateEventEngine:
    """Atomic Development Studio state transition + event recording engine.

    This engine owns Development Studio state only. It does not implement or
    reinterpret KALP orchestration state/event semantics.
    """

    def __init__(self, store: SQLiteStore):
        self.store = store

    def transition_project(
        self,
        project_id: str,
        new_state: str,
        *,
        actor: str,
        reason: str,
        inputs: dict[str, Any] | None = None,
        outputs: dict[str, Any] | None = None,
        source_references: list[str] | None = None,
        event_id: str | None = None,
    ) -> TransitionResult:
        return self._transition(
            "project", project_id, new_state,
            actor=actor, reason=reason, inputs=inputs, outputs=outputs,
            source_references=source_references, event_id=event_id,
        )

    def transition_task(
        self,
        task_id: str,
        new_state: str,
        *,
        actor: str,
        reason: str,
        inputs: dict[str, Any] | None = None,
        outputs: dict[str, Any] | None = None,
        source_references: list[str] | None = None,
        event_id: str | None = None,
    ) -> TransitionResult:
        return self._transition(
            "task", task_id, new_state,
            actor=actor, reason=reason, inputs=inputs, outputs=outputs,
            source_references=source_references, event_id=event_id,
        )

    def list_events(self, project_id: str, task_id: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM events WHERE project_id = ?"
        params: list[Any] = [project_id]
        if task_id is not None:
            query += " AND task_id = ?"
            params.append(task_id)
        query += " ORDER BY timestamp, id"
        cursor = self.store.connection.execute(query, params)
        columns = [column[0] for column in cursor.description]
        return [self._decode_event(dict(zip(columns, row))) for row in cursor.fetchall()]

    def _transition(
        self,
        entity_kind: EntityKind,
        entity_id: str,
        new_state: str,
        *,
        actor: str,
        reason: str,
        inputs: dict[str, Any] | None,
        outputs: dict[str, Any] | None,
        source_references: list[str] | None,
        event_id: str | None,
    ) -> TransitionResult:
        if not actor.strip():
            raise ValueError("actor is required")
        if not reason.strip():
            raise ValueError("reason is required")

        table = "projects" if entity_kind == "project" else "tasks"
        task_id = entity_id if entity_kind == "task" else None
        cursor = self.store.connection.cursor()
        try:
            cursor.execute("BEGIN IMMEDIATE")
            if entity_kind == "project":
                row = cursor.execute(
                    "SELECT id, state FROM projects WHERE id = ?", (entity_id,)
                ).fetchone()
                if row is None:
                    raise LookupError(f"project not found: {entity_id}")
                project_id, previous_state = row
                validate_project_transition(previous_state, new_state)
            else:
                row = cursor.execute(
                    "SELECT id, project_id, state FROM tasks WHERE id = ?", (entity_id,)
                ).fetchone()
                if row is None:
                    raise LookupError(f"task not found: {entity_id}")
                _, project_id, previous_state = row
                validate_task_transition(previous_state, new_state)

            actual_event_id = event_id or f"evt_{uuid4().hex}"
            if cursor.execute(
                "SELECT 1 FROM events WHERE id = ?", (actual_event_id,)
            ).fetchone():
                raise ValueError(f"duplicate event identity: {actual_event_id}")

            cursor.execute(
                f"UPDATE {table} SET state = ? WHERE id = ?",
                (new_state, entity_id),
            )
            cursor.execute(
                """INSERT INTO events
                (id, project_id, task_id, timestamp, previous_state, new_state,
                 actor, reason, inputs, outputs, source_references)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    actual_event_id,
                    project_id,
                    task_id,
                    datetime.now(timezone.utc).isoformat(),
                    previous_state,
                    new_state,
                    actor,
                    reason,
                    json.dumps(inputs or {}, separators=(",", ":"), sort_keys=True),
                    json.dumps(outputs or {}, separators=(",", ":"), sort_keys=True),
                    json.dumps(source_references or [], separators=(",", ":"), sort_keys=True),
                ),
            )
            self.store.connection.commit()
            return TransitionResult(
                entity_kind=entity_kind,
                entity_id=entity_id,
                project_id=project_id,
                previous_state=previous_state,
                new_state=new_state,
                event_id=actual_event_id,
            )
        except Exception:
            self.store.connection.rollback()
            raise

    @staticmethod
    def _decode_event(row: dict[str, Any]) -> dict[str, Any]:
        for field in ("inputs", "outputs", "source_references"):
            row[field] = json.loads(row[field])
        return row
