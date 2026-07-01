# Tâche 2 — Module multilingue et traduction

## Assigné à
**Salma Said**

## Objectif
Développer le module de support multilingue complet, incluant la détection automatique de langue, la traduction dynamique des réponses, et la gestion des contenus bilingues dans le pipeline RAG.

## Étapes d'implémentation

1. **Amélioration de la détection de langue**
   - Intégrer un modèle robuste pour détecter FR, AR standard et Darija
   - Tester avec des messages courts et ambigus
   - Gérer le code-switching (mélange FR/AR dans un même message)
   - Utiliser `fasttext` ou un modèle fine-tuné pour la darija

2. **Développement du module de traduction**
   ```python
   backend/services/
     translation/
       __init__.py
       translator.py       # Interface de traduction
       language_detector.py # Détection robuste de la langue
       darija_handler.py    # Gestion spécifique du darija
   ```
   - Traduction des requêtes utilisateur pour le RAG (si nécessaire)
   - Traduction des réponses dans la langue de l'utilisateur
   - Préservation du contexte et du ton empathique lors de la traduction

3. **Adaptation du pipeline RAG multilingue**
   - Recherche cross-lingue dans la base vectorielle
   - Utilisation d'embeddings multilingues (ex: `multilingual-e5-large`)
   - Filtrage par langue avec fallback cross-lingue

4. **Gestion du Darija**
   - Créer un lexique darija-français pour les termes courants
   - Adapter les réponses au registre informel du darija
   - Tester avec des cas d'usage réels en darija

5. **Tests multilingues**
   - Suite de tests avec messages en FR, AR et Darija
   - Tests de cohérence (même question dans différentes langues)
   - Évaluation de la qualité de traduction

## Outils et ressources
- `fasttext` pour la détection de langue (inclut la darija)
- `sentence-transformers` multilingues
- API de traduction (Google Translate, DeepL) comme fallback
- Corpus de test en darija

## Livrable attendu
- Module multilingue complet dans `backend/services/translation/` avec :
  - Détecteur de langue FR/AR/Darija
  - Service de traduction intégré
  - Pipeline RAG multilingue
  - Suite de tests avec couverture multilingue
  - Documentation des spécificités linguistiques

## Critères de validation
- [ ] La détection de langue est > 95% de précision pour FR et AR
- [ ] La détection de darija fonctionne pour les messages courants
- [ ] Les réponses sont cohérentes quelle que soit la langue d'entrée
- [ ] Le basculement de langue fonctionne en cours de conversation
- [ ] Les traductions préservent le ton empathique
- [ ] Durée : **Semaine 5-6**
