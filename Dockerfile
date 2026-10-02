FROM python:3.11-slim

RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install CPU-only torch to prevent OOM & save ~2GB disk on cloud containers
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

COPY . .
RUN mkdir -p data && chown -R appuser:appuser /app

USER appuser

EXPOSE 8080

# Dynamically bind to cloud provider $PORT (Render, Cloud Run, etc.) or default to 8080
CMD ["sh", "-c", "uvicorn app.gateway:app --host 0.0.0.0 --port ${PORT:-8080}"]
