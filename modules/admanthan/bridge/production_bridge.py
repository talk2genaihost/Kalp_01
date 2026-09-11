from pathlib import Path
import json, uuid

class ProductionBridge:
    """Provider-neutral bridge. It prepares jobs; provider adapters can be added without changing AdManthan."""
    def __init__(self, out_dir): self.out_dir=Path(out_dir); self.out_dir.mkdir(parents=True,exist_ok=True)
    def create_job(self, ad_package):
        job={'job_id':'ADMB-'+uuid.uuid4().hex[:10].upper(),'status':'READY_FOR_PROVIDER','package':ad_package}
        p=self.out_dir/(job['job_id']+'.json'); p.write_text(json.dumps(job,ensure_ascii=False,indent=2),encoding='utf-8')
        return job, p
    def manifest(self, ad_package):
        return {'provider_neutral':True,'assets':['storyboard_frames','voiceover','music_sfx','final_render'],'aspect_ratio':'configurable','scene_count':ad_package['scene_count'],'duration_seconds':ad_package['duration_seconds']}
