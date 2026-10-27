# ==============================================================================
# LecturaFlow Studio - Production Hugging Face Space & Cloud Container
# ==============================================================================
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860

# Install system dependencies: FFmpeg and TrueType fonts for 1080p slide rasterization
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    fonts-dejavu-core \
    fonts-freefont-ttf \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create user with UID 1000 for Hugging Face Spaces compatibility
RUN useradd -m -u 1000 user
USER root

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application codebase
COPY app/ ./app/
COPY run.py .
COPY sample_lectures/ ./sample_lectures/

# Create runtime storage directories and assign permissions
RUN mkdir -p storage/uploads storage/jobs storage/previews \
    && chown -R 1000:1000 /app

USER user

# Expose default Hugging Face Spaces port
EXPOSE 7860

# Launch production server with dynamic port fallback
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
