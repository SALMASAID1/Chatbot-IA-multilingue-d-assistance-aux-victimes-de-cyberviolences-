# Tâche 2 — Développement de l'API Backend (FastAPI)

## Assigné à
**Mohamed Tamzirt**

## Objectif
Développer l'API backend avec FastAPI, incluant les endpoints de conversation, la gestion des sessions, la détection de langue, et l'intégration avec le pipeline RAG.

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

## Critères de validation
- [ ] L'API répond correctement sur tous les endpoints
- [ ] La détection de langue fonctionne pour FR, AR et darija
- [ ] Les sessions sont gérées correctement
- [ ] La documentation Swagger est complète avec exemples trilingues
- [ ] Le temps de réponse de l'API est < 3s
- [ ] Le rate limiting fonctionne
- [ ] L'API s'intègre correctement avec le module RAG
- [ ] Durée : **Semaine 3-4**
