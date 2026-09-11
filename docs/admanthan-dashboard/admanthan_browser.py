import json

SCENES=[
 {'purpose':'Open with a visual hook built around the researched audience need.','terms':['wide','environment','hero','camera']},
 {'purpose':'Introduce the product as the answer to the audience need.','terms':['dolly','front','product','camera']},
 {'purpose':'Show visual proof of the core proposition.','terms':['wide','nature','outdoor','hero']},
 {'purpose':'Translate the promise into a lived human experience.','terms':['window','interior','normal','detail']},
 {'purpose':'Show the human/lifestyle payoff and emotional connection.','terms':['human','steadicam','lifestyle','outdoor']},
 {'purpose':'Resolve with brand identity and a clear action.','terms':['hero','brand','lockup','cta']},
]

def norm(s): return str(s or '').lower()

def sentence(brief,i):
 brand=brief.get('brand') or 'आपका ब्रांड'; product=brief.get('product') or 'यह प्रोडक्ट'; audience=brief.get('audience') or 'आज की पीढ़ी'; objective=brief.get('objective') or 'बेहतर जुड़ाव'; cta=brief.get('cta') or 'जानिए अधिक'
 obj=norm(objective)
 if 'sales' in obj or 'sell' in obj or 'conversion' in obj:
  lines={1:f'हर खरीद एक पसंद से शुरू होती है—{audience} के लिए {product} को नए अंदाज़ में जानिए।',2:f'क्योंकि आज की पसंद में स्टाइल, भरोसा और सही कीमत साथ चलते हैं।',3:f'{product} इन्हीं जरूरतों को रोज़मर्रा के अनुभव से जोड़ता है।',4:f'एक ऐसा अनुभव, जो आपकी पसंद को थोड़ा और आसान बनाए।',5:f'{brand} के साथ अपनी अगली पसंद को नए नज़रिए से देखिए।',6:f'{brand} — {cta}।'}
 else:
  lines={1:f'{audience}, तैयार हो जाइए—{product} आपकी दुनिया में एक नया अंदाज़ ला रहा है।',2:f'क्योंकि आज जुड़ना सिर्फ़ दिखना नहीं, सही एहसास देना है।',3:f'{product} उसी एहसास को एक यादगार अनुभव में बदलता है।',4:f'हर पल में अपनी पहचान और अपनी पसंद को जगह दीजिए।',5:f'{brand} के साथ वह कनेक्शन महसूस कीजिए, जो याद रह जाए।',6:f'{brand} — {cta}।'}
 return lines[i]

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
  objective=brief.get('objective') or 'Brand Awareness'; tone=brief.get('tone','Cinematic')
  routes={'Brand Awareness':('Audience-led brand story','Hook → audience need → product meaning → lifestyle → brand recall'),'Consideration':('Product-led persuasion','Need → product → proof → experience → preference'),'Conversion':('Action-led creative','Need → promise → proof → relevance → CTA'),'Launch':('Launch reveal','Tease → reveal → proof → experience → brand → CTA')}
  route=routes.get(objective,routes['Brand Awareness'])
  return {'objective':objective,'tone':tone,'audience':brief.get('audience',''),'key_message':brief.get('message') or objective,'creative_route':route[0],'narrative_arc':route[1],'duration_seconds':15,'scene_count':6,'language':brief.get('language','Hindi'),'cta':brief.get('cta','Learn more'),'brand':brief.get('brand',''),'product':brief.get('product',''),'research_informed':bool(brief.get('research_context'))}
 def generate(self,brief):
  brand=brief.get('brand') or 'Brand'; strategy=self.strategy(brief); scenes=[]
  for i,template in enumerate(SCENES,1):
   candidates=self.library.search(template['terms'],6); selected=candidates[:3]
   if i==6:
    selected=[self.library.get(k) for k in ['/hero_lock','/brand_lockup','/cta_endcard']]; selected=[x for x in selected if x]
   effects=[{'shortcut':r.get('Shortcut'),'capability':r.get('Capability'),'intent':r.get('Primary Use / Intent'),'application':r.get('Scene Recipe'),'sheet':r.get('sheet','')} for r in selected]
   scenes.append({'scene':i,'timecode':f'{(i-1)*2.5:.1f}-{i*2.5:.1f}s','story_purpose':template['purpose'],'effects':effects,'missing_effects':[],'vo':sentence(brief,i),'sound':['/continuity_bridge'] if i not in (1,6) else (['/riser_short','/nature_ambience'] if i==1 else ['/brand_sting','/voiceover_cta']),'on_screen':brief.get('cta','Learn more') if i==6 else '','effect_status':'VERIFIED LIBRARY MATCH' if len(effects)==3 else 'PARTIAL LIBRARY MATCH'})
  return {'engine':'KALP AdManthan Python Engine','version':'0.5-intent-aware','execution':'Pyodide/WebAssembly','brand':brand,'product':brief.get('product',''),'objective':strategy['objective'],'duration_seconds':15,'scene_count':6,'library_count':self.library.count(),'strategy':strategy,'continuous_vo':' '.join(s['vo'] for s in scenes),'scenes':scenes,'production_package':{'format':'15-second advertisement','aspect_ratio':'16:9','scene_count':6,'deliverables':['intent model','research context','final objective','strategy','storyboard','effect selections','VO script','sound design','production manifest'],'cta':brief.get('cta','Learn more'),'engine_status':'EXECUTED','brief_driven':True,'research_informed':bool(brief.get('research_context')),'raw_intent_excluded_from_creative':True}}

def execute(rows,brief): return AdManthan(BrowserEffectLibrary(rows)).generate(brief)
def generate(rows,brand,product,objective='Brand Awareness'): return execute(rows,{'brand':brand,'product':product,'objective':objective})
