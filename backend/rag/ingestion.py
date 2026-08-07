"""Ingestion module: loading, metadata enrichment, and document splitting.

Handles three data sources:
1. Knowledge base FR (data/knowledge_base/fr/) -- 33 structured Markdown files
2. Knowledge base AR (data/knowledge_base/ar/) -- 24 structured Markdown files
3. Livrable-1 Q&A bases (docs/livrable-1/) -- 32 validated Q&A pairs (FR + AR)
"""
import json
import re
from pathlib import Path
from typing import List, Dict

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import (
    FR_DIR, AR_DIR, FR_METADATA, AR_METADATA,
    EXCLUDED_DIRS, CHUNK_SIZE, CHUNK_OVERLAP,
    QR_FR_PATH, QR_AR_PATH, MOTS_CLES_PATH
)


def load_metadata(metadata_path: Path) -> Dict[str, dict]:
    """
    Load metadata.json and return a dict indexed by file_path.

    Returns:
        {
            "fiches_pratiques/sextorsion.md": {
                "langue": "fr",
                "categorie": "fiches_pratiques",
                "mots_cles": ["sextorsion", "chantage", ...]
            }
        }
    """
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata_list = json.load(f)

    return {
        entry["file_path"]: {
            "langue": entry["langue"],
            "categorie": entry["categorie"],
            "mots_cles": entry.get("mots_cles", [])
        }
        for entry in metadata_list
    }


def load_documents_from_dir(
    base_dir: Path,
    metadata_path: Path,
    langue: str
) -> List[Document]:
    """
    Load all .md files from a knowledge base directory.

    Args:
        base_dir: Path to data/knowledge_base/fr/ or /ar/
        metadata_path: Path to the corresponding metadata.json
        langue: "fr" or "ar"

    Returns:
        List of LangChain Documents with enriched metadata
    """
    metadata_map = load_metadata(metadata_path)
    documents = []

    for md_file in base_dir.rglob("*.md"):
        # --- EXCLUSION of duplicate folders ---
        if any(excluded in md_file.parts for excluded in EXCLUDED_DIRS):
            print(f"  [SKIPPED] Excluded (duplicate): {md_file.relative_to(base_dir)}")
            continue

        # Compute relative path to match with metadata.json
        relative_path = str(md_file.relative_to(base_dir)).replace("\\", "/")

        # Read file content
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()

        if not content.strip():
            print(f"  [WARNING] Empty file ignored: {relative_path}")
            continue

        # Retrieve metadata from metadata.json
        file_metadata = metadata_map.get(relative_path, {})

        # Build the LangChain Document metadata
        doc_metadata = {
            "source": str(md_file),
            "relative_path": relative_path,
            "langue": file_metadata.get("langue", langue),
            "categorie": file_metadata.get("categorie", _infer_category(relative_path)),
            "mots_cles": ", ".join(file_metadata.get("mots_cles", [])),
            "file_name": md_file.stem,
        }

        documents.append(Document(page_content=content, metadata=doc_metadata))
        print(f"  [OK] Loaded: {relative_path} ({len(content)} chars)")

    return documents


def _infer_category(relative_path: str) -> str:
    """Infer category from the directory structure if not in metadata."""
    parts = relative_path.split("/")
    if len(parts) >= 2:
        return parts[0]
    return "inconnue"


def _parse_qa_document(file_path: Path, langue: str) -> List[Document]:
    """
    Parse a Q&A base file (base_questions_reponses_fr/ar.md) into
    individual Q&A pair documents.

    Each Q&A block (starting with ### Q<N>) becomes a separate Document
    with metadata indicating the question number and category.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        return []

    # Split on Q&A headings (### Q1, ### Q2, etc.)
    qa_blocks = re.split(r'(?=### Q\d+)', content)
    documents = []

    for block in qa_blocks:
        block = block.strip()
        if not block or not block.startswith("### Q"):
            continue

        # Extract question number
        q_match = re.match(r'### (Q\d+)', block)
        q_num = q_match.group(1) if q_match else "Q?"

        # Extract category from the text if present
        cat_match = re.search(r'\*\*Cat.gorie\s*:\*\*\s*`([^`]+)`', block)
        categorie = cat_match.group(1) if cat_match else "qa_base"

        doc_metadata = {
            "source": str(file_path),
            "relative_path": f"livrable-1/{file_path.name}",
            "langue": langue,
            "categorie": categorie,
            "question_id": q_num,
            "file_name": file_path.stem,
            "doc_type": "qa_pair",
        }

        documents.append(Document(page_content=block, metadata=doc_metadata))

    print(f"  [OK] Parsed {len(documents)} Q&A pairs from {file_path.name}")
    return documents


def load_livrable1_documents() -> List[Document]:
    """
    Load Q&A bases and trigger keywords from livrable-1.

    These are validated Q&A pairs (32 questions in FR and AR) that serve as
    the primary conversational content for the chatbot.
    """
    documents = []

    # Load FR Q&A base
    if QR_FR_PATH.exists():
        print("  Loading FR Q&A base...")
        documents.extend(_parse_qa_document(QR_FR_PATH, "fr"))

    # Load AR Q&A base
    if QR_AR_PATH.exists():
        print("  Loading AR Q&A base...")
        documents.extend(_parse_qa_document(QR_AR_PATH, "ar"))

    # Load trigger keywords as a reference document
    if MOTS_CLES_PATH.exists():
        with open(MOTS_CLES_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        if content.strip():
            documents.append(Document(
                page_content=content,
                metadata={
                    "source": str(MOTS_CLES_PATH),
                    "relative_path": "livrable-1/mots_cles_declencheurs.md",
                    "langue": "fr",
                    "categorie": "mots_cles",
                    "file_name": "mots_cles_declencheurs",
                    "doc_type": "reference",
                }
            ))
            print(f"  [OK] Loaded trigger keywords ({len(content)} chars)")

    return documents


def load_all_documents() -> List[Document]:
    """Load ALL documents: knowledge base FR + AR + livrable-1 Q&A pairs."""
    print("Loading FR knowledge base documents...")
    fr_docs = load_documents_from_dir(FR_DIR, FR_METADATA, "fr")

    print("\nLoading AR knowledge base documents...")
    ar_docs = load_documents_from_dir(AR_DIR, AR_METADATA, "ar")

    print("\nLoading Livrable-1 Q&A documents...")
    qa_docs = load_livrable1_documents()

    all_docs = fr_docs + ar_docs + qa_docs
    print(f"\nTotal: {len(all_docs)} documents loaded "
          f"({len(fr_docs)} FR KB + {len(ar_docs)} AR KB + {len(qa_docs)} Q&A)")
    return all_docs


def split_documents(documents: List[Document]) -> List[Document]:
    """
    Split documents into chunks with overlap.

    Uses RecursiveCharacterTextSplitter that splits intelligently
    while respecting Markdown structure (headings, paragraphs, lists).
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=[
            "\n## ",     # H2 headings (main sections)
            "\n### ",    # H3 headings (subsections)
            "\n\n",      # Paragraphs
            "\n",        # Lines
            ". ",        # Sentences
            " ",         # Words
        ],
        length_function=len,
    )

    chunks = splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks "
          f"(size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    return chunks


# === Entry point for standalone testing ===
if __name__ == "__main__":
    docs = load_all_documents()
    chunks = split_documents(docs)

    # Display statistics
    langs = {}
    cats = {}
    for chunk in chunks:
        lang = chunk.metadata.get("langue", "?")
        cat = chunk.metadata.get("categorie", "?")
        langs[lang] = langs.get(lang, 0) + 1
        cats[cat] = cats.get(cat, 0) + 1

    print(f"\nChunks by language: {langs}")
    print(f"Chunks by category: {cats}")
