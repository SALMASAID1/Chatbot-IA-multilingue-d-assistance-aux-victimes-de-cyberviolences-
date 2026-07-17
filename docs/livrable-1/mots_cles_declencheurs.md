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
| Q6 | suicide, me tuer, en finir, plus envie de vivre, me faire du mal, envie de mourir, mourir | انتحار, بغيت نموت, ماعندي مع الحياة, نقتل راسي, بغيت نموت | 🔴 CRITIQUE |

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

## Mots-clés cross-catégories (déclenchement multiple)

Certains mots-clés peuvent correspondre à plusieurs questions. Le chatbot doit prioriser selon cette logique :

| Mot-clé | Questions possibles | Priorité |
|---|---|---|
| "chantage" | Q5 (sextorsion) > Q7 (juridique) | Sextorsion d'abord |
| "photos" | Q5 (sextorsion) > Q8 (preuves) | Contexte de menace = Q5 |
| "aide" | Q4 (urgence) > Q12 (E-Helpline) | Vérifier urgence d'abord |
| "police" / "19" | Q4 (urgence) > Q11 (numéros) > Q7 (plainte) | Urgence d'abord |
| "enfant" / "mineur" | Q14 (mineur) > Q4 (urgence si danger) | Vérifier danger d'abord |
| "supprimer" | Q15 (signalement) > Q9 (preuves effacées) | Contexte détermine |

---

## Statistiques

| Métrique | Valeur |
|---|---|
| Total questions | 20 |
| Total mots-clés FR | ~120 |
| Total mots-clés AR/Darija | ~110 |
| Mots-clés d'urgence | 14 (FR) + 12 (AR) |
| Catégories couvertes | 6 |
| Priorités de déclenchement | 3 niveaux (🔴🟡🔵) |
