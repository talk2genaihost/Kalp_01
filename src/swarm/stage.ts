import type { CognitiveState,StageName } from "../shared/types.js";
export interface CognitiveStage { readonly name:StageName; execute(state:CognitiveState):Promise<CognitiveState>; }
