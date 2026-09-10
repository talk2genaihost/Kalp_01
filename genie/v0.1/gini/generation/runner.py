from ..schemas import GenerationJob
from .registry import registry_index
from .selector import select_engine

def plan_generation_job(scene,project_ref,modality,prompt_ref,output_spec=None):
    caps={"video":["video_generation"],"image":["image_generation"],"voice":["voice_synthesis"],"music":["music_generation"]}
    e,reason=select_engine(registry_index(),modality,caps.get(modality,[]))
    return GenerationJob(f"JOB_{scene.scene_id}_{modality.upper()}",project_ref,scene.scene_id,modality,e.engine_id,prompt_ref,[],output_spec or {},"KALP-GENIE-POLICY-v0.1","KALP-GENIE-BUDGET-v0.1","QUEUED",[],engine_selection_reason=reason,capability_snapshot={"engine":e.engine_id,"capabilities":e.capabilities,"version":e.version})

def execute_simulated(job,output_dir):
    job.status="COMPLETED"; return job,{"status":"SIMULATED","real_media_generated":False,"engine_id":job.tool_ref}
