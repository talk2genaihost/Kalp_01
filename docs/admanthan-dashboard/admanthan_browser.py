import json

SCENE_TEMPLATES={1:{'purpose':'Establish scale, aspiration and location.','shortcuts':['/crane_up','/wide_environment','/wide_24mm'],'vo':'सोचिए…','sound':['/riser_short','/nature_ambience']},2:{'purpose':'Move from the destination to the personal idea of home.','shortcuts':['/dolly_in','/three_quarter_front','/steadicam_float'],'vo':'आपका घर सिर्फ़ रहने की जगह नहीं…','sound':['/continuity_bridge']},3:{'purpose':'Make nature and openness the visual proof of the proposition.','shortcuts':['/wide_24mm','/high_hero','/outdoor_nature'],'vo':'जहाँ हर सुबह प्रकृति मिले…','sound':['/nature_ambience']},4:{'purpose':'Translate environment into lived comfort and interior experience.','shortcuts':['/dolly_in','/natural_window_set','/normal_35mm'],'vo':'हर पल सुकून मिले…','sound':['/continuity_bridge','/music_build']},5:{'purpose':'Show lifestyle and human connection rather than only property.','shortcuts':['/steadicam_float','/human_hold','/outdoor_nature'],'vo':'और हर दिन बेहतर लगे।','sound':['/footstep_sync','/music_build']},6:{'purpose':'Resolve the narrative into brand identity and action.','shortcuts':['/hero_lock','/brand_lockup','/cta_endcard'],'vo':'यही है GolfForeste.','sound':['/brand_sting','/voiceover_cta']}}
class BrowserEffectLibrary:
    def __init__(self,rows): self.rows=rows or []; self.by_shortcut={r.get('Shortcut'):r for r in self.rows if r.get('Shortcut')}
    def get(self,shortcut): return self.by_shortcut.get(shortcut)
    def count(self): return len(self.rows)
class AdManthan:
    def __init__(self,library): self.library=library
    def generate_15s_6(self,brand,product,objective='brand awareness',language='Hindi'):
        master_vo='सोचिए… आपका घर सिर्फ़ रहने की जगह नहीं… जहाँ हर सुबह प्रकृति मिले, हर पल सुकून मिले, और हर दिन बेहतर लगे। यही है GolfForeste.'
        scenes=[]
        for i in range(1,7):
            t=SCENE_TEMPLATES[i]; effects=[]; missing=[]
            for shortcut in t['shortcuts']:
                e=self.library.get(shortcut)
                if e: effects.append({'shortcut':e.get('Shortcut'),'capability':e.get('Capability'),'intent':e.get('Primary Use / Intent'),'application':e.get('Scene Recipe'),'sheet':e.get('sheet','')})
                else: missing.append(shortcut)
            scenes.append({'scene':i,'timecode':f'{(i-1)*2.5:.1f}-{i*2.5:.1f}s','story_purpose':t['purpose'],'effects':effects,'missing_effects':missing,'vo':t['vo'],'sound':t['sound'],'on_screen':brand if i==6 else '','effect_status':'VERIFIED LIBRARY MATCH' if not missing else ('PARTIAL LIBRARY MATCH' if effects else 'NOT FOUND IN CURRENT EFFECT LIBRARY')})
        return {'engine':'KALP AdManthan Python Engine','version':'0.1-browser','execution':'Pyodide/WebAssembly','brand':brand,'product':product,'objective':objective,'duration_seconds':15,'scene_count':6,'library_count':self.library.count(),'continuous_vo':master_vo,'scenes':scenes}
def generate(rows,brand,product,objective='brand awareness'): return AdManthan(BrowserEffectLibrary(rows)).generate_15s_6(brand,product,objective)
