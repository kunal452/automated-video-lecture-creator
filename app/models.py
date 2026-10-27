from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class SlideData(BaseModel):
    index: int = 1
    title: str
    bullet_points: List[str] = Field(default_factory=list)
    code_snippet: Optional[str] = None
    spoken_script: str
    duration_seconds: Optional[float] = 0.0

class LectureCreateRequest(BaseModel):
    lecture_title: str
    description: Optional[str] = None
    voice_profile: str = "en-US-ChristopherNeural"
    theme: str = "dark_modern"
    burn_subtitles: bool = True
    ken_burns_effect: bool = False
    slides: List[SlideData]

class GenerateFromTopicRequest(BaseModel):
    topic: str
    num_slides: int = 4
    audience_level: str = "undergraduate" # beginner, undergraduate, advanced
    llm_provider: str = "auto" # "auto", "gemini", "openai"
    api_key: Optional[str] = None

class JobStatusResponse(BaseModel):
    job_id: str
    status: str # queued, generating_slides, synthesizing_audio, rendering_segments, muxing, completed, failed
    progress: int # 0 to 100
    current_step: str
    total_slides: int
    video_url: Optional[str] = None
    srt_url: Optional[str] = None
    vtt_url: Optional[str] = None
    total_duration_seconds: Optional[float] = None
    error_message: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None
