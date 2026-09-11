from pathlib import Path
from .effect_library import EffectLibrary

SCENE_TEMPLATES={
1:{'purpose':'Establish scale, aspiration and location.','shortcuts':['/crane_up','/wide_environment','/wide_24mm'],'vo':'सोचिए…','sound':['/riser_short','/nature_ambience']},
2:{'purpose':'Move from the destination to the personal idea of home.','shortcuts':['/dolly_in','/three_quarter_front','/steadicam_float'],'vo':'आपका घर सिर्फ़ रहने की जगह नहीं…','sound':['/continuity_bridge']},
3:{'purpose':'Make nature and openness the visual proof of the proposition.','shortcuts':['/wide_24mm','/high_hero','/outdoor_nature'],'vo':'जहाँ हर सुबह प्रकृति मिले…','sound':['/nature_ambience']},
4:{'purpose':'Translate environment into lived comfort and interior experience.','shortcuts':['/dolly_in','/natural_window_set','/normal_35mm'],'vo':'हर पल सुकून मिले…','sound':['/continuity_bridge','/music_build']},
5:{'purpose':'Show lifestyle and human connection rather than only property.','shortcuts':['/steadicam_float','/human_hold','/outdoor_nature'],'vo':'और हर दिन बेहतर लगे।','sound':['/footstep_sync','/music_build']},
6:{'purpose':'Resolve the narrative into brand identity and action.','shortcuts':['/hero_lock','/brand_lockup','/cta_endcard'],'vo':'यही है GolfForeste.','sound':['/brand_sting','/voiceover_cta']}}

class AdManthan:
    def __init__(self, library): self.library=library
    def choose_effects(self, terms, n=3):
        candidates=self.library.lookup(terms, limit=12)
        chosen=[]
        for r in candidates:
            if r['Shortcut'] not in [x['Shortcut'] for x in chosen]: chosen.append(r)
            if len(chosen)>=n: break
        return chosen
    def generate_15s_6(self, brand, product, objective='brand awareness', language='Hindi'):
        master_vo='सोचिए… आपका घर सिर्फ़ रहने की जगह नहीं… जहाँ हर सुबह प्रकृति मिले, हर पल सुकून मिले, और हर दिन बेहतर लगे। यही है GolfForeste.'
        scenes=[]
        for i in range(1,7):
            t=SCENE_TEMPLATES[i]
            effects=[self.library.get(x) for x in t['shortcuts'] if self.library.get(x)]
            scenes.append({'scene':i,'timecode':f'{(i-1)*2.5:.1f}-{i*2.5:.1f}s','story_purpose':t['purpose'],'effects':[
                {'shortcut':e['Shortcut'],'capability':e['Capability'],'intent':e['Primary Use / Intent'],'application':e['Scene Recipe']} for e in effects],
                'vo':t['vo'],'sound':t['sound'],'on_screen': brand if i==6 else '',
                'effect_status':'VERIFIED LIBRARY MATCH' if effects else 'NOT FOUND IN CURRENT EFFECT LIBRARY'})
        return {'engine':'KALP AdManthan','version':'0.1','brand':brand,'product':product,'objective':objective,'duration_seconds':15,'scene_count':6,'continuous_vo':master_vo,'scenes':scenes}
