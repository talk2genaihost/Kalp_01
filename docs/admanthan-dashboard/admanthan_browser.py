import json

VERSION = '0.8.3-evidence-safe'

SCENE_TERMS = [['wide','environment','hero','camera'],['dolly','front','product','camera'],['wide','nature','outdoor','hero'],['window','interior','normal','detail'],['human','steadicam','lifestyle','outdoor'],['hero','brand','lockup','cta']]
CLAIM_TERMS = ['thermal','tip','retractable','refillable','waterproof','washable','smudge-proof','quick-dry','fast-drying','non-toxic','durable','leak-proof','shavings','residue','cartridge','eraser mechanism','lasts','long-lasting','writes smoothly','smooth writing','dries instantly','instant drying','erases completely','erases cleanly','without tearing','without shavings','zero residue','no residue','trace-free','without a trace','best','number one','#1','better than','faster than','more durable','guaranteed']
SAFE_REPLACEMENTS = [('zero residue','the erased mark'),('no residue','the erased mark'),('without a trace','the erased mark'),('trace-free','the erased mark'),('erases completely','erases'),('erases cleanly','erases'),('cleanly','away'),('instantly','then'),('instant','simple'),('seamless','continuous'),('premium',''),('perfect',''),('smooth','')]

def norm(value): return str(value or '').lower()
def sanitize_text(value, grounding):
    text=str(value or '')
    low_ground=norm(grounding)
    for term,replacement in SAFE_REPLACEMENTS:
        if term in norm(text) and term not in low_ground: text=text.replace(term,replacement)
    return ' '.join(text.split())

def fallback(brief):
    brand=brief.get('brand') or 'आपका ब्रांड'; product=brief.get('product') or 'यह प्रोडक्ट'; audience=brief.get('audience') or 'आज की पीढ़ी'; cta=brief.get('cta') or 'जानिए अधिक'
    return [audience+', अपनी रोज़मर्रा की दुनिया में एक ऐसी पसंद पर ध्यान दीजिए जो अलग महसूस हो।',product+' उस अनुभव को बेहतर बनाने का एक तरीका है।','जब लिखते हुए कोई गलती हो, तो उसे मिटाकर आगे बढ़िए।','अपने विचारों को फिर से लिखते हुए कहानी को आगे ले जाइए।',brand+' आपके लिखने के अनुभव को आपके लिए प्रासंगिक बनाने की कोशिश करता है।',brand+' — '+cta+'।']

def claim_guard(brief,scenes):
    intent=brief.get('intent_model') or {}; facts=intent.get('user_stated_facts') or {}; research=brief.get('research_context') or {}; verified=research.get('verified_facts') or []
    grounding=norm(json.dumps({'facts':facts,'product':intent.get('product'),'category':intent.get('category'),'verified':verified},ensure_ascii=False)); violations=[]
    for index,scene in enumerate(scenes,1):
        low=norm(' '.join([str(scene.get('vo') or ''),str(scene.get('visual_direction') or ''),str(scene.get('on_screen') or '')]))
        for term in CLAIM_TERMS:
            if term in low and term not in grounding: violations.append({'scene':index,'term':term,'reason':'Unsupported product claim/property.'})
    return {'status':'PASS' if not violations else 'BLOCKED','evidence_policy':'USER_STATED_FACTS + VERIFIED_FACTS_ONLY','violation_count':len(violations),'violations':violations}

def choose_effects(rows,terms,limit=3):
    scored=[]
    for row in rows or []:
        text=' '.join([norm(row.get('Shortcut')),norm(row.get('Capability')),norm(row.get('Primary Use / Intent')),norm(row.get('Scene Recipe')),norm(row.get('Visual / Execution Notes')),norm(row.get('Ad Role'))])
        score=sum(1 for term in terms if norm(term) in text)
        if score: scored.append((score,row))
    scored.sort(key=lambda item:(-item[0],str(item[1].get('Shortcut') or '')))
    return [item[1] for item in scored[:limit]]

def execute(rows,brief):
    ai=brief.get('ai_direction') or {}; ai_scenes=ai.get('scenes') if isinstance(ai.get('scenes'),list) and len(ai.get('scenes'))==6 else None
    intent=brief.get('intent_model') or {}; facts=intent.get('user_stated_facts') or {}; research=brief.get('research_context') or {}; verified=research.get('verified_facts') or []
    grounding=json.dumps({'facts':facts,'product':intent.get('product'),'category':intent.get('category'),'verified':verified},ensure_ascii=False); fallback_lines=fallback(brief); working=[]
    for index in range(6):
        source=ai_scenes[index] if ai_scenes and isinstance(ai_scenes[index],dict) else {}
        working.append({'story_purpose':str(source.get('story_purpose') or source.get('purpose') or 'Develop the advertising story.'),'visual_direction':sanitize_text(source.get('visual_direction') or '',grounding),'vo':sanitize_text(source.get('vo') or fallback_lines[index],grounding),'sound_direction':str(source.get('sound_direction') or ''),'on_screen':sanitize_text(source.get('on_screen') or '',grounding)})
    guard=claim_guard(brief,working); output_scenes=[]
    for index in range(6):
        effects=choose_effects(rows,SCENE_TERMS[index],3)
        effect_data=[{'shortcut':r.get('Shortcut'),'capability':r.get('Capability'),'intent':r.get('Primary Use / Intent'),'application':r.get('Scene Recipe'),'sheet':r.get('sheet','')} for r in effects]
        scene=working[index]
        output_scenes.append({'scene':index+1,'timecode':str(index*2.5)+'-'+str((index+1)*2.5)+'s','story_purpose':scene['story_purpose'],'visual_direction':scene['visual_direction'],'effects':effect_data,'missing_effects':[],'vo':scene['vo'],'sound_direction':scene['sound_direction'],'sound':[],'on_screen':scene['on_screen'],'effect_status':'VERIFIED LIBRARY MATCH' if len(effect_data)==3 else 'PARTIAL LIBRARY MATCH','claim_guard_status':'BLOCKED' if guard['status']=='BLOCKED' else 'PASS'})
    objective=brief.get('objective') or 'Brand Awareness'; strategy={'objective':objective,'tone':brief.get('tone') or 'Cinematic','audience':brief.get('audience') or '','key_message':ai.get('key_message') or brief.get('message') or objective,'creative_route':ai.get('creative_route') or 'Audience-led brand story','narrative_arc':ai.get('narrative_arc') or 'Hook → need → product meaning → experience → brand recall → CTA','duration_seconds':15,'scene_count':6,'language':brief.get('language') or 'Hindi','cta':brief.get('cta') or 'Learn more','brand':brief.get('brand') or '','product':brief.get('product') or '','research_informed':bool(brief.get('research_context')),'ai_composed':bool(ai_scenes)}
    return {'engine':'KALP AdManthan Python Engine','version':VERSION,'execution':'Pyodide/WebAssembly','brand':brief.get('brand') or 'Brand','product':brief.get('product') or '','objective':objective,'duration_seconds':15,'scene_count':6,'library_count':len(rows or []),'strategy':strategy,'continuous_vo':' '.join(scene['vo'] for scene in output_scenes),'script_mode':'AI-composed six-beat continuous VO with deterministic evidence-safe normalization','claim_guard':guard,'release_status':'HOLD_FOR_CLAIM_REVIEW' if guard['status']=='BLOCKED' else 'RELEASE_ELIGIBLE','scenes':output_scenes,'production_package':{'format':'15-second advertisement','aspect_ratio':'16:9','scene_count':6,'deliverables':['AI intent model','research context','claim and evidence guard','final objective','strategy','AI six-beat continuous VO','storyboard','verified effect selections','sound design','production manifest'],'cta':brief.get('cta') or 'Learn more','engine_status':'EXECUTED','brief_driven':True,'research_informed':bool(brief.get('research_context')),'ai_composed':bool(ai_scenes),'raw_intent_excluded_from_creative':True}}

def generate(rows,brand,product,objective='Brand Awareness'): return execute(rows,{'brand':brand,'product':product,'objective':objective})
