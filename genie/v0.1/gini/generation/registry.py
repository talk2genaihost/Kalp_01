from ..schemas import Engine

def builtin_engines():
    return [
      Engine("mock.image.v0","KALP-MOCK","image",["image_generation","character_reference","style_reference"],{"prompt":"string"},{"artifact_type":"image"},["draft"],["png"],"zero","instant","available","0.1"),
      Engine("mock.video.v0","KALP-MOCK","video",["video_generation","image_to_video","camera_motion"],{"prompt":"string"},{"artifact_type":"video"},["draft"],["mp4"],"zero","instant","available","0.1"),
      Engine("mock.voice.v0","KALP-MOCK","voice",["voice_synthesis","language_hindi","style_direction"],{"text":"string"},{"artifact_type":"audio"},["draft"],["wav","mp3"],"zero","instant","available","0.1"),
      Engine("mock.music.v0","KALP-MOCK","music",["music_generation","mood_control","duration_control"],{"prompt":"string"},{"artifact_type":"audio"},["draft"],["wav","mp3"],"zero","instant","available","0.1")]

def registry_index(): return {e.engine_id:e for e in builtin_engines()}
