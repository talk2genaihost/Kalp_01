import type { CognitiveState } from "../shared/types.js";
import type { CognitiveStage } from "./stage.js";
export class Fly implements CognitiveStage {
  readonly name="FLY" as const;
  async execute(state:CognitiveState):Promise<CognitiveState> {
    return {...state,context:[...state.context,"relevance-activated"]};
  }
}
