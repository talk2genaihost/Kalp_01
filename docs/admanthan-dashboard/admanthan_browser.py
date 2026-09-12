import json
import re

VERSION='0.8.7-effect-calibration'
CLAIM_TERMS=['thermal','tip','retractable','refillable','waterproof','washable','smudge-proof','quick-dry','fast-drying','non-toxic','durable','leak-proof','shavings','residue','cartridge','eraser mechanism','lasts','long-lasting','writes smoothly','smooth writing','dries instantly','instant drying','erases completely','erases cleanly','without tearing','without shavings','zero residue','no residue','trace-free','without a trace','best','number one','#1','better than','faster than','more durable','guaranteed']
SAFE_REPLACEMENTS=[('zero residue','the erased mark'),('no residue','the erased mark'),('without a trace','the erased mark'),('trace-free','the erased mark'),('erases completely','erases'),('erases cleanly','erases'),('cleanly','away'),('instantly','then'),('instant','simple'),('seamless','continuous'),('premium',''),('perfect',''),('smooth','')]
OBJECT_CONTEXT_TERMS=['pen tip','tip of the pen','pen-tip','tip pressing','tip pressing on paper','pen tip pressing','tip writes','tip of an erasable pen']
def norm(v): return str(v or '').lower()
def sanitize_text(v,g):
    text=str(v or ''); low=norm(g)
    for term,repl in SAFE_REPLACEMENTS:
        if term in norm(text) and term not in low: text=text.replace(term,repl)
    return ' '.join(text.split())
def claim_term_is_property(term,text):
    low=norm(text)
    if term!='tip': return term in low
    props=['thermal tip','retractable tip','replaceable tip','durable tip','special tip','erasable tip','advanced tip','fine tip','micro tip','felt tip','metal tip','rubber tip','tip technology','tip mechanism']
    return any(p in low for p in props) and not any(p in low for p in OBJECT_CONTEXT_TERMS)
def fallback(brief):
    brand=brief.get('brand') or 'आपका ब्रांड'; product=brief.get('product') or 'यह प्रोडक्ट'; audience=brief.get('audience') or 'आज की पीढ़ी'; cta=brief.get('cta') or 'जानिए अधिक'
    return [audience+', अपनी रोज़मर्रा की दुनिया में एक ऐसी पसंद पर ध्यान दीजिए जो अलग महसूस हो।',product+' उस अनुभव को बेहतर बनाने का एक तरीका है।','जब लिखते हुए कोई गलती हो, तो उसे मिटाकर आगे बढ़िए।','अपने विचारों को फिर से लिखते हुए कहानी को आगे ले जाइए।',brand+' आपके लिखने के अनुभव को आपके लिए प्रासंगिक बनाने की कोशिश करता है।',brand+' — '+cta+'।']
def claim_guard(brief,scenes):
    intent=brief.get('intent_model') or {}; facts=intent.get('user_stated_facts') or {}; research=brief.get('research_context') or {}; verified=research.get('verified_facts') or []
    grounding=norm(json.dumps({'facts':facts,'product':intent.get('product'),'category':intent.get('category'),'verified':verified},ensure_ascii=False)); violations=[]
    for i,s in enumerate(scenes,1):
        text=' '.join([str(s.get('vo') or ''),str(s.get('visual_direction') or ''),str(s.get('on_screen') or '')])
        for term in CLAIM_TERMS:
            if claim_term_is_property(term,text) and term not in grounding: violations.append({'scene':i,'term':term,'reason':'Unsupported product claim/property.'})
    return {'status':'PASS' if not violations else 'BLOCKED','evidence_policy':'USER_STATED_FACTS + VERIFIED_FACTS_ONLY','violation_count':len(violations),'violations':violations}

def scene_profile(scene):
    text=' '.join([scene.get('story_purpose',''),scene.get('visual_direction',''),scene.get('vo',''),scene.get('sound_direction',''),scene.get('on_screen','')]); low=norm(text)
    def anyof(xs): return any(x in low for x in xs)
    actions=[]
    if anyof(['product','pen','erasable','प्रोडक्ट','पेन']): actions+=['product_demo']
    if anyof(['write','writing','scrib','pen moves','pen tip moves','लिख','कलम','स्याही']): actions+=['writing','product_demo']
    if anyof(['erase','erasing','rub','remove','मिट','रगड़','erase mark']): actions+=['erasing','product_demo']
    if anyof(['reveal','unveil','open','pack','box','unbox','खुल']): actions+=['reveal']
    if anyof(['rotate','spin','360','turntable']): actions+=['product_rotation']
    # Keep CLOSE-UP, MACRO and PRODUCT DETAIL distinct. A close-up is not automatically macro.
    if anyof(['macro','extreme close-up','extreme close up','macro detail','मैक्रो']): actions+=['macro_detail']
    elif anyof(['close-up','close up','detail shot','product detail','नज़दीक','डिटेल']): actions+=['close_up']
    if anyof(['hero','logo','brand lockup','final frame','cta']): actions+=['hero_brand']
    if anyof(['hand','finger','हाथ','उंगली']): actions+=['hand_interaction']
    if anyof(['paper','sheet','page','desk','कागज','पन्ना']): actions+=['paper_context']
    if anyof(['camera','dolly','push in','pull out','orbit','crane','lens','कैमरा']): actions+=['camera_motion']
    if anyof(['transition','cut','match cut','whip','कट']): actions+=['edit_transition']
    if anyof(['sound','music','voice','sfx','whoosh','foley','आवाज़','संगीत']): actions+=['audio']
    return {'actions':list(dict.fromkeys(actions or ['general_story'])),'low':low}

def effect_profile(row):
    text=' '.join(norm(row.get(k)) for k in ['Shortcut','Capability','Primary Use / Intent','Scene Recipe','Visual / Execution Notes','Ad Role','Google-Ads Alignment'])
    sc=norm(row.get('Shortcut')); cap=norm(row.get('Capability'))
    p={'family':'unknown','functions':set(),'roles':set(),'tokens':set(),'hard':set()}
    # Macro must be classified before generic optical /push rules.
    if sc.startswith('/macro_'): p['family']='macro'; p['functions']|={'macro_detail','optical'}
    elif sc.startswith(('/dolly','/truck','/pedestal','/crane','/orbit','/arc','/pan','/tilt','/push','/pull','/tracking','/handheld')): p['family']='camera'; p['functions'].add('camera_motion')
    elif sc.startswith(('/hero_','/low_','/ultra_low','/top_','/overhead','/profile','/rear','/front')) or 'angle' in sc or 'perspective' in cap: p['family']='camera'; p['functions'].add('camera_angle')
    elif sc.startswith(('/wide_','/tele_','/shallow_','/deep_','/anamorphic','/fisheye')): p['family']='optical'; p['functions'].add('optical')
    elif sc.startswith(('/front_view','/rear_view','/left_view','/right_view','/three_quarter','/top_view','/bottom_view','/detail_view')): p['family']='product'; p['functions'].add('product_coverage')
    elif sc.startswith(('/turntable','/spin','/slide_product','/product_','/transform')): p['family']='product_motion'; p['functions'].add('product_motion')
    elif sc.startswith(('/brand_','/product_name','/one_claim','/typography','/text_')): p['family']='graphics'; p['functions'].add('graphics')
    elif sc.startswith(('/softbox','/hard_light','/rim_light','/backlight','/gobo','/shadow','/highlight')): p['family']='lighting'; p['functions'].add('lighting')
    elif sc.startswith(('/dust','/mist','/fog','/smoke','/spark','/particle','/glow','/light_streak')): p['family']='vfx'; p['functions'].add('atmosphere_vfx')
    elif sc.startswith(('/glass','/mirror','/wet','/fabric','/paper','/wood','/metal','/stone','/water')): p['family']='material_environment'; p['functions'].add('surface_environment')
    elif sc.startswith(('/match_cut','/whip','/zoom_transition','/speed_ramp','/freeze','/time_')): p['family']='edit'; p['functions'].add('edit_transition')
    elif sc.startswith(('/whoosh','/swoosh','/hit','/riser','/sting','/ambient','/foley','/voiceover')): p['family']='audio'; p['functions'].add('audio')
    if any(x in text for x in ['branding','brand recognition','logo']): p['roles'].add('branding')
    if any(x in text for x in ['attention','hook','punctuation']): p['roles'].add('attention')
    if any(x in text for x in ['connection','lifestyle','context']): p['roles'].add('connection')
    if any(x in text for x in ['direction','message','claim']): p['roles'].add('message')
    if any(x in text for x in ['product','demo','coverage','reveal','feature']): p['roles'].add('product_demo')
    p['tokens']=set(re.findall(r'[a-z]+',text))
    if p['family'] in {'material_environment','vfx'}: p['hard']|={'writing','erasing','hand_interaction'}
    if p['family']=='graphics': p['hard']|={'writing','erasing','hand_interaction','product_motion'}
    return p

def classify_scene(scene): return scene_profile(scene)
def classify_effect(row): return effect_profile(row)

def choose_effects(rows,scene,limit=3):
    sp=classify_scene(scene); actions=set(sp['actions']); candidates=[]; rejected=[]
    explicit_camera='camera_motion' in actions; explicit_macro='macro_detail' in actions; explicit_close='close_up' in actions; explicit_edit='edit_transition' in actions; explicit_audio='audio' in actions; explicit_hero='hero_brand' in actions; explicit_paper='paper_context' in actions
    physical=actions & {'writing','erasing','hand_interaction'}
    low=sp['low']
    for row in rows or []:
        ep=classify_effect(row); funcs=ep['functions']; family=ep['family']; compatibility='INCOMPATIBLE'; score=0; reasons=[]
        if explicit_hero:
            if 'branding' in ep['roles'] and funcs & {'graphics','product_coverage','camera_motion','lighting'}: compatibility='DIRECT MATCH'; score=7; reasons.append('hero/brand production-role match')
            elif funcs & {'product_coverage','camera_motion','lighting'}: compatibility='SUPPORTING MATCH'; score=6; reasons.append('hero product presentation match')
        elif explicit_macro:
            if 'macro_detail' in funcs: compatibility='DIRECT MATCH'; score=7; reasons.append('explicit macro-detail match')
            elif 'camera_motion' in funcs or 'optical' in funcs: compatibility='SUPPORTING MATCH'; score=5; reasons.append('camera technique supports macro/detail action')
        elif explicit_close:
            if 'macro_detail' in funcs or 'optical' in funcs: compatibility='SUPPORTING MATCH'; score=5; reasons.append('macro/optical technique supports close-up')
            elif 'product_coverage' in funcs: compatibility='DIRECT MATCH'; score=6; reasons.append('product-detail coverage match')
            elif 'camera_motion' in funcs: compatibility='SUPPORTING MATCH'; score=5; reasons.append('camera movement supports close-up')
        elif physical:
            if explicit_camera and 'camera_motion' in funcs: compatibility='DIRECT MATCH'; score=7; reasons.append('explicit camera-direction match')
            elif 'product_coverage' in funcs and any(t in low for t in ['product close','product view','product coverage','product presentation','product detail']): compatibility='DIRECT MATCH'; score=6; reasons.append('explicit product-coverage match')
            elif 'product_motion' in funcs and any(t in low for t in ['rotate','spin','turntable','transform','reveal']): compatibility='DIRECT MATCH'; score=6; reasons.append('explicit product-motion match')
            elif family=='audio' and any(t in low for t in ['sfx','sound effect','foley','rub','scratch','erase sound','pen sound','whoosh']): compatibility='SUPPORTING MATCH'; score=4; reasons.append('explicit action sound cue')
            elif family in {'lighting','optical','camera'}: compatibility='SUPPORTING MATCH'; score=4; reasons.append('production technique supports physical action')
        elif explicit_edit and 'edit_transition' in funcs: compatibility='DIRECT MATCH'; score=7; reasons.append('edit function match')
        elif explicit_audio and 'audio' in funcs: compatibility='DIRECT MATCH'; score=6; reasons.append('audio function match')
        elif explicit_paper and any(t in ep['tokens'] for t in ['paper','sheet','page','desk']): compatibility='SUPPORTING MATCH'; score=5; reasons.append('paper-context match')
        elif 'product_demo' in actions and funcs & {'product_coverage','product_motion','macro_detail','optical','camera_motion'}: compatibility='SUPPORTING MATCH'; score=5; reasons.append('product presentation technique')
        # Generic VO/audio presence is not sufficient production necessity.
        if family=='audio' and not any(t in low for t in ['sfx','sound effect','foley','rub','scratch','erase sound','pen sound','whoosh','music cue']):
            compatibility='INCOMPATIBLE'; score=0; reasons=[]
        if compatibility=='INCOMPATIBLE':
            rejected.append({'shortcut':row.get('Shortcut'),'stage':'COMPATIBILITY','compatibility':compatibility,'reason':'No compatible production role for the stated scene.'}); continue
        if physical and family in {'vfx','material_environment','graphics'}:
            rejected.append({'shortcut':row.get('Shortcut'),'stage':'COMPATIBILITY','compatibility':'INCOMPATIBLE','reason':'Decorative/support family is not necessary for the physical pen action.'}); continue
        keyword_hits=len(ep['tokens'] & set(re.findall(r'[a-z]+',low))); score+=min(keyword_hits,1)
        if score<4: rejected.append({'shortcut':row.get('Shortcut'),'stage':'QUALITY_THRESHOLD','compatibility':compatibility,'reason':'Below minimum production compatibility threshold','score':score}); continue
        necessity=2 if compatibility=='DIRECT MATCH' else 1
        # Prefer techniques that materially improve the shot, not effects that merely can be present.
        if family in {'lighting','optical','camera','macro','product','product_motion','edit'}: necessity+=1
        candidates.append({'row':row,'score':score+necessity,'base_score':score,'necessity':necessity,'reasons':reasons,'family':family,'functions':sorted(funcs),'compatibility':compatibility})
    candidates.sort(key=lambda x:(-x['score'], -x['necessity'], x['family'], str(x['row'].get('Shortcut') or '')))
    selected=[]; used_families=set(); used=set()
    for c in candidates:
        key=str(c['row'].get('Shortcut') or '')
        if key in used: continue
        penalty=1 if c['family'] in used_families else 0; c['repetition_penalty']=penalty; c['effective_score']=c['score']-penalty
        if c['effective_score']>=5: selected.append(c); used.add(key); used_families.add(c['family'])
        if len(selected)>=limit: break
    selected.sort(key=lambda x:(-x['effective_score'],-x['score'],str(x['row'].get('Shortcut') or '')))
    diagnostics={'scene_actions':sorted(actions),'candidate_count':len(candidates),'rejected_count':len(rejected),'selected_count':len(selected),'repetition_penalty_applied':any(c.get('repetition_penalty',0)>0 for c in selected),'compatibility_counts':{'DIRECT MATCH':sum(c['compatibility']=='DIRECT MATCH' for c in candidates),'SUPPORTING MATCH':sum(c['compatibility']=='SUPPORTING MATCH' for c in candidates),'INCOMPATIBLE':len(rejected)},'rejections':rejected[:40]}
    return selected,diagnostics

def execute(rows,brief):
    ai=brief.get('ai_direction') or {}; ai_scenes=ai.get('scenes') if isinstance(ai.get('scenes'),list) and len(ai.get('scenes'))==6 else None
    intent=brief.get('intent_model') or {}; facts=intent.get('user_stated_facts') or {}; research=brief.get('research_context') or {}; verified=research.get('verified_facts') or []
    grounding=json.dumps({'facts':facts,'product':intent.get('product'),'category':intent.get('category'),'verified':verified},ensure_ascii=False); fb=fallback(brief); working=[]
    for i in range(6):
        src=ai_scenes[i] if ai_scenes and isinstance(ai_scenes[i],dict) else {}
        working.append({'story_purpose':str(src.get('story_purpose') or src.get('purpose') or 'Develop the advertising story.'),'visual_direction':sanitize_text(src.get('visual_direction') or '',grounding),'vo':sanitize_text(src.get('vo') or fb[i],grounding),'sound_direction':str(src.get('sound_direction') or ''),'on_screen':sanitize_text(src.get('on_screen') or '',grounding)})
    guard=claim_guard(brief,working); out=[]
    for i,scene in enumerate(working):
        chosen,diag=choose_effects(rows,scene,3); effects=[]
        for c in chosen:
            r=c['row']; effects.append({'shortcut':r.get('Shortcut'),'capability':r.get('Capability'),'intent':r.get('Primary Use / Intent'),'application':r.get('Scene Recipe'),'sheet':r.get('sheet',''),'semantic_score':c['score'],'effective_score':c['effective_score'],'effect_family':c['family'],'effect_functions':c['functions'],'compatibility':c['compatibility'],'selection_reasons':c['reasons']})
        missing=[]
        if len(effects)<3: missing.append('No additional production-relevant library effect passed the v0.8.7 calibration gate; no padding applied.')
        relevance='HIGH' if effects and effects[0]['effective_score']>=8 else ('MEDIUM' if effects else 'LOW')
        gate='PASS' if effects else 'PASS_WITH_LIMITED_EFFECTS'
        out.append({'scene':i+1,'timecode':str(i*2.5)+'-'+str((i+1)*2.5)+'s','story_purpose':scene['story_purpose'],'visual_direction':scene['visual_direction'],'effects':effects,'missing_effects':missing,'effect_diagnostics':diag,'effect_quality_gate':{'status':gate,'selected_count':len(effects),'allowed_range':'0-3','padding_applied':False},'vo':scene['vo'],'sound_direction':scene['sound_direction'],'sound':[],'on_screen':scene['on_screen'],'effect_status':'CALIBRATED PRODUCTION MATCH' if effects else 'NO EFFECT PASSED QUALITY GATE','effect_relevance':relevance,'claim_guard_status':'BLOCKED' if guard['status']=='BLOCKED' else 'PASS'})
    objective=brief.get('objective') or 'Brand Awareness'; strategy={'objective':objective,'tone':brief.get('tone') or 'Cinematic','audience':brief.get('audience') or '','key_message':ai.get('key_message') or brief.get('message') or objective,'creative_route':ai.get('creative_route') or 'Audience-led brand story','narrative_arc':ai.get('narrative_arc') or 'Hook → need → product meaning → experience → brand recall → CTA','duration_seconds':15,'scene_count':6,'language':brief.get('language') or 'Hindi','cta':ai.get('cta') or brief.get('cta'),'brand':brief.get('brand') or '','product':brief.get('product') or '','research_informed':bool(research.get('verified_facts')),'research_retrieved':bool(brief.get('research_context')),'evidence_available':bool(research.get('verified_facts')),'ai_composed':bool(ai_scenes)}
    return {'engine':'KALP AdManthan Python Engine','version':VERSION,'execution':'Pyodide/WebAssembly','brand':brief.get('brand') or 'Brand','product':brief.get('product') or '','objective':objective,'duration_seconds':15,'scene_count':6,'library_count':len(rows or []),'strategy':strategy,'continuous_vo':' '.join(s['vo'] for s in out),'script_mode':'AI-composed six-beat continuous VO with deterministic evidence-safe normalization','claim_guard':guard,'release_status':'HOLD_FOR_CLAIM_REVIEW' if guard['status']=='BLOCKED' else 'RELEASE_ELIGIBLE','scenes':out,'production_package':{'format':'15-second advertisement','aspect_ratio':'16:9','scene_count':6,'deliverables':['AI intent model','research context','claim and evidence guard','final objective','strategy','AI six-beat continuous VO','storyboard','quality-gated effect selections','effect diagnostics','sound design','production manifest'],'cta':ai.get('cta') or brief.get('cta'),'engine_status':'EXECUTED','brief_driven':True,'research_informed':bool(research.get('verified_facts')),'research_retrieved':bool(brief.get('research_context')),'evidence_available':bool(research.get('verified_facts')),'ai_composed':bool(ai_scenes),'raw_intent_excluded_from_creative':True}}
def generate(rows,brand,product,objective='Brand Awareness'): return execute(rows,{'brand':brand,'product':product,'objective':objective})
