from dataclasses import dataclass
from typing import Dict, Any
from pathlib import Path
import json

@dataclass
class AdapterResult:
    engine_id: str
    modality: str
    status: str
    output_ref: str
    metadata: Dict[str, Any]

class MockAdapter:
    """
    Contract exercise only. It does not generate media.
    It emits a deterministic execution artifact describing what a real adapter
    would receive and return.
    """
    def __init__(self, engine):
        self.engine = engine

    def execute(self, payload, output_dir):
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        job_key = payload["job_id"]
        artifact = out / f"{job_key}.execution.json"
        artifact.write_text(json.dumps({
            "engine_id": self.engine.engine_id,
            "provider": self.engine.provider,
            "modality": self.engine.modality,
            "status": "SIMULATED",
            "input": payload,
            "real_media_generated": False
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        return AdapterResult(
            engine_id=self.engine.engine_id,
            modality=self.engine.modality,
            status="SIMULATED",
            output_ref=str(artifact),
            metadata={"real_media_generated": False}
        )
