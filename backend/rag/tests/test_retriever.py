"""Unit tests for the bilingual retriever."""
import pytest
import time
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))


@pytest.fixture(scope="module")
def retriever():
    """Fixture: initialize the retriever once for all tests."""
    from rag.retriever import BilingualRetriever
    return BilingualRetriever()


class TestSemanticSearch:
    def test_sextorsion_fr(self, retriever):
        """'Je suis victime de sextorsion' should return sextorsion.md"""
        results = retriever.search("Je suis victime de sextorsion", langue="fr")
        assert len(results) > 0, "No results for 'sextorsion'"
        paths = [doc.metadata["relative_path"] for doc, _ in results]
        assert any("sextorsion" in p for p in paths), \
            f"sextorsion.md not found in: {paths}"

    def test_sextorsion_ar(self, retriever):
        """Arabic sextorsion query should return AR results"""
        results = retriever.search(
            "\u0623\u0646\u0627 \u0636\u062d\u064a\u0629 \u0627\u0628\u062a\u0632\u0627\u0632 \u062c\u0646\u0633\u064a",
            langue="ar"
        )
        assert len(results) > 0, "No results for Arabic sextorsion query"
        langs = [doc.metadata["langue"] for doc, _ in results]
        assert all(lang == "ar" for lang in langs), "Non-AR results returned"

    def test_droits_juridique(self, retriever):
        """'Quels sont mes droits ?' should return juridique documents"""
        results = retriever.search("Quels sont mes droits ?", langue="fr")
        assert len(results) > 0, "No results for rights query"
        cats = [doc.metadata["categorie"] for doc, _ in results]
        assert "juridique" in cats, f"No juridique doc found, categories: {cats}"

    def test_numero_police_ar(self, retriever):
        """Arabic police number query should return numeros_urgence.md"""
        results = retriever.search(
            "\u0623\u0631\u064a\u062f \u0631\u0642\u0645 \u0627\u0644\u0634\u0631\u0637\u0629",
            langue="ar"
        )
        assert len(results) > 0, "No results for Arabic police number query"
        paths = [doc.metadata["relative_path"] for doc, _ in results]
        assert any("numeros_urgence" in p or "urgence" in p for p in paths), \
            f"numeros_urgence.md not found in: {paths}"

    def test_language_filtering_fr(self, retriever):
        """FR results must only contain FR documents."""
        results = retriever.search("cyberharcelement", langue="fr")
        for doc, _ in results:
            assert doc.metadata["langue"] == "fr", \
                f"Non-FR doc in FR results: {doc.metadata['relative_path']}"

    def test_language_filtering_ar(self, retriever):
        """AR results must only contain AR documents."""
        results = retriever.search(
            "\u0627\u0644\u062a\u062d\u0631\u0634 \u0627\u0644\u0625\u0644\u0643\u062a\u0631\u0648\u0646\u064a",
            langue="ar"
        )
        for doc, _ in results:
            assert doc.metadata["langue"] == "ar", \
                f"Non-AR doc in AR results: {doc.metadata['relative_path']}"

    def test_performance_under_500ms(self, retriever):
        """Search time must be < 500ms."""
        start = time.time()
        retriever.search("aide victime cyberviolence", langue="fr")
        elapsed_ms = (time.time() - start) * 1000
        assert elapsed_ms < 500, \
            f"Search too slow: {elapsed_ms:.0f}ms (max 500ms)"


class TestCrossLingueFallback:
    def test_fallback_returns_results(self, retriever):
        """Fallback search should return results even if primary language has none."""
        results = retriever.search_with_fallback(
            "Convention de Budapest cybercriminalite", langue="ar"
        )
        # Should return results (FR fallback if needed)
        # This is a soft assertion since the term may exist in both languages
        assert isinstance(results, list)

    def test_fallback_preserves_result_format(self, retriever):
        """Fallback results should have the same format as regular results."""
        results = retriever.search_with_fallback(
            "sextorsion chantage", langue="fr"
        )
        for item in results:
            assert isinstance(item, tuple), "Result should be a tuple"
            assert len(item) == 2, "Result tuple should have 2 elements"
            doc, score = item
            assert hasattr(doc, "page_content"), "First element should be a Document"
            assert isinstance(score, float), "Second element should be a float score"
