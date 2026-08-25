# Tâche 2 — Développement de l'API Backend (FastAPI) ✅ TERMINÉE

## Assigné à
**Mohamed Tamzirt**

## Objectif
Développer l'API backend avec FastAPI, incluant les endpoints de conversation, la gestion des sessions, la détection de langue, et l'intégration avec le pipeline RAG.


## Statut : ✅ TERMINÉE

> **Décisions d'architecture (écarts assumés par rapport au plan initial) :**
> - **Sessions en mémoire uniquement.** `REDIS_URL` reste lu dans `config.py` mais aucun
>   backend Redis n'est branché : les sessions vivent dans le processus, avec un TTL de
>   30 minutes. Conséquence assumée : un redémarrage vide les conversations, et l'API ne
>   peut pas être répliquée sur plusieurs instances. Acceptable pour le périmètre PFA et
>   pour l'hébergement gratuit mono-conteneur.
> - **`langdetect` écarté.** La détection est **déterministe et écrite à la main**
>   (`services/language_service.py`) : `langdetect` est probabiliste, instable sur les
>   messages courts — ceux d'une victime en détresse — et ne connaît pas l'arabizi.
>   La règle retenue est explicite et testable : script arabe ⇒ `ar` ; script latin ⇒ `fr`
>   sauf si un marqueur darija **complet** est présent.

### Livrables produits
- `backend/main.py` — application FastAPI, CORS, `slowapi`, journal de démarrage
- `backend/api/routes/` — `chat.py`, `health.py`, `admin.py`
- `backend/api/models/schemas.py` — modèles Pydantic v2 (entrée et sortie)
- `backend/api/security.py` — garde par clé d'API sur les routes d'administration
- `backend/services/` — `chat_service.py`, `language_service.py`, `session_service.py`
- `backend/tests/` — `test_chat_routes.py`, `test_schemas.py`, `test_session_service.py`,
  `test_language_service.py`, `test_admin_auth.py`, `test_response_quality.py`
- `Dockerfile` (racine) et `docker-compose.yml` — conteneurisation de l'API

### Endpoints exposés

| Méthode | Chemin | Rôle | Limite |
|---|---|---|---|
| `POST` | `/api/chat` | Envoi d'un message, réponse RAG | 30/min |
| `POST` | `/api/chat/session` | Création d'une session | 30/min |
| `GET` | `/api/chat/history/{session_id}` | Historique de la session | 30/min |
| `POST` | `/api/chat/feedback` | Retour utilisateur sur une réponse | 30/min |
| `GET` | `/api/health` | État de l'API et du pipeline | — |
| `GET` | `/api/admin/sessions` | Liste des sessions actives | 10/min, **clé requise** |
| `DELETE` | `/api/admin/sessions/{session_id}` | Suppression d'une session | 10/min, **clé requise** |

> 🔒 **Correctif de sécurité (25/08/2026).** Les deux routes `/api/admin/*` étaient
> ouvertes sans authentification et exposaient les identifiants de session de toutes les
> victimes connectées. Elles sont désormais protégées par `require_admin_key`
> (`api/security.py`) : sans variable `ADMIN_API_KEY`, le routeur répond **404** — il
> n'existe pas ; avec la variable, une clé manquante ou fausse répond **401**, comparée par
> `secrets.compare_digest`. Couvert par `tests/test_admin_auth.py` (10 tests).

## Prérequis (état actuel du projet)
- ✅ Base de connaissances complète (46 documents FR+AR) prête pour le RAG
- ✅ Metadata JSON disponibles pour la configuration du routage par langue
- ⚠️ Le dossier `backend/` n'existe pas encore — à créer
- ⚠️ Le pipeline RAG (Tâche 1 — Salma) sera développé en parallèle
- ⚠️ Les langues à supporter : Français, Arabe standard, Darija marocain

## Étapes d'implémentation

1. **Initialisation du projet FastAPI**
   ```python
   # Structure cible
   backend/
     main.py              # Point d'entrée FastAPI
     api/
       __init__.py
       routes/
         chat.py           # Endpoints de conversation
         health.py          # Health check
         admin.py           # Administration
       models/
         schemas.py         # Modèles Pydantic
       middleware/
         cors.py            # Configuration CORS
         rate_limit.py      # Limitation de requêtes
     services/
       chat_service.py      # Logique métier
       language_service.py  # Détection de langue (FR/AR/Darija)
       session_service.py   # Gestion des sessions
     config.py              # Configuration
   ```

2. **Développement des endpoints principaux**
   - `POST /api/chat` — Envoi d'un message et réception de la réponse
   - `POST /api/chat/session` — Création d'une nouvelle session
   - `GET /api/chat/history/{session_id}` — Historique de conversation
   - `POST /api/chat/feedback` — Retour utilisateur sur les réponses
   - `GET /api/health` — État de l'API

3. **Implémentation de la détection de langue**
   - Utiliser `langdetect` ou un modèle HuggingFace pour détecter FR/AR/Darija
   - Routage vers le bon pipeline selon la langue détectée
   - Gestion du changement de langue en cours de conversation
   - Le FAQ AR (`data/knowledge_base/ar/faq/faq_cyberviolence.md`) mélange arabe standard et darija — le service doit gérer ce mélange
   - Exemples de messages darija à supporter : "واش نقدر نقدم شكاية", "أش ندير"

4. **Gestion des sessions et de l'historique**
   - Stockage en mémoire (développement) ou Redis (production)
   - Limitation de la taille de l'historique
   - Nettoyage automatique des sessions expirées

5. **Middleware et sécurité**
   - Configuration CORS pour le frontend React (Sprint 3)
   - Rate limiting pour éviter les abus
   - Validation des entrées (taille max, caractères)
   - Logging des interactions (anonymisé)

6. **Documentation API**
   - Documentation automatique Swagger/OpenAPI
   - Exemples de requêtes et réponses pour chaque langue (FR, AR, Darija)
   - Guide d'utilisation pour le frontend

## Intégration avec le pipeline RAG (Tâche 1)

L'API doit s'interfacer avec le module `backend/rag/` développé par Salma :

```python
# Flux attendu
Message utilisateur
  → language_service.detect(message)        # FR / AR / Darija
  → rag.retriever.search(message, lang)     # Recherche dans la bonne langue
  → rag.chain.generate(message, context)    # Génération LLM + contexte
  → Response avec metadata (langue, sources)
```

Les réponses doivent toujours inclure les numéros d'urgence pertinents quand la situation le nécessite :
- Police : **19**, Gendarmerie : **177**, ONDE : **2511** / **0800002511**

## Outils et ressources
- Python 3.10+, FastAPI, Uvicorn
- Pydantic pour la validation
- `langdetect` ou `fasttext` pour la détection de langue
- Redis (optionnel, pour les sessions en production)

## Livrable attendu
- API fonctionnelle avec :
  - Tous les endpoints décrits ci-dessus
  - Documentation Swagger accessible sur `/docs`
  - Tests d'intégration
  - `Dockerfile` pour le déploiement
  - Variables d'environnement documentées dans `.env.example`


## Critères de validation — Résultats

- [x] L'API répond correctement sur tous les endpoints — 7 routes, testées par `TestClient`
- [x] La détection de langue fonctionne pour FR, AR et darija — `language_service.py`, **27 tests**
- [x] Les sessions sont gérées correctement — création, historique, expiration à 30 min (`test_session_service.py`)
- [x] La documentation Swagger est complète avec exemples trilingues — générée sur `/docs`, exemples FR/AR/darija dans les schémas Pydantic
- [x] Le rate limiting fonctionne — `slowapi` : 30/min sur le chat, 10/min sur l'administration
- [x] L'API s'intègre correctement avec le module RAG — `chat_service.py` → `RAGChain.query()`
- [x] Durée : **Semaine 3-4** ✅

### Réserve sur la performance

- [ ] Le temps de réponse de l'API est < 3 s — **non mesuré de bout en bout.**
  La partie maîtrisée est rapide : la récupération vectorielle a une médiane de **19 ms**.
  Le reste dépend entièrement de la latence de l'API Gemini, qui n'a pas été chronométrée
  sur un échantillon représentatif. Le chiffre reste donc à établir sur l'instance
  déployée (voir Sprint 4, tâche 1).
