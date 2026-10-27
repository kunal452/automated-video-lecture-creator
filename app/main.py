import uuid
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from app.config import (
    BASE_DIR,
    APP_DIR,
    STORAGE_DIR,
    UPLOADS_DIR,
    JOBS_DIR,
    VOICE_PROFILES,
    SLIDE_THEMES,
    FFMPEG_EXE
)
from app.models import (
    LectureCreateRequest,
    GenerateFromTopicRequest,
    JobStatusResponse,
    SlideData
)
from app.services.document_parser import parse_pdf, parse_pptx, parse_text_notes
from app.services.script_engine import generate_curriculum_heuristically, generate_via_gemini_or_openai
from app.services.tts_engine import synthesize_speech
from app.workers.orchestrator import ACTIVE_JOBS, run_lecture_generation_job

app = FastAPI(
    title="Automated Video Lecture Creator API",
    description="End-to-end Automated Video Lecture Generation Pipeline with AI Scripting, Edge-TTS, and FFmpeg Compositing.",
    version="1.0.0"
)

# Enable CORS for frontend flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static web UI assets and storage directory
static_dir = APP_DIR / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
app.mount("/storage", StaticFiles(directory=str(STORAGE_DIR)), name="storage")

@app.get("/")
async def root():
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Automated Video Lecture Creator API is running. Access /docs for Swagger."}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "ffmpeg_path": FFMPEG_EXE,
        "active_jobs_count": len(ACTIVE_JOBS)
    }

@app.get("/api/voices")
async def get_voices():
    """Returns the catalog of supported high-fidelity edge voices."""
    return VOICE_PROFILES

@app.get("/api/themes")
async def get_themes():
    """Returns available slide visual styling themes."""
    return SLIDE_THEMES

@app.post("/api/generate-from-topic")
async def generate_from_topic(request: GenerateFromTopicRequest):
    """
    Expands a raw topic into a structured slide deck with spoken lecturer narration.
    """
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")

    slides_data = generate_via_gemini_or_openai(
        topic=request.topic,
        num_slides=request.num_slides,
        audience=request.audience_level,
        provider=request.llm_provider,
        api_key=request.api_key
    )
    return {
        "lecture_title": request.topic.title(),
        "slides": slides_data
    }

@app.post("/api/upload-document")
async def upload_document(file: UploadFile = File(...)):
    """
    Parses an uploaded PDF, PPTX, or text file into structured slides.
    """
    ext = Path(file.filename).suffix.lower()
    temp_upload_path = UPLOADS_DIR / f"{uuid.uuid4()}_{file.filename}"

    with open(temp_upload_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        if ext == ".pdf":
            slides = parse_pdf(temp_upload_path)
        elif ext in [".pptx", ".ppt"]:
            slides = parse_pptx(temp_upload_path)
        elif ext in [".txt", ".md"]:
            content = temp_upload_path.read_text(encoding="utf-8")
            slides = parse_text_notes(content)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload PDF, PPTX, or TXT.")

        clean_title = Path(file.filename).stem.replace("_", " ").title()
        return {
            "lecture_title": clean_title,
            "slides": slides
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse document: {str(e)}")

@app.get("/api/sample-decks")
async def get_sample_decks():
    """Returns curated demo lecture decks for instant 1-click loading."""
    return {
        "cnn": {
            "lecture_title": "Convolutional Neural Networks: Deep Visual Perception",
            "voice_profile": "en-US-ChristopherNeural",
            "theme": "dark_modern",
            "slides": [
                {
                    "index": 1,
                    "title": "Biological Foundations of CNNs",
                    "bullet_points": [
                        "Hubel & Wiesel: Receptive fields in mammalian visual cortex",
                        "Hierarchical processing: From edge detectors to semantic entities",
                        "Spatial invariance and parameter reduction vs dense MLPs"
                    ],
                    "code_snippet": "import torch\nimport torch.nn as nn\n\n# 2D Convolution with 16 filters\nlayer = nn.Conv2d(in_channels=3, out_channels=16, kernel_size=3, padding=1)",
                    "spoken_script": "Welcome to our lecture on Convolutional Neural Networks. In this opening section, we examine the biological motivation behind spatial filtering and discover how hierarchical convolutions overcome the parameter explosion of traditional dense layers."
                },
                {
                    "index": 2,
                    "title": "Convolution Operations & Feature Maps",
                    "bullet_points": [
                        "Kernel cross-correlation sliding across spatial dimensions",
                        "Stride (S) and Zero-Padding (P) determine output resolution",
                        "Feature maps capture translation-invariant local patterns"
                    ],
                    "code_snippet": "# Spatial output dimension formula\n# Output = floor((Input - Kernel + 2*Pad) / Stride) + 1",
                    "spoken_script": "As the kernel moves across our input image, it performs localized dot products. Stride controls downsampling speed, while zero-padding preserves border information, producing activation feature maps."
                },
                {
                    "index": 3,
                    "title": "Downsampling: Max & Average Pooling",
                    "bullet_points": [
                        "Max Pooling: Extracts prominent activation features",
                        "Average Pooling: Aggregates global spatial contextual averages",
                        "Decreases memory footprint and mitigates overfitting"
                    ],
                    "code_snippet": "pool = nn.MaxPool2d(kernel_size=2, stride=2)",
                    "spoken_script": "Following convolutional feature extraction, pooling layers progressively compress the spatial volume. Max pooling selects the strongest signal in each window, providing spatial robustness and computational efficiency."
                },
                {
                    "index": 4,
                    "title": "Modern Horizons: ResNets to Vision Transformers",
                    "bullet_points": [
                        "Residual skip connections: Solving vanishing gradients in deep nets",
                        "Self-attention mechanisms: Global receptive fields in ViTs",
                        "Next Session: Hands-on fine-tuning with PyTorch & Hugging Face"
                    ],
                    "code_snippet": "# Residual Connection\nx_out = f(x) + x",
                    "spoken_script": "In modern production architectures, residual skip connections enable the training of models with hundreds of layers. In our next workshop, we will contrast CNNs against modern Vision Transformers. Thank you."
                }
            ]
        },
        "microservices": {
            "lecture_title": "Modern Distributed Systems & Microservices",
            "voice_profile": "en-GB-RyanNeural",
            "theme": "deep_navy",
            "slides": [
                {
                    "index": 1,
                    "title": "Decomposing the Monolith",
                    "bullet_points": [
                        "Bounded contexts and Domain-Driven Design (DDD)",
                        "Independent deployability and granular horizontal scaling",
                        "Organizational alignment: Conway's Law in practice"
                    ],
                    "code_snippet": "service OrderService {\n  rpc CreateOrder(OrderRequest) returns (OrderResponse);\n}",
                    "spoken_script": "Welcome to our masterclass on Microservices Architecture. Today, we dissect how decomposing monolithic systems into domain-oriented, independently deployable services unlocks enterprise agility and fault isolation."
                },
                {
                    "index": 2,
                    "title": "Inter-Service Communication Protocols",
                    "bullet_points": [
                        "Synchronous: High-performance gRPC vs RESTful HTTP/JSON",
                        "Asynchronous: Event streams via Apache Kafka & RabbitMQ",
                        "Resilience engineering: Circuit breakers, timeouts, and fallbacks"
                    ],
                    "code_snippet": "circuit_breaker.execute(() -> paymentClient.charge(amount));",
                    "spoken_script": "Connecting dozens of decoupled services requires robust transport protocols. We balance synchronous low-latency gRPC calls against asynchronous event streams to decouple producers from consumers."
                },
                {
                    "index": 3,
                    "title": "Distributed Consistency & The Saga Pattern",
                    "bullet_points": [
                        "The fallacies of distributed computing and the CAP Theorem",
                        "Eventual consistency replacing two-phase commit locks",
                        "Orchestrated vs Choreographed compensating transactions"
                    ],
                    "code_snippet": "",
                    "spoken_script": "In distributed persistence, traditional database transactions cannot span network boundaries. We utilize the Saga pattern, executing compensating transactions to guarantee eventual consistency across disparate datastores."
                }
            ]
        },
        "quantum": {
            "lecture_title": "Quantum Computing & Qubit Principles",
            "voice_profile": "en-US-JennyNeural",
            "theme": "cyber_violet",
            "slides": [
                {
                    "index": 1,
                    "title": "The Quantum Advantage & Qubits",
                    "bullet_points": [
                        "Superposition: Linear combinations of |0> and |1> states",
                        "Bloch Sphere representation and probability amplitudes",
                        "Exponential Hilbert state space scaling (2^N states)"
                    ],
                    "code_snippet": "from qiskit import QuantumCircuit\n\nqc = QuantumCircuit(2, 2)\nqc.h(0)  # Hadamard gate for superposition\nqc.cx(0, 1)  # CNOT gate for entanglement",
                    "spoken_script": "Welcome to our overview of Quantum Computing. Unlike classical bits that exist strictly in zero or one, quantum bits leverage superposition to exist as probability amplitudes across complex multi-dimensional Hilbert spaces."
                },
                {
                    "index": 2,
                    "title": "Quantum Entanglement & Bell States",
                    "bullet_points": [
                        "Spooky action at a distance: Correlated composite systems",
                        "Non-local quantum measurements violating Bell inequalities",
                        "Applications in Quantum Key Distribution (QKD) and teleportation"
                    ],
                    "code_snippet": "# Bell State Preparation: |Phi+> = (|00> + |11>) / sqrt(2)\nqc.measure([0, 1], [0, 1])",
                    "spoken_script": "When two qubits become entangled, the state of one cannot be described independently of the other. Einstein famously termed this spooky action at a distance, yet today it forms the cryptographic basis for quantum teleportation."
                },
                {
                    "index": 3,
                    "title": "Noisy Intermediate-Scale Quantum (NISQ)",
                    "bullet_points": [
                        "Environmental decoherence and quantum error mitigation",
                        "Variational Quantum Eigensolvers (VQE) for molecular chemistry",
                        "The road to fault-tolerant topological quantum error correction"
                    ],
                    "code_snippet": "",
                    "spoken_script": "We currently operate in the NISQ era, where quantum systems are prone to environmental thermal noise. Near-term hybrid quantum-classical algorithms like VQE pave the way toward fault-tolerant computing."
                }
            ]
        },
        "python_async": {
            "lecture_title": "High-Throughput Concurrency in Python",
            "voice_profile": "en-US-ChristopherNeural",
            "theme": "emerald",
            "slides": [
                {
                    "index": 1,
                    "title": "The Python Global Interpreter Lock (GIL)",
                    "bullet_points": [
                        "CPU-bound vs I/O-bound bottlenecks in system design",
                        "Threading vs Multiprocessing vs Coroutine event loops",
                        "Why async/await handles 50,000+ concurrent connections"
                    ],
                    "code_snippet": "import asyncio\n\nasync def fetch_api(url: str):\n    async with httpx.AsyncClient() as client:\n        return await client.get(url)",
                    "spoken_script": "Welcome. In this lecture, we demystify Python concurrency. While the Global Interpreter Lock limits true multi-core CPU parallelism in threads, non-blocking asynchronous event loops allow Python to comfortably handle tens of thousands of simultaneous I/O connections."
                },
                {
                    "index": 2,
                    "title": "Task Orchestration: asyncio.gather & TaskGroup",
                    "bullet_points": [
                        "Cooperative multitasking and yield points",
                        "Structured concurrency with Python 3.11+ TaskGroup",
                        "Graceful exception propagation and cancellation semantics"
                    ],
                    "code_snippet": "async with asyncio.TaskGroup() as tg:\n    task1 = tg.create_task(load_users())\n    task2 = tg.create_task(load_metrics())",
                    "spoken_script": "Python 3.11 introduced TaskGroups, bringing modern structured concurrency to async programming. If any child task fails, sibling tasks are cleanly cancelled, preventing silent resource leaks."
                }
            ]
        }
    }

@app.post("/api/preview-voice")
async def preview_voice(
    voice: str = Form("en-US-ChristopherNeural"),
    text: Optional[str] = Form(None)
):
    """Generates an audio sample for voice preview or specific slide narration."""
    clean_sample = text.strip() if text and text.strip() else "Welcome! This is how your lecture narration will sound with this voice profile."
    sample_hash = abs(hash(voice + clean_sample[:40]))
    preview_id = f"preview_{voice.replace(':', '_')}_{sample_hash}"
    preview_dir = STORAGE_DIR / "previews"
    preview_dir.mkdir(exist_ok=True)
    audio_path = preview_dir / f"{preview_id}.mp3"
    srt_path = preview_dir / f"{preview_id}.srt"
    vtt_path = preview_dir / f"{preview_id}.vtt"

    if not audio_path.exists():
        await synthesize_speech(clean_sample, audio_path, srt_path, vtt_path, voice=voice)

    return {"audio_url": f"/storage/previews/{preview_id}.mp3"}

@app.post("/api/lectures/create")
async def create_lecture_job(request: LectureCreateRequest, background_tasks: BackgroundTasks):
    """
    Initiates asynchronous lecture video generation pipeline.
    """
    if not request.slides:
        raise HTTPException(status_code=400, detail="At least one slide is required")

    job_id = str(uuid.uuid4())
    ACTIVE_JOBS[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "progress": 0,
        "current_step": "Job queued in processing queue",
        "total_slides": len(request.slides),
        "video_url": None,
        "srt_url": None,
        "vtt_url": None,
        "total_duration_seconds": None,
        "error_message": None,
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
        "title": request.lecture_title
    }

    # Dispatch to asynchronous background processing
    background_tasks.add_task(run_lecture_generation_job, job_id, request)

    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Lecture creation task dispatched successfully."
    }

@app.get("/api/lectures/{job_id}/status")
async def get_job_status(job_id: str):
    """Polls real-time progress of a lecture generation job."""
    if job_id not in ACTIVE_JOBS:
        # Check if job exists on disk
        job_dir = JOBS_DIR / job_id
        final_video = job_dir / "final_lecture.mp4"
        if final_video.exists():
            return {
                "job_id": job_id,
                "status": "completed",
                "progress": 100,
                "current_step": "Ready",
                "total_slides": 1,
                "video_url": f"/storage/jobs/{job_id}/final_lecture.mp4",
                "srt_url": f"/storage/jobs/{job_id}/final_subtitles.srt",
                "vtt_url": f"/storage/jobs/{job_id}/final_subtitles.vtt"
            }
        raise HTTPException(status_code=404, detail="Job not found")

    return ACTIVE_JOBS[job_id]

@app.get("/api/lectures/recent")
async def get_recent_lectures():
    """Lists completed lectures available on disk."""
    items = []
    if JOBS_DIR.exists():
        for job_folder in sorted(JOBS_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)[:10]:
            if job_folder.is_dir():
                video = job_folder / "final_lecture.mp4"
                if video.exists():
                    items.append({
                        "job_id": job_folder.name,
                        "video_url": f"/storage/jobs/{job_folder.name}/final_lecture.mp4",
                        "size_mb": round(video.stat().st_size / (1024 * 1024), 2),
                        "modified": datetime.fromtimestamp(video.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                    })
    return items
