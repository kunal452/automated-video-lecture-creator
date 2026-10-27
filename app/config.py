import os
import sys
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"
STORAGE_DIR = BASE_DIR / "storage"
UPLOADS_DIR = STORAGE_DIR / "uploads"
JOBS_DIR = STORAGE_DIR / "jobs"

# Ensure runtime directories exist
for folder in [STORAGE_DIR, UPLOADS_DIR, JOBS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# FFmpeg Executable Resolution
def get_ffmpeg_binary() -> str:
    """Finds FFmpeg via imageio-ffmpeg or system PATH."""
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and os.path.exists(exe):
            return exe
    except Exception:
        pass
    return "ffmpeg"

FFMPEG_EXE = get_ffmpeg_binary()

# Supported Edge-TTS Voice Catalog
VOICE_PROFILES = [
    {
        "id": "en-US-ChristopherNeural",
        "name": "Christopher (US Male - Professional Lecturer)",
        "gender": "Male",
        "locale": "en-US",
        "is_default": True
    },
    {
        "id": "en-US-JennyNeural",
        "name": "Jenny (US Female - Clear & Engaging)",
        "gender": "Female",
        "locale": "en-US",
        "is_default": False
    },
    {
        "id": "en-US-GuyNeural",
        "name": "Guy (US Male - Conversational)",
        "gender": "Male",
        "locale": "en-US",
        "is_default": False
    },
    {
        "id": "en-US-AriaNeural",
        "name": "Aria (US Female - Academic & Formal)",
        "gender": "Female",
        "locale": "en-US",
        "is_default": False
    },
    {
        "id": "en-GB-RyanNeural",
        "name": "Ryan (British Male - Authoritative)",
        "gender": "Male",
        "locale": "en-GB",
        "is_default": False
    },
    {
        "id": "en-GB-SoniaNeural",
        "name": "Sonia (British Female - Crisp & Articulate)",
        "gender": "Female",
        "locale": "en-GB",
        "is_default": False
    },
    {
        "id": "en-IN-PrabhatNeural",
        "name": "Prabhat (Indian Male - Clear Technical Accent)",
        "gender": "Male",
        "locale": "en-IN",
        "is_default": False
    },
    {
        "id": "en-IN-NeerjaNeural",
        "name": "Neerja (Indian Female - Expressive & Melodic)",
        "gender": "Female",
        "locale": "en-IN",
        "is_default": False
    }
]

# Slide Styling Themes
SLIDE_THEMES = {
    "dark_modern": {
        "name": "Modern Slate (Dark)",
        "bg_color": "#0F172A",
        "card_bg": "#1E293B",
        "accent_color": "#38BDF8",
        "title_color": "#F8FAFC",
        "text_color": "#CBD5E1",
        "code_bg": "#0B1120",
        "code_text": "#38BDF8",
        "footer_color": "#64748B"
    },
    "deep_navy": {
        "name": "Academic Navy",
        "bg_color": "#0A192F",
        "card_bg": "#112240",
        "accent_color": "#64FFDA",
        "title_color": "#CCD6F6",
        "text_color": "#8892B0",
        "code_bg": "#020C1B",
        "code_text": "#64FFDA",
        "footer_color": "#495670"
    },
    "emerald": {
        "name": "Emerald Studio",
        "bg_color": "#062820",
        "card_bg": "#0C3C30",
        "accent_color": "#34D399",
        "title_color": "#ECFDF5",
        "text_color": "#A7F3D0",
        "code_bg": "#031713",
        "code_text": "#6EE7B7",
        "footer_color": "#059669"
    },
    "minimal_light": {
        "name": "Minimal Clean (Light)",
        "bg_color": "#F8FAFC",
        "card_bg": "#FFFFFF",
        "accent_color": "#2563EB",
        "title_color": "#0F172A",
        "text_color": "#334155",
        "code_bg": "#F1F5F9",
        "code_text": "#1E40AF",
        "footer_color": "#94A3B8"
    },
    "cyber_violet": {
        "name": "Cyberpunk Violet",
        "bg_color": "#0D091A",
        "card_bg": "#1A102F",
        "accent_color": "#C084FC",
        "title_color": "#FAF5FF",
        "text_color": "#E9D5FF",
        "code_bg": "#120A24",
        "code_text": "#F472B6",
        "footer_color": "#A855F7"
    }
}
