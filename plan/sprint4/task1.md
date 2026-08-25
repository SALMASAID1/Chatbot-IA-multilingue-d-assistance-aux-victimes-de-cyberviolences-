# Tâche 1 — Tests, évaluation et amélioration 🔄 EN COURS — campagne automatisée faite, évaluation qualitative à refaire

## Assigné à
**Salma Said** & **Mohamed Tamzirt** (travail collaboratif)

## Objectif
Réaliser une campagne de tests complète (fonctionnels, performance, sécurité, utilisabilité) et évaluer la qualité des réponses du chatbot selon des métriques définies.


## Statut : 🔄 EN COURS

La campagne de tests **automatisés** est faite et verte. La campagne d'**évaluation
qualitative** (pertinence des réponses, latence réelle) est en revanche à refaire : le
rapport `docs/evaluation_llm.md` date du 14 août et décrit un système qui a changé depuis.

### Livrables produits
- **348 tests automatisés, tous verts :**

  | Suite | Tests | Commande |
  |---|---|---|
  | Backend (`pytest`) | 201 réussis, 7 ignorés | `cd backend && pytest` |
  | Frontend (`vitest`) | 100 réussis, 7 ignorés | `cd frontend && npm test` |
  | End-to-end (`playwright`) | 25 réussis, 3 ignorés | `cd frontend && npx playwright test` |
  | Script d'images (`pytest`) | 22 réussis | `pytest scripts/tests` |

  > Les tests ignorés le sont volontairement : ils exigent une clé `GOOGLE_API_KEY`
  > (backend) ou un backend en écoute avec `EMC_LIVE_API=1` (frontend).
  >
  > ⚠️ La suite frontend exige **Node ≥ 20.19** (`.nvmrc` épingle 22.23.1). Avec le
  > `/usr/bin/node` 18 du poste, `vitest` échoue sur une erreur `ERR_REQUIRE_ESM` dans
  > `jsdom` qui n'a rien à voir avec le code du projet. Faire `nvm use` d'abord.

- `docs/scenarios_conversationnels.md` — **27 scénarios conversationnels rédigés**
- `backend/tests/test_response_quality.py` — **20 scénarios automatisés** couvrant les
  5 profils utilisateurs, les deux langues et le protocole d'urgence

### Bogues sérieux trouvés et corrigés pendant la campagne

| # | Défaut | Gravité | État |
|---|---|---|---|
| 1 | Routes `/api/admin/*` accessibles **sans authentification**, exposant les identifiants de session de toutes les victimes connectées | Critique | ✅ Corrigé — clé d'API (`aa2a6de`) |
| 2 | Idées suicidaires en **arabizi** (`bghit nmot`) non détectées comme urgence, alors que la même phrase en écriture arabe l'était | Critique | ✅ Corrigé — `URGENCY_KEYWORDS_ARABIZI` |
| 3 | Base vectorielle **périmée** : 748 vecteurs au lieu de 820, les **72 chunks des paires Q/R arabes** absents de la recherche | Majeure | ✅ Corrigé — réindexation |
| 4 | Trois défauts de défilement du fil de conversation | Majeure | ✅ Corrigé — `e2e/scrolling.spec.ts` |
| 5 | Horodatages backend sans fuseau, messages décalés d'une heure | Mineure | ✅ Contourné côté frontend |

### Revue de sécurité — ce qui a été fait

| Contrôle | État |
|---|---|
| Authentification des routes d'administration | ✅ clé d'API, comparaison à temps constant |
| Limitation de débit | ✅ `slowapi`, 30/min (chat) et 10/min (admin) |
| Validation des entrées | ✅ Pydantic v2, message borné à 2 000 caractères |
| Injection HTML dans les réponses Markdown | ✅ `rehype-sanitize`, aucun `dangerouslySetInnerHTML` |
| Schémas d'URL autorisés | ✅ liste blanche `http` / `https` / `mailto` / `tel` |
| En-têtes de sécurité | ✅ CSP, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`, `X-Robots-Tag` |
| Secrets dans le dépôt ou l'image Docker | ✅ aucun — `.env` exclu par `.dockerignore` et `.gitignore` |
| Données personnelles journalisées | ✅ aucun contenu de message ni profil dans les journaux |

## Étapes d'implémentation

1. **Définition du protocole de test** *(ensemble)*
   - Créer un jeu de test de 50+ conversations couvrant tous les scénarios
   - Définir les métriques d'évaluation :
     - Pertinence (la réponse répond-elle à la question ?)
     - Empathie (le ton est-il approprié ?)
     - Précision (les informations sont-elles correctes ?)
     - Sécurité (aucune réponse dangereuse ?)
     - Multilingue (la qualité est-elle constante entre les langues ?)

2. **Tests fonctionnels** *(Salma)*
   - Tester chaque scénario conversationnel défini au Sprint 1
   - Vérifier la détection correcte du type de cyberviolence
   - Tester les cas limites et les situations d'urgence
   - Documenter les bugs et les réponses insatisfaisantes

3. **Tests de performance** *(Mohamed)*
   - Mesurer les temps de réponse sous charge
   - Tester avec des requêtes simultanées (load testing)
   - Vérifier la stabilité sur des sessions longues
   - Optimiser les goulots d'étranglement identifiés

4. **Tests de sécurité** *(ensemble)*
   - Tester les injections de prompt (prompt injection)
   - Vérifier que le chatbot ne divulgue pas de données sensibles
   - Tester les tentatives de manipulation
   - Valider la conformité RGPD / Loi 09-08

5. **Évaluation qualitative**
   - Faire tester par des utilisateurs externes (si possible)
   - Recueillir des retours sur l'expérience utilisateur
   - Évaluer l'adéquation culturelle des réponses

6. **Correction et amélioration**
   - Corriger les bugs identifiés
   - Améliorer les prompts en fonction des résultats
   - Enrichir la base de connaissances si nécessaire

## Outils et ressources
- Scripts de tests automatisés (pytest, Playwright)
- Locust ou k6 pour les tests de charge
- Grille d'évaluation qualitative
- Utilisateurs testeurs (collègues, encadrants)

## Livrable attendu
- Rapport de tests `docs/rapport_tests.md` avec :
  - Résultats des tests par catégorie
  - Métriques de qualité des réponses
  - Liste des bugs corrigés
  - Recommandations d'amélioration
  - Captures d'écran des tests


## Critères de validation — Résultats

- [x] Aucune faille de sécurité **critique** identifiée reste ouverte — les deux failles critiques trouvées (administration non authentifiée, urgence arabizi) sont corrigées et couvertes par des tests
- [x] Tous les bugs critiques sont corrigés — voir le tableau des 5 défauts ci-dessus

### Réserves — trois critères non atteints

- [ ] **50+ scénarios de test exécutés — 47 à ce jour, et pas sous la forme prévue.**
  Le décompte réel : **27 scénarios conversationnels rédigés** dans
  `docs/scenarios_conversationnels.md` et **20 scénarios automatisés** dans
  `test_response_quality.py`. Ce ne sont pas 50 conversations réelles jouées de bout en
  bout avec un LLM en ligne, ce que demandait le plan. **À compléter** par une session de
  test manuelle sur l'instance déployée.
- [ ] **Score de pertinence > 85 % — non mesuré.**
  Aucune notation humaine des réponses n'a été réalisée. `docs/evaluation_llm.md` **ne
  peut pas être cité en l'état** : il annonce Gemini 2.5 Flash alors que la configuration
  utilise `gemini-3.5-flash-lite`, donne 184 et 76 lignes pour des prompts qui en font
  106 et 98, et date d'avant l'ajout des 72 vecteurs arabes. **À refaire avant la
  soutenance**, et c'est le point le plus coûteux qui reste.
- [ ] **Temps de réponse moyen < 3 secondes — non mesuré.**
  Seule la récupération vectorielle est chronométrée : **19 ms de médiane** sur
  20 exécutions. La latence de bout en bout dépend de l'API Gemini et n'a pas été
  échantillonnée. Mesure à faire sur l'instance déployée, sur au moins 20 requêtes réelles.
- [ ] Durée : **Semaine 7** — dépassée, finalisation en cours
