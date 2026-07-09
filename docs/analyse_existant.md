# Analyse de l'existant et étude comparative

> **Sprint 1 — Tâche 1**
> **Réalisé par :** Salma Said & Mohamed Tamzirt
> **Date :** Juillet 2026

---

## 1. EMC Chatbot Beta

**URL :** https://emc-chatbot.vercel.app/

### 1.1 Description générale

L'EMC Chatbot Beta est un prototype d'assistant conversationnel développé pour l'Espace Maroc Cyberconfiance (EMC). Il se présente sous forme d'un widget flottant intégrable dans une page web.

### 1.2 Architecture technique observée

- **Framework :** Application web hébergée sur Vercel (suggère Next.js ou React)
- **Interface :** Widget flottant en bas à droite de la page
- **Backend :** Connexion à un LLM (probablement via API OpenAI)
- **Déploiement :** Vercel (plateforme cloud)

### 1.3 Fonctionnalités observées

| Fonctionnalité | Détail | Statut |
|---|---|---|
| Widget de chat | Bouton flottant en bas à droite, ouvre la fenêtre de conversation | ✅ Fonctionnel |
| Message de bienvenue | « Bonjour! Je suis l'Assistant EMC. Comment puis-je vous aider aujourd'hui? » | ✅ Présent |
| Badge BETA | Badge vert « BETA » visible dans l'en-tête | ✅ Présent |
| Indicateur de statut | Pastille verte « Online » | ✅ Présent |
| Saisie de texte | Champ avec placeholder « Écrivez votre message... » | ✅ Fonctionnel |
| Bouton d'envoi | Icône avion en papier, s'active quand du texte est saisi | ✅ Fonctionnel |
| Bouton d'information | Icône ⓘ dans l'en-tête | ✅ Présent |
| Bouton fermer | Icône ✕ pour fermer le widget | ✅ Fonctionnel |
| Détection de langue | Le bot détecte automatiquement la langue de l'utilisateur | ✅ Fonctionnel |
| Réponse en français | Réponse empathique et contextualisée en FR | ✅ Fonctionnel |
| Réponse en arabe | Réponse en arabe standard quand le message est en arabe | ✅ Fonctionnel |

### 1.4 Analyse de l'interface

**Points forts :**
- Design minimaliste et non intrusif (widget flottant)
- Le badge BETA gère les attentes des utilisateurs
- Icône du bot cohérente et professionnelle
- Bulles de messages distinctes (bot à gauche, utilisateur à droite)
- Le statut « Online » rassure l'utilisateur

**Points faibles :**
- Pas de sélecteur de langue explicite (choix FR/AR/Darija)
- Pas de boutons de suggestion rapide pour guider l'utilisateur
- Pas de support RTL visible pour les réponses en arabe (texte arabe affiché en LTR)
- Pas d'écran d'accueil avec présentation des capacités du bot
- Pas de bouton « Quitter rapidement » (sécurité pour les victimes)
- Pas de mode sombre
- Pas de responsive mobile observé (widget fixe en desktop)
- L'arrière-plan de la page hôte est vide (pas de page d'accueil informative)

### 1.5 Test conversationnel

| Message envoyé | Réponse obtenue | Qualité |
|---|---|---|
| « Bonjour » | « Bonjour ! 👋 Je suis votre assistant de l'Espace Maroc Cyberconfiance (EMC). Je suis là pour vous informer et vous soutenir face aux cyberviolences. Comment puis-je vous aider aujourd'hui ? » | ✅ Bon — empathique, contextualisé |
| « salam » (translittéré) | Réponse en arabe standard avec présentation du bot | ✅ Bon — détection multilingue fonctionnelle |

---

## 2. Plateforme eVigilance

**URL :** https://evigilance.ma/fr

### 2.1 Description générale

eVigilance est la **Ligne Nationale d'Assistance** (HELPLINE) pour la protection des enfants, des jeunes et des femmes en ligne. C'est une plateforme web complète de signalement et d'assistance.

### 2.2 Architecture technique observée

- **Framework :** Application Angular (SPA)
- **UI Framework :** Angular Material + Bootstrap 4/5
- **Polices :** Rubik, Open Sans, Poppins, Raleway, Roboto
- **Animations :** AOS (Animate on Scroll)
- **Design :** Material Design avec thème personnalisé

### 2.3 Fonctionnalités et contenu

| Fonctionnalité | Détail |
|---|---|
| Helpline | Ligne d'assistance pour les victimes de cyberviolence |
| Stopline | Signalement anonyme de contenus illicites |
| Formation | Programmes de sensibilisation (NTIC) |
| E-Biblio | Bibliothèque de ressources sur la cyberviolence |
| Multilingue | Interface disponible en français et arabe |
| Responsive | Design adaptatif pour mobile et desktop |

### 2.4 Catégories de cyberviolence identifiées sur eVigilance

- Cyberharcèlement
- Exploitation sexuelle en ligne
- Contenus illicites
- Menaces et intimidation
- Atteinte à la vie privée
- Usurpation d'identité

### 2.5 Analyse

**Points forts :**
- Plateforme institutionnelle reconnue (CMRPI)
- Interface bilingue (FR/AR)
- Signalement anonyme via Stopline
- Bibliothèque de ressources éducatives
- Design professionnel et moderne

**Points faibles :**
- Pas de chatbot IA intégré
- Navigation principalement basée sur des formulaires statiques
- Pas d'assistance conversationnelle en temps réel
- Le contenu est surtout informatif, pas interactif
- Pas d'aide immédiate contextuelle

---

## 3. Plateforme CyberConfiance (CyberEConfiance)

**URL :** https://www.cyberconfiance.ma/

### 3.1 Description générale

CyberConfiance (Espace Maroc Cyberconfiance) est le portail principal du CMRPI dédié à la protection en ligne. Il héberge les services EMC-Helpline et EMC-Stopline.

### 3.2 Services identifiés

| Service | Description |
|---|---|
| EMC-Helpline | Ligne d'assistance pour les victimes de cyberviolence et cyberharcèlement |
| EMC-Stopline | Signalement anonyme et confidentiel de contenus illicites en ligne |
| EMC-Biblio | Bibliothèque en ligne de sensibilisation au cyberharcèlement |
| Sensibilisation | Campagnes et activités de prévention |

### 3.3 Analyse

**Points forts :**
- Hub central pour tous les services EMC
- Services structurés (Helpline, Stopline, Biblio)
- Branding cohérent avec le CMRPI
- Orientation claire vers les ressources compétentes

**Points faibles :**
- Pas de chatbot IA intégré sur le portail
- Assistance principalement par formulaire ou contact humain
- Pas de disponibilité 24h/24 (dépend des horaires des conseillers)
- Design fonctionnel mais pas modernisé pour le mobile

---

## 4. Benchmark international

### 4.1 Chatbots d'assistance similaires dans le monde

| Solution | Pays | Cible | Approche |
|---|---|---|---|
| **rAInbow** (Vodafone/Nesta) | UK | Femmes victimes de violence domestique | IA conversationnelle avec arbre de décision, orientation vers services locaux |
| **Woebot** | USA | Santé mentale | CBT (thérapie cognitivo-comportementale) automatisée, suivi quotidien |
| **Crisis Text Line** | USA/Canada | Personnes en crise | IA pour triage + mise en relation avec conseillers humains |
| **Childline / Shout** | UK | Enfants et jeunes | Chat texte avec conseillers formés, IA pour triage et routing |
| **Tess (X2AI)** | International | Santé mentale | Chatbot IA multilingue, intégration sur différentes plateformes |

### 4.2 Bonnes pratiques identifiées

1. **Protocole de crise obligatoire** — Détection automatique de mots-clés de crise (suicide, danger immédiat) avec redirection immédiate vers des numéros d'urgence
2. **Bouton de sortie rapide** — Permet de quitter instantanément l'interface (sécurité pour les victimes dont l'appareil est surveillé)
3. **Transparence IA** — Informer clairement l'utilisateur qu'il interagit avec une IA, pas un humain
4. **Protection des données** — Conversations sensibles pouvant servir de preuve, conformité avec la Loi 09-08 (données personnelles)
5. **Human-in-the-loop** — Possibilité d'escalade vers un conseiller humain quand la situation dépasse les capacités de l'IA
6. **Validation d'experts** — Contenu validé par des professionnels de la psychologie et du droit

---

## 5. Matrice comparative

| Critère | EMC Chatbot Beta | eVigilance | CyberConfiance | Notre solution (cible) |
|---|---|---|---|---|
| **Type** | Chatbot IA | Plateforme web | Portail web | Chatbot IA + RAG |
| **Disponibilité** | 24h/24 | Horaires limités | Horaires limités | 24h/24 |
| **IA générative** | ✅ Oui | ❌ Non | ❌ Non | ✅ Oui (GPT-4/Claude/Mistral) |
| **Base de connaissances** | Limitée | Riche (non structurée) | Riche (non structurée) | ✅ 46 docs structurés (RAG) |
| **Multilingue** | ✅ FR/AR (auto) | ✅ FR/AR | ✅ FR | ✅ FR/AR/Darija |
| **Support Darija** | ⚠️ Partiel | ❌ Non | ❌ Non | ✅ Oui |
| **RTL (arabe)** | ⚠️ Limité | ✅ Oui | ⚠️ Partiel | ✅ Oui |
| **Signalement** | ❌ Non | ✅ Stopline | ✅ Stopline | ✅ Orientation |
| **Protocole d'urgence** | ⚠️ Non vérifié | ✅ Oui | ✅ Oui | ✅ Oui (automatique) |
| **Sélecteur de langue** | ❌ Non (auto) | ✅ Oui | ⚠️ Limité | ✅ Oui (explicite) |
| **Bouton sortie rapide** | ❌ Non | ❌ Non | ❌ Non | ✅ À implémenter |
| **Mobile responsive** | ⚠️ Widget fixe | ✅ Oui | ⚠️ Partiel | ✅ Mobile-first |
| **Mode sombre** | ❌ Non | ❌ Non | ❌ Non | ✅ À implémenter |
| **Historique conversation** | ⚠️ Session | ❌ N/A | ❌ N/A | ✅ Oui (avec sessions) |
| **Feedback utilisateur** | ❌ Non | ❌ Non | ❌ Non | ✅ Oui |
| **Stack technique** | React/Vercel | Angular | WordPress | React + FastAPI + LangChain |

---

## 6. Analyse SWOT pour le nouveau chatbot

### Forces (Strengths)
- Base de connaissances bilingue structurée (46 documents, 7 catégories)
- Stack technologique moderne (RAG + LLM + FastAPI + React)
- Support trilingue (FR, AR, Darija) avec détection automatique
- Disponibilité 24h/24, 7j/7
- Informations juridiques vérifiées et à jour (3 lois marocaines)
- Numéros d'urgence vérifiés (Police 19, Gendarmerie 177, ONDE 2511)

### Faiblesses (Weaknesses)
- Dépendance aux API LLM (coût, latence, disponibilité)
- Pas de connexion directe aux services de signalement (E-Blagh, Stopline)
- Risque de hallucination de l'IA sur les informations juridiques
- Besoin de validation continue par des experts (Mme Belaous)
- Projet limité à 8 semaines (risque de fonctionnalités incomplètes)

### Opportunités (Opportunities)
- Aucun chatbot IA dédié à la cyberviolence n'existe actuellement au Maroc
- Intégration possible avec les plateformes existantes (eVigilance, CyberConfiance)
- La darija est très peu couverte par les solutions existantes
- Potentiel d'extension vers d'autres langues (amazighe)
- Appui institutionnel du CMRPI

### Menaces (Threats)
- Risque de réponses inappropriées dans des situations de crise
- Problèmes de confidentialité des données des victimes
- Conformité nécessaire avec la Loi 09-08 (données personnelles)
- Risque de sur-confiance de l'utilisateur envers l'IA
- Évolution rapide des interfaces des réseaux sociaux (les guides de signalement deviennent obsolètes)

---

## 7. Recommandations pour le nouveau chatbot

### 7.1 Recommandations techniques

1. **Architecture RAG** — Utiliser notre base de 46 documents comme source de vérité pour éviter les hallucinations du LLM
2. **Fallback multi-modèles** — GPT-4 (principal) → Claude (secondaire) → Mistral (local) pour assurer la disponibilité
3. **Embeddings multilingues** — Utiliser `multilingual-e5-large` ou similaire pour le support FR/AR natif
4. **Cache intelligent** — Mettre en cache les réponses aux questions fréquentes (FAQ) pour réduire les coûts API
5. **Streaming des réponses** — Afficher les réponses progressivement pour améliorer la perception de rapidité

### 7.2 Recommandations fonctionnelles

1. **Bouton de sortie rapide** — Un bouton visible qui ferme immédiatement l'application (sécurité des victimes)
2. **Sélecteur de langue explicite** — Choix FR/AR/Darija dès l'accueil, en plus de la détection automatique
3. **Suggestions rapides** — Boutons pré-remplis (« Je suis victime de cyberharcèlement », « أحتاج مساعدة ») pour guider l'utilisateur
4. **Protocole de crise automatique** — Détection des situations d'urgence avec affichage immédiat des numéros d'urgence
5. **Disclaimer IA** — Message clair que le chatbot est une IA et ne remplace pas un professionnel
6. **Feedback par réponse** — Pouces haut/bas sur chaque réponse pour l'amélioration continue

### 7.3 Recommandations UX/Design

1. **Mobile-first** — Concevoir d'abord pour mobile (la majorité des victimes utilisent leur téléphone)
2. **Support RTL natif** — Basculement automatique de la direction du texte pour l'arabe
3. **Palette rassurante** — Couleurs calmes (bleu, vert) conformes à l'identité CMRPI/EMC
4. **Accessibilité WCAG 2.1 AA** — Contraste, taille de police, navigation au clavier
5. **Mode sombre** — Option pour les utilisateurs qui consultent la nuit
