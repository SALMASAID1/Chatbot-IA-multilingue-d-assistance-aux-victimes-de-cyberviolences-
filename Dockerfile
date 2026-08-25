# ─────────────────────────────────────────────────────────────────────────────
# EMC Helpline — backend image for Hugging Face Spaces (SDK: docker)
#
# Hugging Face requires the Dockerfile at the repository root and serves the
# container on port 7860. See docs/guide_deploiement.md for the full procedure.
#
# Two build-time decisions make the demo reliable:
#   1. The embedding model is downloaded during the build, so the first user
#      request never waits on a 458 MB download.
#   2. The Chroma vector store is built during the build, so the container
#      starts deterministically with 748 vectors already in place.
# Together they turn a ~30 s first-request penalty into a warm start.
#
# torch is installed from PyTorch's CPU index: the default wheel bundles CUDA
# libraries (~2 GB) that are useless on the free CPU tier.
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim

# Hugging Face Spaces runs containers as UID 1000.
RUN useradd -m -u 1000 user

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    HOME=/home/user \
    HF_HOME=/home/user/.cache/huggingface \
    PATH=/home/user/.local/bin:$PATH

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc curl \
    && rm -rf /var/lib/apt/lists/*

USER user
WORKDIR /home/user/app

# ── Dependencies ────────────────────────────────────────────────────────────
COPY --chown=user requirements.txt ./
# CPU-only torch first, so the resolver does not pull the CUDA build afterwards.
RUN pip install --no-cache-dir --user torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir --user -r requirements.txt

# ── Application code and knowledge base ─────────────────────────────────────
COPY --chown=user backend/ ./backend/
COPY --chown=user data/knowledge_base/ ./data/knowledge_base/
COPY --chown=user docs/livrable-1/ ./docs/livrable-1/

# ── Bake the embedding model into the image ─────────────────────────────────
RUN python -c "\
from huggingface_hub import snapshot_download; \
snapshot_download('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')"

# ── Build the vector store into the image (no Gemini call, no API key needed) ─
RUN python -m backend.rag.embeddings

# The model is present locally: refuse to reach the network at runtime.
ENV EMBEDDING_LOCAL_FILES_ONLY=true \
    API_HOST=0.0.0.0 \
    API_PORT=7860

# GOOGLE_API_KEY, ADMIN_API_KEY and CORS_ORIGINS are injected by the Space's
# "Secrets and variables" panel — never baked into the image.

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -fsS http://localhost:7860/api/health || exit 1

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
