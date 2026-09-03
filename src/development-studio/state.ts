/**
 * Development Studio state only. These states intentionally do not represent
 * KALP orchestration state.
 */
export const projectStates = [
  "CREATED", "DISCOVERY", "REQUIREMENTS", "REQUIREMENTS_APPROVED", "ARCHITECTURE",
  "DESIGN", "IMPLEMENTATION_PLANNED", "IMPLEMENTING", "BUILDING", "TESTING",
  "VALIDATION", "RELEASE_READY", "DELIVERED", "BLOCKED", "AWAITING_CLARIFICATION",
  "FAILED", "UNRESOLVED", "UNAVAILABLE",
] as const;
export type ProjectState = (typeof projectStates)[number];

export const taskStates = ["PENDING", "READY", "ASSIGNED", "EXECUTING", "COMPLETED", "BLOCKED", "FAILED", "UNRESOLVED", "UNAVAILABLE"] as const;
export type TaskState = (typeof taskStates)[number];

const projectTransitions: Readonly<Record<ProjectState, readonly ProjectState[]>> = {
  CREATED: ["DISCOVERY", "BLOCKED", "AWAITING_CLARIFICATION", "FAILED", "UNRESOLVED", "UNAVAILABLE"],
  DISCOVERY: ["REQUIREMENTS", "BLOCKED", "AWAITING_CLARIFICATION", "FAILED", "UNRESOLVED", "UNAVAILABLE"],
  REQUIREMENTS: ["REQUIREMENTS_APPROVED", "BLOCKED", "AWAITING_CLARIFICATION", "FAILED", "UNRESOLVED", "UNAVAILABLE"],
  REQUIREMENTS_APPROVED: ["ARCHITECTURE", "BLOCKED", "FAILED", "UNRESOLVED", "UNAVAILABLE"],
  ARCHITECTURE: ["DESIGN", "BLOCKED", "FAILED", "UNRESOLVED", "UNAVAILABLE"], DESIGN: ["IMPLEMENTATION_PLANNED", "BLOCKED", "FAILED", "UNRESOLVED", "UNAVAILABLE"],
  IMPLEMENTATION_PLANNED: ["IMPLEMENTING", "BLOCKED", "FAILED", "UNRESOLVED", "UNAVAILABLE"], IMPLEMENTING: ["BUILDING", "BLOCKED", "FAILED", "UNRESOLVED", "UNAVAILABLE"],
  BUILDING: ["TESTING", "BLOCKED", "FAILED", "UNRESOLVED", "UNAVAILABLE"], TESTING: ["VALIDATION", "BLOCKED", "FAILED", "UNRESOLVED", "UNAVAILABLE"],
  VALIDATION: ["RELEASE_READY", "BLOCKED", "FAILED", "UNRESOLVED", "UNAVAILABLE"], RELEASE_READY: ["DELIVERED", "BLOCKED", "FAILED", "UNRESOLVED", "UNAVAILABLE"],
  DELIVERED: [], BLOCKED: ["DISCOVERY", "REQUIREMENTS", "ARCHITECTURE", "DESIGN", "IMPLEMENTATION_PLANNED", "IMPLEMENTING", "BUILDING", "TESTING", "VALIDATION", "RELEASE_READY", "FAILED", "UNRESOLVED", "UNAVAILABLE"],
  AWAITING_CLARIFICATION: ["DISCOVERY", "REQUIREMENTS", "BLOCKED", "FAILED", "UNRESOLVED", "UNAVAILABLE"], FAILED: [], UNRESOLVED: [], UNAVAILABLE: [],
};
const taskTransitions: Readonly<Record<TaskState, readonly TaskState[]>> = {
  PENDING: ["READY", "BLOCKED", "FAILED", "UNRESOLVED", "UNAVAILABLE"], READY: ["ASSIGNED", "BLOCKED", "FAILED", "UNRESOLVED", "UNAVAILABLE"],
  ASSIGNED: ["EXECUTING", "BLOCKED", "FAILED", "UNRESOLVED", "UNAVAILABLE"], EXECUTING: ["COMPLETED", "BLOCKED", "FAILED", "UNRESOLVED", "UNAVAILABLE"],
  COMPLETED: [], BLOCKED: ["READY", "ASSIGNED", "FAILED", "UNRESOLVED", "UNAVAILABLE"], FAILED: [], UNRESOLVED: [], UNAVAILABLE: [],
};

export const canTransitionProject = (from: ProjectState, to: ProjectState) => projectTransitions[from].includes(to);
export const canTransitionTask = (from: TaskState, to: TaskState) => taskTransitions[from].includes(to);
export function assertProjectTransition(from: ProjectState, to: ProjectState): void { if (!canTransitionProject(from, to)) throw new Error(`Invalid project transition: ${from} -> ${to}`); }
export function assertTaskTransition(from: TaskState, to: TaskState): void { if (!canTransitionTask(from, to)) throw new Error(`Invalid task transition: ${from} -> ${to}`); }
