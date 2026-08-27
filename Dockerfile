# Multi-Platform Production Dockerfile for Agri Nirvana FastAPI AI Backend
# Compatible with: Hugging Face Spaces, Railway, Koyeb, Fly.io, Cloud Run, AWS App Runner, Docker Compose

FROM python:3.11-slim AS base

# System dependencies for OpenCV, PyTorch, and LibGL
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copy backend application source code
COPY backend/ /app/backend/

# Create non-root user for security (required by Hugging Face Spaces & security standards)
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/backend/db /app/backend/uploads && \
    chown -R appuser:appuser /app

USER appuser

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    AI_MODEL_PROVIDER=real \
    AI_CONFIDENCE_THRESHOLD=0.70 \
    MAX_IMAGE_SIZE_MB=10 \
    ALLOWED_ORIGINS="https://agri-nirvana.vercel.app,http://localhost:5173,http://localhost:3000"

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

EXPOSE 8000 7860

# Start FastAPI server using dynamic PORT environment variable
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
