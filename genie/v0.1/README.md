# KALP Gini v0.1
## First executable slice: Idea -> Plan -> 18 Scenes

This is an implementation artifact derived from the retrieved KALP Genie Step 22 technical baseline.

### What is frozen
Schema version: **0.1.0**

Frozen contracts:
1. CreativeRequest
2. CreativeContext
3. CreativePlan
4. Scene
5. Asset
6. Engine
7. GenerationJob
8. CreativeQA
9. RevisionPlan
10. DeliveryPackage

The schema fields preserve the Step 22 contract vocabulary. v0.1 adds only bounded implementation metadata where needed for execution traceability and testability.

### What is executable now
`CreativeRequest -> CreativeContext -> CreativePlan -> exactly 18 Scene objects`

The slice:
- makes assumptions explicit
- preserves locked decisions
- creates an 18-scene production plan
- carries continuity state scene-to-scene
- creates production-oriented camera, performance, audio, VFX/SFX and verification placeholders
- verifies scene count and total duration
- writes JSON artifacts plus an execution receipt

### Generation Engine Layer v0.1
The provider-independent engine boundary is executable.

Components:
- Engine Registry
- Capability-based Engine Selector
- GenerationJob planner
- Adapter interface
- Deterministic mock adapters
- Engine execution receipt

For each 18-scene story, the simulated matrix creates:
- 18 video jobs
- 18 voice jobs
- 18 music jobs
- 54 total GenerationJobs
- 54 simulated completions
- 0 real media files generated

The mock adapters generate execution manifests, not media. This proves the contract and routing path before real providers are connected.

### Real Provider Layer v0.1
A real-provider adapter boundary is present without making any provider part of the core Gini architecture.

Current concrete adapter:
- OpenAI image generation
- OpenAI speech generation

Provider configuration:
- `OPENAI_API_KEY` environment variable only
- credentials are never written into Gini schemas, jobs, receipts or manifests

The provider adapter is optional. If no provider credential is configured, planning and simulation continue to work. Real video and music execution are intentionally not claimed in this pass.

### Run
```bash
PYTHONPATH=. python -m gini.main --idea "Create a cinematic Hindi reel about courage overcoming anxiety using Hanuman as a metaphor."
```

### Test
```bash
PYTHONPATH=. python -m pytest -q
```

### Stress test
```bash
GINI_STRESS_SCENARIOS=1000 PYTHONPATH=. python -m pytest -q tests/test_stress.py -s
```

### GitHub CI
The repository runs the Gini unit/contract suite and the configurable stress suite through GitHub Actions. CI uses deterministic mock adapters and does not require provider credentials.

### What is deliberately NOT connected
Real image/video/voice/music generation engines are not required for the v0.1 simulation path. No MoneyPrinterTurbo dependency or adapter is included.

### Authority note
This package is an implementation artifact derived from the retrieved KALP Step 22 baseline. It is **not** itself a new canonical KALP source registration. Formal promotion/registration requires the governed KALP registration process.
