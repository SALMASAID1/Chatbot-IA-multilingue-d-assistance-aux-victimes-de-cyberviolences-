# Synthèse de l'étude des ressources EMC

> **Projet :** EMC Helpline Chatbot
> **Réalisé par :** Salma Said & Mohamed Tamzirt
> **Date :** Juillet 2026

---

## 1. Cyberconfiance.ma — Plateforme officielle EMC

**URL :** [https://www.cyberconfiance.ma](https://www.cyberconfiance.ma)

### Services identifiés
| Service | Description | Pertinence chatbot |
|---|---|---|
| **EMC-Helpline** | Ligne d'assistance pour victimes de cyberviolence/cyberharcèlement | ⭐⭐⭐ Principale référence |
| **EMC-Stopline** | Signalement et aide à la suppression de contenus illicites | ⭐⭐⭐ Orientation signalement |
| **EMC-Biblio** | Bibliothèque de sensibilisation (guides, capsules, dépliants) | ⭐⭐ Contenu éducatif |
| **EMC-Youth** | Programme jeunesse | ⭐ Référence secondaire |

### Contenus exploitables
- **Guides EMC** : Guides de protection en ligne (PDF)
- **Capsules vidéo** : Sensibilisation au cyberharcèlement
- **Dépliants** : Fiches pratiques imprimables
- **Rapports** : Données statistiques sur la cyberviolence au Maroc
- **Formations** : Programmes pour professionnels, écoles, associations

### Points clés pour le chatbot
- ✅ Disponible en **FR et AR** (pages bilingues)
- ✅ Formulaire de **signalement en ligne** disponible
- ✅ Partenariat avec CMRPI (Centre Marocain de Recherches Polytechniques et d'Innovation)
- ✅ Campagnes nationales annuelles (Safer Internet Day, campagnes de prévention)
- ⚠️ Pas d'API publique pour intégration directe

---

## 2. eVigilance.ma — Ligne Nationale d'Assistance (DGSN)

**URL :** [https://www.evigilance.ma](https://www.evigilance.ma)

### Caractéristiques
- Plateforme de la **DGSN** (Direction Générale de la Sûreté Nationale)
- Application Angular avec design moderne
- Focus sur le **signalement** et l'**assistance** en ligne
- Interface bilingue (FR/AR)

### Fonctionnalités identifiées
- Formulaire de signalement en ligne
- Catégorisation des types de cyberviolence
- Orientation vers les services compétents

### Points clés pour le chatbot
- ✅ Source officielle pour les signalements auprès des autorités
- ✅ Complément à E-Blagh pour les signalements en ligne
- ⚠️ Application SPA (Single Page Application) — contenu dynamique non scrappable

---

## 3. EMC Chatbot Beta — Version existante

**URL :** [https://emc-chatbot.vercel.app/](https://emc-chatbot.vercel.app/)

### Analyse technique
| Aspect | Détail |
|---|---|
| **Framework** | Next.js (React) |
| **Hébergement** | Vercel |
| **Titre** | "EMC Assistant (BETA)" |
| **Description** | "AI-Powered Chat Assistant" |
| **Police** | Inter (Google Fonts) |
| **État** | Version Beta — interface fonctionnelle minimale |

### Observations
- ✅ Interface de chat fonctionnelle
- ✅ Design épuré et responsive
- ⚠️ Contenu conversationnel limité dans la version Beta
- ⚠️ Pas de gestion multilingue avancée dans la version actuelle
- ⚠️ Pas de pipeline RAG visible (réponses probablement statiques ou LLM direct)

### Améliorations à apporter dans notre version
1. **Pipeline RAG** avec base de connaissances structurée (46 documents FR/AR)
2. **Support trilingue** natif (FR, AR standard, Darija)
3. **Protocole d'urgence** avec détection automatique de mots-clés de crise
4. **Mots-clés déclencheurs** pour des réponses contextualisées
5. **Ton empathique** validé et adapté aux victimes
6. **Gestion de l'historique** de conversation

---

## 4. Base de connaissances du projet (état actuel)

### Inventaire

| Catégorie | Docs FR | Docs AR | Total |
|---|---|---|---|
| Juridique | 3 | 3 | 6 |
| Ressources | 3 | 3 | 6 |
| Fiches pratiques | 6 | 6 | 12 |
| Prévention | 4 | 4 | 8 |
| Psychologie | 3 | 3 | 6 |
| Rapports internationaux | 4 | 4 | 8 |
| FAQ | 1 | 1 | 2 |
| **Total** | **24** | **24** | **48** |

### Qualité du contenu
- ✅ Contenu structuré en Markdown avec métadonnées JSON
- ✅ Parité parfaite FR/AR (chaque document a son miroir)
- ✅ Mots-clés indexés dans `metadata.json` (FR et AR)
- ✅ Ton empathique et bienveillant validé
- ✅ Numéros d'urgence vérifiés (19, 177, 2511, 15)
- ✅ Références juridiques précises (articles, peines)

---

## 5. Recommandations pour le chatbot

### Priorités de contenu
1. **Urgences** — Toujours afficher les numéros d'urgence en cas de danger détecté
2. **Sextorsion** — Sujet le plus fréquent selon les statistiques EMC, réponse immédiate nécessaire
3. **Cyberharcèlement** — 2ème sujet le plus courant, accompagnement structuré
4. **Orientation juridique** — Information sur les lois sans conseil juridique formel
5. **Soutien psychologique** — Reconnaître l'impact émotionnel, orienter vers des professionnels

### Ton à adopter
- Empathique et non-jugeant
- Clair et actionnable
- Respectueux de la culture marocaine (prise en compte de la حشومة/hchouma)
- Responsabilisant sans être directif
