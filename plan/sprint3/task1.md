# Tâche 1 — Développement de l'interface React (Frontend) ✅ TERMINÉE

## Assigné à
**Mohamed Tamzirt**

## Objectif
Développer l'interface utilisateur du chatbot avec React.js, incluant un design responsive, le support RTL pour l'arabe, une expérience conversationnelle fluide, et une intégration avec l'API backend.


## Statut : ✅ TERMINÉE

> **Décisions d'architecture (écarts assumés par rapport au plan initial) :**
> - **TypeScript en mode strict** plutôt que JavaScript : les réponses de l'API sont
>   validées à l'exécution par des schémas **Zod**, si bien qu'un changement de contrat
>   backend produit une erreur explicite au lieu d'un écran blanc.
> - **TanStack Query** plutôt qu'`axios` seul, pour le cache d'historique et les états de
>   chargement. Règle de sécurité appliquée : **`POST /api/chat` n'est jamais rejoué
>   automatiquement**, un renvoi automatique dupliquerait le message d'une victime.
> - **`react-markdown` + `rehype-sanitize`** : `dangerouslySetInnerHTML` n'apparaît nulle
>   part dans le code. Les liens sont filtrés par une liste blanche de schémas
>   (`http`, `https`, `mailto`, `tel`) et reçoivent `rel="noopener noreferrer"`.
> - **Aucune interface d'administration n'a été développée**, volontairement (voir la
>   réserve en fin de fiche).

### Livrables produits
- `frontend/` — application React 19 + Vite 7, **55 fichiers source** (30 `.tsx`, 25 `.ts`),
  4 706 lignes hors tests
- `frontend/src/features/chat/` — `ChatView`, `ChatComposer`, `ChatTimeline`,
  `MessageBubble`, `SourceDisclosure`, `WelcomePanel`, `UrgentResponsePanel`,
  `EmergencyContacts`, `FeedbackControl`
- `frontend/src/lib/api/` — client `fetch` typé, schémas Zod, taxonomie d'erreurs
- `frontend/src/lib/security/` — liste blanche de schémas d'URL, schéma d'assainissement
  Markdown, stockage restreint à l'identifiant de session
- `frontend/src/i18n/locales/` — `fr.json`, `ar.json`, `ary.json` (jeux de clés identiques)
- `frontend/src/styles/index.css` — jetons de design Tailwind v4 (`@theme`)
- 100 tests unitaires + 25 tests end-to-end Playwright

### Confidentialité — règles tenues

| Règle | Mise en œuvre |
|---|---|
| Aucun contenu de message journalisé | aucun `console.log` de message en production |
| Aucune analytique, publicité, empreinte, rejeu de session | aucune dépendance tierce de ce type |
| Seul l'identifiant de session est stocké | `sessionStorage`, jamais `localStorage` |
| Le classement `user_profile` n'est pas montré | absent de l'interface |
| Aucun appel téléphonique déclenché automatiquement | les numéros sont des liens `tel:` que l'utilisateur active |

> 🐛 **Défauts de défilement corrigés (24/08/2026).** Trois bogues réels signalés en revue :
> la page ne suivait pas les nouveaux messages (la mesure initiale désactivait le suivi dès
> que le panneau d'accueil dépassait la hauteur de fenêtre), le fil « rebondissait » vers le
> bas pendant la lecture, et la pastille « nouvelle réponse » recouvrait la zone de saisie.
> Corrigés dans `useConversationScroll.ts` et `ChatView.tsx`, avec `e2e/scrolling.spec.ts`
> en garde-fou.

## Étapes d'implémentation

1. **Initialisation du projet React**
   - Créer le projet avec Vite (`npx -y create-vite@latest frontend --template react`)
   - Installer les dépendances : `axios`, `react-markdown`, `i18next`
   - Configurer la structure du projet

2. **Développement des composants principaux**
   ```
   frontend/src/
     components/
       ChatWindow.jsx       # Fenêtre de conversation principale
       MessageBubble.jsx    # Bulle de message (user/bot)
       InputBar.jsx         # Barre de saisie avec envoi
       LanguageSelector.jsx # Sélecteur FR/AR
       Header.jsx           # En-tête avec logo CMRPI/EMC
       WelcomeScreen.jsx    # Écran d'accueil
       TypingIndicator.jsx  # Indicateur de saisie du bot
       ResourceCard.jsx     # Carte de ressource d'aide
     pages/
       ChatPage.jsx         # Page principale du chat
     services/
       api.js               # Appels API backend
     styles/
       global.css           # Styles globaux
       chat.css             # Styles du chat
       rtl.css              # Styles RTL pour l'arabe
   ```

3. **Design UI/UX**
   - Palette de couleurs conforme à l'identité CMRPI/EMC
   - Design responsive (mobile-first)
   - Mode sombre optionnel
   - Animations de transition fluides
   - Accessibilité (WCAG 2.1 AA)

4. **Support RTL (Right-to-Left)**
   - Basculement automatique de la direction du texte
   - Adaptation du layout pour l'arabe
   - Tests visuels en mode RTL

5. **Intégration avec l'API backend**
   - Service API avec gestion des erreurs
   - Indicateur de chargement pendant la génération
   - Gestion de la reconnexion
   - Streaming des réponses (si supporté)

6. **Fonctionnalités additionnelles**
   - Historique de conversation scrollable
   - Boutons de suggestion rapide
   - Partage/export de la conversation
   - Responsive design pour mobile

## Outils et ressources
- React.js + Vite
- CSS Modules ou styled-components
- Axios pour les appels API
- react-i18next pour l'internationalisation
- Figma ou Adobe XD pour les maquettes (optionnel)

## Livrable attendu
- Application frontend complète dans `frontend/` avec :
  - Interface de chat fonctionnelle en FR et AR
  - Support RTL pour l'arabe
  - Design responsive et accessible
  - Intégration API fonctionnelle
  - README avec instructions de lancement


## Critères de validation — Résultats

- [x] L'interface fonctionne sur mobile, tablette et desktop — mises en page fluides, projet Playwright `mobile-chrome` (Pixel 7) en plus du bureau
- [x] Le mode RTL s'active automatiquement en arabe — `dir` piloté par la langue, propriétés CSS logiques, test axe dédié à l'interface arabe
- [x] Les messages s'affichent avec formatage (markdown, liens) — `react-markdown` assaini, liens externes filtrés
- [x] L'indicateur de chargement fonctionne — état de rédaction annoncé aux lecteurs d'écran (`aria-live="polite"`)
- [x] Durée : **Semaine 5-6** ✅

### Réserves — deux critères non validés en l'état

- [ ] **Score Lighthouse > 85 en accessibilité — non mesuré.** Lighthouse n'a pas été
  exécuté. Ce qui *a* été fait : **axe-core ne relève aucune violation** sur six états de
  l'interface (accueil, conversation en cours, état d'urgence, interface arabe RTL,
  boîte de dialogue d'aide, service dégradé), et un test dédié vérifie les rapports de
  contraste de la palette au seuil WCAG 2.2 AA. C'est une garantie plus étroite qu'un
  score Lighthouse : **à exécuter avant la soutenance** pour pouvoir citer le chiffre.
- [ ] **L'identité visuelle CMRPI/EMC est respectée — à faire valider.** Aucune charte
  graphique officielle CMRPI/EMC ne nous a été transmise. La palette et la typographie
  ont été construites comme un système de jetons cohérent avec le registre institutionnel
  d'EMC, mais **la conformité à la charte réelle reste à confirmer par l'encadrante.**

### Limitation assumée — pas d'interface d'administration

Aucun écran d'administration n'a été développé, **délibérément**. Les routes
`/api/admin/*` n'étaient pas authentifiées au moment du développement du frontend :
construire une interface par-dessus aurait rendu visible et commode une surface exposant
les identifiants de session des victimes. Ces routes sont depuis protégées par une clé
d'API (Sprint 2, tâche 2), mais la décision est maintenue pour le périmètre PFA :
l'administration se fait en ligne de commande, par un opérateur détenant la clé.
