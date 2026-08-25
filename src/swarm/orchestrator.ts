import type { CognitiveState } from "../shared/types.js";
import type { CognitiveStage } from "./stage.js";
import { EventStore } from "../audit/event-store.js";
export class SwarmOrchestrator {
 constructor(private stages:CognitiveStage[],private events:EventStore){}
 async run(state:CognitiveState){
  let current=state;
  for(const stage of this.stages){
   current=await stage.execute(current);
   this.events.append({id:crypto.randomUUID(),type:"STAGE_COMPLETED",stage:stage.name,authority:"ACTIVE",
    payload:{requestId:state.request.id},createdAt:new Date().toISOString()});
  }
  return current;
 }
}
