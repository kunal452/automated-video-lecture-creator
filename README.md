---
title: LecturaFlow Studio
emoji: 🎓
colorFrom: orange
colorTo: red
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# LecturaFlow — Automated Video Lecture Creator 🎓🎥
> **Automated End-to-End AI Video Lecture Production System**

An end-to-end automated platform that transforms raw academic notes, presentation slides (`.pptx`, `.pdf`), or simple topic prompts into professional 1080p video lectures with natural AI teacher narration, synchronized subtitles (`.srt`/`.vtt`), and slide transitions.

---

## 🌟 Key Features & Innovations

1. **Multi-Modal Ingestion Pipeline**:
   - **Topic-to-Lecture Engine**: Input any concept (e.g., *Quantum Computing*, *Convolutional Neural Networks*) to auto-generate a complete curriculum and conversational spoken narration.
   - **Document Parser**: Ingests raw `.pdf` documents and PowerPoint `.pptx` decks, extracting slide structures, bullet points, and presenter notes automatically.
2. **Pedagogical Speech Synthesis (TTS)**:
   - Powered by Microsoft Edge-TTS neural models (high naturalness, multi-accent, zero API cost).
   - Word boundary timestamp extraction for automated subtitle alignment.
3. **1080p Visual Slide Compositor**:
   - High-resolution (1920×1080) slide rendering with modern glassmorphism, accent borders, and code syntax blocks.
   - Multiple color themes (Slate Dark, Academic Navy, Emerald Studio, Minimal Light).
4. **Hardware-Accelerated FFmpeg Video Pipeline**:
   - Dynamic slide duration padding synchronized to speech runtime.
   - Burned-in custom subtitles and optional slow cinematic Ken Burns pan/zoom.
   - Lossless concatenation of multi-slide segments into a single downloadable `.mp4`.
5. **Interactive Web Studio**:
   - Modern HTML5/CSS glassmorphic UI.
   - Live 16:9 canvas slide previewer.
   - Interactive slide editor, voice sample player, live progress polling, and built-in HTML5 video player.

---

## 🏗️ System Architecture

```text
[Input Source] (Topic / PDF / PPTX / Markdown)
       │
       ▼
[1. Document Parser & Script Generator] (pypdf, python-pptx, Heuristic/Gemini LLM)
       │
       ▼
[2. Speech & Subtitle Synthesizer] (Edge-TTS + WordBoundary Timestamp Extractor)
       │
       ▼
[3. 1080p Slide Visualizer] (Pillow Card Layout, Typography, Code Blocks)
       │
       ▼
[4. Media Compositor & FFmpeg Muxer] (ImageIO-FFmpeg Libx264 + AAC + Subtitle Filter)
       │
       ▼
[Final Output] (1080p MP4 Video Lecture + Synchronized Subtitles)
```

---

## 📁 Project Directory Structure

```text
Automated video Leacture Creator/
├── app/
│   ├── __init__.py
│   ├── config.py              # Voice catalog, color themes, paths & FFmpeg detector
│   ├── main.py                # FastAPI endpoints, static mounts, and API routing
│   ├── models.py              # Pydantic schemas (Slide, LectureRequest, JobStatus)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── document_parser.py # PDF, PPTX, and Markdown text parsing
│   │   ├── script_engine.py   # Smart pedagogical expansion (Offline + LLM fallback)
│   │   ├── slide_renderer.py  # 1920x1080 programmatic slide image generator
│   │   ├── tts_engine.py      # Edge-TTS voice synthesis & SRT/VTT converter
│   │   └── video_renderer.py  # FFmpeg segment encoding & concatenation
│   ├── static/
│   │   ├── css/style.css      # Dark-mode glassmorphic styling
│   │   ├── js/app.js          # Reactive controller, canvas preview & polling
│   │   └── index.html         # Web studio dashboard
│   └── workers/
│       └── orchestrator.py    # Background pipeline task runner
├── database/
│   └── schema.sql             # PostgreSQL production schema for project report
├── sample_lectures/
│   ├── sample_slides.json     # Pre-built 4-slide lecture on CNNs
│   └── sample_notes.txt       # Sample notes on Microservices
├── storage/                   # Auto-generated outputs (MP4s, SRTs, PNGs, MP3s)
├── requirements.txt           # Python dependencies
├── run.py                     # Single-command application launcher
└── README.md                  # Project handbook & documentation
```

---

## 🚀 Quickstart Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch the Application
```bash
python run.py
```
Open your browser and navigate to:
👉 **`http://127.0.0.1:8000`**

Interactive API documentation (Swagger) is available at:
👉 **`http://127.0.0.1:8000/docs`**

---

## 📊 Database Schema (PostgreSQL DDL)
The relational schema used for persisting users, lecture projects, slides, audio tracks, and render deliverables is located at [`database/schema.sql`](file:///c:/Users/kunal/OneDrive/Documents/DOCUMENTS/Project/Automated%20video%20Leacture%20Creator/database/schema.sql).

---

## 🎯 Final Year Project Evaluation Notes
- **Zero Ongoing Cost**: All core features (Edge-TTS, Pillow, FFmpeg, Offline Heuristic Scripting) run completely free without requiring paid API keys or cloud GPUs.
- **Modularity**: Components are decoupled into specialized service modules (`document_parser`, `script_engine`, `slide_renderer`, `tts_engine`, `video_renderer`), making it straightforward to swap in custom local LLMs (Ollama) or avatars (SadTalker/Wav2Lip) as future milestones.
