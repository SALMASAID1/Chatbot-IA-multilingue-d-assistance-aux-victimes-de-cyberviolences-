# Tâche 1 — Développement du pipeline RAG (LangChain)

## Assigné à
**Salma Said**

## Objectif
Développer le pipeline RAG (Retrieval-Augmented Generation) complet utilisant LangChain, incluant l'ingestion des documents, la vectorisation, la recherche sémantique et l'augmentation du contexte pour le LLM.

## Étapes d'implémentation

1. **Configuration de l'environnement Python**
   - Créer un environnement virtuel (`venv` ou `conda`)
   - Installer les dépendances : `langchain`, `chromadb`, `openai`, `sentence-transformers`
   - Configurer les variables d'environnement (clés API)

2. **Développement du module d'ingestion**
   ```python
   # Structure cible
   backend/
     rag/
       __init__.py
       ingestion.py      # Chargement et découpage des documents
       embeddings.py     # Vectorisation avec embeddings
       retriever.py      # Recherche sémantique
       chain.py          # Pipeline RAG complet
   ```
   - Charger les documents depuis `data/knowledge_base/`
   - Découper en chunks avec `RecursiveCharacterTextSplitter`
   - Configurer les métadonnées (langue, catégorie, source)

3. **Configuration de la base vectorielle**
   - Initialiser ChromaDB (développement local) ou Pinecone (production)
   - Choisir le modèle d'embeddings (OpenAI ou HuggingFace multilingue)
   - Indexer les documents FR et AR séparément ou avec filtres

4. **Développement du retriever**
   - Recherche sémantique avec filtrage par langue
   - Implémentation du score de similarité
   - Gestion du nombre de documents retournés (top-k)

5. **Construction de la chaîne RAG**
   - Intégration avec LangChain `RetrievalQA` ou `ConversationalRetrievalChain`
   - Conception des prompts (system prompt empathique)
   - Gestion de l'historique de conversation

6. **Tests unitaires du pipeline**
   - Tests d'ingestion et de recherche
   - Évaluation de la pertinence des résultats
   - Benchmarks de performance (temps de réponse)

## Outils et ressources
- Python 3.10+
- LangChain, ChromaDB / Pinecone
- OpenAI API ou modèles HuggingFace
- `sentence-transformers` pour les embeddings multilingues
- pytest pour les tests

## Livrable attendu
- Module `backend/rag/` fonctionnel avec :
  - Script d'ingestion des documents
  - Pipeline de recherche sémantique
  - Chaîne RAG complète avec gestion de contexte
  - Tests unitaires (>80% coverage)
  - `requirements.txt` mis à jour

## Critères de validation
- [ ] Les documents FR et AR sont correctement ingérés et vectorisés
- [ ] La recherche sémantique retourne des résultats pertinents
- [ ] Le pipeline RAG génère des réponses contextualisées
- [ ] Le temps de recherche est < 500ms
- [ ] Les tests passent avec succès
- [ ] Durée : **Semaine 3-4**
