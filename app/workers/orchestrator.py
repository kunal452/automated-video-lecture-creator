import asyncio
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from app.config import JOBS_DIR
from app.models import LectureCreateRequest
from app.services.slide_renderer import render_slide_image
from app.services.tts_engine import synthesize_speech
from app.services.video_renderer import (
    render_slide_segment,
    concatenate_segments,
    merge_subtitles
)

# In-memory registry of active and completed lecture jobs
ACTIVE_JOBS: Dict[str, Dict[str, Any]] = {}

async def run_lecture_generation_job(job_id: str, request: LectureCreateRequest):
    """
    Asynchronous end-to-end pipeline execution for a lecture job.
    """
    job_dir = JOBS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    job_state = ACTIVE_JOBS[job_id]
    total_slides = len(request.slides)
    job_state["total_slides"] = total_slides

    try:
        slide_images = []
        audio_files = []
        srt_files = []
        durations = []
        segment_files = []

        # -------------------------------------------------------------
        # STEP 1: Generate High-Resolution Slide Images
        # -------------------------------------------------------------
        job_state["status"] = "generating_slides"
        job_state["current_step"] = "Rendering 1080p slide images"
        job_state["progress"] = 10

        for idx, slide in enumerate(request.slides, start=1):
            slide_img_path = job_dir / f"slide_{idx:02d}.png"
            render_slide_image(
                slide_title=slide.title,
                bullet_points=slide.bullet_points,
                slide_number=idx,
                total_slides=total_slides,
                output_path=slide_img_path,
                lecture_title=request.lecture_title,
                theme_key=request.theme,
                code_snippet=slide.code_snippet
            )
            slide_images.append(slide_img_path)

        # -------------------------------------------------------------
        # STEP 2: Synthesize Voice Narration & Word Timestamps (TTS)
        # -------------------------------------------------------------
        job_state["status"] = "synthesizing_audio"
        for idx, slide in enumerate(request.slides, start=1):
            pct = 15 + int((idx / total_slides) * 35) # 15% -> 50%
            job_state["progress"] = pct
            job_state["current_step"] = f"Synthesizing voice narration for slide {idx}/{total_slides}"

            audio_path = job_dir / f"audio_{idx:02d}.mp3"
            srt_path = job_dir / f"subtitles_{idx:02d}.srt"
            vtt_path = job_dir / f"subtitles_{idx:02d}.vtt"

            dur = await synthesize_speech(
                text=slide.spoken_script,
                output_audio_path=audio_path,
                output_srt_path=srt_path,
                output_vtt_path=vtt_path,
                voice=request.voice_profile
            )
            audio_files.append(audio_path)
            srt_files.append(srt_path)
            durations.append(dur)

        # -------------------------------------------------------------
        # STEP 3: Video Segment Compositing via FFmpeg
        # -------------------------------------------------------------
        job_state["status"] = "rendering_segments"
        for idx in range(total_slides):
            pct = 50 + int(((idx + 1) / total_slides) * 35) # 50% -> 85%
            job_state["progress"] = pct
            job_state["current_step"] = f"Compositing video segment {idx + 1}/{total_slides}"

            segment_path = job_dir / f"segment_{idx + 1:02d}.mp4"
            render_slide_segment(
                slide_image=slide_images[idx],
                audio_file=audio_files[idx],
                subtitle_file=srt_files[idx],
                duration=durations[idx],
                output_segment=segment_path,
                burn_subtitles=request.burn_subtitles,
                ken_burns=request.ken_burns_effect
            )
            segment_files.append(segment_path)

        # -------------------------------------------------------------
        # STEP 4: Concatenation and Final Subtitle Assembly
        # -------------------------------------------------------------
        job_state["status"] = "muxing"
        job_state["progress"] = 90
        job_state["current_step"] = "Muxing final video and synchronizing master captions"

        final_video_path = job_dir / "final_lecture.mp4"
        concatenate_segments(segment_files, final_video_path)

        final_srt_path = job_dir / "final_subtitles.srt"
        final_vtt_path = job_dir / "final_subtitles.vtt"
        merge_subtitles(srt_files, durations, final_srt_path, final_vtt_path)

        total_duration = sum(durations)

        # -------------------------------------------------------------
        # SUCCESS STATE
        # -------------------------------------------------------------
        job_state["status"] = "completed"
        job_state["progress"] = 100
        job_state["current_step"] = "Lecture ready for playback & download"
        job_state["video_url"] = f"/storage/jobs/{job_id}/final_lecture.mp4"
        job_state["srt_url"] = f"/storage/jobs/{job_id}/final_subtitles.srt"
        job_state["vtt_url"] = f"/storage/jobs/{job_id}/final_subtitles.vtt"
        job_state["total_duration_seconds"] = round(total_duration, 2)
        job_state["completed_at"] = datetime.now().isoformat()

    except Exception as e:
        tb = traceback.format_exc()
        print(f"Error in job {job_id}:\n{tb}")
        job_state["status"] = "failed"
        job_state["progress"] = 0
        job_state["error_message"] = str(e)
        job_state["current_step"] = f"Failed: {str(e)}"
