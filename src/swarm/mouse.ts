import type { CognitiveState } from "../shared/types.js";
import type { CognitiveStage } from "./stage.js";
export class Mouse implements CognitiveStage {
  readonly name="MOUSE" as const;
  async execute(state:CognitiveState):Promise<CognitiveState> {
    return {...state,context:[...state.context,"state-navigated"]};
  }
}
