from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict
@dataclass
class ProviderResult:
    provider: str; engine_id: str; status: str; output_refs: list[str]; metadata: Dict[str,Any]
class ProviderAdapter(ABC):
    @abstractmethod
    def health(self)->Dict[str,Any]: ...
    @abstractmethod
    def execute(self,job:Dict[str,Any])->ProviderResult: ...
