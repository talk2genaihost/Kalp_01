import type { CognitiveState } from "../shared/types.js";
import type { CognitiveStage } from "./stage.js";
export class Crow implements CognitiveStage {
  readonly name="CROW" as const;
  async execute(state:CognitiveState):Promise<CognitiveState> {
    return {...state,plan:[...state.plan,"plan-created"]};
  }
}
