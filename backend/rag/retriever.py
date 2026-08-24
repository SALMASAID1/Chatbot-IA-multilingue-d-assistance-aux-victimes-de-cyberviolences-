"""Bilingual semantic search with language filtering and lexical reranking."""
import io
import re
from typing import List, Optional, Tuple
from langchain_core.documents import Document

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import TOP_K, SIMILARITY_THRESHOLD
from rag.embeddings import load_vector_store


class BilingualRetriever:
    """
    Bilingual retriever with:
    - Language filtering (FR or AR)
    - Similarity scoring
    - Cross-lingual fallback when no relevant results found
    """

    def __init__(self, top_k: int = TOP_K, threshold: float = SIMILARITY_THRESHOLD):
        self.vector_store = load_vector_store()
        self.top_k = top_k
        self.threshold = threshold

    def search(
        self,
        query: str,
        langue: str = "fr",
        top_k: Optional[int] = None,
        categorie: Optional[str] = None,
    ) -> List[Tuple[Document, float]]:
        """
        Semantic search with filtering.

        Args:
            query: User question
            langue: "fr" or "ar" -- filters results by language
            top_k: Number of results (default: config.TOP_K)
            categorie: Filter by category (optional)

        Returns:
            List of tuples (Document, similarity_score)
        """
        k = top_k or self.top_k
        candidate_k = max(k * 4, 12)

        # Build ChromaDB filter
        where_filter = {"langue": langue}
        if categorie:
            where_filter = {
                "$and": [
                    {"langue": langue},
                    {"categorie": categorie}
                ]
            }

        # Search with scores
        results = self.vector_store.similarity_search_with_relevance_scores(
            query=query,
            k=candidate_k,
            filter=where_filter,
        )

        # The multilingual embedding model can under-rank short Arabic queries.
        # Combine semantic similarity with exact terms in curated metadata/content.
        reranked = []
        query_terms = self._meaningful_terms(query)
        for doc, semantic_score in results:
            metadata_text = " ".join((
                str(doc.metadata.get("mots_cles", "")),
                str(doc.metadata.get("relative_path", "")),
                str(doc.metadata.get("categorie", "")),
            )).lower()
            content_text = doc.page_content.lower()

            if query_terms:
                metadata_overlap = sum(
                    term in metadata_text for term in query_terms
                ) / len(query_terms)
                content_overlap = sum(
                    term in content_text for term in query_terms
                ) / len(query_terms)
            else:
                metadata_overlap = 0.0
                content_overlap = 0.0

            combined_score = min(
                1.0,
                semantic_score + (0.12 * metadata_overlap) + (0.04 * content_overlap),
            )
            reranked.append((doc, combined_score))

        reranked.sort(key=lambda item: item[1], reverse=True)
        filtered = [
            (doc, score)
            for doc, score in reranked
            if score >= self.threshold
        ][:k]

        return filtered

    @staticmethod
    def _meaningful_terms(text: str) -> set[str]:
        """Extract useful French/Arabic terms for lightweight lexical reranking."""
        stop_words = {
            "je", "j", "de", "du", "des", "le", "la", "les", "un", "une",
            "mes", "mon", "ma", "est", "sont", "que", "qui", "quoi", "comment",
            "أريد", "اريد", "ما", "هو", "هي", "من", "في", "على", "كيف", "واش",
        }
        terms = {
            term
            for term in re.findall(r"[\w\u0600-\u06FF]+", text.lower())
            if len(term) > 1 and term not in stop_words
        }
        return terms

    def search_with_fallback(
        self,
        query: str,
        langue: str = "fr",
        top_k: Optional[int] = None,
    ) -> List[Tuple[Document, float]]:
        """
        Search with cross-lingual fallback.

        If no relevant results in the requested language,
        search in the other language.
        """
        results = self.search(query, langue=langue, top_k=top_k)

        if not results:
            # Fallback: search in the other language
            other_langue = "ar" if langue == "fr" else "fr"
            print(f"[FALLBACK] No results in '{langue}', falling back to '{other_langue}'")
            results = self.search(query, langue=other_langue, top_k=top_k)

        return results

    def format_context(self, results: List[Tuple[Document, float]]) -> str:
        """
        Format search results as text context for the LLM.

        Returns:
            Formatted text ready to be injected into the prompt
        """
        if not results:
            return "Aucun document pertinent trouve dans la base de connaissances."

        context_parts = []
        for i, (doc, score) in enumerate(results, 1):
            meta = doc.metadata
            context_parts.append(
                f"--- Document {i} (relevance: {score:.2f}) ---\n"
                f"Source: {meta.get('relative_path', 'unknown')}\n"
                f"Category: {meta.get('categorie', 'unknown')}\n"
                f"Language: {meta.get('langue', '?')}\n"
                f"Content:\n{doc.page_content}\n"
            )

        return "\n".join(context_parts)


# === Test the retriever ===
if __name__ == "__main__":
    # Ensure the Windows terminal can display Arabic test queries and results.
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    retriever = BilingualRetriever()

    test_queries = [
        ("Je suis victime de sextorsion", "fr"),
        ("\u0623\u0646\u0627 \u0636\u062d\u064a\u0629 \u0627\u0628\u062a\u0632\u0627\u0632 \u062c\u0646\u0633\u064a", "ar"),
        ("Quels sont mes droits ?", "fr"),
        ("\u0623\u0631\u064a\u062f \u0631\u0642\u0645 \u0627\u0644\u0634\u0631\u0637\u0629", "ar"),
    ]

    for query, lang in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: '{query}' (langue={lang})")
        results = retriever.search_with_fallback(query, langue=lang)
        for doc, score in results:
            print(f"  [{score:.3f}] {doc.metadata['relative_path']} "
                  f"-- {doc.page_content[:80]}...")
