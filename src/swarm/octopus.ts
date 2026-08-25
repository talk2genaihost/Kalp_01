import type { CognitiveState } from "../shared/types.js";
import type { CognitiveStage } from "./stage.js";
export class Octopus implements CognitiveStage {
  readonly name="OCTOPUS" as const;
  async execute(state:CognitiveState):Promise<CognitiveState> {
    return {...state,tasks:[...state.tasks,"task-delegated"]};
  }
}
