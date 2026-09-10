from __future__ import annotations
from pathlib import Path
import json, uuid
from .schemas import *

def uid(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:10]}"

def build_context(req: CreativeRequest) -> CreativeContext:
    assumptions = []
    platform = req.target_platform or "Instagram Reels"
    language = req.language or "Hindi"
    duration = req.duration or 60
    aspect = req.aspect_ratio or "9:16"
    style = req.style or "cinematic"
    tone = req.tone or "emotionally grounded"
    audience = req.audience or "general social audience"
    for label, value in [("target_platform", platform), ("language", language), ("duration", duration), ("aspect_ratio", aspect), ("style", style), ("tone", tone), ("audience", audience)]:
        if getattr(req, label, None) is None:
            assumptions.append(f"{label} defaulted to {value}")
    return CreativeContext(
        context_id=uid("CTX"),
        intent={"user_intent": req.user_intent, "content_type": req.content_type},
        narrative_state={"status": "idea", "objective": "convert idea into coherent short-form narrative"},
        world_state={"location": "story-defined", "time": "story-defined", "weather": "story-defined"},
        character_state=req.characters,
        visual_language={"style": style, "aspect_ratio": aspect},
        audio_language={"language": language, "music_role": "narrative state", "sfx": "contextual"},
        performance_language={"delivery": "conversational", "emotion": tone},
        platform_constraints={"platform": platform, "duration": duration, "aspect_ratio": aspect},
        continuity_state={"character": {}, "world": {}, "temporal": {}},
        safety_constraints={"risk_profile": req.risk_profile or "standard"},
        production_constraints={"scene_count": 18, "scene_duration_seconds": round(duration / 18, 3), "real_generation_engines_connected": False},
        locked_decisions=list(req.locked_elements),
        assumptions=assumptions,
        provenance_refs=[req.request_id],
    )

def build_plan(req: CreativeRequest, ctx: CreativeContext) -> CreativePlan:
    idea = req.user_intent.strip()
    logline = idea if len(idea) <= 180 else idea[:177] + "..."
    duration = ctx.platform_constraints["duration"]
    n = ctx.production_constraints["scene_count"]
    per = duration / n
    beats = [("HOOK", "establish the central tension"), ("SETUP", "show the ordinary state"), ("DISTURBANCE", "introduce the problem"), ("ESCALATION", "increase pressure"), ("CONFRONTATION", "force a choice"), ("TURN", "change the emotional/narrative direction"), ("RESOLUTION", "show the consequence"), ("PAYOFF", "land the central idea")]
    beat_sheet = [{"beat_id": f"B{i+1:02}", "type": b, "purpose": p} for i, (b, p) in enumerate(beats)]
    scene_plan = []
    for i in range(n):
        beat = beat_sheet[min((i * len(beat_sheet)) // n, len(beat_sheet) - 1)]
        scene_plan.append({"scene_id": f"S{i+1:02}", "duration": round(per, 3) if i < n - 1 else round(duration - round(per, 3) * (n - 1), 3), "beat": beat["type"], "purpose": beat["purpose"], "causal_role": "advance story state"})
    return CreativePlan(
        plan_id=uid("PLAN"), context_ref=ctx.context_id, logline=logline,
        narrative_arc={"opening": "hook", "middle": "pressure and transformation", "ending": "payoff"},
        beat_sheet=beat_sheet, scene_plan=scene_plan, shot_plan=[],
        performance_plan={"source": "scene state + character state"},
        media_plan={"video": "planned", "voice": "planned", "music": "planned"},
        delivery_plan={"target": ctx.platform_constraints["platform"]},
    )

def scene_text(req, beat, index, total):
    subject = req.user_intent.strip()
    return f"Scene {index}/{total}: {beat}. Advance the central idea through observable cinematic action. Story reference: {subject}"

def build_scenes(req: CreativeRequest, ctx: CreativeContext, plan: CreativePlan):
    scenes = []
    state = {"scene": 0, "character": "stable", "world": "established", "knowledge": "baseline"}
    for i, p in enumerate(plan.scene_plan, 1):
        beat = p["beat"]
        out = dict(state)
        out["scene"] = i
        out["knowledge"] = f"state after {beat.lower()}"
        scenes.append(Scene(
            scene_id=p["scene_id"], sequence=i, duration=p["duration"], narrative_purpose=p["purpose"],
            emotional_state={"before": "current state", "turn": beat.lower(), "after": "updated state"},
            characters=[c.get("id", c.get("name", "protagonist")) for c in ctx.character_state] or ["protagonist"],
            environment="story-defined environment; preserve spatial continuity",
            action=scene_text(req, beat, i, len(plan.scene_plan)),
            dialogue_vo={"language": ctx.audio_language["language"], "text": "", "duration_target": min(4.0, p["duration"])},
            camera={"shot": "medium-to-close", "lens": "35-50mm", "movement": "motivated movement", "focus": "story subject"},
            lighting={"source": "world-consistent", "continuity": "inherit unless narrative change"},
            performance={"emotion": beat.lower(), "body_language": "observable and motivated", "facial": "restrained, readable"},
            vfx=[], sfx=[{"type": "diegetic", "trigger": "action", "timing": "action-synchronous"}],
            music={"cue": beat.lower(), "role": "narrative state", "intensity": "matched to emotion"},
            ambience="world-consistent room/environment tone", transition="motivated cut",
            continuity_in=dict(state), continuity_out=out, generation_prompt_ref=None,
            verification_profile={"identity": True, "world": True, "temporal": True, "constraints": True},
        ))
        state = out
    return scenes

def execute_idea_to_plan_to_scenes(req: CreativeRequest):
    ctx = build_context(req)
    plan = build_plan(req, ctx)
    scenes = build_scenes(req, ctx, plan)
    assert len(scenes) == 18
    assert abs(sum(s.duration for s in scenes) - ctx.platform_constraints["duration"]) < 0.01
    return ctx, plan, scenes

def write_slice(output_dir, req):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    ctx, plan, scenes = execute_idea_to_plan_to_scenes(req)
    write_json(out / "creative_request.json", req)
    write_json(out / "creative_context.json", ctx)
    write_json(out / "creative_plan.json", plan)
    (out / "scenes.json").write_text(json.dumps([dump(s) for s in scenes], ensure_ascii=False, indent=2), encoding="utf-8")
    manifest = {"slice": "Idea -> Plan -> 18 Scenes", "schema_version": SCHEMA_VERSION, "status": "EXECUTED", "generation_engines": "NOT CONNECTED", "scene_count": len(scenes), "duration_seconds": sum(s.duration for s in scenes), "trace": {"request": req.request_id, "context": ctx.context_id, "plan": plan.plan_id, "scenes": [s.scene_id for s in scenes]}}
    (out / "execution_receipt.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest
