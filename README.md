---
title: EMC Helpline
emoji: 🛡️
colorFrom: indigo
colorTo: green
sdk: docker
app_port: 7860
pinned: false
short_description: Assistant multilingue d'aide aux victimes de cyberviolences au Maroc
---

<!-- The YAML block above configures the Hugging Face Space (SDK Docker, port
     7860). It is required by Hugging Face and is ignored by GitHub. -->

# Chatbot IA multilingue — assistance aux victimes de cyberviolences

Assistant conversationnel développé pour le **CMRPI — Espace Maroc Cyberconfiance (EMC)**.
Il informe et oriente les personnes touchées par les cyberviolences au Maroc, en
**français**, **arabe standard** et **darija marocaine** (écriture arabe et arabizi).

> ⚠️ Ce service ne remplace ni la police, ni les secours, ni un avocat, ni un
> professionnel de santé mentale. **En cas de danger immédiat : Police 19 ·
> Gendarmerie Royale 177 · Protection Civile 15 · ONDE 2511.**

| | |
|---|---|
| **Étudiants** | Salma Said & Mohamed Tamzirt (Data & AI Engineering) |
| **Encadrants** | M. Anass Bentaleb (IA) & Mme Fadwa Belaous (Psychologie) |
| **Période** | 1ᵉʳ juillet — 30 août 2026 |

## Architecture

```
React + Vite (frontend/)  →  FastAPI (backend/)  →  RAG (LangChain + ChromaDB)  →  Gemini
                                     ↓
                       Base de connaissances FR/AR vérifiée
                       (droit marocain, signalement, prévention, soutien psychologique)
```

- **Détection de langue** déterministe FR / AR / darija (y compris arabizi)
- **Protocole d'urgence** : les messages de danger immédiat court-circuitent le
  LLM et renvoient directement les numéros officiels
- **Adaptation au profil** : victime, parent, enseignant, témoin, jeune, détresse émotionnelle
- **820 vecteurs** issus de 122 documents (535 FR / 285 AR)

## Démarrage rapide

```bash
# 1. Backend
python -m venv venv && venv/bin/pip install -r requirements.txt
cp .env.example .env            # renseigner GOOGLE_API_KEY
venv/bin/python -m backend.rag.embeddings      # construire la base vectorielle
venv/bin/python -m uvicorn backend.main:app --reload --port 8000

# 2. Frontend (Node >= 20.19)
cd frontend && npm install && npm run dev      # http://localhost:5173
```

Démonstration en terminal, sans frontend : `venv/bin/python backend/demo_cli.py --auto`

## Tests

```bash
venv/bin/python -m pytest backend -q      # 170 tests backend
cd frontend && npm test && npm run test:e2e   # 100 tests + 25 e2e
```

## Documentation

| Document | Contenu |
|---|---|
| [docs/guide_deploiement.md](docs/guide_deploiement.md) | Déploiement Hugging Face Spaces + Vercel |
| [frontend/README.md](frontend/README.md) | Interface : installation, tests, décisions techniques |
| [docs/analyse_existant.md](docs/analyse_existant.md) | Analyse de l'existant et étude comparative |
| [docs/scenarios_conversationnels.md](docs/scenarios_conversationnels.md) | Parcours conversationnels et soutien psychologique |
| [docs/evaluation_llm.md](docs/evaluation_llm.md) | Évaluation du LLM et des system prompts |
| [plan/](plan/) | Planification des 4 sprints |

## Sécurité

- Les endpoints `/api/admin/*` sont **désactivés** tant que `ADMIN_API_KEY` n'est
  pas configurée, et exigent l'en-tête `X-Admin-Key` sinon.
- Aucun secret n'est versionné : `.env` est ignoré par Git.
- Le contenu des conversations n'est ni journalisé en production ni persisté
  côté navigateur (seul l'identifiant de session vit dans `sessionStorage`).
