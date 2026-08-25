import type { KalpEvent } from "../shared/types.js";
export class EventStore {
  private events: KalpEvent[]=[];
  append(e:KalpEvent){this.events.push(e);}
  all(){return [...this.events];}
}
