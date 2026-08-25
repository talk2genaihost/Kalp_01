# Boot and Command Governance

Exact `\KALPBOOT` uses the full source-driven chain:
Bootstrap Trigger → Cross-Chat Boot Contract → Master Retrieval Index → Source Authority Graph →
Current Architecture Manifest → Startup.

Stages:
FULLSYNC → INDEX → MAP → AUTHORITY → MANIFEST → STARTUP

Each stage reports:
COMPLETED / PARTIAL / UNAVAILABLE / FAILED

State labels:
RETRIEVED / RECONSTRUCTED / REMEMBERED / MISSING / INFERRED

Generic `\KALP:<COMMAND>` must retrieve the canonical contract before execution.
If absent: COMMAND SEMANTICS MISSING.
