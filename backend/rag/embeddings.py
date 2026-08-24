"""Embeddings module: vectorization and ChromaDB storage."""
import hashlib
import logging
from functools import lru_cache
from typing import List, Optional, Tuple

import chromadb
from huggingface_hub import snapshot_download
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

import sys
import io
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import (
    EMBEDDING_MODEL,
    EMBEDDING_LOCAL_FILES_ONLY,
    CHROMA_PERSIST_DIR,
    CHROMA_COLLECTION_NAME,
)

logger = logging.getLogger(__name__)
_rag_runtime_status = "not_checked"


@lru_cache(maxsize=1)
def _resolve_embedding_source() -> Tuple[str, bool]:
    """Prefer a complete local model snapshot without making a network call."""
    mode = EMBEDDING_LOCAL_FILES_ONLY
    if mode not in {"auto", "true", "false"}:
        raise ValueError(
            "EMBEDDING_LOCAL_FILES_ONLY must be 'auto', 'true', or 'false'"
        )

    if mode != "false":
        try:
            local_path = snapshot_download(
                repo_id=EMBEDDING_MODEL,
                local_files_only=True,
            )
            logger.info(f"Using cached embedding model: {local_path}")
            return local_path, True
        except Exception as exc:
            if mode == "true":
                raise RuntimeError(
                    f"Embedding model is not available locally: {EMBEDDING_MODEL}"
                ) from exc
            logger.info("No complete local embedding snapshot; download is required")

    return EMBEDDING_MODEL, False


@lru_cache(maxsize=1)
def get_embedding_model() -> HuggingFaceEmbeddings:
    """
    Initialize the multilingual embedding model.

    paraphrase-multilingual-MiniLM-L12-v2:
    - Supports 50+ languages including FR and AR
    - 384 dimensions
    - Fast (~14ms per sentence on CPU)
    - Good performance for semantic search
    """
    global _rag_runtime_status
    try:
        model_source, is_local = _resolve_embedding_source()
        model_kwargs = {"device": "cpu"}
        if is_local:
            model_kwargs["local_files_only"] = True

        model = HuggingFaceEmbeddings(
            model_name=model_source,
            model_kwargs=model_kwargs,
            encode_kwargs={"normalize_embeddings": True},
        )
        _rag_runtime_status = "healthy"
        return model
    except Exception:
        _rag_runtime_status = "error"
        raise


def create_vector_store(
    chunks: List[Document],
    embedding_model: Optional[HuggingFaceEmbeddings] = None,
    reset_collection: bool = True,
) -> Chroma:
    """
    Create and persist a ChromaDB vector store from chunks.

    Args:
        chunks: List of split Documents (output of split_documents)
        embedding_model: Embedding model (created automatically if None)

    Returns:
        Chroma instance ready for search
    """
    if embedding_model is None:
        embedding_model = get_embedding_model()

    if not chunks:
        raise ValueError("Cannot create a vector store from an empty chunk list")

    CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)

    if reset_collection:
        client = chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIR))
        collection_names = {collection.name for collection in client.list_collections()}
        if CHROMA_COLLECTION_NAME in collection_names:
            client.delete_collection(CHROMA_COLLECTION_NAME)
            logger.info(f"Reset Chroma collection: {CHROMA_COLLECTION_NAME}")

    # Stable IDs plus collection reset make repeated ingestion idempotent.
    ids = []
    for index, chunk in enumerate(chunks):
        identity = "\0".join((
            str(index),
            str(chunk.metadata.get("langue", "")),
            str(chunk.metadata.get("relative_path", "")),
            chunk.page_content,
        ))
        ids.append(hashlib.sha256(identity.encode("utf-8")).hexdigest())

    print(f"Vectorizing {len(chunks)} chunks with {EMBEDDING_MODEL}...")
    print(f"Storage directory: {CHROMA_PERSIST_DIR}")

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        ids=ids,
        persist_directory=str(CHROMA_PERSIST_DIR),
        collection_name=CHROMA_COLLECTION_NAME,
    )

    global _rag_runtime_status
    _rag_runtime_status = "healthy"
    _load_default_vector_store.cache_clear()
    print(f"Vector store created: {vector_store._collection.count()} vectors")
    return vector_store


def _new_vector_store(embedding_model: HuggingFaceEmbeddings) -> Chroma:
    """Construct a Chroma wrapper around the persisted collection."""
    return Chroma(
        persist_directory=str(CHROMA_PERSIST_DIR),
        embedding_function=embedding_model,
        collection_name=CHROMA_COLLECTION_NAME,
    )


@lru_cache(maxsize=1)
def _load_default_vector_store() -> Chroma:
    global _rag_runtime_status
    try:
        vector_store = _new_vector_store(get_embedding_model())
        if vector_store._collection.count() == 0:
            _rag_runtime_status = "empty"
            raise RuntimeError(
                "Chroma collection is empty. Run: python -m backend.rag.embeddings"
            )
        _rag_runtime_status = "healthy"
        return vector_store
    except Exception:
        if _rag_runtime_status != "empty":
            _rag_runtime_status = "error"
        raise


def load_vector_store(
    embedding_model: Optional[HuggingFaceEmbeddings] = None,
) -> Chroma:
    """
    Load an existing ChromaDB vector store (for queries).

    Returns:
        Chroma instance ready for search
    """
    if embedding_model is None:
        return _load_default_vector_store()

    return _new_vector_store(embedding_model)


def get_vector_store_status() -> str:
    """Validate persisted vectors and local model readiness without an API call."""
    if _rag_runtime_status in {"error", "empty"}:
        return _rag_runtime_status

    if not CHROMA_PERSIST_DIR.exists():
        return "not_initialized"

    try:
        client = chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIR))
        names = {collection.name for collection in client.list_collections()}
        if CHROMA_COLLECTION_NAME not in names:
            return "not_initialized"
        if client.get_collection(CHROMA_COLLECTION_NAME).count() == 0:
            return "empty"

        _, is_local = _resolve_embedding_source()
        return "healthy" if is_local else "requires_model_download"
    except Exception:
        return "error"


# === Full ingestion script ===
if __name__ == "__main__":
    # Ensure stdout can handle multilingual (Arabic) output on Windows
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    try:
        from rag.ingestion import load_all_documents, split_documents
    except ImportError:
        from ingestion import load_all_documents, split_documents

    # 1. Load documents
    docs = load_all_documents()

    # 2. Split into chunks
    chunks = split_documents(docs)

    # 3. Vectorize and store
    vector_store = create_vector_store(chunks)

    # 4. Quick test
    print("\nRunning quick search test...")
    results = vector_store.similarity_search("sextorsion", k=3)
    for i, doc in enumerate(results):
        print(f"  [{i+1}] {doc.metadata.get('relative_path')} "
              f"(lang={doc.metadata.get('langue')}) -- "
              f"{doc.page_content[:100]}...")
