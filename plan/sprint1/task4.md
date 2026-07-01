# Tâche 4 — Construction de la base de connaissances (Arabe + Darija)

## Assigné à
**Mohamed Tamzirt**

## Objectif
Collecter, traduire et structurer la base de connaissances en arabe standard et en darija marocain, en miroir de la base française, tout en adaptant le contenu aux spécificités linguistiques et culturelles.

## Étapes d'implémentation

1. **Traduction des contenus juridiques**
   - Traduire les résumés de lois en arabe standard
   - Adapter en darija pour les contenus d'aide pratique
   - Vérifier la terminologie juridique arabe officielle

2. **Traduction des ressources d'aide**
   - Traduire l'annuaire des services en arabe
   - Adapter les procédures en darija (langage parlé)
   - Vérifier que les noms officiels sont en arabe

3. **Rédaction des fiches pratiques en arabe**
   - Fiches par type de cyberviolence en arabe standard
   - Versions simplifiées en darija pour les conseils pratiques
   - FAQ en arabe et darija

4. **Gestion du support RTL (Right-to-Left)**
   - S'assurer que les documents sont correctement encodés (UTF-8)
   - Tester l'affichage RTL des contenus
   - Documenter les particularités de la darija (translittération latine)

5. **Structuration et préparation**
   - Même structure que la base française
   - Métadonnées incluant la langue (ar, darija)
   - Préparation pour la vectorisation

## Outils et ressources
- Base de connaissances française (comme référence)
- Dictionnaires juridiques arabe-français
- Ressources officielles arabes du gouvernement marocain
- Outils de vérification de l'encodage UTF-8

## Livrable attendu
- Répertoire `data/knowledge_base/ar/` contenant :
  - `juridique/` — textes de loi en arabe
  - `ressources/` — annuaire des services en arabe
  - `fiches_pratiques/` — guides en arabe et darija
  - `prevention/` — conseils en arabe
  - `faq/` — FAQ en arabe et darija
  - `metadata.json` — métadonnées avec tags de langue

## Critères de validation
- [ ] Contenu miroir de la base française en arabe
- [ ] Au moins 10 documents en darija pour les contenus pratiques
- [ ] Encodage UTF-8 vérifié pour tous les fichiers
- [ ] Terminologie juridique arabe validée
- [ ] Format prêt pour l'ingestion dans le pipeline RAG
- [ ] Durée : **Semaine 1-2**
