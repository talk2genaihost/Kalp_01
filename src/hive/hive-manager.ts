import { TaskLedger } from "./task-ledger.js";
export class HiveManager {
 readonly tasks=new TaskLedger();
 createTask(title:string,assignedTo?:string){const t={id:crypto.randomUUID(),title,status:"PENDING" as const,assignedTo};this.tasks.add(t);return t;}
}
