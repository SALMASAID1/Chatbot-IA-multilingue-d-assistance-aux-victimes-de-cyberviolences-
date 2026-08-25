# Tâche 2 — Optimisation et déploiement en production

## Assigné à
**Mohamed Tamzirt** (déploiement) & **Salma Said** (validation end-to-end)

## Objectif
Rendre le chatbot accessible publiquement via une URL HTTPS gratuite, en vue de la
démonstration aux encadrants, sans dégrader la qualité du pipeline RAG déjà validé.

## Statut : 🟡 EN COURS — code prêt, déploiement à effectuer

> **Fait (25 août) :** sécurisation des endpoints d'administration, image Docker
> du Space, configuration Vercel, `.env.example`, guide de déploiement.
> **Reste à faire (manuel) :** créer le Space et le projet Vercel, y renseigner
> les secrets, pousser, puis dérouler la validation end-to-end de la section 5.

---

## Décision d'architecture — Hugging Face Spaces + Vercel

| Composant | Plateforme | Coût | Justification |
|---|---|---|---|
| **Backend** (FastAPI + RAG) | **Hugging Face Spaces** (SDK Docker) | Gratuit | Seul palier gratuit offrant assez de RAM (2 vCPU / 16 Go) pour `torch` + `sentence-transformers` |
| **Frontend** (React/Vite) | **Vercel** (Hobby) | Gratuit | Build statique, HTTPS automatique, et `rewrites` pour proxifier `/api` |

### Pourquoi ce choix

1. **Contrainte mémoire.** Le pipeline embarque le modèle d'embeddings local
   `paraphrase-multilingual-MiniLM-L12-v2`, soit environ **1,8 Go** à l'exécution
   (torch 1,2 Go + transformers 114 Mo + poids du modèle 458 Mo). Les paliers
   gratuits classiques (Render : 512 Mo de RAM) provoquent un dépassement mémoire.
   Hugging Face Spaces fournit 16 Go de RAM gratuitement.
2. **Aucune modification du pipeline RAG.** La solution alternative (remplacer les
   embeddings locaux par l'API d'embeddings Gemini) réduirait l'image à ~150 Mo,
   mais **changerait la distribution des scores de similarité**. Or
   `SIMILARITY_THRESHOLD = 0.15` et les poids de reclassement lexical
   (`0.12` / `0.04` dans `backend/rag/retriever.py`) ont été calibrés pour ce modèle
   précis. Un changement imposerait une ré-ingestion et un recalibrage complets —
   inenvisageable à quelques jours de la soutenance.
3. **Mise en veille tolérable.** Un Space se met en veille après ~48 h d'inactivité,
   contre 15 minutes chez Render : le service reste chaud le jour de la démonstration.
4. **Pertinence pédagogique.** Hugging Face est la plateforme de référence pour un
   projet d'IA ; le choix est immédiatement lisible pour l'encadrement technique.

> **Amélioration post-PFA (hors périmètre) :** migrer vers les embeddings Gemini
> pour diviser l'image par 10 et réduire le démarrage à froid de ~30 s à ~2 s.
> Voir `docs/guide_deploiement.md`, section « Évolutions ».

---

## Étapes d'implémentation

### 1. Sécurisation préalable ✅ FAIT
- [x] Protéger les endpoints `/api/admin/*` par une clé d'API (`ADMIN_API_KEY`)
- [x] Comportement par défaut : **si la clé n'est pas configurée, le routeur admin
      n'est pas monté du tout** (une exposition publique non authentifiée
      permettrait de lister et supprimer les sessions des victimes)
- [x] Tests unitaires : accès refusé sans clé, accepté avec la bonne clé

### 2. Image Docker pour Hugging Face Spaces ✅ FAIT
- [x] `Dockerfile` à la racine (exigé par le SDK Docker de HF), port **7860**
- [x] Installer `torch` depuis l'index **CPU** (évite ~2 Go de dépendances CUDA inutiles)
- [x] **Pré-télécharger le modèle d'embeddings pendant le build**, puis
      `EMBEDDING_LOCAL_FILES_ONLY=true` à l'exécution
- [x] **Construire la base vectorielle pendant le build**
      (`python -m backend.rag.embeddings`) : démarrage déterministe, aucun
      téléchargement de 458 Mo pendant la démonstration
- [x] `README.md` racine avec l'en-tête YAML requis par Hugging Face

### 3. Déploiement du frontend (Vercel) — 🟡 configuration prête
- [x] `vercel.json` : build Vite, sortie `frontend/dist`, fallback SPA
- [x] `rewrites` de `/api/*` vers l'URL du Space → **même origine**, donc aucun
      CORS à configurer et la CSP stricte (`connect-src 'self'`) reste valable
- [x] En-têtes de sécurité (CSP, `X-Frame-Options`, `Referrer-Policy`)

### 4. Configuration et secrets
- [ ] `GOOGLE_API_KEY` et `ADMIN_API_KEY` dans le panneau *Secrets* du Space —
      **jamais** dans l'image ni dans Git
- [ ] `CORS_ORIGINS` renseigné avec l'URL Vercel (filet de sécurité)
- [x] `.env.example` mis à jour

### 5. Validation end-to-end
- [ ] `GET /api/health` renvoie `status: healthy` en production
- [ ] Conversation complète FR, AR et darija depuis un téléphone réel
- [ ] Protocole d'urgence vérifié en production (réponse immédiate, liens `tel:`)
- [ ] `/api/admin/sessions` renvoie **401** sans clé
- [ ] Suite de tests complète toujours verte après les modifications

### 6. Documentation ✅ FAIT
- [x] `docs/guide_deploiement.md` — procédure pas à pas, rollback, dépannage

---

## Constat lors de la mise en place (25 août)

La base vectorielle persistée localement était **périmée** : elle contenait 748
vecteurs alors que la base de connaissances actuelle en produit **820**.
Les 72 vecteurs manquants correspondaient exactement aux **paires questions-réponses
arabes** de `docs/livrable-1/base_questions_reponses_ar.md`, dont l'analyse
(`(?:Q|س)`) n'a été ajoutée qu'au commit `f8ca6b0` — postérieur à la dernière
ingestion. Autrement dit, le volet arabe/darija répondait **sans** les 32 paires
Q/R validées du livrable 1.

La reconstruction a corrigé le problème (**+34 % de contenu arabe indexé**) et
justifie la décision de construire la base vectorielle **pendant le build Docker**
plutôt que d'embarquer un artefact figé.

| | Avant | Après |
|---|---|---|
| Vecteurs FR | 535 | 535 |
| Vecteurs AR | 213 | **285** |
| **Total** | 748 | **820** |

---

## Rétroplanning (soutenance le 30 août 2026)

| Date | Action |
|---|---|
| **25 août** | Sécurisation admin + image Docker → backend en ligne |
| **26 août** | Frontend Vercel + vérification end-to-end sur mobile |
| **27 août** | Répétition de la démonstration, captures d'écran de secours |
| **28 août** | **Gel du code.** Documentation et rapport uniquement |
| 29–30 août | Marge de sécurité |

---

## Outils et ressources
- Hugging Face Spaces (SDK Docker, palier CPU basic gratuit)
- Vercel Hobby (frontend statique + `rewrites`)
- Docker (build multi-étapes déjà en place pour le frontend)
- Plan de repli hors ligne : `python backend/demo_cli.py --auto`

## Livrable attendu
- URL publique HTTPS fonctionnelle (frontend + backend)
- `Dockerfile` racine (Space) et `vercel.json` versionnés
- Endpoints d'administration authentifiés
- `docs/guide_deploiement.md` permettant une reproduction complète

## Critères de validation
- [ ] L'application est accessible via une URL publique en HTTPS
- [ ] Le temps de réponse en production est < 5 secondes (hors démarrage à froid)
- [ ] Les endpoints `/api/admin/*` sont inaccessibles sans clé
- [ ] Aucun secret n'est présent dans l'image ni dans le dépôt Git
- [ ] Les numéros d'urgence restent affichés même si le backend est indisponible
- [ ] Le guide de déploiement permet une reproduction complète
- [ ] Durée : **Semaine 7-8**
