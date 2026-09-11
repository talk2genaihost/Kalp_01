import json

VERSION = '0.8.5-semantic-effects'
CLAIM_TERMS = ['thermal','tip','retractable','refillable','waterproof','washable','smudge-proof','quick-dry','fast-drying','non-toxic','durable','leak-proof','shavings','residue','cartridge','eraser mechanism','lasts','long-lasting','writes smoothly','smooth writing','dries instantly','instant drying','erases completely','erases cleanly','without tearing','without shavings','zero residue','no residue','trace-free','without a trace','best','number one','#1','better than','faster than','more durable','guaranteed']
SAFE_REPLACEMENTS = [('zero residue','the erased mark'),('no residue','the erased mark'),('without a trace','the erased mark'),('trace-free','the erased mark'),('erases completely','erases'),('erases cleanly','erases'),('cleanly','away'),('instantly','then'),('instant','simple'),('seamless','continuous'),('premium',''),('perfect',''),('smooth','')]
OBJECT_CONTEXT_TERMS = ['pen tip','tip of the pen','pen-tip','tip pressing','tip pressing on paper','pen tip pressing','tip writes','tip of an erasable pen']

def norm(value): return str(value or '').lower()

def sanitize_text(value, grounding):
    text=str(value or '')
    low_ground=norm(grounding)
    for term,replacement in SAFE_REPLACEMENTS:
        if term in norm(text) and term not in low_ground: text=text.replace(term,replacement)
    return ' '.join(text.split())

def claim_term_is_property(term, text):
    low=norm(text)
    if term != 'tip': return term in low
    property_context=['thermal tip','retractable tip','replaceable tip','durable tip','special tip','erasable tip','advanced tip','fine tip','micro tip','felt tip','metal tip','rubber tip','tip technology','tip mechanism']
    if any(p in low for p in property_context): return True
    if any(p in low for p in OBJECT_CONTEXT_TERMS): return False
    return False

def fallback(brief):
    brand=brief.get('brand') or 'आपका ब्रांड'; product=brief.get('product') or 'यह प्रोडक्ट'; audience=brief.get('audience') or 'आज की पीढ़ी'; cta=brief.get('cta') or 'जानिए अधिक'
    return [audience+', अपनी रोज़मर्रा की दुनिया में एक ऐसी पसंद पर ध्यान दीजिए जो अलग महसूस हो।',product+' उस अनुभव को बेहतर बनाने का एक तरीका है।','जब लिखते हुए कोई गलती हो, तो उसे मिटाकर आगे बढ़िए।','अपने विचारों को फिर से लिखते हुए कहानी को आगे ले जाइए।',brand+' आपके लिखने के अनुभव को आपके लिए प्रासंगिक बनाने की कोशिश करता है।',brand+' — '+cta+'।']

def claim_guard(brief,scenes):
    intent=brief.get('intent_model') or {}; facts=intent.get('user_stated_facts') or {}; research=brief.get('research_context') or {}; verified=research.get('verified_facts') or []
    grounding=norm(json.dumps({'facts':facts,'product':intent.get('product'),'category':intent.get('category'),'verified':verified},ensure_ascii=False)); violations=[]
    for index,scene in enumerate(scenes,1):
        text=' '.join([str(scene.get('vo') or ''),str(scene.get('visual_direction') or ''),str(scene.get('on_screen') or '')])
        for term in CLAIM_TERMS:
            if claim_term_is_property(term, text) and term not in grounding:
                violations.append({'scene':index,'term':term,'reason':'Unsupported product claim/property.'})
    return {'status':'PASS' if not violations else 'BLOCKED','evidence_policy':'USER_STATED_FACTS + VERIFIED_FACTS_ONLY','violation_count':len(violations),'violations':violations}

def scene_terms(scene):
    text=' '.join([scene.get('story_purpose',''),scene.get('visual_direction',''),scene.get('vo',''),scene.get('sound_direction',''),scene.get('on_screen','')])
    low=norm(text)
    groups=[]
    vocab={
      'writing':['write','writing','pen','paper','ink','लिख','कलम','स्याही','कागज'],
      'erase':['erase','erasing','rub','remove','ink','मिट','मिटाना','रगड़','स्याही'],
      'product':['product','pen','erasable','पेन','प्रोडक्ट'],
      'macro':['close-up','close up','macro','detail','close','नज़दीक','डिटेल'],
      'camera':['camera','dolly','push','pull','orbit','crane','handheld','lens','कैमरा'],
      'hand':['hand','हाथ','finger','उंगली'],
      'paper':['paper','sheet','page','desk','कागज','पन्ना'],
      'hero':['hero','brand','lockup','logo','product hero'],
      'sound':['sound','music','voice','sfx','writing sound','rubbing sound','आवाज़','संगीत']
    }
    for group,terms in vocab.items():
        if any(t in low for t in terms): groups.append(group)
    return groups

def choose_effects(rows,scene,limit=3):
    groups=scene_terms(scene); scored=[]
    for row in rows or []:
        fields={k:norm(row.get(k)) for k in ['Shortcut','Capability','Primary Use / Intent','Scene Recipe','Visual / Execution Notes','Ad Role','Google-Ads Alignment']}
        text=' '.join(fields.values())
        score=0; matched=[]
        for group in groups:
            terms={
              'writing':['write','writing','pen','paper','ink'],
              'erase':['erase','erasing','rub','remove','ink'],
              'product':['product','pen','erasable'],
              'macro':['macro','detail','close','close-up'],
              'camera':['camera','dolly','push','pull','orbit','crane','handheld','lens'],
              'hand':['hand','human'],
              'paper':['paper','sheet','page','desk'],
              'hero':['hero','brand','lockup','logo'],
              'sound':['sound','music','voice','sfx','writing','rubbing']
            }[group]
            hits=sum(1 for term in terms if term in text)
            if hits:
                score += min(hits,2)
                matched.append(group)
        if score:
            # Penalize environment-only effects when the scene is a controlled product/demo action.
            if not any(g in groups for g in ['hero']) and any(x in text for x in ['beach environment','nature environment','outdoor lifestyle','leaves drifting','nature ambience']): score -= 5
            if any(g in groups for g in ['writing','erase','product','paper','macro']) and any(x in text for x in ['beach','nature','outdoor','leaves','birds']): score -= 4
            if score > 0: scored.append((score,len(matched),row,matched))
    scored.sort(key=lambda item:(-item[0],-item[1],str(item[2].get('Shortcut') or '')))
    selected=[]; used=set()
    for score,coverage,row,matched in scored:
        key=str(row.get('Shortcut') or '')
        if key not in used:
            selected.append((row,score,matched)); used.add(key)
        if len(selected)>=limit: break
    return selected

def execute(rows,brief):
    ai=brief.get('ai_direction') or {}; ai_scenes=ai.get('scenes') if isinstance(ai.get('scenes'),list) and len(ai.get('scenes'))==6 else None
    intent=brief.get('intent_model') or {}; facts=intent.get('user_stated_facts') or {}; research=brief.get('research_context') or {}; verified=research.get('verified_facts') or []
    grounding=json.dumps({'facts':facts,'product':intent.get('product'),'category':intent.get('category'),'verified':verified},ensure_ascii=False); fallback_lines=fallback(brief); working=[]
    for index in range(6):
        source=ai_scenes[index] if ai_scenes and isinstance(ai_scenes[index],dict) else {}
        working.append({'story_purpose':str(source.get('story_purpose') or source.get('purpose') or 'Develop the advertising story.'),'visual_direction':sanitize_text(source.get('visual_direction') or '',grounding),'vo':sanitize_text(source.get('vo') or fallback_lines[index],grounding),'sound_direction':str(source.get('sound_direction') or ''),'on_screen':sanitize_text(source.get('on_screen') or '',grounding)})
    guard=claim_guard(brief,working); output_scenes=[]
    for index in range(6):
        scene=working[index]; chosen=choose_effects(rows,scene,3)
        effect_data=[]
        for r,score,matched in chosen:
            effect_data.append({'shortcut':r.get('Shortcut'),'capability':r.get('Capability'),'intent':r.get('Primary Use / Intent'),'application':r.get('Scene Recipe'),'sheet':r.get('sheet',''),'semantic_score':score,'matched_scene_dimensions':matched})
        missing=[]
        if len(effect_data)<3: missing.append('No additional sufficiently relevant shortcut found in current effect library.')
        relevance='HIGH' if effect_data and effect_data[0]['semantic_score']>=4 else ('MEDIUM' if effect_data else 'LOW')
        output_scenes.append({'scene':index+1,'timecode':str(index*2.5)+'-'+str((index+1)*2.5)+'s','story_purpose':scene['story_purpose'],'visual_direction':scene['visual_direction'],'effects':effect_data,'missing_effects':missing,'vo':scene['vo'],'sound_direction':scene['sound_direction'],'sound':[],'on_screen':scene['on_screen'],'effect_status':'SEMANTICALLY VERIFIED SCENE MATCH' if relevance=='HIGH' else ('PARTIAL SEMANTIC MATCH' if effect_data else 'NO VERIFIED SCENE MATCH'),'effect_relevance':relevance,'claim_guard_status':'BLOCKED' if guard['status']=='BLOCKED' else 'PASS'})
    objective=brief.get('objective') or 'Brand Awareness'; strategy={'objective':objective,'tone':brief.get('tone') or 'Cinematic','audience':brief.get('audience') or '','key_message':ai.get('key_message') or brief.get('message') or objective,'creative_route':ai.get('creative_route') or 'Audience-led brand story','narrative_arc':ai.get('narrative_arc') or 'Hook → need → product meaning → experience → brand recall → CTA','duration_seconds':15,'scene_count':6,'language':brief.get('language') or 'Hindi','cta':brief.get('cta'),'brand':brief.get('brand') or '','product':brief.get('product') or '','research_informed':bool(research.get('verified_facts')),'research_retrieved':bool(brief.get('research_context')),'evidence_available':bool(research.get('verified_facts')),'ai_composed':bool(ai_scenes)}
    return {'engine':'KALP AdManthan Python Engine','version':VERSION,'execution':'Pyodide/WebAssembly','brand':brief.get('brand') or 'Brand','product':brief.get('product') or '','objective':objective,'duration_seconds':15,'scene_count':6,'library_count':len(rows or []),'strategy':strategy,'continuous_vo':' '.join(scene['vo'] for scene in output_scenes),'script_mode':'AI-composed six-beat continuous VO with deterministic evidence-safe normalization','claim_guard':guard,'release_status':'HOLD_FOR_CLAIM_REVIEW' if guard['status']=='BLOCKED' else 'RELEASE_ELIGIBLE','scenes':output_scenes,'production_package':{'format':'15-second advertisement','aspect_ratio':'16:9','scene_count':6,'deliverables':['AI intent model','research context','claim and evidence guard','final objective','strategy','AI six-beat continuous VO','storyboard','verified effect selections','sound design','production manifest'],'cta':brief.get('cta'),'engine_status':'EXECUTED','brief_driven':True,'research_informed':bool(research.get('verified_facts')),'research_retrieved':bool(brief.get('research_context')),'evidence_available':bool(research.get('verified_facts')),'ai_composed':bool(ai_scenes),'raw_intent_excluded_from_creative':True}}

def generate(rows,brand,product,objective='Brand Awareness'): return execute(rows,{'brand':brand,'product':product,'objective':objective})
