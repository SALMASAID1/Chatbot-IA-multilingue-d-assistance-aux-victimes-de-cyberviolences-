# Tâche 1 — Développement de l'interface React (Frontend)

## Assigné à
**Mohamed Tamzirt**

## Objectif
Développer l'interface utilisateur du chatbot avec React.js, incluant un design responsive, le support RTL pour l'arabe, une expérience conversationnelle fluide, et une intégration avec l'API backend.

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

## Critères de validation
- [ ] L'interface fonctionne sur mobile, tablette et desktop
- [ ] Le mode RTL s'active automatiquement en arabe
- [ ] Les messages s'affichent avec formatage (markdown, liens)
- [ ] L'indicateur de chargement fonctionne
- [ ] L'identité visuelle CMRPI/EMC est respectée
- [ ] Score Lighthouse > 85 en accessibilité
- [ ] Durée : **Semaine 5-6**
