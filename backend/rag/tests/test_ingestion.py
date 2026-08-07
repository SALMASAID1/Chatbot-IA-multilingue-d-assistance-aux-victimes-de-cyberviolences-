"""Unit tests for the ingestion module."""
import pytest
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from rag.ingestion import (
    load_metadata, load_documents_from_dir, load_all_documents,
    split_documents, load_livrable1_documents
)
from config import FR_DIR, AR_DIR, FR_METADATA, AR_METADATA, EXCLUDED_DIRS


class TestLoadMetadata:
    def test_load_fr_metadata(self):
        metadata = load_metadata(FR_METADATA)
        # FR now has 33 entries (expanded knowledge base)
        assert len(metadata) >= 23, f"FR metadata must have at least 23 entries, got {len(metadata)}"

    def test_load_ar_metadata(self):
        metadata = load_metadata(AR_METADATA)
        assert len(metadata) >= 23, f"AR metadata must have at least 23 entries, got {len(metadata)}"

    def test_metadata_has_required_fields(self):
        metadata = load_metadata(FR_METADATA)
        for path, data in metadata.items():
            assert "langue" in data, f"Field 'langue' missing in {path}"
            assert "categorie" in data, f"Field 'categorie' missing in {path}"
            assert "mots_cles" in data, f"Field 'mots_cles' missing in {path}"

    def test_metadata_langue_values(self):
        fr_metadata = load_metadata(FR_METADATA)
        for path, data in fr_metadata.items():
            assert data["langue"] == "fr", f"Expected langue='fr' for {path}"

        ar_metadata = load_metadata(AR_METADATA)
        for path, data in ar_metadata.items():
            assert data["langue"] == "ar", f"Expected langue='ar' for {path}"

    def test_metadata_categories_are_valid(self):
        valid_categories = {
            "juridique", "ressources", "fiches_pratiques", "prevention",
            "psychologie", "rapports_internationaux", "faq"
        }
        metadata = load_metadata(FR_METADATA)
        for path, data in metadata.items():
            assert data["categorie"] in valid_categories, \
                f"Invalid category '{data['categorie']}' for {path}"


class TestLoadDocuments:
    def test_load_fr_documents(self):
        docs = load_documents_from_dir(FR_DIR, FR_METADATA, "fr")
        # FR now has 33 files
        assert len(docs) >= 23, f"Expected >= 23 FR docs, got {len(docs)}"

    def test_load_ar_documents(self):
        docs = load_documents_from_dir(AR_DIR, AR_METADATA, "ar")
        assert len(docs) >= 23, f"Expected >= 23 AR docs, got {len(docs)}"

    def test_excluded_dirs_not_loaded(self):
        """Verify that cyberviolence_ressources_verified_md is excluded."""
        docs = load_documents_from_dir(FR_DIR, FR_METADATA, "fr")
        for doc in docs:
            for excluded in EXCLUDED_DIRS:
                assert excluded not in doc.metadata["source"], \
                    f"Excluded document was loaded: {doc.metadata['source']}"

    def test_all_documents_have_metadata(self):
        docs = load_documents_from_dir(FR_DIR, FR_METADATA, "fr")
        for doc in docs:
            assert doc.metadata.get("langue") == "fr"
            assert doc.metadata.get("categorie") != "inconnue", \
                f"Unknown category for {doc.metadata.get('relative_path')}"

    def test_load_all_returns_both_languages(self):
        docs = load_all_documents()
        langues = set(doc.metadata["langue"] for doc in docs)
        assert "fr" in langues, "FR documents missing"
        assert "ar" in langues, "AR documents missing"

    def test_documents_have_content(self):
        docs = load_all_documents()
        for doc in docs:
            assert len(doc.page_content.strip()) > 0, \
                f"Empty content in {doc.metadata.get('relative_path')}"


class TestLivrable1Ingestion:
    def test_livrable1_loads_qa_pairs(self):
        docs = load_livrable1_documents()
        assert len(docs) > 0, "No livrable-1 documents loaded"

    def test_livrable1_has_fr_and_ar(self):
        docs = load_livrable1_documents()
        langues = set(doc.metadata.get("langue") for doc in docs)
        assert "fr" in langues, "FR Q&A pairs missing from livrable-1"
        assert "ar" in langues, "AR Q&A pairs missing from livrable-1"

    def test_livrable1_qa_pairs_have_question_id(self):
        docs = load_livrable1_documents()
        qa_docs = [d for d in docs if d.metadata.get("doc_type") == "qa_pair"]
        assert len(qa_docs) > 0, "No Q&A pair documents found"
        for doc in qa_docs:
            assert doc.metadata.get("question_id", "").startswith("Q"), \
                f"Missing question_id in {doc.metadata}"

    def test_all_documents_includes_livrable1(self):
        docs = load_all_documents()
        qa_docs = [d for d in docs if d.metadata.get("doc_type") == "qa_pair"]
        assert len(qa_docs) > 0, "Q&A pairs not included in load_all_documents"


class TestSplitDocuments:
    def test_split_produces_chunks(self):
        docs = load_all_documents()
        chunks = split_documents(docs)
        assert len(chunks) > len(docs), \
            "Splitting must produce more chunks than documents"

    def test_chunks_preserve_metadata(self):
        docs = load_all_documents()
        chunks = split_documents(docs)
        for chunk in chunks:
            assert "langue" in chunk.metadata
            assert "categorie" in chunk.metadata

    def test_chunk_size_reasonable(self):
        docs = load_all_documents()
        chunks = split_documents(docs)
        # Verify that most chunks are under the max size (with some margin)
        oversized = [c for c in chunks if len(c.page_content) > 600]
        ratio = len(oversized) / len(chunks) if chunks else 0
        assert ratio < 0.15, \
            f"{ratio*100:.0f}% of chunks exceed max size (expected < 15%)"
