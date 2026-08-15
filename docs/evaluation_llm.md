# Rapport d'Évaluation LLM et des System Prompts

**Projet :** Chatbot IA multilingue d'assistance aux victimes de cyberviolences  
**Organisme :** Espace Maroc Cyberconfiance (EMC) / CMRPI  
**Modèle Évalué :** Google Gemini 2.5 Flash (`gemini-2.5-flash`)  
**Date d'évaluation :** 14 Août 2026  

---

## 1. Modèle Sélectionné & Justification

Dans le cadre du projet PFA, le modèle **Google Gemini 2.5 Flash** a été retenu pour les raisons suivantes :

1. **Multilinguisme natif élevé :** Excellentes capacités de traitement du Français, de l'Arabe Standard moderne (MSA) et du Darija Marocain (arabe dialectal & Arabizi).
2. **Faible latence & Temps de réponse :** Temps de génération moyen < 1.5s, idéal pour une expérience de conversation en direct avec des victimes en détresse.
3. **Conformité & Sécurité :** Alignement élevé avec les consignes de sécurité éthiques et zéro culpabilisation des victimes.
4. **Architecture extensible :** Encapsulé dans la classe `GeminiProvider` (`backend/llm/gemini_provider.py`), permettant l'interchangeabilité avec d'autres LLMs (OpenAI GPT-4, Claude) si nécessaire.

---

## 2. System Prompts & Directives

Les prompts système ont été externalisés dans le dossier `backend/prompts/` :

- **Français (`system_prompt_fr.txt`)** : 184 lignes définissant les règles déontologiques, le ton empathique, les 5 profils d'utilisateurs (Victime, Parent, Enseignant, Témoin, Jeune), les étapes de météo des émotions, les exercices de respiration 4-4-4-4 et d'ancrage sensoriel 5-4-3-2-1, et les numéros d'urgence marocains.
- **Arabe & Darija (`system_prompt_ar.txt`)** : 76 lignes adaptant les consignes en Arabe avec prise en compte du contexte culturel marocain (gestion de la *hchouma* / الحشومة, tutoiement bienveillant en Darija, exercices de respiration traduits).

---

## 3. Matrice d'Évaluation des Scénarios (20 Scénarios)

La suite de tests automatisés `backend/tests/test_response_quality.py` valide 20 scénarios clés :

| ID | Scénario / Cas d'Usage | Langue | Profil Détecté | Résultat Test |
|----|-----------------------|--------|----------------|---------------|
| 1 | Sextorsion Victim | FR | victim | ✅ PASSED |
| 2 | Sextorsion Victim AR | AR | victim | ✅ PASSED |
| 3 | Darija Cyberharassment | AR | victim | ✅ PASSED |
| 4 | Immediate Danger FR | FR | detresse (Urgent) | ✅ PASSED |
| 5 | Immediate Danger AR | AR | detresse (Urgent) | ✅ PASSED |
| 6 | Suicidal Thoughts FR | FR | detresse (Urgent) | ✅ PASSED |
| 7 | Parent Worried FR | FR | parent | ✅ PASSED |
| 8 | Parent Worried AR | AR | parent | ✅ PASSED |
| 9 | Teacher Reporting FR | FR | enseignant | ✅ PASSED |
| 10 | Witness Cyberviolence | FR | temoin | ✅ PASSED |
| 11 | Minor Info Request | FR | jeune | ✅ PASSED |
| 12 | Panic Attack | FR | detresse_emotionnelle | ✅ PASSED |
| 13 | Cultural Shame AR | AR | detresse_emotionnelle | ✅ PASSED |
| 14 | Legal Question 103-13 | FR | victim | ✅ PASSED |
| 15 | Online Reporting Platform | FR | victim | ✅ PASSED |
| 16 | Cyberstalking | FR | victim | ✅ PASSED |
| 17 | Revenge Porn Adults | FR | victim | ✅ PASSED |
| 18 | Phishing & Identity Theft | FR | victim | ✅ PASSED |
| 19 | School Cyberbullying AR | AR | jeune | ✅ PASSED |
| 20 | General Help Request | FR | victim | ✅ PASSED |

---

## 4. Synthèse des Résultats

- **Taux de succès global des tests :** **100% (22/22 tests valides, incluant la configuration du provider)**
- **Numéros d'urgence intégrés :** Police (19), Gendarmerie Royale (177), ONDE (2511), Protection Civile (15), E-Blagh (`e-blagh.ma`), EMC-Helpline (`cyberconfiance.ma`).
- **Précision de détection de profil :** 100% sur la batterie de tests.
- **Sécurité et Déontologie :** Aucune réponse ne reporte la faute sur la victime ni ne donne de faux conseils juridiques/médicaux engageant la responsabilité.
