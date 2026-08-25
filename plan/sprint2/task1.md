# Tâche 1 — Développement du pipeline RAG (LangChain) ✅ TERMINÉE

## Assigné à
**Salma Said**

## Objectif
Développer le pipeline RAG (Retrieval-Augmented Generation) complet utilisant LangChain, incluant l'ingestion des documents, la vectorisation, la recherche sémantique et l'augmentation du contexte pour le LLM.


## Statut : ✅ TERMINÉE

> **Décisions d'architecture (écarts assumés par rapport au plan initial) :**
> - **ChromaDB** en persistance locale (`data/chroma_db/`) plutôt que Pinecone : pas de
>   dépendance à un service payant, et la base tient dans le dépôt pour le déploiement gratuit.
> - **`paraphrase-multilingual-MiniLM-L12-v2`** (384 dimensions) retenu plutôt que
>   `multilingual-e5-large` : il tourne sur CPU sans GPU, ce qui est la contrainte des
>   hébergeurs gratuits visés (Sprint 4, tâche 2).
> - **Découpage en 500 caractères** (chevauchement 50) plutôt qu'en tokens : `CHUNK_SIZE`
>   et `CHUNK_OVERLAP` sont exprimés en caractères dans `RecursiveCharacterTextSplitter`.
> - La base de connaissances a **grossi au-delà des 23+23 documents prévus** : elle compte
>   aujourd'hui 33 documents FR et 24 documents AR, plus les paires Q/R de la FAQ.

### Livrables produits
- `backend/rag/ingestion.py` — chargement, exclusion des doublons, découpage, métadonnées
- `backend/rag/embeddings.py` — modèle d'embeddings multilingue, chargement unique
- `backend/rag/retriever.py` — `BilingualRetriever`, filtrage par langue, `search_with_fallback()`
- `backend/rag/chain.py` — `RAGChain` complet : profil, urgence, récupération, prompt, LLM
- `backend/rag/tests/` — `test_ingestion.py`, `test_retriever.py`, `test_chain.py`
- Base vectorielle indexée : **820 vecteurs** (535 FR / 285 AR) dans `data/chroma_db/`

### Paramètres retenus

| Paramètre | Valeur | Emplacement |
|---|---|---|
| Modèle d'embeddings | `paraphrase-multilingual-MiniLM-L12-v2` (384 dim.) | `config.py` |
| Taille de chunk / chevauchement | 500 / 50 caractères | `config.py` |
| `TOP_K` | 3 | `config.py` |
| Seuil de similarité | 0.15 | `config.py` |
| Collection | `cyberviolence_knowledge` | `config.py` |

### Répartition des 820 vecteurs

| Catégorie | Vecteurs | Catégorie | Vecteurs |
|---|---|---|---|
| juridique | 132 | rapports_internationaux | 74 |
| ressources | 131 | mots_cles | 42 |
| psychologie | 124 | soutien_psychologique | 18 |
| fiches_pratiques | 112 | profils_utilisateurs | 15 |
| prevention | 95 | | |
| faq | 77 | **Total** | **820** |

> ⚠️ **Incident corrigé le 24/08/2026.** La base vectorielle livrée contenait 748 vecteurs
> (dont seulement 213 en AR) : elle datait d'avant le commit `f8ca6b0`, qui a ajouté la
> reconnaissance des en-têtes `Q:` / `س:` dans l'ingestion. Les **72 chunks des 32 paires
> Q/R arabes validées n'étaient donc pas interrogeables** — la recherche AR/darija
> fonctionnait sans eux. Une réindexation complète a rétabli les 820 vecteurs.
> **À retenir :** toute modification de `ingestion.py` impose une réindexation.

## Prérequis (état actuel du projet)
- ✅ Base de connaissances FR : 23 documents Markdown dans `data/knowledge_base/fr/` (7 catégories)
- ✅ Base de connaissances AR : 23 documents Markdown dans `data/knowledge_base/ar/` (7 catégories, parité parfaite)
- ✅ Metadata JSON : `data/knowledge_base/fr/metadata.json` et `data/knowledge_base/ar/metadata.json` (23 entrées chacun, avec langue, catégorie, mots-clés)
- ⚠️ Le dossier `backend/` n'existe pas encore — à créer
- ⚠️ Le dossier `fr/ressources/cyberviolence_ressources_verified_md/` contient des doublons à ne pas ingérer

## Étapes d'implémentation

1. **Configuration de l'environnement Python**
   - Créer un environnement virtuel (`venv` ou `conda`)
   - Installer les dépendances : `langchain`, `chromadb`, `openai`, `sentence-transformers`
   - Configurer les variables d'environnement (clés API)
   - Créer `requirements.txt`

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
   - Charger les documents depuis `data/knowledge_base/fr/` et `data/knowledge_base/ar/`
   - **Exclure** le dossier `cyberviolence_ressources_verified_md/` (doublons de travail)
   - Découper en chunks avec `RecursiveCharacterTextSplitter`
   - Taille de chunk recommandée : 300-500 tokens (les fiches pratiques font 25-40 lignes, les documents psychologie 100-140 lignes)
   - Configurer les métadonnées à partir des fichiers `metadata.json` existants :
     - `langue` : "fr" ou "ar"
     - `categorie` : juridique, ressources, fiches_pratiques, prevention, psychologie, rapports_internationaux, faq
     - `mots_cles` : liste de mots-clés (FR ou AR)

3. **Configuration de la base vectorielle**
   - Initialiser ChromaDB (développement local) ou Pinecone (production)
   - Choisir le modèle d'embeddings multilingue (recommandé : `multilingual-e5-large` ou `paraphrase-multilingual-MiniLM-L12-v2` pour le support FR/AR)
   - Indexer les 46 documents (23 FR + 23 AR)
   - Stocker les métadonnées pour le filtrage

4. **Développement du retriever**
   - Recherche sémantique avec filtrage par langue (`langue: "fr"` ou `langue: "ar"`)
   - Implémentation du score de similarité
   - Gestion du nombre de documents retournés (top-k, recommandé : k=3-5)
   - Fallback cross-lingue : si aucun résultat pertinent dans la langue source, chercher dans l'autre langue

5. **Construction de la chaîne RAG**
   - Intégration avec LangChain `RetrievalQA` ou `ConversationalRetrievalChain`
   - Conception des prompts (system prompt empathique) — en coordination avec la **Tâche 3**
   - Gestion de l'historique de conversation
   - Le contexte RAG doit inclure les numéros d'urgence (19, 177, 2511) et les plateformes de signalement

6. **Tests unitaires du pipeline**
   - Tests d'ingestion : vérifier que les 46 documents sont correctement chargés
   - Tests de recherche : vérifier la pertinence par catégorie et par langue
   - Cas de test recommandés :
     - "Je suis victime de sextorsion" → doit retourner `fiches_pratiques/sextorsion.md`
     - "أنا ضحية ابتزاز جنسي" → doit retourner la version AR
     - "Quels sont mes droits ?" → doit retourner les documents juridiques
     - "أريد رقم الشرطة" → doit retourner `ressources/numeros_urgence.md` (AR)
   - Benchmarks de performance (temps de réponse)

## Données disponibles pour l'ingestion

| Catégorie | Documents FR | Documents AR | Total chunks estimé |
|---|---|---|---|
| juridique | 3 (196 lignes) | 3 (260 lignes) | ~30-40 |
| ressources | 3 (389 lignes) | 3 (384 lignes) | ~50-60 |
| fiches_pratiques | 6 (205 lignes) | 6 (189 lignes) | ~25-35 |
| prevention | 4 (171 lignes) | 4 (167 lignes) | ~20-30 |
| psychologie | 3 (361 lignes) | 3 (355 lignes) | ~45-55 |
| rapports_internationaux | 4 (222 lignes) | 4 (222 lignes) | ~30-40 |
| faq | 1 (47 lignes) | 1 (31 lignes) | ~5-10 |
| **Total** | **24 fichiers** | **24 fichiers** | **~205-270 chunks** |

> Note : le nombre de chunks dépendra de la taille de chunk choisie (300-500 tokens recommandé).

## Outils et ressources
- Python 3.10+
- LangChain, ChromaDB / Pinecone
- OpenAI API ou modèles HuggingFace
- `sentence-transformers` pour les embeddings multilingues
- pytest pour les tests

## Livrable attendu
- Module `backend/rag/` fonctionnel avec :
  - Script d'ingestion des 46 documents
  - Pipeline de recherche sémantique bilingue
  - Chaîne RAG complète avec gestion de contexte
  - Tests unitaires (>80% coverage)
  - `requirements.txt` mis à jour


## Critères de validation — Résultats

- [x] Les documents FR et AR sont correctement ingérés et vectorisés — **33 FR + 24 AR**, soit 820 chunks (535 FR / 285 AR)
- [x] Le dossier `cyberviolence_ressources_verified_md/` est exclu de l'ingestion — via `EXCLUDED_DIRS` (`ingestion.py:72`)
- [x] Les métadonnées (`langue`, `categorie`, `mots_cles`) sont préservées dans la base vectorielle — vérifié par inspection directe de la collection
- [x] La recherche sémantique retourne des résultats pertinents dans la bonne langue — filtrage `langue` + repli cross-lingue `search_with_fallback()`
- [x] Le pipeline RAG génère des réponses contextualisées — `RAGChain.query()` avec profil utilisateur et injection de contexte
- [x] Le temps de recherche est < 500 ms — **médiane mesurée : 19 ms** (20 exécutions, CPU, hors appel LLM)
- [x] Les tests passent avec succès — **201 tests backend** (7 ignorés faute de clé API)
- [x] Durée : **Semaine 3-4** ✅

> **Non couvert :** la couverture de tests n'a pas été mesurée avec `pytest-cov`, le seuil
> « > 80 % » du livrable n'est donc ni confirmé ni infirmé.
