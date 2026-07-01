# Tâche 1 — Tests, évaluation et amélioration

## Assigné à
**Salma Said** & **Mohamed Tamzirt** (travail collaboratif)

## Objectif
Réaliser une campagne de tests complète (fonctionnels, performance, sécurité, utilisabilité) et évaluer la qualité des réponses du chatbot selon des métriques définies.

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

## Critères de validation
- [ ] 50+ scénarios de test exécutés
- [ ] Score de pertinence > 85%
- [ ] Aucune faille de sécurité critique identifiée
- [ ] Temps de réponse moyen < 3 secondes
- [ ] Tous les bugs critiques sont corrigés
- [ ] Durée : **Semaine 7**
