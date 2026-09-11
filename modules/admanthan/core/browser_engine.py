import json

SCENE_TEMPLATES = {
1:{'purpose':'Establish scale, aspiration and location.','shortcuts':['/crane_up','/wide_environment','/wide_24mm'],'vo':'सोचिए…','sound':['/riser_short','/nature_ambience']},
2:{'purpose':'Move from destination to the personal idea of home.','shortcuts':['/dolly_in','/three_quarter_front','/steadicam_float'],'vo':'आपका घर सिर्फ़ रहने की जगह नहीं…','sound':['/continuity_bridge']},
3:{'purpose':'Make nature and openness the visual proof of the proposition.','shortcuts':['/wide_24mm','/high_hero','/outdoor_nature'],'vo':'जहाँ हर सुबह प्रकृति मिले…','sound':['/nature_ambience']},
4:{'purpose':'Translate environment into lived comfort and interior experience.','shortcuts':['/dolly_in','/natural_window_set','/normal_35mm'],'vo':'हर पल सुकून मिले…','sound':['/continuity_bridge','/music_build']},
5:{'purpose':'Show lifestyle and human connection rather than only property.','shortcuts':['/steadicam_float','/human_hold','/outdoor_nature'],'vo':'और हर दिन बेहतर लगे।','sound':['/footstep_sync','/music_build']},
6:{'purpose':'Resolve the narrative into brand identity and action.','shortcuts':['/hero_lock','/brand_lockup','/cta_endcard'],'vo':'यही है ब्रांड.','sound':['/brand_sting','/voiceover_cta']}}

class BrowserEffectLibrary:
    def __init__(self, rows):
        self.rows = rows or []
        self.by_shortcut = {str(r.get('Shortcut')).strip(): r for r in self.rows if r.get('Shortcut')}
    def get(self, shortcut): return self.by_shortcut.get(shortcut)
    def count(self): return len(self.by_shortcut)

class AdManthanBrowserEngine:
    VERSION = '0.2-browser'
    def __init__(self, rows): self.library = BrowserEffectLibrary(rows)
    def strategy(self, brand, product, objective, audience, tone):
        proposition = f'{product} positioned for {audience} with a {tone} creative expression.'
        return {'brand':brand,'product':product,'objective':objective,'audience':audience,'tone':tone,'proposition':proposition,'creative_route':'Human benefit → visual proof → lifestyle → brand CTA','duration_seconds':15,'frame_count':6}
    def generate(self, brief):
        brand=brief.get('brand') or 'Brand'; product=brief.get('product') or 'Product'; objective=brief.get('objective') or 'brand awareness'; audience=brief.get('audience') or 'Urban premium audience'; tone=brief.get('tone') or 'cinematic'; cta=brief.get('cta') or f'Discover {brand}'
        scenes=[]
        for i in range(1,7):
            t=SCENE_TEMPLATES[i]; effects=[]; missing=[]
            for shortcut in t['shortcuts']:
                row=self.library.get(shortcut)
                if row: effects.append({'shortcut':shortcut,'capability':row.get('Capability',''),'intent':row.get('Primary Use / Intent',''),'application':row.get('Scene Recipe',''),'sheet':row.get('sheet',row.get('Sheet',''))})
                else: missing.append(shortcut)
            vo=t['vo'].replace('ब्रांड',brand) if i==6 else t['vo']
            scenes.append({'scene':i,'timecode':f'{(i-1)*2.5:.1f}-{i*2.5:.1f}s','story_purpose':t['purpose'],'effects':effects,'missing_effects':missing,'vo':vo,'sound':t['sound'],'on_screen':cta if i==6 else '','effect_status':'VERIFIED LIBRARY MATCH' if not missing else ('PARTIAL LIBRARY MATCH' if effects else 'NOT FOUND IN CURRENT EFFECT LIBRARY')})
        return {'engine':'KALP AdManthan Python Engine','version':self.VERSION,'execution':'Python-in-browser adapter','brief':brief,'strategy':self.strategy(brand,product,objective,audience,tone),'duration_seconds':15,'scene_count':6,'library_count':self.library.count(),'continuous_vo':f'सोचिए… {product} सिर्फ़ एक जगह नहीं… जहाँ हर सुबह प्रकृति मिले, हर पल सुकून मिले, और हर दिन बेहतर लगे। यही है {brand}.','scenes':scenes,'production_package':{'format':'15s / 6-frame storyboard','aspect_ratio':'9:16','deliverables':['storyboard.json','scene prompts','effect manifest','audio cue manifest','CTA/end-card specification'],'cta':cta,'engine_status':'EXECUTED'}}

def execute(rows, brief):
    return AdManthanBrowserEngine(rows).generate(brief)
