import assert from "node:assert/strict";
import { existsSync, mkdtempSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";
import type { Approval, Artifact, DevelopmentStudioEvent, Project, Release, Task } from "../src/development-studio/domain.js";
import { FileDevelopmentStudioRepository } from "../src/development-studio/repository.js";
import { assertProjectTransition, assertTaskTransition } from "../src/development-studio/state.js";

const stamp = "2026-09-03T00:00:00.000Z";
const provenance = { sourceReferences: ["stage-1-test"], authority: "INFERENCE" as const, createdAt: stamp };
function repository() { return new FileDevelopmentStudioRepository(join(mkdtempSync(join(tmpdir(), "kalp-stage-1-")), "studio.json")); }
function project(id = "project-1"): Project { return { id, userIntent: "Create a bounded project", status: "CREATED", platform: "WEB", deploymentMode: "OFFLINE", executionMetadata: {}, traceReferences: [], ...provenance }; }
function task(id = "task-1"): Task { return { id, projectId: "project-1", capabilityReference: "implementation", state: "PENDING", inputs: {}, outputs: {}, retryIds: [], ...provenance }; }
function artifact(id = "artifact-1", version = "1.0.0", parentArtifactId?: string): Artifact { return { id, projectId: "project-1", type: "SOURCE_CODE", version, createdBy: "agent-1", status: "PROPOSED", validationStatus: "PROPOSED", ...(parentArtifactId ? { parentArtifactId } : {}), ...provenance }; }

test("persists and retrieves a valid project with schema version 1", () => { const folder = mkdtempSync(join(tmpdir(), "kalp-schema-")); const path = join(folder, "studio.json"); const repo = new FileDevelopmentStudioRepository(path); repo.save("projects", project()); assert.deepEqual(repo.get<Project>("projects", "project-1"), project()); assert.equal(repo.list<Project>("projects").length, 1); assert.ok(existsSync(path)); assert.equal(JSON.parse(readFileSync(path, "utf8")).schemaVersion, 1); });

test("rejects missing identifiers, invalid states, and duplicate identities", () => { const repo = repository(); assert.throws(() => repo.save("projects", { ...project(), id: "" }), /id is required/); assert.throws(() => repo.save("projects", { ...project(), status: "NOT_A_STATE" as "CREATED" }), /Invalid project state/); repo.save("projects", project()); assert.throws(() => repo.save("projects", project()), /Duplicate projects identity/); });
test("persists and retrieves all related entities", () => {
  const repo = repository(); repo.save("projects", project()); repo.save("tasks", task());
  repo.save("agentAssignments", { id: "assignment-1", projectId: "project-1", taskId: "task-1", agentReference: "agent-1", status: "PROPOSED", ...provenance });
  repo.save("requirements", { id: "requirement-1", projectId: "project-1", description: "A requirement", source: "user", status: "DRAFT", dependencyIds: [], traceReferences: [], ...provenance });
  repo.save("builds", { id: "build-1", projectId: "project-1", state: "PENDING", version: "1", ...provenance }); repo.save("testRuns", { id: "test-1", projectId: "project-1", buildId: "build-1", type: "UNIT", state: "PENDING", ...provenance });
  repo.save("retries", { id: "retry-1", projectId: "project-1", taskId: "task-1", attempt: 1, reason: "retry", status: "PROPOSED", ...provenance }); repo.save("checkpoints", { id: "checkpoint-1", projectId: "project-1", taskId: "task-1", state: "PENDING", status: "PROPOSED", ...provenance });
  assert.equal(repo.list("agentAssignments", "project-1").length, 1); assert.equal(repo.list("testRuns", "project-1").length, 1);
});
test("centralized state validation accepts lifecycle transitions and rejects invalid ones", () => { assertProjectTransition("CREATED", "DISCOVERY"); assertTaskTransition("PENDING", "READY"); assert.throws(() => assertProjectTransition("CREATED", "DELIVERED")); assert.throws(() => assertTaskTransition("PENDING", "COMPLETED")); });
test("preserves artifact lineage and validates dependency references", () => {
  const repo = repository(); repo.save("projects", project()); repo.save("tasks", task()); repo.save("artifacts", artifact()); repo.save("artifacts", artifact("artifact-2", "1.0.1", "artifact-1"));
  repo.save("dependencies", { id: "dependency-1", projectId: "project-1", kind: "TASK_TO_ARTIFACT", fromId: "task-1", toId: "artifact-1", status: "PROPOSED", ...provenance });
  assert.equal(repo.get<Artifact>("artifacts", "artifact-2")?.parentArtifactId, "artifact-1"); assert.throws(() => repo.save("dependencies", { id: "bad-dependency", projectId: "project-1", kind: "ARTIFACT_TO_TASK", fromId: "missing", toId: "task-1", status: "PROPOSED", ...provenance }), /Invalid dependency/);
});
test("persists immutable events, approvals, and release artifact lineage", () => {
  const repo = repository(); repo.save("projects", project()); repo.save("tasks", task()); repo.save("artifacts", artifact());
  const approval: Approval = { id: "approval-1", projectId: "project-1", approvalType: "RELEASE", requested: true, required: true, decision: "APPROVED", actor: "reviewer", reason: "validated", decidedAt: stamp, ...provenance }; repo.save("approvals", approval);
  const event: DevelopmentStudioEvent = { id: "event-1", projectId: "project-1", taskId: "task-1", previousState: "PENDING", newState: "READY", actor: "system", reason: "ready", inputs: {}, outputs: {}, ...provenance }; repo.save("events", event);
  const release: Release = { id: "release-1", projectId: "project-1", artifactId: "artifact-1", artifactVersion: "1.0.0", validationStatus: "PROPOSED", approvalId: "approval-1", status: "PROPOSED", ...provenance }; repo.save("releases", release);
  assert.deepEqual(repo.get<DevelopmentStudioEvent>("events", "event-1"), event); assert.equal(repo.get<Release>("releases", "release-1")?.artifactId, "artifact-1");
  assert.throws(() => repo.save("releases", { ...release, id: "bad-release", artifactVersion: "9" }), /Invalid release artifact/); assert.throws(() => repo.save("approvals", { ...approval, id: "bad-approval", actor: undefined }), /Decided approval/);
});
