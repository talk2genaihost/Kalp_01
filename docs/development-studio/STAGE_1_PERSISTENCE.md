# Development Studio Stage 1 Persistence (Derived)

Development Studio is a proposed/derived domain subsystem beneath KALP. It does not define KALP orchestration, authority, retrieval, workforce, or persona semantics.

No persistence technology existed in the recovered repository baseline. Stage 1 therefore uses a small JSON-file repository with schema version `1`, atomic replacement writes, and application-level relationship validation. This is a development persistence foundation, **not** a production database or deployment architecture.

The persistent collections are `projects`, `requirements`, `tasks`, `agentAssignments`, `dependencies`, `artifacts`, `builds`, `testRuns`, `approvals`, `retries`, `checkpoints`, `releases`, and `events`. Events and artifacts are append-only through the repository API; identity and artifact type/version collisions are rejected.
