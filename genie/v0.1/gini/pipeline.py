from __future__ import annotations
from pathlib import Path
import json, uuid
from dataclasses import asdict
from .schemas import *

def uid(prefix): return f"{prefix}_{uuid.uuid4().hex[:10]}"

def build_context(req):
    platform=req.target_platform or "Instagram Reels"; language=req.language or "Hindi"; duration=req.duration or 60
    aspect=req.aspect_ratio or "9:16"; assumptions=[]
    for k,v in [("target_platform",platform),("language",language),("duration",duration),("aspect_ratio",aspect)]:
        if getattr(req,k,None) is None: assumptions.append(f"{k} defaulted to {v}")
    return CreativeContext(uid("CTX"), {"user_intent":req.user_intent,"content_type":req.content_type},
      {"status":"idea"},{"location":"story-defined","time":"story-defined"},req.characters,
      {"style":req.style or "cinematic","aspect_ratio":aspect},{"language":language},
      {"delivery":"conversational"},{"platform":platform,"duration":duration,"aspect_ratio":aspect},
      {"character":{},"world":{},"temporal":{}},{"risk_profile":req.risk_profile or "standard"},
      {"scene_count":18,"scene_duration_seconds":duration/18,"real_generation_engines_connected":False},
      list(req.locked_elements),assumptions,[req.request_id])

def build_plan(req,ctx):
    n=18; d=ctx.platform_constraints["duration"]
    beats=[("HOOK","establish the central tension"),("SETUP","show the ordinary state"),("DISTURBANCE","introduce the problem"),("ESCALATION","increase pressure"),("CONFRONTATION","force a choice"),("TURN","change direction"),("RESOLUTION","show consequence"),("PAYOFF","land the central idea")]
    bs=[{"beat_id":f"B{i+1:02}","type":b,"purpose":p} for i,(b,p) in enumerate(beats)]
    sp=[]
    for i in range(n):
        b=bs[min((i*len(bs))//n,len(bs)-1)]; sp.append({"scene_id":f"S{i+1:02}","duration":d/n,"beat":b["type"],"purpose":b["purpose"]})
    return CreativePlan(uid("PLAN"),ctx.context_id,req.user_intent[:180],{"opening":"hook","middle":"pressure and transformation","ending":"payoff"},bs,sp,[],{"source":"scene state + character state"},{"video":"planned","voice":"planned","music":"planned"},{"target":ctx.platform_constraints["platform"]})

def build_scenes(req,ctx,plan):
    scenes=[]; state={"scene":0,"character":"stable","world":"established"}; duration=ctx.platform_constraints["duration"]; n=18; rounded=round(duration/n,3)
    for i,p in enumerate(plan.scene_plan,1):
        dur=rounded if i<n else round(duration-rounded*(n-1),3); out=dict(state); out["scene"]=i
        scenes.append(Scene(p["scene_id"],i,dur,p["purpose"],{"turn":p["beat"].lower()},[c.get("id",c.get("name","protagonist")) for c in ctx.character_state] or ["protagonist"],"story-defined environment","Advance the story through observable action.",{"language":ctx.audio_language["language"],"text":""},{"shot":"medium-to-close","lens":"35-50mm","movement":"motivated movement"},{"source":"world-consistent"},{"emotion":p["beat"].lower() },[],[{"type":"diegetic"}],{"cue":p["beat"].lower()},"world-consistent ambience","motivated cut",state,out,None,{"identity":True,"world":True,"temporal":True})
        state=out
    return scenes

def execute_idea_to_plan_to_scenes(req):
    c=build_context(req); p=build_plan(req,c); s=build_scenes(req,c,p); assert len(s)==18; assert abs(sum(x.duration for x in s)-c.platform_constraints["duration"])<.01; return c,p,s

def write_slice(output_dir,req):
    out=Path(output_dir); out.mkdir(parents=True,exist_ok=True); c,p,s=execute_idea_to_plan_to_scenes(req)
    (out/"creative_request.json").write_text(json.dumps(asdict(req),ensure_ascii=False,indent=2)); (out/"creative_context.json").write_text(json.dumps(asdict(c),ensure_ascii=False,indent=2)); (out/"creative_plan.json").write_text(json.dumps(asdict(p),ensure_ascii=False,indent=2)); (out/"scenes.json").write_text(json.dumps([asdict(x) for x in s],ensure_ascii=False,indent=2))
    return {"status":"EXECUTED","schema_version":SCHEMA_VERSION,"scene_count":18,"duration_seconds":sum(x.duration for x in s)}
