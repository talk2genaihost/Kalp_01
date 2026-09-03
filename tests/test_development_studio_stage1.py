import unittest
from development_studio.domain.models import Project, Requirement, Task, Artifact, Event
from development_studio.domain.state import validate_project_transition, validate_task_transition
from development_studio.persistence.sqlite import SQLiteStore
from development_studio.repositories import ProjectRepository, RequirementRepository, TaskRepository, ArtifactRepository, EventStore

class Stage1Tests(unittest.TestCase):
    def setUp(self): self.store = SQLiteStore()
    def tearDown(self): self.store.close()
    def test_project_persistence(self):
        p = Project(intent="offline Mac storage manager", platform="macOS", deployment_mode="OFFLINE")
        ProjectRepository(self.store).save(p)
        self.assertEqual(ProjectRepository(self.store).get(p.id)["intent"], p.intent)
    def test_requirement_not_automatically_approved(self):
        p = Project(); ProjectRepository(self.store).save(p)
        r = Requirement(project_id=p.id, description="Store data locally")
        RequirementRepository(self.store).save(r)
        self.assertFalse(RequirementRepository(self.store).get(r.id)["approved"])
    def test_task_and_artifact_persistence(self):
        p = Project(); ProjectRepository(self.store).save(p)
        t = Task(project_id=p.id, capability_id="DS-CAP-001"); TaskRepository(self.store).save(t)
        a = Artifact(project_id=p.id, type="REQUIREMENTS", created_by="test"); ArtifactRepository(self.store).save(a)
        self.assertIsNotNone(TaskRepository(self.store).get(t.id)); self.assertIsNotNone(ArtifactRepository(self.store).get(a.id))
    def test_event_persistence(self):
        p = Project(); ProjectRepository(self.store).save(p)
        e = Event(project_id=p.id, previous_state="CREATED", new_state="DISCOVERY", actor="test"); EventStore(self.store).save(e)
        self.assertEqual(EventStore(self.store).get(e.id)["new_state"], "DISCOVERY")
    def test_invalid_transitions_rejected(self):
        with self.assertRaises(ValueError): validate_project_transition("CREATED", "DELIVERED")
        with self.assertRaises(ValueError): validate_task_transition("PENDING", "COMPLETED")

if __name__ == "__main__": unittest.main()
