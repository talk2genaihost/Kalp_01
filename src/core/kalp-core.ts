import type { KalpRequest,CognitiveState } from "../shared/types.js";
import { SwarmOrchestrator } from "../swarm/orchestrator.js";
import { HiveManager } from "../hive/hive-manager.js";
export class KalpCore {
 constructor(private swarm:SwarmOrchestrator,private hive:HiveManager){}
 async handle(request:KalpRequest):Promise<CognitiveState>{
  const state:CognitiveState={request,context:[],evidence:[],plan:[],personas:[],tasks:[],executionGraph:[]};
  const result=await this.swarm.run(state);
  this.hive.createTask(`Execute: ${request.input}`,result.personas[0]);
  return {...result,outcome:"KALP kernel pipeline completed"};
 }
}
