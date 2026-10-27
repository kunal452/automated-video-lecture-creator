import asyncio
import re
from pathlib import Path
from typing import Tuple, Dict, Any, List
import edge_tts
from mutagen.mp3 import MP3

def srt_to_vtt(srt_content: str) -> str:
    """Converts SubRip (SRT) format to WebVTT format for HTML5 video players."""
    vtt = ["WEBVTT\n"]
    for line in srt_content.splitlines():
        # Replace comma with period in timestamps: 00:00:01,234 -> 00:00:01.234
        line = re.sub(r"(\d{2}:\d{2}:\d{2}),(\d{3})", r"\1.\2", line)
        vtt.append(line)
    return "\n".join(vtt)

async def synthesize_speech(
    text: str,
    output_audio_path: Path,
    output_srt_path: Path,
    output_vtt_path: Path,
    voice: str = "en-US-ChristopherNeural"
) -> float:
    """
    Synthesizes speech using edge-tts, generates word-aligned SRT & VTT subtitles,
    and returns the audio duration in seconds.
    """
    output_audio_path.parent.mkdir(parents=True, exist_ok=True)
    clean_text = text.strip()
    if not clean_text:
        clean_text = "Continuing to the next topic."

    communicate = edge_tts.Communicate(clean_text, voice)
    submaker = edge_tts.SubMaker()

    with open(output_audio_path, "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.feed(chunk)

    srt_text = submaker.get_srt()
    if not srt_text.strip():
        # Fallback subtitle if no word boundaries fired
        srt_text = f"1\n00:00:00,000 --> 00:00:05,000\n{clean_text[:60]}...\n"

    with open(output_srt_path, "w", encoding="utf-8") as srt_file:
        srt_file.write(srt_text)

    with open(output_vtt_path, "w", encoding="utf-8") as vtt_file:
        vtt_file.write(srt_to_vtt(srt_text))

    # Read precise duration
    try:
        audio = MP3(str(output_audio_path))
        duration = float(audio.info.length)
    except Exception:
        # Fallback estimation if mutagen fails: ~150 words per minute
        duration = max(3.0, len(clean_text.split()) / 2.5)

    return duration
