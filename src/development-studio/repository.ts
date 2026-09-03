import { existsSync, readFileSync, renameSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";
import { mkdirSync } from "node:fs";
import type { AgentAssignment, Approval, Artifact, Build, Checkpoint, Dependency, DevelopmentStudioData, DevelopmentStudioEvent, Project, Release, Requirement, Retry, Task, TestRun } from "./domain.js";
import { emptyDevelopmentStudioData } from "./domain.js";
import { projectStates, taskStates } from "./state.js";

type CollectionName = Exclude<keyof DevelopmentStudioData, "schemaVersion">;
type Entity = Project | Requirement | Task | AgentAssignment | Dependency | Artifact | Build | TestRun | Approval | Retry | Checkpoint | Release | DevelopmentStudioEvent;
const collections: readonly CollectionName[] = ["projects", "requirements", "tasks", "agentAssignments", "dependencies", "artifacts", "builds", "testRuns", "approvals", "retries", "checkpoints", "releases", "events"];

export interface DevelopmentStudioRepository { save<T extends Entity>(collection: CollectionName, entity: T): T; get<T extends Entity>(collection: CollectionName, id: string): T | undefined; list<T extends Entity>(collection: CollectionName, projectId?: string): T[]; }

export class FileDevelopmentStudioRepository implements DevelopmentStudioRepository {
  private data: DevelopmentStudioData;
  constructor(private readonly filePath: string) { this.data = this.load(); }
  save<T extends Entity>(collection: CollectionName, entity: T): T { validateEntity(collection, entity, this.data); const items = this.data[collection] as Entity[]; if (items.some(item => item.id === entity.id)) throw new Error(`Duplicate ${collection} identity: ${entity.id}`); items.push(structuredClone(entity)); this.persist(); return structuredClone(entity); }
  get<T extends Entity>(collection: CollectionName, id: string): T | undefined { const value = (this.data[collection] as Entity[]).find(item => item.id === id); return value && structuredClone(value) as T; }
  list<T extends Entity>(collection: CollectionName, projectId?: string): T[] { return (this.data[collection] as Entity[]).filter(item => !projectId || ("projectId" in item && item.projectId === projectId)).map(item => structuredClone(item) as T); }
  private load(): DevelopmentStudioData { if (!existsSync(this.filePath)) return emptyDevelopmentStudioData(); const parsed: unknown = JSON.parse(readFileSync(this.filePath, "utf8")); validateSchema(parsed); return parsed as DevelopmentStudioData; }
  private persist(): void { mkdirSync(dirname(this.filePath), { recursive: true }); const temporary = `${this.filePath}.tmp`; writeFileSync(temporary, `${JSON.stringify(this.data, null, 2)}\n`, "utf8"); renameSync(temporary, this.filePath); }
}

function validateSchema(value: unknown): asserts value is DevelopmentStudioData { if (!value || typeof value !== "object" || (value as { schemaVersion?: unknown }).schemaVersion !== 1) throw new Error("Unsupported Development Studio persistence schema"); for (const name of collections) if (!Array.isArray((value as Record<string, unknown>)[name])) throw new Error(`Invalid persistence collection: ${name}`); }
function requireText(value: unknown, label: string): asserts value is string { if (typeof value !== "string" || !value.trim()) throw new Error(`${label} is required`); }
function validateEntity(collection: CollectionName, entity: Entity, data: DevelopmentStudioData): void {
  requireText(entity.id, "id"); requireText(entity.createdAt, "createdAt"); if (!entity.sourceReferences.length) throw new Error("sourceReferences is required");
  if (collection === "projects" && !projectStates.includes((entity as Project).status)) throw new Error("Invalid project state");
  if (collection === "tasks" && !taskStates.includes((entity as Task).state)) throw new Error("Invalid task state");
  if (collection !== "projects") { const projectId = (entity as { projectId?: unknown }).projectId; requireText(projectId, "projectId"); if (!data.projects.some(p => p.id === projectId)) throw new Error(`Invalid project reference: ${projectId}`); }
  if (collection === "agentAssignments" && !data.tasks.some(t => t.id === (entity as AgentAssignment).taskId)) throw new Error("Invalid task reference for assignment");
  if (collection === "retries" && !data.tasks.some(t => t.id === (entity as Retry).taskId && t.projectId === (entity as Retry).projectId)) throw new Error("Invalid task reference for retry");
  if (collection === "checkpoints") { const item = entity as Checkpoint; if (item.taskId && !data.tasks.some(t => t.id === item.taskId && t.projectId === item.projectId)) throw new Error("Invalid task reference for checkpoint"); }
  if (collection === "builds") { const item = entity as Build; if (item.artifactId && !data.artifacts.some(a => a.id === item.artifactId && a.projectId === item.projectId)) throw new Error("Invalid build artifact reference"); }
  if (collection === "testRuns") { const item = entity as TestRun; if (item.buildId && !data.builds.some(b => b.id === item.buildId && b.projectId === item.projectId)) throw new Error("Invalid test build reference"); if (item.artifactId && !data.artifacts.some(a => a.id === item.artifactId && a.projectId === item.projectId)) throw new Error("Invalid test artifact reference"); }
  if (collection === "artifacts") { const item = entity as Artifact; if (item.parentArtifactId && !data.artifacts.some(a => a.id === item.parentArtifactId && a.projectId === item.projectId)) throw new Error("Invalid parent artifact reference"); if (data.artifacts.some(a => a.projectId === item.projectId && a.type === item.type && a.version === item.version)) throw new Error("Duplicate artifact type/version"); }
  if (collection === "dependencies") validateDependency(entity as Dependency, data);
  if (collection === "releases") { const item = entity as Release; const artifact = data.artifacts.find(a => a.id === item.artifactId && a.projectId === item.projectId); if (!artifact || artifact.version !== item.artifactVersion) throw new Error("Invalid release artifact/version reference"); if (item.approvalId && !data.approvals.some(a => a.id === item.approvalId && a.projectId === item.projectId)) throw new Error("Invalid release approval reference"); }
  if (collection === "events") { const event = entity as DevelopmentStudioEvent; requireText(event.newState, "newState"); requireText(event.actor, "actor"); requireText(event.reason, "reason"); if (event.taskId && !data.tasks.some(t => t.id === event.taskId && t.projectId === event.projectId)) throw new Error("Invalid event task reference"); }
  if (collection === "approvals") { const approval = entity as Approval; if (!approval.requested && approval.required) throw new Error("Required approval must be requested"); if (approval.decision !== "PENDING" && (!approval.actor || !approval.reason || !approval.decidedAt)) throw new Error("Decided approval requires actor, reason, and decidedAt"); }
}
function validateDependency(dependency: Dependency, data: DevelopmentStudioData): void { if (dependency.fromId === dependency.toId) throw new Error("Dependency cannot reference itself"); const hasTask = (id: string) => data.tasks.some(t => t.id === id && t.projectId === dependency.projectId); const hasArtifact = (id: string) => data.artifacts.some(a => a.id === id && a.projectId === dependency.projectId); const valid = dependency.kind === "TASK_TO_TASK" ? hasTask(dependency.fromId) && hasTask(dependency.toId) : dependency.kind === "ARTIFACT_TO_TASK" ? hasArtifact(dependency.fromId) && hasTask(dependency.toId) : hasTask(dependency.fromId) && hasArtifact(dependency.toId); if (!valid) throw new Error(`Invalid dependency references for ${dependency.kind}`); }
