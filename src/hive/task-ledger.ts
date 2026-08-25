export interface Task { id:string; title:string; status:"PENDING"|"RUNNING"|"DONE"|"FAILED"; assignedTo?:string; }
export class TaskLedger { private tasks=new Map<string,Task>(); add(t:Task){this.tasks.set(t.id,t);} list(){return [...this.tasks.values()];} }
