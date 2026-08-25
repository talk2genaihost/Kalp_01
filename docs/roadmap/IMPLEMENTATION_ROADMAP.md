# Implementation Roadmap

## Wave 0 — Repository and governance
- establish source registry and ADRs
- import authoritative source manifests
- lock core contracts
Acceptance: provenance and authority checks work.

## Wave 1 — Trustworthy kernel
- request/context model
- authority engine
- event model
- Cognitive Swarm
Acceptance: end-to-end request produces traceable stages.

## Wave 2 — Smriti and evidence
- memory scopes
- evidence/provenance
- gatekeeper
Acceptance: retrieval cannot silently override authority.

## Wave 3 — Persona and workforce
- Persona DNA
- capability matching
- activation
- workforce registry adapters
Acceptance: selection respects authority and scope.

## Wave 4 — Hive runtime
- mailboxes
- blackboard
- task graph
- lifecycle/checkpoints/recovery
Acceptance: bounded multi-agent execution.

## Wave 5 — Verification and Virodh
- critical checks
- output verification
- escalation
Acceptance: failures produce revise/escalate paths.

## Wave 6 — Learning
- evaluation
- QA
- promotion controls
Acceptance: learning remains governed.

## Wave 7 — Provider/tool adapters
Acceptance: persona identity survives provider changes.

## Wave 8 — Operations
- observability
- reliability
- testing
- DR
Acceptance: production readiness gates.

## Wave 9 — Domain applications
- Genie
- DADI
- Kalplok
- Enterprise/SAP
Acceptance: applications consume stable KALP contracts.
