# Matrice des Mots-Clés Déclencheurs

> **Projet :** EMC Helpline Chatbot
> **Réalisé par :** Salma Said & Mohamed Tamzirt
> **Date :** Juillet 2026

---

## Mode d'emploi

Chaque question de la base Q/R est associée à une liste de **mots-clés déclencheurs** en français, arabe standard et darija. Le chatbot doit déclencher la réponse correspondante lorsqu'il détecte un ou plusieurs de ces mots-clés dans le message de l'utilisateur.

**Priorité de déclenchement :**
1. 🔴 **Urgence** — Mots-clés de crise toujours prioritaires
2. 🟡 **Spécifique** — Mots-clés liés à un type de cyberviolence précis
3. 🔵 **Général** — Mots-clés généraux nécessitant une clarification

---

## Tableau complet des mots-clés

### 🔴 Mots-clés d'urgence (priorité absolue)

| Q# | Mots-clés FR | Mots-clés AR / Darija | Priorité |
|---|---|---|---|
| Q4 | danger, en danger, urgence, urgent, aide immédiate, menacé physiquement, il est chez moi, il va me frapper | خطر, ف خطر, طوارئ, مهدد, غادي يضربني, راه عند الباب | 🔴 CRITIQUE |
| Q6 | suicide, me tuer, en finir, finir avec la vie, plus envie de vivre, plus la force, me faire du mal, envie de mourir, mourir, automutilation, danger immédiat | انتحار, بغيت نموت, ماعندي مع الحياة, نقتل راسي, بغيت نموت, ما بقات عندي القوة | 🔴 CRITIQUE |

---

### Catégorie 1 : Questions générales (Q1-Q3)

| Q# | Mots-clés FR | Mots-clés AR / Darija |
|---|---|---|
| Q1 | cyberviolence, violence en ligne, violence numérique, c'est quoi, définition | العنف الرقمي, عنف إلكتروني, أش هو, تعريف |
| Q2 | types, formes, quelles sont, catégories, exemples, différentes formes | أنواع, أشكال, أش هي, فئات, أمثلة |
| Q3 | qui, victime, touché, concerné, vulnérable | شكون, ضحية, معني, معرض |

---

### Catégorie 2 : Urgences (Q4-Q6)

| Q# | Mots-clés FR | Mots-clés AR / Darija |
|---|---|---|
| Q4 | danger, urgence, aide immédiate, numéros urgence, police, gendarmerie | خطر, طوارئ, مساعدة فورية, الشرطة, الدرك |
| Q5 | photos intimes, menace publier, chantage photos, sextorsion, chantage sexuel, images intimes, ne pas payer | صور حميمية, تهديد بالنشر, ابتزاز صور, ابتزاز جنسي, ماتخلصش |
| Q6 | suicide, dépression, mal-être, anxiété, pensées noires, plus envie de vivre, automutilation | انتحار, اكتئاب, قلق, أفكار سلبية, ماعندي مع الحياة |

---

### Catégorie 3 : Démarches juridiques (Q7-Q10)

| Q# | Mots-clés FR | Mots-clés AR / Darija |
|---|---|---|
| Q7 | porter plainte, plainte, loi, harcèlement loi, droits, code pénal, 103-13, 07-03, juridique | شكاية, قانون, تحرش قانون, حقوق, القانون الجنائي |
| Q8 | capture écran, preuve, screenshot, preuves valables, conserver preuves | capture d'écran, دليل, صورة الشاشة, أدلة |
| Q9 | supprimé, messages effacés, plus de preuves, effacé conversations | مسحت, رسائل محذوفة, بلا أدلة |
| Q10 | faux profil, anonyme, retrouver agresseur, identifier, IP | حساب مزيف, مجهول, لقاو المعتدي, تعرفو عليه |

---

### Catégorie 4 : Aide et ressources (Q11-Q14)

| Q# | Mots-clés FR | Mots-clés AR / Darija |
|---|---|---|
| Q11 | numéros urgence, police, gendarmerie, 19, 177, ONDE, 2511, 15, contact | أرقام الطوارئ, الشرطة, الدرك, 19, 177, ONDE, 2511, اتصال |
| Q12 | E-Helpline, Cyberconfiance, gratuit, payant, service, coût | E-Helpline, Cyberconfiance, مجاني, خلاص, خدمة |
| Q13 | agresseur proche, famille, conjoint, peur porter plainte, proche | المعتدي قريب, العائلة, الزوج, خايف نقدم شكاية |
| Q14 | mineur, enfant, adolescent, sans parents, aide mineur, ONDE | قاصر, طفل, مراهق, بلا الوالدين, مساعدة قاصر |

---

### Catégorie 5 : Actions pratiques (Q15-Q19)

| Q# | Mots-clés FR | Mots-clés AR / Darija |
|---|---|---|
| Q15 | signaler, signalement, Facebook, Instagram, TikTok, WhatsApp, Snapchat, réseaux sociaux, supprimer contenu | بلّغ, تبليغ, فيسبوك, إنستغرام, تيك توك, واتساب, سناب شات, شبكات اجتماعية |
| Q16 | sécuriser, mot de passe, 2FA, double authentification, protéger compte, piraté | حماية, كلمة مرور, 2FA, مصادقة ثنائية, حساب مخترق |
| Q17 | cyberharcèlement, harcelé, harcèlement en ligne, insultes, menaces répétées, que faire | تحرش إلكتروني, تنمر, إهانات, تهديدات متكررة, أش ندير |
| Q18 | phishing, arnaque, hameçonnage, lien suspect, faux mail, escroquerie, faux concours | تصيد, احتيال, رابط مشبوه, إيميل مزيف, نصب |
| Q19 | faux profil, usurpation identité, vol identité, quelqu'un utilise mon nom | حساب مزيف, انتحال هوية, سرقة هوية, شي واحد كيستعمل اسمي |

---

### Catégorie 6 : Soutien psychologique (Q20)

| Q# | Mots-clés FR | Mots-clés AR / Darija |
|---|---|---|
| Q20 | psychologique, anxiété, dépression, stress, peur, honte, hchouma, impact, santé mentale, mal-être, traumatisme, PTSD | نفسي, قلق, اكتئاب, توتر, خوف, حشومة, تأثير, صحة نفسية, صدمة |

---

### Catégorie 7 : EMC et Signalement (Q21-Q24)

| Q# | Mots-clés FR | Mots-clés AR / Darija |
|---|---|---|
| Q21 | EMC, Espace Maroc Cyberconfiance, CMRPI, qui êtes-vous, c'est quoi EMC, mission, objectifs, EMC-Helpline | EMC, فضاء المغرب, الثقة الرقمية, CMRPI, شكون نتوما, أش هو EMC |
| Q22 | signaler, signalement, où signaler, eVigilance, IWF, StopNCII, Take It Down, Google Report, E-Blagh | بلّغ, تبليغ, فين نبلّغ, eVigilance, IWF, StopNCII |
| Q23 | porter plainte, plainte, où porter plainte, parquet, ministère public, plaintes.pmp.ma, cellules, ministère justice | شكاية, فين نقدم شكاية, النيابة العامة, وزارة العدل |
| Q24 | protection enfants, loi enfants, loi 27-14, loi 88-13, article 503-2, traite, exploitation sexuelle, textes juridiques | حماية الأطفال, قانون الأطفال, 27-14, 88-13, 503-2, استغلال جنسي |

---

### Catégorie 8 : Protection des enfants (Q25-Q26)

| Q# | Mots-clés FR | Mots-clés AR / Darija |
|---|---|---|
| Q25 | grooming, prédateur, manipulation enfant, faux profil adulte, rencontre en ligne, pedophile | غرومينغ, مفترس, تلاعب بالطفل, حساب مزيف ديال بالغ |
| Q26 | signaux alerte, signes, parents, comportement, sommeil, scolaire, enfant victime, alerte | علامات إنذار, الوالدين, سلوك, النوم, الدراسة, طفل ضحية |

---

---

### Catégorie 9 : Prévention et rôles (Q27-Q28)

| Q# | Mots-clés FR | Mots-clés AR / Darija |
|---|---|---|
| Q27 | bonnes pratiques, prévention, protéger, mot de passe, géolocalisation, objets connectés, jeux en ligne, réseaux sociaux | ممارسات جيدة, وقاية, حماية, كلمة مرور, أجهزة متصلة, ألعاب |
| Q28 | témoin, ne pas amplifier, soutenir victime, signaler, liker, partager, rumeur | شاهد, ما تزيدش ف النار, ساند الضحية, بلّغ, جام, إشاعة |

---

### Catégorie 10 : Soutien Émotionnel, Psychoéducation & Profils Utilisateurs (Q29-Q32 — Mme Belaous)

| Q# | Mots-clés FR | Mots-clés AR / Darija |
|---|---|---|
| Q29 | sidération, honte, culpabilité, météo des émotions, choc, freeze, hypervigilance, anxiété, déculpabiliser, blocage | صدمة, حشومة, إحساس بالذنب, نشرة المشاعر, خوف, قلق, شلل فكري |
| Q30 | parent, mon enfant, fils, fille, ado victime, confisquer écran, punir, écouter parent, ONDE 2511 | الوالدين, ولدي, بنتي, طفل ضحية, حيد التلفون, حماية الطفل |
| Q31 | enseignant, prof, professeur, éducateur, école, collège, lycée, établissement scolaire, procédure élève | أستاذ, مربي, مدرسة, ثانوية, مؤسسة تعليمية, تلميذ ضحية |
| Q32 | respiration, ancrage, exercice, respiration carrée, 4-4-4-4, 5-4-3-2-1, météo émotions, panique, calmer | تنفس, ترسيخ, تمرين, تنفس مربع, نوبة هلع, مهدئ, استرخاء |

---

## Mots-clés cross-catégories (déclenchement multiple)

Certains mots-clés peuvent correspondre à plusieurs questions. Le chatbot doit prioriser selon cette logique :

| Mot-clé | Questions possibles | Priorité |
|---|---|---|
| "chantage" | Q5 (sextorsion) > Q7 (juridique) | Sextorsion d'abord |
| "photos" | Q5 (sextorsion) > Q8 (preuves) | Contexte de menace = Q5 |
| "aide" | Q4 (urgence) > Q12 (E-Helpline) | Vérifier urgence d'abord |
| "police" / "19" | Q4 (urgence) > Q11 (numéros) > Q7 (plainte) | Urgence d'abord |
| "enfant" / "mineur" | Q14 (mineur) > Q25 (grooming) > Q30 (parent) > Q4 (urgence) | Vérifier danger d'abord |
| "supprimer" | Q15 (signalement) > Q9 (preuves effacées) | Contexte détermine |
| "signaler" / "signalement" | Q22 (plateformes) > Q15 (réseaux sociaux) | Q22 pour orientation générale |
| "plainte" / "porter plainte" | Q23 (guide complet) > Q7 (base légale) | Q23 pour procédure détaillée |
| "grooming" / "prédateur" | Q25 (grooming) > Q14 (mineur) | Grooming d'abord |
| "EMC" / "Cyberconfiance" | Q21 (présentation) > Q12 (gratuité) | Q21 si demande générale |
| "prof" / "enseignant" | Q31 (éducateur) > Q28 (témoin) | Q31 pour cadre scolaire |
| "panique" / "stress" | Q32 (respiration) > Q29 (psychoéducation) | Q32 pour apaisement immédiat |

---

## Statistiques

| Métrique | Valeur |
|---|---|
| Total questions | 32 |
| Total mots-clés FR | ~220 |
| Total mots-clés AR/Darija | ~195 |
| Mots-clés d'urgence | 18 (FR) + 14 (AR) |
| Catégories couvertes | 10 |
| Priorités de déclenchement | 3 niveaux (🔴🟡🔵) |

