# Tâche 3 — Intégration LLM et conception des prompts ✅ TERMINÉE

## Assigné à
**Salma Said** & **Mohamed Tamzirt** (travail collaboratif)

## Objectif
Intégrer le modèle LLM (Google Gemini), concevoir les system prompts optimisés pour l'assistance aux victimes de cyberviolences en français et arabe/darija, et mettre en place la suite de tests de qualité.

## Statut : ✅ TERMINÉE

> **Décision d'architecture :** Utilisation de **Google Gemini** comme modèle LLM principal
> via `backend/llm/gemini_provider.py`. Le modèle est **configurable** et non figé dans le
> code : `GEMINI_MODEL` vaut `gemini-3.5-flash-lite` par défaut, avec repli automatique sur
> `GEMINI_FALLBACK_MODELS` (`gemini-3.1-flash-lite`, `gemini-3.6-flash`) lorsque le quota du
> modèle principal est épuisé — ce qui arrive avec un compte gratuit. La couche d'abstraction
> `GeminiProvider` permet de changer de fournisseur à tout moment.

### Livrables produits
- `backend/prompts/system_prompt_fr.txt` — System prompt français (106 lignes)
- `backend/prompts/system_prompt_ar.txt` — System prompt arabe et darija (98 lignes)
- `backend/llm/gemini_provider.py` — Module d'intégration Gemini avec gestion centralisée des erreurs et configuration
- `backend/tests/test_response_quality.py` — Suite de tests d'évaluation de la qualité des réponses (20 scénarios paramétrés)
- `docs/evaluation_llm.md` — Rapport d'évaluation et de validation des réponses LLM

> ⚠️ **Fiche corrigée le 25/08/2026.** Elle annonçait « Gemini 2.5 Flash » et des prompts de
> 184 et 76 lignes. Ni l'un ni l'autre n'était exact : la configuration utilise
> `gemini-3.5-flash-lite` et les prompts font 106 et 98 lignes. `docs/evaluation_llm.md`
> porte encore les mêmes erreurs et **reste à réécrire** (voir Sprint 4, tâche 1).

## Critères de validation — Résultats

- [x] Modèle LLM configuré : Gemini via le fournisseur abstrait `GeminiProvider`, modèle et replis pilotés par variables d'environnement
- [x] System prompts externalisés et validés en FR et AR dans `backend/prompts/`
- [x] Les réponses sont empathiques et contextuellement pertinentes (validation psychoéducation & météo des émotions)
- [x] Les réponses citent correctement les numéros d'urgence (Police 19, Gendarmerie 177, ONDE 2511, Protection Civile 15)
- [x] Aucune réponse dangereuse ou inappropriée dans la suite de tests (20/20 scénarios valides)
- [x] Les réponses et exercices en darija sont intégrés et naturels
- [x] Durée : **Semaine 3-4** ✅

