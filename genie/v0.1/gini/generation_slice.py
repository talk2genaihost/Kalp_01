from dataclasses import asdict

from .generation import registry_index, plan_generation_job, execute_simulated

def build_generation_manifest(ctx, plan, scenes, output_dir):
    """
    Exercises the Engine contract without connecting a real generation provider.
    For each scene, creates video + voice + music GenerationJobs and simulates
    adapter execution into execution manifests.
    """
    from pathlib import Path
    import json
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    jobs = []
    results = []
    for scene in scenes:
        for modality in ("video", "voice", "music"):
            prompt_ref = f"PROMPT_{scene.scene_id}_{modality.upper()}"
            job = plan_generation_job(
                scene,
                project_ref=plan.plan_id,
                modality=modality,
                prompt_ref=prompt_ref,
                output_spec={
                    "scene_id": scene.scene_id,
                    "duration": scene.duration,
                    "aspect_ratio": ctx.visual_language["aspect_ratio"]
                }
            )
            job, result = execute_simulated(
                job,
                prompt_payload={
                    "scene_id": scene.scene_id,
                    "modality": modality,
                    "generation_prompt": scene.action,
                    "performance": scene.performance,
                    "camera": scene.camera,
                    "music": scene.music,
                },
                output_dir=out / "simulated_jobs"
            )
            jobs.append(job)
            results.append({
                "job_id": job.job_id,
                "engine_id": job.tool_ref,
                "status": result.status,
                "output_ref": result.output_ref,
                "real_media_generated": False
            })
    manifest = {
        "schema_version": "0.1.0",
        "execution_mode": "SIMULATED_ENGINE_CONTRACT",
        "real_generation_engines_connected": False,
        "scenes": len(scenes),
        "jobs": len(jobs),
        "completed_jobs": sum(1 for j in jobs if j.status == "COMPLETED"),
        "results": results
    }
    (out / "generation_engine_receipt.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out / "generation_jobs.json").write_text(
        json.dumps([asdict(j) for j in jobs], ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    return manifest
