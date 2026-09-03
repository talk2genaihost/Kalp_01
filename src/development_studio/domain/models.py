from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"

@dataclass
class Project:
    id: str = field(default_factory=lambda: new_id("prj")); intent: str = ""; platform: str = ""; deployment_mode: str = ""; state: str = "CREATED"; created_at: str = field(default_factory=now_iso)
@dataclass
class Requirement:
    id: str = field(default_factory=lambda: new_id("req")); project_id: str = ""; description: str = ""; source: str = ""; status: str = "DRAFT"; approved: bool = False
@dataclass
class Task:
    id: str = field(default_factory=lambda: new_id("tsk")); project_id: str = ""; capability_id: str = ""; state: str = "PENDING"; inputs: dict[str, Any] = field(default_factory=dict); outputs: dict[str, Any] = field(default_factory=dict)
@dataclass
class AgentAssignment:
    id: str = field(default_factory=lambda: new_id("asg")); task_id: str = ""; agent_ref: str = ""; capability_id: str = ""; status: str = "PENDING"; provenance: str = ""
@dataclass
class Dependency:
    id: str = field(default_factory=lambda: new_id("dep")); source_id: str = ""; target_id: str = ""; dependency_type: str = "TASK"
@dataclass
class Artifact:
    id: str = field(default_factory=lambda: new_id("art")); project_id: str = ""; type: str = ""; version: str = "1.0"; created_by: str = ""; created_at: str = field(default_factory=now_iso); parent_artifact: str | None = None; status: str = "DRAFT"; integrity: str | None = None; source_references: list[str] = field(default_factory=list); validation_status: str = "UNVALIDATED"
@dataclass
class Build:
    id: str = field(default_factory=lambda: new_id("bld")); project_id: str = ""; status: str = "QUEUED"; input_refs: list[str] = field(default_factory=list); output_refs: list[str] = field(default_factory=list)
@dataclass
class TestRun:
    id: str = field(default_factory=lambda: new_id("tst")); project_id: str = ""; test_type: str = ""; target_ref: str = ""; status: str = "QUEUED"; result: str = "NOT_RUN"; evidence: dict[str, Any] = field(default_factory=dict)
@dataclass
class Approval:
    id: str = field(default_factory=lambda: new_id("apr")); project_id: str = ""; approval_type: str = ""; required: bool = True; decision: str = "PENDING"; actor: str = ""; reason: str = ""; timestamp: str = field(default_factory=now_iso)
@dataclass
class Retry:
    id: str = field(default_factory=lambda: new_id("rty")); target_id: str = ""; failure_class: str = ""; attempt: int = 1; outcome: str = "PENDING"; reason: str = ""
@dataclass
class Checkpoint:
    id: str = field(default_factory=lambda: new_id("chk")); project_id: str = ""; milestone: str = ""; snapshot_ref: str = ""; timestamp: str = field(default_factory=now_iso)
@dataclass
class Release:
    id: str = field(default_factory=lambda: new_id("rel")); project_id: str = ""; version: str = "0.1.0"; artifact_refs: list[str] = field(default_factory=list); validation_state: str = "UNVALIDATED"; approval_state: str = "PENDING"; state: str = "DRAFT"
@dataclass
class Event:
    id: str = field(default_factory=lambda: new_id("evt")); project_id: str = ""; task_id: str | None = None; timestamp: str = field(default_factory=now_iso); previous_state: str | None = None; new_state: str | None = None; actor: str = ""; reason: str = ""; inputs: dict[str, Any] = field(default_factory=dict); outputs: dict[str, Any] = field(default_factory=dict); source_references: list[str] = field(default_factory=list)

def to_record(entity: Any) -> dict[str, Any]: return asdict(entity)
