from gini.schemas import CreativeRequest
from gini.pipeline import execute_idea_to_plan_to_scenes
from gini.generation_slice import build_generation_manifest

def test_engine_contract_simulation(tmp_path):
    req = CreativeRequest(
        request_id="REQ_ENGINE_TEST",
        user_intent="A cinematic reel about courage.",
        content_type="short-form-reel",
        target_platform="Instagram Reels",
        language="Hindi", duration=60, aspect_ratio="9:16"
    )
    ctx, plan, scenes = execute_idea_to_plan_to_scenes(req)
    m = build_generation_manifest(ctx, plan, scenes, tmp_path)
    assert m["scenes"] == 18
    assert m["jobs"] == 54
    assert m["completed_jobs"] == 54
    assert m["real_generation_engines_connected"] is False
    assert all(x["real_media_generated"] is False for x in m["results"])
