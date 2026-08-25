export type AuthorityLevel = "LOCKED"|"APPROVED"|"CANONICAL"|"ACTIVE"|"VERSIONED"|"SUPPORTING"|"CHAT_MEMORY"|"INFERENCE";
export type StageName = "FLY"|"MOUSE"|"CROW"|"BEE"|"OCTOPUS"|"ANT";

export interface KalpRequest { id:string; input:string; context?:Record<string,unknown>; }
export interface CognitiveState {
  request: KalpRequest;
  context: string[];
  evidence: string[];
  plan: string[];
  personas: string[];
  tasks: string[];
  executionGraph: string[];
  outcome?: string;
}
export interface KalpEvent {
  id:string; type:string; stage?:StageName; authority:AuthorityLevel;
  payload:Record<string,unknown>; createdAt:string;
}
