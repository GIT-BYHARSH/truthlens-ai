# TruthLens AI — FastAPI backend (Render / Docker)
FROM python:3.12-slim-bookworm

WORKDIR /app

# EasyOCR / OpenCV runtime libs (CPU)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install CPU torch first so EasyOCR does not pull a huge CUDA wheel.
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt

COPY app ./app
RUN mkdir -p /app/uploads

ENV PYTHONUNBUFFERED=1 \
    APP_ENV=production \
    DEBUG=false \
    UPLOAD_DIR=/app/uploads \
    PORT=10000

EXPOSE 10000

# Render injects $PORT; bind on 0.0.0.0 for public traffic.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --app-dir ."]
