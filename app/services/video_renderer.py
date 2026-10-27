import subprocess
import re
from pathlib import Path
from typing import List
from app.config import FFMPEG_EXE
from app.services.tts_engine import srt_to_vtt

def format_ffmpeg_path(p: Path) -> str:
    """Formats path for FFmpeg filtergraph escaping colons and backslashes."""
    s = str(p.resolve()).replace("\\", "/")
    # Windows drive letter colon escaping
    return s.replace(":", "\\:")

def render_slide_segment(
    slide_image: Path,
    audio_file: Path,
    subtitle_file: Path,
    duration: float,
    output_segment: Path,
    burn_subtitles: bool = True,
    ken_burns: bool = False
) -> Path:
    """
    Renders an individual slide segment into a 1080p MP4 with audio and optional burned subtitles.
    """
    output_segment.parent.mkdir(parents=True, exist_ok=True)
    filters = ["scale=1920:1080", "format=yuv420p"]

    if ken_burns:
        # Subtle slow cinematic zoom
        fps = 30
        total_frames = int(duration * fps)
        filters.insert(0, f"zoompan=z='min(zoom+0.0006,1.06)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080")

    if burn_subtitles and subtitle_file.exists():
        escaped_srt = format_ffmpeg_path(subtitle_file)
        sub_filter = (
            f"subtitles='{escaped_srt}':force_style="
            "'FontName=Arial,FontSize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=3,MarginV=30'"
        )
        filters.append(sub_filter)

    vf_string = ",".join(filters)

    cmd = [
        FFMPEG_EXE, "-y",
        "-loop", "1",
        "-framerate", "30",
        "-t", f"{duration:.3f}",
        "-i", str(slide_image.resolve()),
        "-i", str(audio_file.resolve()),
        "-vf", vf_string,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(output_segment.resolve())
    ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        # If subtitle filter fails (e.g. fontconfig/libass glitch), fallback without subtitles
        if burn_subtitles:
            fallback_cmd = [
                FFMPEG_EXE, "-y",
                "-loop", "1",
                "-framerate", "30",
                "-t", f"{duration:.3f}",
                "-i", str(slide_image.resolve()),
                "-i", str(audio_file.resolve()),
                "-vf", "scale=1920:1080,format=yuv420p",
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-crf", "22",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                str(output_segment.resolve())
            ]
            fallback_res = subprocess.run(fallback_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if fallback_res.returncode != 0:
                raise RuntimeError(f"FFmpeg failed: {fallback_res.stderr}")
        else:
            raise RuntimeError(f"FFmpeg failed: {result.stderr}")

    return output_segment

def concatenate_segments(segment_paths: List[Path], final_video_path: Path) -> Path:
    """
    Concatenates multiple slide video segments using FFmpeg's concat demuxer.
    """
    final_video_path.parent.mkdir(parents=True, exist_ok=True)
    concat_list_file = final_video_path.parent / "concat_list.txt"

    with open(concat_list_file, "w", encoding="utf-8") as f:
        for seg in segment_paths:
            normalized = str(seg.resolve()).replace("\\", "/")
            f.write(f"file '{normalized}'\n")

    cmd = [
        FFMPEG_EXE, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list_file.resolve()),
        "-c", "copy",
        str(final_video_path.resolve())
    ]

    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg concatenation failed: {res.stderr}")

    return final_video_path

def offset_srt_timestamp(ts_str: str, offset_seconds: float) -> str:
    """Adds offset_seconds to HH:MM:SS,mmm timestamp."""
    match = re.match(r"(\d{2}):(\d{2}):(\d{2}),(\d{3})", ts_str)
    if not match:
        return ts_str
    h, m, s, ms = map(int, match.groups())
    total_ms = (h * 3600 + m * 60 + s) * 1000 + ms + int(offset_seconds * 1000)
    
    new_h = total_ms // 3600000
    total_ms %= 3600000
    new_m = total_ms // 60000
    total_ms %= 60000
    new_s = total_ms // 1000
    new_ms = total_ms % 1000
    return f"{new_h:02d}:{new_m:02d}:{new_s:02d},{new_ms:03d}"

def merge_subtitles(srt_files: List[Path], durations: List[float], final_srt_path: Path, final_vtt_path: Path):
    """
    Merges individual slide subtitles into a single timeline for the entire video.
    """
    cumulative_offset = 0.0
    merged_entries = []
    global_index = 1

    for srt_path, dur in zip(srt_files, durations):
        if not srt_path.exists():
            cumulative_offset += dur
            continue

        content = srt_path.read_text(encoding="utf-8")
        blocks = content.strip().split("\n\n")

        for block in blocks:
            lines = block.strip().split("\n")
            if len(lines) >= 3 and "-->" in lines[1]:
                times = lines[1].split("-->")
                start_ts = offset_srt_timestamp(times[0].strip(), cumulative_offset)
                end_ts = offset_srt_timestamp(times[1].strip(), cumulative_offset)
                text_lines = "\n".join(lines[2:])
                merged_entries.append(f"{global_index}\n{start_ts} --> {end_ts}\n{text_lines}")
                global_index += 1

        cumulative_offset += dur

    full_srt = "\n\n".join(merged_entries)
    final_srt_path.write_text(full_srt, encoding="utf-8")
    final_vtt_path.write_text(srt_to_vtt(full_srt), encoding="utf-8")
