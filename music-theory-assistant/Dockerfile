# music-theory-assistant/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# System deps if you need them (uncomment as needed)
# RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

# Copy just the requirements first for better layer caching
COPY music-theory-assistant/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy app code
COPY music-theory-assistant/ /app/

# Default envs can be overridden by compose
ENV QDRANT_URL=http://qdrant:6333
ENV QDRANT_COLLECTION=zoomcamp-music-theory-assistant
ENV EMBED_MODEL=jinaai/jina-embeddings-v2-small-en
ENV EMBED_DIM=512
ENV TOP_K=5

# Expose (optional; Compose does host mapping anyway)
EXPOSE 8501
EXPOSE 8000
