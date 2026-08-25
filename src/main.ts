import { EventStore } from "./audit/event-store.js";
import { Fly } from "./swarm/fly.js"; import { Mouse } from "./swarm/mouse.js"; import { Crow } from "./swarm/crow.js";
import { Bee } from "./swarm/bee.js"; import { Octopus } from "./swarm/octopus.js"; import { Ant } from "./swarm/ant.js";
import { SwarmOrchestrator } from "./swarm/orchestrator.js"; import { HiveManager } from "./hive/hive-manager.js"; import { KalpCore } from "./core/kalp-core.js";
const events=new EventStore();
const swarm=new SwarmOrchestrator([new Fly(),new Mouse(),new Crow(),new Bee(),new Octopus(),new Ant()],events);
const kalp=new KalpCore(swarm,new HiveManager());
const result=await kalp.handle({id:crypto.randomUUID(),input:"Initialize full KALP architecture repository"});
console.log(JSON.stringify({result,audit:events.all()},null,2));
