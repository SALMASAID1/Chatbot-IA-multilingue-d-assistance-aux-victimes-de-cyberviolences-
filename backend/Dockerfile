FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Build the RAG assets into the image. The generated ChromaDB collection and
# Hugging Face model cache are then available immediately at runtime, without
# relying on Railway's ephemeral filesystem or a slow first-request download.
RUN python -m backend.rag.embeddings

# Expose the API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

# Start the API
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
