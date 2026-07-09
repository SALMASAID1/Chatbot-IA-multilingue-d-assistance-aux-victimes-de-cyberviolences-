# Tâche 3 — Construction de la base de connaissances (Français) ✅ TERMINÉE

## Assigné à
**Salma Said**

## Objectif
Collecter, structurer et préparer la base de connaissances en français couvrant tous les aspects des cyberviolences au Maroc : cadre juridique, ressources d'aide, conseils pratiques, et informations de prévention.

## Statut : ✅ TERMINÉE

### Résultat final — 23 documents structurés

```
data/knowledge_base/fr/
├── juridique/
│   ├── loi_103_13.md       ← Loi contre les violences faites aux femmes (68 lignes)
│   ├── loi_09_08.md        ← Protection des données personnelles / CNDP (71 lignes)
│   └── loi_07_03.md        ← Cybercriminalité / piratage (57 lignes)
├── ressources/
│   ├── associations_aide.md          ← Annuaire vérifié (128 lignes)
│   ├── numeros_urgence.md            ← Police 19, Gendarmerie 177, ONDE 2511 (98 lignes)
│   └── signalement_reseaux_sociaux.md ← Guide Facebook/Instagram/TikTok/WhatsApp/Snapchat (163 lignes)
├── fiches_pratiques/
│   ├── cyberharcelement.md     ← Méthode des 4 règles (32 lignes)
│   ├── sextorsion.md           ← Chantage sexuel en ligne (40 lignes)
│   ├── usurpation_identite.md  ← Faux profils / vol d'identité (33 lignes)
│   ├── phishing.md             ← Hameçonnage (31 lignes)
│   ├── revenge_porn.md         ← Pornographie non consensuelle (35 lignes)
│   └── cyberstalking.md        ← Harcèlement obsessionnel (34 lignes)
├── prevention/
│   ├── securiser_comptes.md                ← Mots de passe + 2FA (33 lignes)
│   ├── confidentialite_reseaux_sociaux.md  ← Paramètres de confidentialité (41 lignes)
│   ├── protection_mineurs.md              ← Guide parents / contrôle parental (38 lignes)
│   └── vigilance_phishing.md              ← Arnaques en ligne (59 lignes)
├── psychologie/
│   ├── impact_psychologique.md  ← Effets psychologiques + stats HCP (104 lignes)
│   ├── soutien_empathique.md    ← Premiers secours psychologiques (140 lignes)
│   └── resilience_coping.md     ← Stratégies de reconstruction (117 lignes)
├── rapports_internationaux/
│   ├── oms.md             ← OMS / INSPIRE / HBSC (49 lignes)
│   ├── unicef.md          ← UNICEF / protection enfants (59 lignes)
│   ├── conseil_europe.md  ← Budapest / Lanzarote (60 lignes)
│   └── unesco.md          ← Citoyenneté numérique (54 lignes)
├── faq/
│   └── faq_cyberviolence.md  ← 10 questions fréquentes (47 lignes)
└── metadata.json             ← 23 entrées indexées (147 lignes)
```

## Critères de validation — Résultats

- [x] Minimum 20 documents structurés en français → **23 documents**
- [x] Couverture de tous les types de cyberviolence identifiés → **6 types couverts**
- [x] Informations juridiques vérifiées et à jour → **3 lois avec articles et peines**
- [x] Ressources d'aide avec coordonnées vérifiées → **URLs et numéros sourcés**
- [x] Format prêt pour l'ingestion dans le pipeline RAG → **Markdown structuré + metadata.json**
- [x] Durée : **Semaine 1-2** ✅

## Point d'attention pour le Sprint 2
- Le dossier `fr/ressources/cyberviolence_ressources_verified_md/` contient des fichiers de travail (doublons) qui ne sont **pas** dans le metadata.json. Il faut les supprimer avant l'ingestion RAG pour éviter une double indexation.
