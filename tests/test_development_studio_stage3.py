import pytest

from src.development_studio.artifact_service import ArtifactService
from src.development_studio.domain.models import Artifact, Project
from src.development_studio.persistence.sqlite import SQLiteStore
from src.development_studio.repositories import ProjectRepository


def make_service():
    store = SQLiteStore()
    ProjectRepository(store).save(Project(id="p1", intent="build", platform="python", deployment_mode="OFFLINE"))
    return store, ArtifactService(store)


def test_artifact_preserves_governed_metadata_and_source_references():
    store, service = make_service()
    try:
        artifact = Artifact(
            id="a1", project_id="p1", type="SOURCE_CODE", version="1.0",
            created_by="agent-1", source_references=["SRC-1"],
            validation_status="VALIDATED",
        )
        service.create(artifact)
        saved = service.get("a1")
        assert saved["type"] == "SOURCE_CODE"
        assert saved["version"] == "1.0"
        assert saved["created_by"] == "agent-1"
        assert saved["source_references"] == ["SRC-1"]
        assert saved["validation_status"] == "VALIDATED"
    finally:
        store.close()


def test_parent_artifact_creates_inspectable_lineage_without_overwriting_parent():
    store, service = make_service()
    try:
        service.create(Artifact(id="a1", project_id="p1", type="REQUIREMENTS", version="1.0", created_by="user"))
        service.create(Artifact(id="a2", project_id="p1", type="REQUIREMENTS", version="2.0", created_by="user", parent_artifact="a1"))
        lineage = service.lineage("a2")
        assert [item["id"] for item in lineage] == ["a2", "a1"]
        assert service.get("a1")["version"] == "1.0"
    finally:
        store.close()


def test_missing_parent_is_rejected_without_partial_artifact_creation():
    store, service = make_service()
    try:
        with pytest.raises(LookupError, match="parent artifact not found"):
            service.create(Artifact(id="a2", project_id="p1", type="SOURCE_CODE", created_by="agent", parent_artifact="missing"))
        assert service.get("a2") is None
    finally:
        store.close()


def test_cross_project_parent_is_rejected():
    store, service = make_service()
    try:
        ProjectRepository(store).save(Project(id="p2", intent="other", platform="python", deployment_mode="OFFLINE"))
        service.create(Artifact(id="a1", project_id="p1", type="SOURCE_CODE", created_by="agent"))
        with pytest.raises(ValueError, match="same project"):
            service.create(Artifact(id="a2", project_id="p2", type="SOURCE_CODE", created_by="agent", parent_artifact="a1"))
        assert service.get("a2") is None
    finally:
        store.close()


def test_required_artifact_metadata_and_identity_are_enforced():
    store, service = make_service()
    try:
        with pytest.raises(ValueError, match="artifact fields required"):
            service.create(Artifact(id="", project_id="p1", type="SOURCE_CODE", created_by="agent"))
        service.create(Artifact(id="a1", project_id="p1", type="SOURCE_CODE", created_by="agent"))
        with pytest.raises(ValueError, match="artifact already exists"):
            service.create(Artifact(id="a1", project_id="p1", type="SOURCE_CODE", created_by="agent"))
    finally:
        store.close()
