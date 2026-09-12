from pathlib import Path
from ..schemas import GenerationJob
from .registry import registry_index
from .selector import select_engine
from .adapters import MockAdapter

MODALITY_CAPABILITIES = {
    "video": ["video_generation"],
    "image": ["image_generation"],
    "voice": ["voice_synthesis"],
    "music": ["music_generation"],
}

def plan_generation_job(scene, project_ref, modality, prompt_ref, output_spec=None):
    registry = registry_index()
    engine, reason = select_engine(registry, modality, MODALITY_CAPABILITIES.get(modality, []), quality="draft")
    return GenerationJob(
        job_id=f"JOB_{scene.scene_id}_{modality.upper()}", project_ref=project_ref, scene_ref=scene.scene_id,
        modality=modality, tool_ref=engine.engine_id, prompt_ref=prompt_ref, input_assets=[],
        output_spec=output_spec or {}, policy_ref="KALP-GENIE-POLICY-v0.1", budget_ref="KALP-GENIE-BUDGET-v0.1",
        status="QUEUED", outputs=[], engine_selection_reason=reason,
        capability_snapshot={"engine": engine.engine_id, "capabilities": engine.capabilities, "version": engine.version},
    )

def execute_simulated(job, prompt_payload, output_dir):
    registry = registry_index()
    engine = registry[job.tool_ref]
    job.status = "RUNNING"
    result = MockAdapter(engine).execute(
        {"job_id": job.job_id, "prompt": prompt_payload, "output_spec": job.output_spec}, output_dir
    )
    job.status = "COMPLETED"
    job.outputs = [result.output_ref]
    return job, result
