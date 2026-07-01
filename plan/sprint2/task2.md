# Tâche 2 — Développement de l'API Backend (FastAPI)

## Assigné à
**Mohamed Tamzirt**

## Objectif
Développer l'API backend avec FastAPI, incluant les endpoints de conversation, la gestion des sessions, la détection de langue, et l'intégration avec le pipeline RAG.

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
       language_service.py  # Détection de langue
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
   - Routage vers le bon pipeline selon la langue
   - Gestion du changement de langue en cours de conversation

4. **Gestion des sessions et de l'historique**
   - Stockage en mémoire (développement) ou Redis (production)
   - Limitation de la taille de l'historique
   - Nettoyage automatique des sessions expirées

5. **Middleware et sécurité**
   - Configuration CORS pour le frontend React
   - Rate limiting pour éviter les abus
   - Validation des entrées (taille max, caractères)
   - Logging des interactions (anonymisé)

6. **Documentation API**
   - Documentation automatique Swagger/OpenAPI
   - Exemples de requêtes et réponses
   - Guide d'utilisation pour le frontend

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
- [ ] La documentation Swagger est complète
- [ ] Le temps de réponse de l'API est < 3s
- [ ] Le rate limiting fonctionne
- [ ] Durée : **Semaine 3-4**
