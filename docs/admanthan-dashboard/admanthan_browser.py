import json

SCENES=[
 {'purpose':'Hook the audience with the product promise and visual world.','terms':['wide','environment','hero','camera'],'vo':'सोचिए… एक ऐसी जगह, जहाँ आपकी कहानी की शुरुआत ही बेहतर हो।'},
 {'purpose':'Introduce the product as the answer to the audience need.','terms':['dolly','front','product','camera'],'vo':'जहाँ आपका चुनाव सिर्फ़ एक जगह नहीं, एक बेहतर एहसास बने।'},
 {'purpose':'Provide visual proof of the core proposition.','terms':['wide','nature','outdoor','hero'],'vo':'खुली जगह, बेहतर माहौल और हर दिन के लिए नई ऊर्जा।'},
 {'purpose':'Translate the promise into a lived human experience.','terms':['window','interior','normal','detail'],'vo':'हर पल में आराम, हर नज़र में अपनापन महसूस हो।'},
 {'purpose':'Show the human/lifestyle payoff and emotional connection.','terms':['human','steadicam','lifestyle','outdoor'],'vo':'क्योंकि सही जगह सिर्फ़ दिखती नहीं… ज़िंदगी में महसूस होती है।'},
 {'purpose':'Resolve with brand identity, proof point and clear action.','terms':['hero','brand','lockup','cta'],'vo':'अब अपनी अगली कहानी का सही पता चुनिए।'},
]

def norm(s): return str(s or '').lower()

class BrowserEffectLibrary:
 def __init__(self,rows):
  self.rows=rows or []
  self.by_shortcut={r.get('Shortcut'):r for r in self.rows if r.get('Shortcut')}
 def get(self,shortcut): return self.by_shortcut.get(shortcut)
 def count(self): return len(self.rows)
 def search(self,terms,limit=6):
  terms=[norm(x) for x in terms]
  scored=[]
  for r in self.rows:
   text=' '.join(norm(r.get(k,'')) for k in ['Shortcut','Capability','Primary Use / Intent','Scene Recipe','Visual / Execution Notes','Ad Role'])
   score=sum(2 if term in norm(r.get('Shortcut','')) else 1 for term in terms if term in text)
   if score: scored.append((score,r))
  scored.sort(key=lambda x:(-x[0],x[1].get('Shortcut','')))
  return [r for _,r in scored[:limit]]

class AdManthan:
 def __init__(self,library): self.library=library
 def strategy(self,brief):
  objective=brief.get('objective','Brand Awareness')
  tone=brief.get('tone','Cinematic')
  audience=brief.get('audience','')
  message=brief.get('message','')
  routes={
   'Brand Awareness':('Emotional brand story','Hook → aspiration → proof → lifestyle → brand recall'),
   'Consideration':('Product-led persuasion','Need → product → proof → experience → preference'),
   'Conversion':('Action-led creative','Problem → promise → proof → urgency → CTA'),
   'Launch':('Launch reveal','Tease → reveal → proof → experience → brand → CTA')}
  route=routes.get(objective,routes['Brand Awareness'])
  return {'objective':objective,'tone':tone,'audience':audience,'key_message':message,'creative_route':route[0],'narrative_arc':route[1],'duration_seconds':15,'scene_count':6,'language':brief.get('language','Hindi'),'cta':brief.get('cta','Learn more')}
 def generate(self,brief):
  brand=brief.get('brand') or 'Brand'; product=brief.get('product') or 'Product'; strategy=self.strategy(brief)
  scenes=[]
  for i,template in enumerate(SCENES,1):
   candidates=self.library.search(template['terms'],6)
   selected=candidates[:3]
   if i==6:
    selected=[]
    for key in ['/hero_lock','/brand_lockup','/cta_endcard']:
     row=self.library.get(key)
     if row: selected.append(row)
   effects=[{'shortcut':r.get('Shortcut'),'capability':r.get('Capability'),'intent':r.get('Primary Use / Intent'),'application':r.get('Scene Recipe'),'sheet':r.get('sheet','')} for r in selected]
   scenes.append({'scene':i,'timecode':f'{(i-1)*2.5:.1f}-{i*2.5:.1f}s','story_purpose':template['purpose'],'effects':effects,'missing_effects':[],'vo':template['vo'],'sound':['/continuity_bridge'] if i not in (1,6) else (['/riser_short','/nature_ambience'] if i==1 else ['/brand_sting','/voiceover_cta']),'on_screen':brief.get('cta','Learn more') if i==6 else '','effect_status':'VERIFIED LIBRARY MATCH' if len(effects)==3 else 'PARTIAL LIBRARY MATCH'})
  continuous=' '.join(s['vo'] for s in scenes)
  return {'engine':'KALP AdManthan Python Engine','version':'0.3-browser-studio','execution':'Pyodide/WebAssembly','brand':brand,'product':product,'objective':strategy['objective'],'duration_seconds':15,'scene_count':6,'library_count':self.library.count(),'strategy':strategy,'continuous_vo':continuous,'scenes':scenes,'production_package':{'format':'15-second advertisement','aspect_ratio':'16:9','scene_count':6,'deliverables':['storyboard','effect selections','VO script','sound design','production manifest'],'cta':brief.get('cta','Learn more'),'engine_status':'EXECUTED'}}

def execute(rows,brief): return AdManthan(BrowserEffectLibrary(rows)).generate(brief)
def generate(rows,brand,product,objective='Brand Awareness'): return execute(rows,{'brand':brand,'product':product,'objective':objective})
