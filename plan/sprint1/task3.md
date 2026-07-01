# Tâche 3 — Construction de la base de connaissances (Français)

## Assigné à
**Salma Said**

## Objectif
Collecter, structurer et préparer la base de connaissances en français couvrant tous les aspects des cyberviolences au Maroc : cadre juridique, ressources d'aide, conseils pratiques, et informations de prévention.

## Étapes d'implémentation

1. **Collecte des données juridiques**
   - Loi 103-13 relative à la lutte contre les violences faites aux femmes
   - Articles du Code pénal relatifs à la cybercriminalité
   - Textes de loi sur la protection des données personnelles (Loi 09-08)
   - Résumer chaque texte en langage accessible

2. **Collecte des ressources d'aide**
   - Numéros d'urgence et lignes d'écoute (police, DGSN, associations)
   - Services d'aide juridique gratuits
   - Associations d'aide aux victimes au Maroc
   - Procédures de signalement sur les réseaux sociaux

3. **Rédaction des fiches pratiques**
   - Fiche par type de cyberviolence (définition, exemples, que faire)
   - Guides de prévention (sécurité des comptes, paramètres de confidentialité)
   - FAQ des questions fréquentes

4. **Structuration des documents**
   - Organiser en catégories (juridique, psychologique, pratique, prévention)
   - Format Markdown structuré pour faciliter l'ingestion RAG
   - Ajouter des métadonnées (catégorie, langue, mots-clés)

5. **Préparation pour la vectorisation**
   - Découpage en chunks de taille optimale (300-500 tokens)
   - Vérification de la cohérence et de la qualité du contenu

## Outils et ressources
- Sources officielles marocaines (SGG, DGSN, CNDP)
- Site eVigilance.ma
- Documentation CMRPI
- Éditeur Markdown (VS Code)

## Livrable attendu
- Répertoire `data/knowledge_base/fr/` contenant :
  - `juridique/` — textes de loi résumés et accessibles
  - `ressources/` — annuaire des services d'aide
  - `fiches_pratiques/` — guides par type de cyberviolence
  - `prevention/` — conseils de prévention
  - `faq/` — questions fréquentes et réponses
  - `metadata.json` — métadonnées de chaque document

## Critères de validation
- [ ] Minimum 20 documents structurés en français
- [ ] Couverture de tous les types de cyberviolence identifiés
- [ ] Informations juridiques vérifiées et à jour
- [ ] Ressources d'aide avec coordonnées vérifiées
- [ ] Format prêt pour l'ingestion dans le pipeline RAG
- [ ] Durée : **Semaine 1-2**
