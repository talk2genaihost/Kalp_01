import os
import time
from pathlib import Path

from gini.schemas import CreativeRequest
from gini.pipeline import execute_idea_to_plan_to_scenes
from gini.generation import plan_generation_job, execute_simulated


def test_1000_scenario_stress(tmp_path):
    scenarios = int(os.getenv("GINI_STRESS_SCENARIOS", "1000"))
    durations = (15, 30, 45, 60, 90, 120)
    total_jobs = 0
    total_scenes = 0
    started = time.perf_counter()

    for i in range(scenarios):
        duration = durations[i % len(durations)]
        req = CreativeRequest(
            request_id=f"REQ_STRESS_{i:05d}",
            user_intent=f"Stress scenario {i}: create a cinematic short-form reel about courage.",
            content_type="short-form-reel",
            target_platform="Instagram Reels",
            language="Hindi",
            duration=duration,
            aspect_ratio="9:16",
        )
        ctx, plan, scenes = execute_idea_to_plan_to_scenes(req)
        assert len(scenes) == 18
        assert abs(sum(s.duration for s in scenes) - duration) < 0.01

        for scene in scenes:
            for modality in ("video", "voice", "music"):
                job = plan_generation_job(
                    scene,
                    project_ref=plan.plan_id,
                    modality=modality,
                    prompt_ref=f"PROMPT_{scene.scene_id}_{modality.upper()}",
                    output_spec={"scene_id": scene.scene_id, "duration": scene.duration},
                )
                job, result = execute_simulated(
                    job,
                    prompt_payload={"scene_id": scene.scene_id, "modality": modality},
                    output_dir=Path(tmp_path) / f"scenario_{i:05d}",
                )
                assert job.status == "COMPLETED"
                assert result.status == "SIMULATED"
                total_jobs += 1

        total_scenes += len(scenes)

    elapsed = time.perf_counter() - started
    assert total_scenes == scenarios * 18
    assert total_jobs == scenarios * 54
    print(
        f"STRESS_PASS scenarios={scenarios} scenes={total_scenes} "
        f"jobs={total_jobs} elapsed_seconds={elapsed:.3f}"
    )
