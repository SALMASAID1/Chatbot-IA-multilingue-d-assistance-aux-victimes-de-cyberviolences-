# Tâche 3 — Intégration LLM et conception des prompts

## Assigné à
**Salma Said** & **Mohamed Tamzirt** (travail collaboratif)

## Objectif
Intégrer un ou plusieurs LLM (GPT-4, Claude, Mistral) dans le pipeline, concevoir les system prompts optimisés pour l'assistance aux victimes de cyberviolences, et mettre en place un système de fallback multi-modèles.

## Étapes d'implémentation

1. **Configuration des API LLM**
   - Configurer les clés API pour OpenAI (GPT-4), Anthropic (Claude), Mistral
   - Implémenter une couche d'abstraction pour changer de modèle facilement
   - Gérer les quotas et le fallback entre modèles

2. **Conception du system prompt principal** *(Salma)*
   - Prompt en français définissant le rôle empathique du chatbot
   - Instructions pour le ton (bienveillant, non-jugeant, professionnel)
   - Règles de sécurité (ne pas donner de conseils médicaux/juridiques formels)
   - Instructions pour l'utilisation du contexte RAG

3. **Conception du system prompt arabe** *(Mohamed)*
   - Adaptation du prompt en arabe standard
   - Version darija pour les réponses informelles
   - Gestion des spécificités culturelles

4. **Prompt engineering et optimisation**
   - Tester différentes variantes de prompts
   - Évaluer la qualité des réponses (empathie, précision, pertinence)
   - Optimiser les prompts avec des exemples few-shot
   - Documenter les prompts finaux

5. **Mise en place du fallback multi-modèles**
   - Modèle principal : GPT-4 ou Claude
   - Fallback : Mistral (open-source, hébergeable localement)
   - Gestion des erreurs et des timeouts

6. **Tests de qualité des réponses**
   - Créer un jeu de test avec 20+ scénarios de conversation
   - Évaluer sur des critères : empathie, précision, sécurité, langue
   - Documenter les résultats

## Outils et ressources
- OpenAI API, Anthropic API, Mistral API
- LangChain pour l'orchestration
- Jeu de données de test (scénarios de conversation)

## Livrable attendu
- Module `backend/llm/` avec :
  - Gestionnaire multi-modèles
  - Prompts optimisés (FR et AR) dans `backend/prompts/`
  - Rapport d'évaluation des modèles
  - Tests de qualité documentés

## Critères de validation
- [ ] Au moins 2 LLM configurés avec fallback
- [ ] System prompts validés en FR et AR
- [ ] Les réponses sont empathiques et contextuellement pertinentes
- [ ] Aucune réponse dangereuse ou inappropriée dans les tests
- [ ] Durée : **Semaine 3-4** (en parallèle avec les tâches 1 et 2)
