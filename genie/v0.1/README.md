# KALP Gini v0.1

Executable implementation foundation for the KALP Gini creative-agent product layer.

Frozen contracts: CreativeRequest, CreativeContext, CreativePlan, Scene, Asset, Engine, GenerationJob, CreativeQA, RevisionPlan, DeliveryPackage.

Execution slice: Idea -> Context -> Plan -> 18 Scenes.

Generation layer: provider-independent Engine Registry, capability selection, GenerationJob routing, mock adapters, and a real provider adapter boundary.

Current concrete provider boundary includes optional OpenAI image and voice adapters. Credentials are environment-only and never persisted. Video/music provider execution is intentionally not claimed complete.

MoneyPrinterTurbo is not a dependency, fork, or adapter.

This is implementation code derived from KALP technical baselines and is not itself a canonical source registration.
