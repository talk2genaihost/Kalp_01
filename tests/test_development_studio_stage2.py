import unittest

from development_studio.domain.models import Event, Project, Task
from development_studio.persistence.sqlite import SQLiteStore
from development_studio.repositories import ProjectRepository, TaskRepository
from development_studio.state_event_engine import StateEventEngine


class Stage2Tests(unittest.TestCase):
    def setUp(self):
        self.store = SQLiteStore()
        self.engine = StateEventEngine(self.store)
        self.projects = ProjectRepository(self.store)
        self.tasks = TaskRepository(self.store)

    def tearDown(self):
        self.store.close()

    def test_project_transition_updates_state_and_records_event(self):
        project = Project(intent="stage 2 test", platform="macOS", deployment_mode="OFFLINE")
        self.projects.save(project)

        result = self.engine.transition_project(
            project.id,
            "DISCOVERY",
            actor="system",
            reason="begin discovery",
            source_references=["DS-B003", "DS-B004"],
        )

        self.assertEqual(result.previous_state, "CREATED")
        self.assertEqual(result.new_state, "DISCOVERY")
        self.assertEqual(self.projects.get(project.id)["state"], "DISCOVERY")
        events = self.engine.list_events(project.id)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["previous_state"], "CREATED")
        self.assertEqual(events[0]["new_state"], "DISCOVERY")
        self.assertEqual(events[0]["source_references"], ["DS-B003", "DS-B004"])

    def test_task_transition_records_project_and_task_event_context(self):
        project = Project()
        self.projects.save(project)
        task = Task(project_id=project.id, capability_id="DS-CAP-001")
        self.tasks.save(task)

        self.engine.transition_task(
            task.id,
            "READY",
            actor="scheduler",
            reason="dependencies satisfied",
        )

        self.assertEqual(self.tasks.get(task.id)["state"], "READY")
        events = self.engine.list_events(project.id, task.id)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["task_id"], task.id)
        self.assertEqual(events[0]["project_id"], project.id)

    def test_invalid_transition_is_rejected_without_state_or_event_change(self):
        project = Project()
        self.projects.save(project)

        with self.assertRaises(ValueError):
            self.engine.transition_project(
                project.id,
                "DELIVERED",
                actor="system",
                reason="invalid shortcut",
            )

        self.assertEqual(self.projects.get(project.id)["state"], "CREATED")
        self.assertEqual(self.engine.list_events(project.id), [])

    def test_duplicate_event_identity_rolls_back_state_change(self):
        project = Project()
        self.projects.save(project)
        self.engine.transition_project(
            project.id,
            "DISCOVERY",
            actor="system",
            reason="first transition",
            event_id="evt-fixed",
        )

        with self.assertRaises(ValueError):
            self.engine.transition_project(
                project.id,
                "REQUIREMENTS",
                actor="system",
                reason="second transition with duplicate event id",
                event_id="evt-fixed",
            )

        self.assertEqual(self.projects.get(project.id)["state"], "DISCOVERY")
        self.assertEqual(len(self.engine.list_events(project.id)), 1)

    def test_missing_actor_or_reason_does_not_mutate_state(self):
        project = Project()
        self.projects.save(project)

        with self.assertRaises(ValueError):
            self.engine.transition_project(project.id, "DISCOVERY", actor="", reason="start")
        with self.assertRaises(ValueError):
            self.engine.transition_project(project.id, "DISCOVERY", actor="system", reason="")

        self.assertEqual(self.projects.get(project.id)["state"], "CREATED")
        self.assertEqual(self.engine.list_events(project.id), [])

    def test_event_history_is_replayable_in_recorded_order(self):
        project = Project()
        self.projects.save(project)
        self.engine.transition_project(project.id, "DISCOVERY", actor="system", reason="one")
        self.engine.transition_project(project.id, "REQUIREMENTS", actor="system", reason="two")
        self.engine.transition_project(project.id, "REQUIREMENTS_APPROVED", actor="reviewer", reason="approved")

        events = self.engine.list_events(project.id)
        transitions = [(event["previous_state"], event["new_state"]) for event in events]
        self.assertEqual(
            transitions,
            [("CREATED", "DISCOVERY"), ("DISCOVERY", "REQUIREMENTS"), ("REQUIREMENTS", "REQUIREMENTS_APPROVED")],
        )


if __name__ == "__main__":
    unittest.main()
