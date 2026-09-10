from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

SCHEMA_VERSION = "0.1.0"

@dataclass
class CreativeRequest:
    request_id: str; user_intent: str; content_type: str
    target_platform: Optional[str]=None; audience: Optional[str]=None; language: Optional[str]=None
    duration: Optional[int]=None; aspect_ratio: Optional[str]=None; style: Optional[str]=None; tone: Optional[str]=None
    characters: List[Dict[str,Any]]=field(default_factory=list); references: List[str]=field(default_factory=list)
    constraints: List[str]=field(default_factory=list); locked_elements: List[str]=field(default_factory=list)
    desired_outputs: List[str]=field(default_factory=list); deadline: Optional[str]=None; risk_profile: Optional[str]=None
    schema_version: str=SCHEMA_VERSION

@dataclass
class CreativeContext:
    context_id: str; intent: Dict[str,Any]; narrative_state: Dict[str,Any]; world_state: Dict[str,Any]
    character_state: List[Dict[str,Any]]; visual_language: Dict[str,Any]; audio_language: Dict[str,Any]
    performance_language: Dict[str,Any]; platform_constraints: Dict[str,Any]; continuity_state: Dict[str,Any]
    safety_constraints: Dict[str,Any]; production_constraints: Dict[str,Any]; locked_decisions: List[str]
    assumptions: List[str]; provenance_refs: List[str]; completeness_status: str="CONTEXT READY"
    schema_version: str=SCHEMA_VERSION

@dataclass
class CreativePlan:
    plan_id: str; context_ref: str; logline: str; narrative_arc: Dict[str,Any]; beat_sheet: List[Dict[str,Any]]
    scene_plan: List[Dict[str,Any]]; shot_plan: List[Dict[str,Any]]; performance_plan: Dict[str,Any]
    media_plan: Dict[str,Any]; delivery_plan: Dict[str,Any]; schema_version: str=SCHEMA_VERSION

@dataclass
class Scene:
    scene_id: str; sequence: int; duration: float; narrative_purpose: str; emotional_state: Dict[str,Any]
    characters: List[str]; environment: str; action: str; dialogue_vo: Dict[str,Any]; camera: Dict[str,Any]
    lighting: Dict[str,Any]; performance: Dict[str,Any]; vfx: List[Dict[str,Any]]; sfx: List[Dict[str,Any]]
    music: Dict[str,Any]; ambience: str; transition: str; continuity_in: Dict[str,Any]
    continuity_out: Dict[str,Any]; generation_prompt_ref: Optional[str]; verification_profile: Dict[str,Any]
    schema_version: str=SCHEMA_VERSION

@dataclass
class Asset:
    asset_id: str; type: str; source: str; project_ref: str; scene_refs: List[str]; character_refs: List[str]
    version: str; provenance_refs: List[str]; technical_metadata: Dict[str,Any]; continuity_state: str
    quality_state: str; schema_version: str=SCHEMA_VERSION

@dataclass
class Engine:
    engine_id: str; provider: str; modality: str; capabilities: List[str]; input_schema: Dict[str,Any]
    output_schema: Dict[str,Any]; quality_profiles: List[str]; formats: List[str]; cost_profile: str
    latency_profile: str; availability: str; version: str; schema_version: str=SCHEMA_VERSION

@dataclass
class GenerationJob:
    job_id: str; project_ref: str; scene_ref: Optional[str]; modality: str; tool_ref: str; prompt_ref: Optional[str]
    input_assets: List[str]; output_spec: Dict[str,Any]; policy_ref: str; budget_ref: str; status: str
    outputs: List[str]; error_ref: Optional[str]=None; attempt_number: int=1; parent_job_id: Optional[str]=None
    engine_selection_reason: Optional[str]=None; capability_snapshot: Dict[str,Any]=field(default_factory=dict)
    schema_version: str=SCHEMA_VERSION

@dataclass
class CreativeQA:
    qa_id: str; project_ref: str; target_ref: str; technical: Dict[str,Any]; continuity: Dict[str,Any]
    creative: Dict[str,Any]; constraint_compliance: Dict[str,Any]; virodh: Dict[str,Any]; score: float
    status: str; findings: List[Dict[str,Any]]; schema_version: str=SCHEMA_VERSION

@dataclass
class RevisionPlan:
    revision_id: str; project_ref: str; target_refs: List[str]; findings_refs: List[str]; priority: str
    strategy: str; changes: List[Dict[str,Any]]; bounded: bool; max_attempts: int; status: str
    schema_version: str=SCHEMA_VERSION

@dataclass
class DeliveryPackage:
    package_id: str; project_ref: str; master_script_ref: str; scene_list_ref: str; storyboard_ref: str
    generation_prompts_ref: Optional[str]; performance_directions_ref: Optional[str]; vo_script_ref: Optional[str]
    music_plan_ref: Optional[str]; vfx_sfx_plan_ref: Optional[str]; asset_manifest_ref: str
    continuity_bible_ref: str; qa_report_ref: str; provenance_manifest_ref: str; status: str
    schema_version: str=SCHEMA_VERSION
