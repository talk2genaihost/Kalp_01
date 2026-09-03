import type { AuthorityLevel } from "../shared/types.js";
import type { ProjectState, TaskState } from "./state.js";

export type DeploymentMode = "OFFLINE" | "ONLINE" | "HYBRID";
export type RecordStatus = "PROPOSED" | "DERIVED" | "ACTIVE" | "VERSIONED" | "SUPPORTING" | "UNRESOLVED" | "UNAVAILABLE";
export type RequirementStatus = "DRAFT" | "PENDING_APPROVAL" | "APPROVED" | "REJECTED" | "BLOCKED";
export type ArtifactType = "REQUIREMENTS" | "ARCHITECTURE" | "UX_SPEC" | "UI_SPEC" | "SOURCE_CODE" | "CONFIGURATION" | "DATABASE_SCHEMA" | "API_SPEC" | "TEST_PLAN" | "TEST_RESULT" | "BUILD_LOG" | "BUILD_ARTIFACT" | "SECURITY_REPORT" | "PERFORMANCE_REPORT" | "RELEASE_PACKAGE" | "RELEASE_NOTES" | "TRACE_RECORD";
export type BuildState = "PENDING" | "RUNNING" | "SUCCEEDED" | "FAILED" | "BLOCKED" | "UNAVAILABLE";
export type TestType = "UNIT" | "INTEGRATION" | "CONTRACT" | "SYSTEM" | "SECURITY" | "PERFORMANCE";
export type TestState = "PENDING" | "RUNNING" | "PASSED" | "FAILED" | "BLOCKED" | "UNAVAILABLE";
export type ApprovalDecision = "PENDING" | "APPROVED" | "REJECTED";
export type DependencyKind = "TASK_TO_TASK" | "ARTIFACT_TO_TASK" | "TASK_TO_ARTIFACT";

export interface Provenanced { sourceReferences: string[]; authority: AuthorityLevel; createdAt: string; }
export interface Project extends Provenanced { id: string; userIntent: string; status: ProjectState; platform: string; deploymentMode: DeploymentMode; executionMetadata: Record<string, unknown>; traceReferences: string[]; }
export interface Requirement extends Provenanced { id: string; projectId: string; description: string; source: string; status: RequirementStatus; priority?: string; dependencyIds: string[]; approvalId?: string; traceReferences: string[]; }
export interface Task extends Provenanced { id: string; projectId: string; capabilityReference: string; assignmentId?: string; state: TaskState; inputs: Record<string, unknown>; outputs: Record<string, unknown>; failureInformation?: string; retryIds: string[]; }
export interface AgentAssignment extends Provenanced { id: string; projectId: string; taskId: string; agentReference: string; status: RecordStatus; }
export interface Dependency extends Provenanced { id: string; projectId: string; kind: DependencyKind; fromId: string; toId: string; status: RecordStatus; }
export interface Artifact extends Provenanced { id: string; projectId: string; type: ArtifactType; version: string; createdBy: string; parentArtifactId?: string; status: RecordStatus; integrityHash?: string; validationStatus: RecordStatus; }
export interface Build extends Provenanced { id: string; projectId: string; artifactId?: string; state: BuildState; version: string; }
export interface TestRun extends Provenanced { id: string; projectId: string; buildId?: string; artifactId?: string; type: TestType; state: TestState; }
export interface Approval extends Provenanced { id: string; projectId: string; approvalType: string; requested: boolean; required: boolean; decision: ApprovalDecision; actor?: string; reason?: string; decidedAt?: string; }
export interface Retry extends Provenanced { id: string; projectId: string; taskId: string; attempt: number; reason: string; status: RecordStatus; }
export interface Checkpoint extends Provenanced { id: string; projectId: string; taskId?: string; state: string; status: RecordStatus; }
export interface Release extends Provenanced { id: string; projectId: string; artifactId: string; artifactVersion: string; validationStatus: RecordStatus; approvalId?: string; status: RecordStatus; }
export interface DevelopmentStudioEvent extends Provenanced { id: string; projectId: string; taskId?: string; previousState?: string; newState: string; actor: string; reason: string; inputs: Record<string, unknown>; outputs: Record<string, unknown>; }

export interface DevelopmentStudioData { schemaVersion: 1; projects: Project[]; requirements: Requirement[]; tasks: Task[]; agentAssignments: AgentAssignment[]; dependencies: Dependency[]; artifacts: Artifact[]; builds: Build[]; testRuns: TestRun[]; approvals: Approval[]; retries: Retry[]; checkpoints: Checkpoint[]; releases: Release[]; events: DevelopmentStudioEvent[]; }
export const emptyDevelopmentStudioData = (): DevelopmentStudioData => ({ schemaVersion: 1, projects: [], requirements: [], tasks: [], agentAssignments: [], dependencies: [], artifacts: [], builds: [], testRuns: [], approvals: [], retries: [], checkpoints: [], releases: [], events: [] });
