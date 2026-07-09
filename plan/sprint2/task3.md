# Tâche 3 — Intégration LLM et conception des prompts

## Assigné à
**Salma Said** & **Mohamed Tamzirt** (travail collaboratif)

## Objectif
Intégrer un ou plusieurs LLM (GPT-4, Claude, Mistral) dans le pipeline, concevoir les system prompts optimisés pour l'assistance aux victimes de cyberviolences, et mettre en place un système de fallback multi-modèles.

## Prérequis (état actuel du projet)
- ✅ Base de connaissances FR complète : 23 documents structurés en Markdown dans `data/knowledge_base/fr/`
- ✅ Base de connaissances AR complète : 23 documents miroir dans `data/knowledge_base/ar/`
- ✅ Metadata JSON : index complet avec mots-clés FR et AR
- ✅ Catégories couvertes : juridique (3 lois), ressources (3), fiches pratiques (6), prévention (4), psychologie (3), rapports internationaux (4), FAQ (1)
- ⚠️ Le pipeline RAG (Tâche 1) et l'API FastAPI (Tâche 2) doivent être en cours ou fonctionnels
- ⚠️ Le dossier `backend/` n'existe pas encore — les modules `backend/rag/` et `backend/api/` seront créés par les Tâches 1 et 2

## Étapes d'implémentation

1. **Configuration des API LLM**
   - Configurer les clés API pour OpenAI (GPT-4), Anthropic (Claude), Mistral
   - Implémenter une couche d'abstraction pour changer de modèle facilement
   - Gérer les quotas et le fallback entre modèles
   ```python
   # Structure cible (à créer dans le backend existant)
   backend/
     llm/
       __init__.py
       provider.py        # Couche d'abstraction multi-modèles
       openai_client.py    # Client OpenAI/GPT-4
       anthropic_client.py # Client Anthropic/Claude
       mistral_client.py   # Client Mistral
       fallback.py         # Logique de fallback
     prompts/
       system_prompt_fr.txt  # Prompt système français
       system_prompt_ar.txt  # Prompt système arabe
       system_prompt_darija.txt # Prompt système darija
   ```

2. **Conception du system prompt principal (FR)** *(Salma)*
   - Prompt en français définissant le rôle empathique du chatbot
   - Instructions pour le ton (bienveillant, non-jugeant, professionnel)
   - Règles de sécurité (ne pas donner de conseils médicaux/juridiques formels)
   - Instructions pour l'utilisation du contexte RAG
   - S'appuyer sur le ton déjà établi dans les fichiers `psychologie/soutien_empathique.md` et `psychologie/resilience_coping.md`

3. **Conception du system prompt arabe** *(Mohamed)*
   - Adaptation du prompt en arabe standard
   - Version darija pour les réponses informelles (s'inspirer du ton du `faq/faq_cyberviolence.md` AR)
   - Gestion des spécificités culturelles (référence au concept de حشومة/hchouma)

4. **Prompt engineering et optimisation**
   - Tester différentes variantes de prompts
   - Évaluer la qualité des réponses (empathie, précision, pertinence)
   - Optimiser les prompts avec des exemples few-shot tirés des scénarios de la base de connaissances
   - Documenter les prompts finaux

5. **Mise en place du fallback multi-modèles**
   - Modèle principal : GPT-4 ou Claude
   - Fallback : Mistral (open-source, hébergeable localement)
   - Gestion des erreurs et des timeouts

6. **Tests de qualité des réponses**
   - Créer un jeu de test avec 20+ scénarios couvrant les 6 types de cyberviolence documentés
   - Scénarios à inclure obligatoirement :
     - Cyberharcèlement (FR et AR)
     - Sextorsion avec demande d'aide urgente
     - Question juridique sur les lois 103-13, 09-08, 07-03
     - Demande de numéros d'urgence
     - Situation de danger immédiat (test du protocole d'urgence)
     - Message en darija
   - Évaluer sur des critères : empathie, précision, sécurité, langue
   - Documenter les résultats

## Ressources du projet disponibles
- 23 documents FR + 23 documents AR structurés et indexés
- Numéros d'urgence vérifiés : Police 19, Gendarmerie 177, ONDE 2511
- Plateformes référencées : E-Blagh, Cyberconfiance, eVigilance
- 3 textes de loi résumés avec peines et articles précis
- Contenu psychologique validé (impact, soutien, résilience)

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
- [ ] Les réponses citent correctement les numéros d'urgence (19, 177, 2511)
- [ ] Aucune réponse dangereuse ou inappropriée dans les tests
- [ ] Les réponses en darija sont naturelles et compréhensibles
- [ ] Durée : **Semaine 3-4** (en parallèle avec les tâches 1 et 2)
