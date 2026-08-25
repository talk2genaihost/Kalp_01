export interface Persona { id:string; name:string; role:string; capabilities:string[]; authorityScope:string[]; }
export class PersonaRegistry {
 private personas=new Map<string,Persona>();
 register(p:Persona){this.personas.set(p.id,p);}
 select(capability:string){return [...this.personas.values()].filter(p=>p.capabilities.includes(capability));}
}
