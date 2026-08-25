# Tâche 3 — Intégration Frontend-Backend et tests end-to-end 🔄 TERMINÉE — trois critères non vérifiés

## Assigné à
**Salma Said** & **Mohamed Tamzirt** (travail collaboratif)

## Objectif
Réaliser l'intégration complète entre le frontend React et le backend FastAPI, configurer le déploiement, et valider le fonctionnement end-to-end du chatbot.


## Statut : 🔄 TERMINÉE, avec trois critères explicitement non vérifiés

L'intégration frontend–backend fonctionne et est couverte par des tests. Trois critères de
validation n'ont **pas** pu être vérifiés sur le poste de développement et sont documentés
comme tels plus bas, plutôt que cochés par confort.

### Livrables produits
- Client d'API typé côté React (`frontend/src/lib/api/`), branché sur les 5 routes publiques
- CORS configuré côté FastAPI pour l'origine du frontend
- **7 tests de contrat exécutés contre le backend réel** (`live-contract.test.ts`, activés
  par `EMC_LIVE_API=1`) — ils vérifient que les schémas Zod correspondent aux réponses
  réellement émises par FastAPI, et pas seulement aux simulations
- **25 tests end-to-end Playwright** (`e2e/chat.spec.ts`, `mobile.spec.ts`, `scrolling.spec.ts`)
  sur API simulée, projets `desktop-chrome` et `mobile-chrome`
- `Dockerfile` racine (API + modèle d'embeddings préchargé), `frontend/Dockerfile`
  (multi-étages `node:22-alpine` → `nginx:1.27-alpine`), `docker-compose.yml`, `vercel.json`

### Détail découvert à l'intégration

Le backend émet ses horodatages avec `datetime.utcnow()`, donc **sans indicateur de fuseau**
(`"2026-08-24T19:59:24.616487"`). Interprétés tels quels par le navigateur, les messages
apparaissaient décalés d'une heure. `frontend/src/lib/datetime.ts` ajoute explicitement le
suffixe `Z` à l'analyse, avec un test dédié. Corriger la cause côté backend
(`datetime.now(timezone.utc)`) reste préférable, mais sortait du périmètre confié.

## Étapes d'implémentation

1. **Configuration de la communication Frontend-Backend**
   - Finaliser la configuration CORS sur FastAPI
   - Connecter le service API React aux endpoints FastAPI
   - Gérer les erreurs réseau côté frontend
   - Implémenter le retry automatique

2. **Tests d'intégration** *(Salma)*
   - Tester le flux complet : message → détection langue → RAG → LLM → réponse
   - Vérifier l'affichage correct des réponses en FR et AR
   - Tester le changement de langue en cours de conversation
   - Tester les cas limites (messages vides, très longs, caractères spéciaux)

3. **Optimisation des performances** *(Mohamed)*
   - Mesurer le temps de réponse bout-en-bout
   - Optimiser le chargement du frontend (lazy loading, code splitting)
   - Implémenter le caching côté backend (réponses fréquentes)
   - Compresser les réponses API (gzip)

4. **Configuration du déploiement**
   - Créer les fichiers Docker (Dockerfile frontend + backend)
   - Configurer `docker-compose.yml` pour le développement local
   - Préparer la configuration de production (Vercel + Cloud)

5. **Tests de compatibilité navigateur**
   - Chrome, Firefox, Safari, Edge
   - Responsive : mobile, tablette, desktop
   - Tests RTL sur différents navigateurs

## Outils et ressources
- Docker et docker-compose
- Outils de test (Postman, curl, navigateur)
- Lighthouse pour les audits de performance
- Vercel CLI pour le déploiement frontend

## Livrable attendu
- Application intégrée fonctionnelle avec :
  - Communication frontend-backend validée
  - `docker-compose.yml` pour le lancement local
  - Rapport de tests d'intégration
  - Guide de déploiement


## Critères de validation — Résultats

- [x] Le flux complet fonctionne de bout en bout — validé par les 7 tests de contrat contre l'API réelle **et** par un aller-retour de conversation réel
- [x] Les tests d'intégration passent tous — **348 tests automatisés** : 201 backend, 100 frontend, 25 end-to-end, 22 sur le script d'acquisition d'images
- [x] Durée : **Semaine 5-6** ✅

### Réserves — trois critères non validés en l'état

- [ ] **L'application fonctionne sur les 4 navigateurs principaux — non vérifié.**
  Playwright est configuré avec `channel: 'chrome'` sur ses deux projets : les tests
  s'exécutent **uniquement sur Google Chrome** (bureau et émulation Pixel 7). Firefox,
  Safari/WebKit et Edge n'ont **pas** été testés. Pour lever la réserve :
  `npx playwright install firefox webkit`, puis ajouter les projets correspondants.
- [ ] **Le déploiement Docker fonctionne avec `docker compose up` — non exécuté.**
  Le poste de développement n'avait plus l'espace disque nécessaire pour construire les
  images (≈ 2,1 Go libres). Ce qui a été fait à la place : `docker build --check` sur les
  deux `Dockerfile` et `docker compose config`, tous deux sans erreur. **Cela valide la
  syntaxe, pas la construction ni l'exécution.** À faire tourner avant la soutenance.
- [ ] **Le temps de réponse total est < 5 secondes — non mesuré.**
  Voir Sprint 2, tâche 2 : seule la récupération vectorielle est chronométrée (19 ms de
  médiane). La latence de l'API Gemini n'a pas été échantillonnée.
