class EngineSelectionError(RuntimeError): pass

def select_engine(registry,modality,required_capabilities=None,quality="draft"):
    required_capabilities=required_capabilities or []
    candidates=[e for e in registry.values() if e.modality==modality and e.availability=="available" and quality in e.quality_profiles and all(c in e.capabilities for c in required_capabilities)]
    if not candidates: raise EngineSelectionError(f"No engine satisfies modality={modality}, capabilities={required_capabilities}, quality={quality}")
    candidates.sort(key=lambda e:(e.cost_profile,e.latency_profile,e.engine_id)); e=candidates[0]
    return e,f"capability_match={required_capabilities}; quality={quality}; provider={e.provider}"
