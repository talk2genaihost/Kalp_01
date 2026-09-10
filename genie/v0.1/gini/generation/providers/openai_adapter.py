import os
from pathlib import Path
from .base import ProviderAdapter,ProviderResult
class OpenAIProviderAdapter(ProviderAdapter):
    provider="openai"
    def __init__(self): self.api_key_present=bool(os.getenv("OPENAI_API_KEY"))
    def health(self): return {"provider":self.provider,"configured":self.api_key_present,"status":"READY" if self.api_key_present else "NOT_CONFIGURED"}
    def execute(self,job):
        if not self.api_key_present: raise RuntimeError("OPENAI_API_KEY is not configured")
        from openai import OpenAI
        client=OpenAI(); modality=job["modality"]; model=job.get("model")
        if modality=="image":
            response=client.images.generate(model=model or "gpt-image-2",prompt=job["prompt"])
            return ProviderResult(self.provider,job["engine_id"],"SUBMITTED",[],{"provider_request_id":getattr(response,"id",None)})
        if modality=="voice":
            output=Path(job["output_path"]); output.parent.mkdir(parents=True,exist_ok=True)
            with client.audio.speech.with_streaming_response.create(model=model or "gpt-4o-mini-tts",voice=job.get("voice","alloy"),input=job["text"]) as response: response.stream_to_file(output)
            return ProviderResult(self.provider,job["engine_id"],"COMPLETED",[str(output)],{"model":model or "gpt-4o-mini-tts"})
        raise NotImplementedError(f"No concrete OpenAI adapter for modality={modality}")
