import json
import re

SCENES=[
 {'purpose':'Open with a visual hook built around the researched audience need.','terms':['wide','environment','hero','camera']},
 {'purpose':'Introduce the product as the answer to the audience need.','terms':['dolly','front','product','camera']},
 {'purpose':'Show visual proof of the core proposition.','terms':['wide','nature','outdoor','hero']},
 {'purpose':'Translate the promise into a lived human experience.','terms':['window','interior','normal','detail']},
 {'purpose':'Show the human/lifestyle payoff and emotional connection.','terms':['human','steadicam','lifestyle','outdoor']},
 {'purpose':'Resolve with brand identity and a clear action.','terms':['hero','brand','lockup','cta']},
]

# Conservative factual-claim lexicon. These terms trigger review when they
# introduce product properties that are not explicitly grounded in the brief
# or a research evidence pack. Creative/emotional language is not blocked.
CLAIM_TERMS={
 'feature':['thermal','tip','retractable','refillable','waterproof','washable','smudge-proof','smudge proof','quick-dry','quick dry','fast-drying','fast drying','non-toxic','non toxic','durable','leak-proof','leak proof','shavings','residue','cartridge','eraser mechanism'],
 'performance':['lasts','long-lasting','long lasting','writes smoothly','smooth writing','dries instantly','instant drying','erases completely','erases cleanly','without tearing','without shavings','zero residue','no residue','trace-free','without a trace'],
 'comparative':['best','number one','#1','most','better than','faster than','more durable','guaranteed']
}

def norm(s): return str(s or '').lower()

def fallback_lines(brief):
 brand=brief.get('brand') or 'आपका ब्रांड'; product=brief.get('product') or 'यह प्रोडक्ट'; audience=brief.get('audience') or 'आज की पीढ़ी'; cta=brief.get('cta') or 'जानिए अधिक'
 return [f'{audience}, अपनी रोज़मर्रा की दुनिया में एक ऐसी पसंद पर ध्यान दीजिए जो अलग महसूस हो।',f'{product} सिर्फ़ एक नाम नहीं—यह उस अनुभव को बेहतर बनाने का एक तरीका है।',f'जब सही चीज़ आपकी ज़रूरत और आपकी शैली, दोनों से जुड़ जाए, तो बात याद रहती है।',f'हर दिन के छोटे पलों में वही जुड़ाव धीरे-धीरे भरोसे में बदलता है।',f'{brand} इसी पहचान को आपके लिए और प्रासंगिक बनाने की कोशिश करता है।',f'{brand} — {cta}।']

def ai_scene_data(brief):
 ai=brief.get('ai_direction') or {}; scenes=ai.get('scenes')
 if not isinstance(scenes,list) or len(scenes)!=6: return None
 out=[]
 for idx,s in enumerate(scenes,1):
  if not isinstance(s,dict): return None
  vo=str(s.get('vo') or '').strip(); purpose=str(s.get('story_purpose') or s.get('purpose') or '').strip()
  if not vo or not purpose: return None
  out.append({'vo':vo,'story_purpose':purpose,'visual_direction':str(s.get('visual_direction') or '').strip(),'sound_direction':str(s.get('sound_direction') or '').strip(),'on_screen':str(s.get('on_screen') or '').strip()})
 return out

def _grounding_text(brief):
 i=brief.get('intent_model') or {}
 facts=i.get('user_stated_facts') or {}
 ctx=brief.get('research_context') or {}
 verified=ctx.get('verified_facts') or []
 return norm(json.dumps({'intent_facts':facts,'product':i.get('product'),'category':i.get('category'),'verified_facts':verified},ensure_ascii=False))

def claim_guard(brief, ai_scenes):
 """Deterministic post-generation gate for unsupported factual product claims.

    The guard is intentionally conservative: it does not claim that research
    exists merely because research was attempted. It only treats explicit
    user-stated facts and non-empty verified_facts as factual evidence.
    """
 grounding=_grounding_text(brief)
 violations=[]
 for idx,s in enumerate(ai_scenes or [],1):
  text=' '.join([s.get('vo',''),s.get('visual_direction',''),s.get('on_screen','')])
  low=norm(text)
  for kind,terms in CLAIM_TERMS.items():
   for term in terms:
    if term in low and term not in grounding:
     violations.append({'scene':idx,'type':kind,'term':term,'text':text[:500],'reason':'Product claim/property is not grounded in explicit user facts or verified research evidence.'})
 # Duplicate violations by scene/term only.
 unique=[]; seen=set()
 for v in violations:
  key=(v['scene'],v['type'],v['term'])
  if key not in seen: seen.add(key); unique.append(v)
 return {'status':'PASS' if not unique else 'BLOCKED','evidence_policy':'USER_STATED_FACTS + VERIFIED_FACTS_ONLY','violation_count':len(unique),'violations':unique}

class BrowserEffectLibrary:
 def __init__(self,rows): self.rows=rows or []; self.by_shortcut={r.get('Shortcut'):r for r in self.rows if r.get('Shortcut')}
 def get(self,shortcut): return self.by_shortcut.get(shortcut)
 def count(self): return len(self.rows)
 def search(self,terms,limit=6):
  terms=[norm(x) for x in terms]; scored=[]
  for r in self.rows:
   text=' '.join(norm(r.get(k,'')) for k in ['Shortcut','Capability','Primary Use / Intent','Scene Recipe','Visual / Execution Notes','Ad Role'])
   score=sum(2 if term in norm(r.get('Shortcut','')) else 1 for term in terms if term in text)
   if score: scored.append((score,r))
  scored.sort(key=lambda x:(-x[0],x[1].get('Shortcut',''))); return [r for _,r in scored[:limit]]

class AdManthan:
 def __init__(self,library): self.library=library
 def strategy(self,brief):
  objective=brief.get('objective') or 'Brand Awareness'; tone=brief.get('tone','Cinematic'); ai=brief.get('ai_direction') or {}
  return {'objective':objective,'tone':tone,'audience':brief.get('audience',''),'key_message':ai.get('key_message') or brief.get('message') or objective,'creative_route':ai.get('creative_route') or 'Audience-led brand story','narrative_arc':ai.get('narrative_arc') or 'Hook → need → product meaning → experience → brand recall → CTA','duration_seconds':15,'scene_count':6,'language':brief.get('language','Hindi'),'cta':brief.get('cta','Learn more'),'brand':brief.get('brand',''),'product':brief.get('product',''),'research_informed':bool(brief.get('research_context')),'ai_composed':bool(ai.get('scenes'))}
 def generate(self,brief):
  brand=brief.get('brand') or 'Brand'; strategy=self.strategy(brief); ai_scenes=ai_scene_data(brief); fallback=fallback_lines(brief); guard=claim_guard(brief,ai_scenes or []); scenes=[]
  # A blocked claim set does not silently pass through as verified. The
  # package carries the gate result so the UI/release layer can stop release.
  for i,template in enumerate(SCENES,1):
   candidates=self.library.search(template['terms'],6); selected=candidates[:3]
   if i==6:
    selected=[self.library.get(k) for k in ['/hero_lock','/brand_lockup','/cta_endcard']]; selected=[x for x in selected if x]
   effects=[{'shortcut':r.get('Shortcut'),'capability':r.get('Capability'),'intent':r.get('Primary Use / Intent'),'application':r.get('Scene Recipe'),'sheet':r.get('sheet','')} for r in selected]
   ai=ai_scenes[i-1] if ai_scenes else {'vo':fallback[i-1],'story_purpose':template['purpose'],'visual_direction':'','sound_direction':'','on_screen':brief.get('cta','Learn more') if i==6 else ''}
   scenes.append({'scene':i,'timecode':f'{(i-1)*2.5:.1f}-{i*2.5:.1f}s','story_purpose':ai['story_purpose'],'visual_direction':ai['visual_direction'],'effects':effects,'missing_effects':[],'vo':ai['vo'],'sound_direction':ai['sound_direction'],'sound':['/continuity_bridge'] if i not in (1,6) else (['/riser_short','/nature_ambience'] if i==1 else ['/brand_sting','/voiceover_cta']),'on_screen':ai['on_screen'],'effect_status':'VERIFIED LIBRARY MATCH' if len(effects)==3 else 'PARTIAL LIBRARY MATCH','claim_guard_status':'BLOCKED' if guard['status']=='BLOCKED' else 'PASS'})
  continuous=' '.join(x['vo'] for x in scenes)
  release_status='HOLD_FOR_CLAIM_REVIEW' if guard['status']=='BLOCKED' else 'RELEASE_ELIGIBLE'
  return {'engine':'KALP AdManthan Python Engine','version':'0.8-claim-evidence-guard','execution':'Pyodide/WebAssembly','brand':brand,'product':brief.get('product',''),'objective':strategy['objective'],'duration_seconds':15,'scene_count':6,'library_count':self.library.count(),'strategy':strategy,'continuous_vo':continuous,'script_mode':'AI-composed six-beat continuous VO with deterministic fallback','claim_guard':guard,'release_status':release_status,'scenes':scenes,'production_package':{'format':'15-second advertisement','aspect_ratio':'16:9','scene_count':6,'deliverables':['AI intent model','research context','claim and evidence guard','final objective','strategy','AI six-beat continuous VO','storyboard','verified effect selections','sound design','production manifest'],'cta':brief.get('cta','Learn more'),'engine_status':'EXECUTED','brief_driven':True,'research_informed':bool(brief.get('research_context')),'ai_composed':bool(ai_scenes),'raw_intent_excluded_from_creative':True}}

def execute(rows,brief): return AdManthan(BrowserEffectLibrary(rows)).generate(brief)
def generate(rows,brand,product,objective='Brand Awareness'): return execute(rows,{'brand':brand,'product':product,'objective':objective})
