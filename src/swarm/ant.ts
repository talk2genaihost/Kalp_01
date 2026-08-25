import type { CognitiveState } from "../shared/types.js";
import type { CognitiveStage } from "./stage.js";
export class Ant implements CognitiveStage {
  readonly name="ANT" as const;
  async execute(state:CognitiveState):Promise<CognitiveState> {
    return {...state,executionGraph:[...state.executionGraph,"parallel-execution-ready"]};
  }
}
