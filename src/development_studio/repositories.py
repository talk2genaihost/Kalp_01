from __future__ import annotations
from typing import Any
from .persistence.sqlite import SQLiteStore
from .domain.models import to_record

class EntityRepository:
    def __init__(self, store: SQLiteStore, table: str): self.store, self.table = store, table
    def save(self, entity: Any) -> None: self.store.insert(self.table, to_record(entity))
    def get(self, entity_id: str) -> dict[str, Any] | None: return self.store.get(self.table, entity_id)

class ProjectRepository(EntityRepository):
    def __init__(self, store): super().__init__(store, "projects")
class RequirementRepository(EntityRepository):
    def __init__(self, store): super().__init__(store, "requirements")
class TaskRepository(EntityRepository):
    def __init__(self, store): super().__init__(store, "tasks")
class ArtifactRepository(EntityRepository):
    def __init__(self, store): super().__init__(store, "artifacts")
class EventStore(EntityRepository):
    def __init__(self, store): super().__init__(store, "events")
