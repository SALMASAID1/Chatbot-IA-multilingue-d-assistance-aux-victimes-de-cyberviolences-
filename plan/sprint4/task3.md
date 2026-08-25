# Tâche 3 — Documentation, guide d'administration et rapport final 🔄 EN COURS

## Assigné à
**Salma Said**

## Objectif
Rédiger toute la documentation technique et fonctionnelle du projet, incluant le guide d'administration, la documentation utilisateur, et le rapport de stage final.


## Statut : 🔄 EN COURS — c'est la tâche la plus en retard du projet

La documentation technique est faite. Il reste **la rédaction proprement dite** : les
passages du rapport que seuls les auteurs peuvent écrire, le guide d'administration, et
les diapositives de soutenance.

### Livrables produits
- `docs/rapport_projet.tex` + `docs/rapport_projet.pdf` — **24 pages A4**, compilées avec
  `pdflatex` (deux passes, aucune dépendance hors TeX Live standard, donc ouvrable tel quel
  dans Overleaf). Contient : page de garde, résumé FR et *abstract* EN, table des matières,
  5 chapitres, schéma d'architecture TikZ, 5 captures de l'interface, 8 tableaux de données
  mesurées, annexes, bibliographie
- `docs/guide_deploiement.md` — procédure de déploiement gratuit (187 lignes)
- `README.md` — présentation, installation, lancement
- `frontend/README.md` — architecture frontend, scripts, conteneurisation
- `WORKSPACE_ANALYSIS.md` — analyse complète du dépôt
- `docs/analyse_existant.md` — étude de l'existant (Sprint 1)
- `docs/scenarios_conversationnels.md` — 27 scénarios
- `ATTRIBUTIONS.md` — provenance et licences des ressources visuelles

### Reste à faire — par ordre de priorité

1. **Les 12 encadrés `\todo{}` du rapport.** Ils marquent volontairement ce qui ne peut
   pas être rédigé à votre place : remerciements, introduction, présentation du CMRPI,
   synthèse SWOT, les 5 personas, justification du choix de détection déterministe,
   diagramme de Gantt, latence de production, évaluation LLM actualisée, URL publique,
   conclusion, références internationales.
2. **Réexécuter l'évaluation LLM** (voir Sprint 4, tâche 1) : `docs/evaluation_llm.md`
   est périmé sur trois points et ne doit pas être cité tel quel.
3. **Rédiger le guide d'administration** — voir la réserve ci-dessous.
4. **Préparer les diapositives de soutenance.**

## Étapes d'implémentation

1. **Guide d'administration**
   - Comment ajouter/modifier du contenu dans la base de connaissances
   - Comment mettre à jour les prompts
   - Procédure de réindexation de la base vectorielle
   - Gestion des clés API et des quotas LLM
   - Monitoring et résolution des problèmes courants

2. **Documentation technique**
   - Architecture du système (diagrammes à jour)
   - Documentation de l'API (compléter Swagger)
   - Guide d'installation pour les développeurs
   - Structure du code et conventions

3. **Documentation utilisateur**
   - Guide d'utilisation du chatbot
   - FAQ des fonctionnalités
   - Captures d'écran annotées

4. **Rapport de stage final**
   - Mettre à jour le rapport LaTeX avec les résultats finaux
   - Ajouter les captures d'écran de l'application
   - Documenter les choix techniques et les compromis
   - Rédiger les perspectives et améliorations futures
   - Compiler le PDF final

5. **Préparation de la présentation**
   - Préparer les slides de soutenance (PowerPoint ou Beamer)
   - Préparer une démo live du chatbot
   - Anticiper les questions du jury

## Outils et ressources
- LaTeX pour le rapport (fichier existant `docs/rapport_projet.tex`)
- Markdown pour la documentation technique
- PowerPoint / Google Slides / Beamer pour la présentation
- Outils de capture d'écran

## Livrable attendu
- Documentation complète :
  - `docs/guide_administration.md` — Guide admin
  - `docs/guide_utilisateur.md` — Guide utilisateur
  - `docs/architecture.md` — Documentation technique
  - `docs/rapport_projet.pdf` — Rapport final compilé
  - `docs/presentation/` — Slides de soutenance
  - `README.md` — README principal du projet mis à jour


## Critères de validation — Résultats

- [x] La documentation technique est complète et à jour — README racine, README frontend, guide de déploiement, analyse du dépôt
- [x] Le README principal est complet avec instructions d'installation — installation, variables d'environnement, lancement backend et frontend, tests

### Réserves — trois critères non atteints

- [ ] **Le rapport de stage est finalisé et compilé en PDF — compilé, pas finalisé.**
  Le PDF existe et fait 24 pages, mais **12 encadrés `\todo{}`** signalent des sections
  encore vides. Le rapport n'est pas remettable en l'état.
- [ ] **Le guide d'administration couvre toutes les opérations courantes — non rédigé.**
  `docs/guide_deploiement.md` traite du *déploiement*, pas de l'*administration*. Il manque
  la procédure d'ajout ou de modification d'un document dans la base de connaissances, la
  mise à jour des prompts, et surtout **la procédure de réindexation** — c'est elle qui a
  manqué au projet : la base vectorielle est restée périmée pendant plusieurs jours
  (Sprint 2, tâche 1). Ce guide n'est pas cosmétique, il documente le geste qui a manqué.
- [ ] **Les slides de présentation sont prêtes — non commencées.**
- [ ] Durée : **Semaine 7-8** — en cours
