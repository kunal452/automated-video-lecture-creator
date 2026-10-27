import sys
import uvicorn
from app.config import FFMPEG_EXE

# Ensure UTF-8 output handling on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

if __name__ == "__main__":
    print("=" * 70)
    print("[*] AUTOMATED VIDEO LECTURE CREATOR - INITIALIZING")
    print("=" * 70)
    print(f"[*] Detected FFmpeg Engine: {FFMPEG_EXE}")
    print("[*] Starting Web Studio Dashboard on: http://127.0.0.1:8000")
    print("[*] Interactive Swagger API Docs:    http://127.0.0.1:8000/docs")
    print("=" * 70)
    
    # Run the server
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
