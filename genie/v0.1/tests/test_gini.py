from gini.schemas import CreativeRequest
from gini.pipeline import execute_idea_to_plan_to_scenes
from gini.generation.runner import plan_generation_job

def test_18_scene_slice():
    r=CreativeRequest("REQ_TEST","A cinematic Hindi reel about courage.","short-form-reel",target_platform="Instagram Reels",language="Hindi",duration=60,aspect_ratio="9:16")
    c,p,s=execute_idea_to_plan_to_scenes(r)
    assert len(s)==18
    assert round(sum(x.duration for x in s),3)==60

def test_engine_contract():
    r=CreativeRequest("REQ_ENGINE","A reel.","short-form-reel",duration=60)
    c,p,s=execute_idea_to_plan_to_scenes(r)
    j=plan_generation_job(s[0],p.plan_id,"video","PROMPT_S01_VIDEO")
    assert j.tool_ref=="mock.video.v0"
    assert j.status=="QUEUED"
