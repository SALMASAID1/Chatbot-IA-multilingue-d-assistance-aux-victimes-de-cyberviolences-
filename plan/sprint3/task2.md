# Tâche 2 — Module multilingue et traduction ✅ TERMINÉE

## Assigné à
**Salma Said**

## Objectif
Développer le module de support multilingue complet, incluant la détection automatique de langue, la traduction dynamique des réponses, et la gestion des contenus bilingues dans le pipeline RAG.


## Statut : ✅ TERMINÉE

> **Décision d'architecture : pas de traduction automatique.** Le plan initial prévoyait
> une « traduction dynamique des réponses ». Elle a été écartée. Traduire mécaniquement
> un message d'accompagnement à une victime, c'est risquer de déformer un conseil
> juridique ou de casser le ton empathique — précisément ce qui compte ici. À la place,
> **chaque langue possède son propre contenu de bout en bout** : base de connaissances FR
> et AR séparées, prompt système FR et prompt système AR distincts, interface traduite
> à la main en `fr` / `ar` / `ary`. Le LLM répond dans la langue du contexte qu'il reçoit,
> jamais par traduction d'une réponse déjà écrite.

### Livrables produits
- `backend/services/language_service.py` — détection déterministe FR / AR / darija
  (**53 marqueurs darija en écriture arabe, 50 marqueurs arabizi en écriture latine**)
- `backend/tests/test_language_service.py` — **27 tests**
- `backend/prompts/system_prompt_fr.txt` (106 lignes) et `system_prompt_ar.txt` (98 lignes)
- `frontend/src/i18n/locales/` — `fr.json`, `ar.json`, `ary.json`, jeux de clés identiques
  (vérifié par `languages.test.ts`)
- Repli cross-lingue dans le retriever : `search_with_fallback()`

### Règle de détection retenue

1. **Présence d'un caractère arabe ⇒ `ar`.** Exact par construction, sans exception.
2. **Écriture latine ⇒ `fr`**, *sauf* si un marqueur arabizi **complet** est présent
   (comparaison par mot entier, jamais par sous-chaîne).
3. Les orthographes ambiguës qui sont aussi des mots français (`fin`) sont listées dans
   `DARIJA_AMBIGUOUS_LATIN` et ne suffisent jamais à elles seules à basculer en darija.

> 🚨 **Angle mort de sécurité corrigé (25/08/2026).** La détection de langue gérait
> l'arabizi, mais **pas la détection d'urgence** : `URGENCY_KEYWORDS_AR` ne contenait que
> des mots en écriture arabe. Conséquence — `« بغيت نموت »` déclenchait le protocole
> d'urgence, mais **`« bghit nmot »`, le même aveu d'idées suicidaires tapé au clavier
> latin, ne le déclenchait pas.** Une victime écrivant en arabizi, c'est-à-dire la façon
> la plus courante d'écrire la darija sur un téléphone, ne recevait aucun numéro d'urgence.
>
> Correctif : `URGENCY_KEYWORDS_ARABIZI` (**38 entrées**, avec les variantes
> orthographiques — l'arabizi n'a pas d'orthographe normalisée), comparées **sur des
> limites de mots** pour qu'un jeton court comme `nmot` ne puisse jamais se déclencher à
> l'intérieur d'un mot français. `detect_urgency()` teste en outre la liste française sur
> tout message en écriture latine routé vers `ar` : les locuteurs de darija alternent
> constamment avec le français, et `« wach kayn chi urgence »` doit compter.
> Couvert par `TestArabiziUrgencyDetection` — 16 formulations qui doivent alerter,
> 10 questions ordinaires qui ne doivent pas.

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


## Critères de validation — Résultats

- [x] La détection de darija fonctionne pour les messages courants — 103 marqueurs, écritures arabe et latine, 27 tests
- [x] Les réponses sont cohérentes quelle que soit la langue d'entrée — contenu dédié par langue plutôt que traduction
- [x] Le basculement de langue fonctionne en cours de conversation — détection message par message, plus un sélecteur explicite dans l'interface
- [x] Les traductions préservent le ton empathique — prompts rédigés séparément en FR et en AR, avec prise en compte de la *hchouma*
- [x] Durée : **Semaine 5-6** ✅

### Réserve sur la précision annoncée

- [ ] **La détection de langue est > 95 % de précision pour FR et AR — chiffre non mesuré.**
  Aucun corpus annoté n'a été constitué, aucun taux de précision n'a donc été calculé :
  **le seuil de 95 % ne doit pas être cité comme un résultat.** Ce qui est établi :
  la règle 1 (écriture arabe ⇒ `ar`) est exacte par construction, et 27 tests couvrent les
  cas de bascule. Le risque résiduel porte sur le **rappel en arabizi** — un message darija
  en écriture latine sans marqueur connu est traité comme du français.
  Pour mesurer réellement : annoter 200 messages réels (FR, AR, darija arabe, arabizi) et
  calculer précision et rappel par classe.
