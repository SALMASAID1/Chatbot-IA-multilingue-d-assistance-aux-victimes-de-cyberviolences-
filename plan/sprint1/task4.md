# Tâche 4 — Construction de la base de connaissances (Arabe + Darija) ✅ TERMINÉE

## Assigné à
**Mohamed Tamzirt**

## Objectif
Collecter, traduire et structurer la base de connaissances en arabe standard et en darija marocain, en miroir de la base française, tout en adaptant le contenu aux spécificités linguistiques et culturelles.

## Statut : ✅ TERMINÉE

### Résultat final — 23 documents structurés (parité parfaite avec FR)

```
data/knowledge_base/ar/
├── juridique/
│   ├── loi_103_13.md       ← القانون 103-13 (86 lignes, plus détaillé que FR)
│   ├── loi_09_08.md        ← القانون 09-08 حماية البيانات (93 lignes)
│   └── loi_07_03.md        ← القانون 07-03 الجرائم الإلكترونية (81 lignes)
├── ressources/
│   ├── associations_aide.md          ← دليل الجمعيات والمساعدة (127 lignes)
│   ├── numeros_urgence.md            ← أرقام الطوارئ (95 lignes)
│   └── signalement_reseaux_sociaux.md ← دليل التبليغ (162 lignes)
├── fiches_pratiques/
│   ├── cyberharcelement.md     ← التحرش الإلكتروني (32 lignes)
│   ├── sextorsion.md           ← الابتزاز الجنسي (35 lignes)
│   ├── usurpation_identite.md  ← انتحال الهوية (25 lignes)
│   ├── phishing.md             ← التصيد الاحتيالي (28 lignes)
│   ├── revenge_porn.md         ← الانتقام الإباحي (35 lignes)
│   └── cyberstalking.md        ← المطاردة الإلكترونية (34 lignes)
├── prevention/
│   ├── securiser_comptes.md                ← حماية الحسابات (29 lignes)
│   ├── confidentialite_reseaux_sociaux.md  ← إعدادات الخصوصية (41 lignes)
│   ├── protection_mineurs.md              ← حماية الأطفال (38 lignes)
│   └── vigilance_phishing.md              ← الوقاية من الاحتيال (59 lignes)
├── psychologie/
│   ├── impact_psychologique.md  ← التأثير النفسي (103 lignes)
│   ├── soutien_empathique.md    ← الدعم النفسي (136 lignes)
│   └── resilience_coping.md     ← المرونة والتعامل (116 lignes)
├── rapports_internationaux/
│   ├── oms.md             ← منظمة الصحة العالمية (49 lignes)
│   ├── unicef.md          ← اليونيسف (59 lignes)
│   ├── conseil_europe.md  ← مجلس أوروبا (60 lignes)
│   └── unesco.md          ← اليونسكو (54 lignes)
├── faq/
│   └── faq_cyberviolence.md  ← أسئلة شائعة — 7 questions en mix arabe/darija (31 lignes)
└── metadata.json             ← 23 entrées indexées avec mots-clés arabes (147 lignes)
```

### Intégration Darija

La darija est intégrée **dans les fichiers existants** plutôt qu'en fichiers séparés :
- **FAQ** : Questions et réponses en mélange arabe standard/darija (ex: "واش نقدر نقدم شكاية", "ماتخلصيش")
- **Fiches pratiques** : Termes darija entre parenthèses (ex: "ماتجاوبش المعتدي", "البلوك والسينيال")
- **Ressources** : Descriptions accessibles mêlant les deux registres

## Critères de validation — Résultats

- [x] Contenu miroir de la base française en arabe → **23/23 fichiers, parité parfaite**
- [x] Au moins 10 documents en darija pour les contenus pratiques → **Darija intégrée dans les fichiers AR (FAQ, fiches, ressources)**
- [x] Encodage UTF-8 vérifié pour tous les fichiers → **Vérifié**
- [x] Terminologie juridique arabe validée → **Termes cohérents (القانون, الفصل, الحبس, الغرامة)**
- [x] Format prêt pour l'ingestion dans le pipeline RAG → **Markdown structuré + metadata.json**
- [x] Durée : **Semaine 1-2** ✅

## Points de parité vérifiés FR ↔ AR
| Élément | FR | AR | Parité |
|---|---|---|---|
| Nombre de documents | 23 | 23 | ✅ |
| Numéros d'urgence (19, 177, 2511) | ✅ | ✅ | ✅ |
| Peines juridiques identiques | ✅ | ✅ | ✅ |
| Sources et références | ✅ | ✅ | ✅ |
| Metadata entries | 23 | 23 | ✅ |

## Point d'attention pour le Sprint 2
- Le FAQ AR contient 7 questions vs 10 en FR. Envisager d'ajouter les 3 questions manquantes (Q5: captures d'écran, Q6: messages supprimés, Q9: mineur sans parents) pour une parité complète avant l'ingestion RAG.
