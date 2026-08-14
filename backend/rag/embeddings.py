"""Embeddings module: vectorization and ChromaDB storage."""
from typing import List, Optional

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

import sys
import io
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import (
    EMBEDDING_MODEL, CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME
)


def get_embedding_model() -> HuggingFaceEmbeddings:
    """
    Initialize the multilingual embedding model.

    paraphrase-multilingual-MiniLM-L12-v2:
    - Supports 50+ languages including FR and AR
    - 384 dimensions
    - Fast (~14ms per sentence on CPU)
    - Good performance for semantic search
    """
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},  # change to "cuda" if GPU available
        encode_kwargs={"normalize_embeddings": True}
    )


def create_vector_store(
    chunks: List[Document],
    embedding_model: Optional[HuggingFaceEmbeddings] = None
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

    print(f"Vectorizing {len(chunks)} chunks with {EMBEDDING_MODEL}...")
    print(f"Storage directory: {CHROMA_PERSIST_DIR}")

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=str(CHROMA_PERSIST_DIR),
        collection_name=CHROMA_COLLECTION_NAME,
    )

    print(f"Vector store created: {vector_store._collection.count()} vectors")
    return vector_store


def load_vector_store(
    embedding_model: Optional[HuggingFaceEmbeddings] = None
) -> Chroma:
    """
    Load an existing ChromaDB vector store (for queries).

    Returns:
        Chroma instance ready for search
    """
    if embedding_model is None:
        embedding_model = get_embedding_model()

    return Chroma(
        persist_directory=str(CHROMA_PERSIST_DIR),
        embedding_function=embedding_model,
        collection_name=CHROMA_COLLECTION_NAME,
    )


# === Full ingestion script ===
if __name__ == "__main__":
    # Ensure stdout can handle multilingual (Arabic) output on Windows
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

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
