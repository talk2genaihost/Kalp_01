from gini.schemas import CreativeRequest, SCHEMA_VERSION
from gini.pipeline import execute_idea_to_plan_to_scenes

def test_18_scene_slice():
    req = CreativeRequest(
        request_id="REQ_TEST_001",
        user_intent="Create a cinematic Hindi reel about courage overcoming anxiety using Hanuman as a metaphor.",
        content_type="short-form-reel",
        target_platform="Instagram Reels",
        language="Hindi",
        duration=60,
        aspect_ratio="9:16"
    )
    ctx, plan, scenes = execute_idea_to_plan_to_scenes(req)
    assert ctx.schema_version == SCHEMA_VERSION
    assert plan.schema_version == SCHEMA_VERSION
    assert len(scenes) == 18
    assert round(sum(s.duration for s in scenes), 3) == 60
    assert [s.sequence for s in scenes] == list(range(1,19))
    assert scenes[0].continuity_out["scene"] == 1
    assert scenes[-1].continuity_out["scene"] == 18
