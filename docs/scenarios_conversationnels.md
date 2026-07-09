# Scénarios conversationnels — EMC Helpline Chatbot

> **Sprint 1 — Tâche 2**
> **Réalisé par :** Salma Said & Mohamed Tamzirt
> **À valider par :** Mme Fadwa Belaous (psychologie)
> **Date :** Juillet 2026

---

## 1. Flux d'accueil

### 1.1 Diagramme du flux d'accueil

```mermaid
flowchart TD
    A["🔵 Utilisateur ouvre le chatbot"] --> B["Bot : Message de bienvenue"]
    B --> C{"Choix de langue"}
    C -->|Français| D["Accueil FR"]
    C -->|العربية| E["Accueil AR"]
    C -->|Darija| F["Accueil Darija"]
    C -->|Auto-détection| G["Détection automatique"]
    D --> H["Présentation + Limites + Suggestions"]
    E --> H
    F --> H
    G --> H
    H --> I{"Type de demande"}
    I -->|Urgence détectée| J["🔴 Protocole d'urgence"]
    I -->|Question générale| K["Flux conversationnel principal"]
    I -->|Signaler un contenu| L["Orientation signalement"]
    I -->|Hors sujet| M["Recentrage bienveillant"]
```

### 1.2 Message de bienvenue — Français

> **Bot :** Bienvenue sur l'EMC Helpline 💙
>
> Je suis l'assistant IA de l'Espace Maroc Cyberconfiance. Je suis là pour vous informer et vous accompagner face aux cyberviolences.
>
> ⚠️ **Important :** Je suis une intelligence artificielle. En cas de danger immédiat, appelez la **police (19)** ou la **gendarmerie (177)**.
>
> Comment puis-je vous aider ?
>
> 💬 Suggestions :
> - « Je suis victime de cyberharcèlement »
> - « On me fait du chantage avec des photos »
> - « Je veux signaler un contenu »
> - « Quels sont mes droits ? »

### 1.3 Message de bienvenue — Arabe

> **البوت :** مرحباً بك في خط المساعدة EMC Helpline 💙
>
> أنا المساعد الذكي لفضاء المغرب للثقة الرقمية. أنا هنا لمساعدتك ومواكبتك في مواجهة العنف الرقمي.
>
> ⚠️ **مهم:** أنا ذكاء اصطناعي. في حالة خطر فوري، اتصل بـ **الشرطة (19)** أو **الدرك الملكي (177)**.
>
> كيف يمكنني مساعدتك؟
>
> 💬 اقتراحات :
> - « أنا ضحية تحرش إلكتروني »
> - « شي واحد كيهددني بنشر صوري »
> - « بغيت نبلّغ على محتوى »
> - « أش هي حقوقي؟ »

### 1.4 Message de bienvenue — Darija

> **البوت :** مرحبا بيك ف EMC Helpline 💙
>
> أنا مساعد ذكي ديال فضاء المغرب للثقة الرقمية. أنا هنا باش نساعدك ونوجهك إلى الحلول فحالة العنف الرقمي.
>
> ⚠️ **مهم:** أنا ذكاء اصطناعي. إلا كنتي فخطر، عيط للشرطة (19) ولا الدرك (177).
>
> كيفاش نقدر نعاونك؟

---

## 2. Protocole d'urgence

### 2.1 Déclencheurs de crise

Le protocole d'urgence se déclenche automatiquement lorsque le chatbot détecte :

| Catégorie | Mots-clés FR | Mots-clés AR/Darija |
|---|---|---|
| **Suicide / Automutilation** | suicide, me tuer, en finir, plus envie de vivre, me faire du mal | انتحار, بغيت نموت, ماعندي مع الحياة, نقتل راسي |
| **Danger physique immédiat** | il va me frapper, il est devant chez moi, menacé physiquement, danger | غادي يضربني, راه عند الباب, مهدد, خطر |
| **Victime mineure en danger** | mon père me touche, un adulte me demande des photos, prof me harcèle | بابا كيحسسني, واحد كبير كيطلب مني تصاور, الأستاذ كيتحرش بيا |
| **Chantage actif** | il va publier maintenant, il a mis un délai, il veut de l'argent | غادي ينشر دابا, عطاني مهلة, بغا الفلوس |

### 2.2 Réponse d'urgence — Français

> **Bot :** 🔴 **Ce que vous décrivez est une situation grave qui nécessite une aide immédiate.**
>
> **Appelez maintenant :**
> - 🚨 **Police : 19** (en ville)
> - 🚨 **Gendarmerie : 177** (zone rurale)
> - 🚨 **Protection Civile : 15** (urgence médicale)
> - 📞 **ONDE : 2511** (si la victime est un enfant)
>
> Vous n'êtes pas seul(e). L'aide est disponible.
>
> Souhaitez-vous que je vous aide à préparer ce que vous allez dire aux autorités ?

### 2.3 Réponse d'urgence — Arabe/Darija

> **البوت :** 🔴 **هاد الوضعية خطيرة وخاصها مساعدة فورية.**
>
> **عيّط دابا :**
> - 🚨 **الشرطة : 19** (المدينة)
> - 🚨 **الدرك الملكي : 177** (القرية)
> - 🚨 **الوقاية المدنية : 15** (حالة طبية)
> - 📞 **ONDE : 2511** (إلا كانت الضحية طفل/طفلة)
>
> ماشي بوحدك. المساعدة موجودة.
>
> بغيتي نعاونك تحضّر أش غادي تقول للسلطات؟

### 2.4 Diagramme du protocole d'urgence

```mermaid
flowchart TD
    A["Message utilisateur"] --> B{"Détection mots-clés de crise"}
    B -->|Oui| C["🔴 Affichage immédiat numéros d'urgence"]
    C --> D["Message empathique + validation"]
    D --> E{"La personne est-elle mineure ?"}
    E -->|Oui| F["Ajouter ONDE 2511"]
    E -->|Non| G["Proposer aide préparation plainte"]
    F --> G
    G --> H{"L'utilisateur souhaite continuer ?"}
    H -->|Oui| I["Accompagnement guidé"]
    H -->|Non| J["Message de clôture bienveillant"]
    B -->|Non| K["Flux conversationnel normal"]
```

---

## 3. Scénarios par type de cyberviolence

### 3.1 Scénario : Cyberharcèlement

```mermaid
flowchart TD
    A["Utilisateur : Je suis harcelé(e) en ligne"] --> B["Bot : Je suis désolé. Pouvez-vous me dire sur quelle plateforme ?"]
    B --> C{"Plateforme identifiée"}
    C -->|Facebook/Instagram/TikTok/WhatsApp/Snapchat| D["Guide de signalement spécifique"]
    C -->|Autre/Non spécifié| E["Conseils généraux"]
    D --> F["Bot : Avez-vous conservé les preuves ?"]
    E --> F
    F --> G{"Preuves conservées ?"}
    G -->|Non| H["Bot : Voici comment faire des captures d'écran..."]
    G -->|Oui| I["Bot : Très bien. Voici vos options..."]
    H --> I
    I --> J["Options : 1. Bloquer 2. Signaler 3. Porter plainte"]
    J --> K["Bot : Souhaitez-vous les numéros utiles ?"]
    K --> L["Affichage ressources pertinentes"]
```

**Template FR :**
> **Bot :** Je suis vraiment désolé(e) d'apprendre cela. Ce que vous vivez est sérieux et vous avez bien fait d'en parler.
>
> Pouvez-vous me dire :
> - Sur quelle plateforme cela se passe ? (Facebook, Instagram, TikTok, WhatsApp...)
> - Est-ce que vous avez conservé les preuves (captures d'écran) ?
>
> Je vais vous guider étape par étape.

**Template AR :**
> **البوت :** كنتأسف بزاف على هاد الوضعية. اللي كتعيشو خطير وحسنتي ديرتي ملي هضرتي عليه.
>
> واش تقدر تقول ليا :
> - فين كيوقع هادشي؟ (فيسبوك، إنستغرام، تيك توك، واتساب...)
> - واش عندك الأدلة (صور الشاشة)؟
>
> غادي نوجهك خطوة بخطوة.

---

### 3.2 Scénario : Sextorsion / Chantage sexuel

```mermaid
flowchart TD
    A["Utilisateur : On me fait du chantage avec mes photos"] --> B["Bot : Vérification sécurité immédiate"]
    B --> C{"Danger immédiat détecté ?"}
    C -->|Oui| D["🔴 Protocole d'urgence"]
    C -->|Non| E["Bot : Ce n'est PAS votre faute. Ne payez pas."]
    E --> F["Bot : Conseils immédiats - Ne pas payer, ne pas céder"]
    F --> G["Bot : Conservez toutes les preuves"]
    G --> H["Bot : Voici comment signaler et porter plainte"]
    H --> I["Orientation : Police 19 + E-Helpline"]
```

**Template FR :**
> **Bot :** Merci de m'en parler. Ce que vous vivez s'appelle la **sextorsion** — c'est une infraction grave.
>
> 🔵 **3 choses importantes tout de suite :**
> 1. **Ne payez pas et ne cédez pas.** Payer ne garantit jamais que la personne arrêtera.
> 2. **Conservez toutes les preuves** : captures d'écran des menaces, profil de l'agresseur, conversations.
> 3. **Bloquez l'agresseur** sur toutes les plateformes.
>
> Ensuite :
> - Appelez la **police (19)** pour porter plainte
> - Contactez l'**E-Helpline de Cyberconfiance** pour un accompagnement
>
> **Vous n'êtes pas responsable.** La responsabilité est uniquement celle de l'agresseur.

**Template AR :**
> **البوت :** شكراً أنك هضرتي معايا. هاد الوضعية اسمها **الابتزاز الجنسي** — وهي جريمة خطيرة.
>
> 🔵 **3 حوايج مهمين دابا :**
> 1. **ماتخلصش وماتستسلمش.** الخلاص ما كيضمن والو.
> 2. **احتفظ بالأدلة** : صور الشاشة ديال التهديدات، الحساب ديال المعتدي، المحادثات.
> 3. **بلوكي المعتدي** فجميع المنصات.
>
> من بعد :
> - عيّط للشرطة (**19**) باش تقدم شكاية
> - تواصل مع **خط المساعدة E-Helpline** ديال Cyberconfiance
>
> **ماشي غلطتك.** المسؤولية كاملة على المعتدي.

---

### 3.3 Scénario : Revenge Porn

**Template FR :**
> **Bot :** Ce que vous décrivez — la diffusion d'images intimes sans votre consentement — est un **délit grave** puni par la Loi 103-13. Vous êtes protégé(e) par la loi marocaine.
>
> **Actions immédiates :**
> 1. **Signalez le contenu** à la plateforme pour demander sa suppression
> 2. **Conservez les preuves** (captures d'écran, liens, profils)
> 3. **Portez plainte** auprès de la police (19) ou gendarmerie (177)
> 4. Contactez l'**E-Stopline** de Cyberconfiance pour l'aide à la suppression
>
> **Peines prévues :** 1 à 5 ans d'emprisonnement et 5 000 à 50 000 DH d'amende en cas de circonstances aggravantes.
>
> Vous n'avez rien à vous reprocher.

---

### 3.4 Scénario : Usurpation d'identité

**Template FR :**
> **Bot :** La création d'un faux profil utilisant votre identité est une infraction. Voici ce que vous pouvez faire :
>
> 1. **Signalez le faux profil** directement sur la plateforme (« signaler une usurpation d'identité »)
> 2. **Faites des captures d'écran** du faux profil (nom, photos, URL)
> 3. **Prévenez vos contacts** que ce n'est pas vous
> 4. **Portez plainte** auprès de la police (19) ou gendarmerie (177)
>
> 📋 La loi 07-03 punit l'accès frauduleux aux systèmes informatiques et la loi 09-08 protège vos données personnelles.

---

### 3.5 Scénario : Phishing / Arnaque en ligne

**Template FR :**
> **Bot :** Merci de me signaler cela. Voici comment réagir face à une tentative d'arnaque :
>
> **Si vous n'avez pas encore cliqué :**
> - Ne cliquez sur aucun lien suspect
> - Vérifiez l'expéditeur du message
> - Signalez le message comme spam
>
> **Si vous avez déjà donné vos informations :**
> 1. **Changez immédiatement** vos mots de passe
> 2. **Activez la double authentification (2FA)** sur tous vos comptes
> 3. **Contactez votre banque** si vous avez partagé des informations bancaires
> 4. **Signalez** sur la plateforme eVigilance
>
> 💡 Aucune banque ou administration ne vous demandera jamais votre mot de passe par email ou SMS.

---

### 3.6 Scénario : Cyberstalking

**Template FR :**
> **Bot :** Le harcèlement obsessionnel en ligne (cyberstalking) est une situation préoccupante. Votre sécurité est la priorité.
>
> **Actions immédiates :**
> 1. **Vérifiez vos appareils** : Assurez-vous qu'aucun logiciel espion n'est installé
> 2. **Changez vos mots de passe** et activez la 2FA
> 3. **Rendez vos profils privés** sur tous les réseaux sociaux
> 4. **Bloquez l'agresseur** sur toutes les plateformes
> 5. **Conservez les preuves** de surveillance ou de suivi
>
> ⚠️ Si la personne connaît votre adresse ou vos déplacements, contactez la **police (19)** immédiatement.
>
> La loi 07-03 punit l'accès frauduleux aux systèmes informatiques, y compris l'installation de logiciels espions.

---

## 4. Cas limites

### 4.1 Questions hors sujet

**Template FR :**
> **Bot :** Je comprends votre question, mais mon domaine d'expertise est limité à l'assistance aux victimes de cyberviolences au Maroc. Je peux vous aider avec :
>
> - Le cyberharcèlement
> - Le chantage et la sextorsion
> - La diffusion d'images intimes
> - L'usurpation d'identité
> - Le piratage de comptes
> - Les arnaques en ligne
>
> Avez-vous une question sur l'un de ces sujets ?

### 4.2 Langue non supportée

**Template :**
> **Bot :** I'm sorry, I currently support **French** (Français), **Arabic** (العربية) and **Darija** (الدارجة).
>
> 🇫🇷 Pour continuer en français, écrivez votre message.
> 🇲🇦 للمتابعة بالعربية، اكتب رسالتك.

### 4.3 Messages vides ou incompréhensibles

**Template FR :**
> **Bot :** Je n'ai pas bien compris votre message. Pouvez-vous le reformuler ?
>
> Vous pouvez aussi choisir une des options suivantes :
> - « Je suis victime de cyberharcèlement »
> - « J'ai besoin d'aide urgente »
> - « Je veux connaître mes droits »

---

## 5. Flux de clôture

### 5.1 Message de clôture — Français

> **Bot :** Merci d'avoir utilisé l'EMC Helpline. J'espère avoir pu vous aider.
>
> **Rappel :** En cas d'urgence, n'hésitez pas à appeler :
> - Police : **19** | Gendarmerie : **177** | ONDE : **2511**
>
> Prenez soin de vous. Vous pouvez revenir à tout moment. 💙

### 5.2 Message de clôture — Arabe

> **البوت :** شكراً لأنك استعملتي خط المساعدة EMC Helpline. كنتمنى نكون عاونتك.
>
> **تذكير :** في حالة طوارئ :
> - الشرطة : **19** | الدرك : **177** | ONDE : **2511**
>
> ديري بالك على راسك. يمكنك ترجع في أي وقت. 💙

---

## 6. Tableau récapitulatif des ressources d'orientation

| Situation | Ressource | Contact |
|---|---|---|
| Danger physique immédiat (ville) | Police Secours | **19** |
| Danger physique immédiat (rural) | Gendarmerie Royale | **177** |
| Urgence médicale / tentative de suicide | Protection Civile | **15** |
| Enfant victime de violence | ONDE | **2511** / **0800002511** |
| Cyberviolence / cyberharcèlement | EMC-Helpline | cyberconfiance.ma |
| Signalement de contenu illicite | E-Blagh (DGSN) | e-blagh.ma |
| Signalement anonyme | EMC-Stopline | cyberconfiance.ma |
| Assistance en ligne | eVigilance | evigilance.ma |
| Femme victime de violence | Fondation YTTO | — |
| Enfant en situation difficile | AMANE / Bayti | — |

---

## 7. Principes conversationnels transversaux

### 7.1 Ton et posture

| Principe | Exemple à suivre | Exemple à éviter |
|---|---|---|
| Empathique | « Je suis désolé(e) pour ce que vous vivez » | « Ce n'est pas si grave » |
| Non-jugeant | « Ce n'est pas votre faute » | « Pourquoi avez-vous envoyé cette photo ? » |
| Respectueux | « Vous avez bien fait d'en parler » | « Vous auriez dû bloquer plus tôt » |
| Clair | « Voici les étapes à suivre » | Jargon juridique complexe |
| Responsabilisant | « Voici vos options, c'est à vous de décider » | « Vous devez absolument porter plainte » |

### 7.2 Règles de sécurité du chatbot

1. **Ne jamais donner de conseil médical formel** — Orienter vers un professionnel
2. **Ne jamais donner de conseil juridique formel** — Orienter vers un avocat ou une association
3. **Ne jamais promettre un résultat** — « La police peut enquêter » ≠ « La police va le retrouver »
4. **Ne jamais demander d'informations personnelles identifiantes** — Pas de nom, adresse, numéro de téléphone
5. **Toujours rappeler les numéros d'urgence** en cas de situation grave
6. **Toujours préciser que le bot est une IA** — Disclaimer dans l'accueil
