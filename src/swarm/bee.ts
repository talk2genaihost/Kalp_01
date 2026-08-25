import type { CognitiveState } from "../shared/types.js";
import type { CognitiveStage } from "./stage.js";
export class Bee implements CognitiveStage {
  readonly name="BEE" as const;
  async execute(state:CognitiveState):Promise<CognitiveState> {
    return {...state,personas:[...state.personas,"default-specialist-selected"]};
  }
}
