from __future__ import annotations

from typing import Any

from .domain.models import Artifact, to_record
from .repositories import ArtifactRepository
from .persistence.sqlite import SQLiteStore


class ArtifactService:
    """Validate and persist Development Studio artifacts without promoting authority."""

    def __init__(self, store: SQLiteStore):
        self.store = store
        self.repository = ArtifactRepository(store)

    def create(self, artifact: Artifact) -> None:
        self._validate_artifact(artifact)
        if self.store.get("projects", artifact.project_id) is None:
            raise LookupError(f"project not found: {artifact.project_id}")
        if self.store.get("artifacts", artifact.id) is not None:
            raise ValueError(f"artifact already exists: {artifact.id}")
        if artifact.parent_artifact:
            parent = self.store.get("artifacts", artifact.parent_artifact)
            if parent is None:
                raise LookupError(f"parent artifact not found: {artifact.parent_artifact}")
            if parent["project_id"] != artifact.project_id:
                raise ValueError("parent artifact must belong to the same project")
        self.repository.save(artifact)

    def get(self, artifact_id: str) -> dict[str, Any] | None:
        return self.repository.get(artifact_id)

    def lineage(self, artifact_id: str) -> list[dict[str, Any]]:
        current = self.get(artifact_id)
        if current is None:
            raise LookupError(f"artifact not found: {artifact_id}")

        chain: list[dict[str, Any]] = []
        seen: set[str] = set()
        while current is not None:
            current_id = current["id"]
            if current_id in seen:
                raise ValueError("artifact lineage cycle detected")
            seen.add(current_id)
            chain.append(current)
            parent_id = current.get("parent_artifact")
            current = self.get(parent_id) if parent_id else None
        return chain

    @staticmethod
    def _validate_artifact(artifact: Artifact) -> None:
        required = {
            "id": artifact.id,
            "project_id": artifact.project_id,
            "type": artifact.type,
            "version": artifact.version,
            "created_by": artifact.created_by,
            "created_at": artifact.created_at,
            "status": artifact.status,
            "validation_status": artifact.validation_status,
        }
        missing = [name for name, value in required.items() if not str(value).strip()]
        if missing:
            raise ValueError(f"artifact fields required: {', '.join(missing)}")
        if not isinstance(artifact.source_references, list):
            raise ValueError("source_references must be a list")
        if artifact.integrity is not None and not str(artifact.integrity).strip():
            raise ValueError("integrity must be nonblank when supplied")
