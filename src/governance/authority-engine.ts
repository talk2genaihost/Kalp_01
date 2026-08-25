import type { AuthorityLevel } from "../shared/types.js";
const order: AuthorityLevel[]=["LOCKED","APPROVED","CANONICAL","ACTIVE","VERSIONED","SUPPORTING","CHAT_MEMORY","INFERENCE"];
export const outranks=(a:AuthorityLevel,b:AuthorityLevel)=>order.indexOf(a)<order.indexOf(b);
export const resolveHighest=(levels:AuthorityLevel[])=>levels.slice().sort((a,b)=>order.indexOf(a)-order.indexOf(b))[0];
