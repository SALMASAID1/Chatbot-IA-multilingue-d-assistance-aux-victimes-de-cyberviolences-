# Guide de déploiement — EMC Helpline

Déploiement gratuit du chatbot : **backend sur Hugging Face Spaces**, **frontend sur
Vercel**. Durée totale : environ 45 minutes, dont ~15 minutes de build automatique.

> Justification du choix de plateformes : voir [plan/sprint4/task2.md](../plan/sprint4/task2.md).

---

## 0. Prérequis

| Élément | Où l'obtenir |
|---|---|
| Compte Hugging Face | <https://huggingface.co/join> |
| Compte Vercel | <https://vercel.com/signup> (connexion via GitHub) |
| Clé API Google Gemini | <https://aistudio.google.com/apikey> |
| Clé d'administration | `python -c "import secrets; print(secrets.token_urlsafe(32))"` |

> ⚠️ **Ne jamais versionner `.env`.** Le fichier est ignoré par Git ; les secrets
> se configurent uniquement dans les panneaux des plateformes.

---

## 1. Backend — Hugging Face Spaces

### 1.1 Créer le Space

1. Aller sur <https://huggingface.co/new-space>
2. Renseigner :
   - **Owner** : votre compte (ou l'organisation CMRPI)
   - **Space name** : `emc-helpline`
   - **License** : au choix
   - **SDK** : **Docker** → *Blank*
   - **Hardware** : *CPU basic · 2 vCPU · 16 Go* (gratuit)
   - **Visibility** : *Public* (ou *Private* si la démonstration doit rester interne)
3. Cliquer sur **Create Space**

### 1.2 Configurer les secrets

Dans le Space : **Settings → Variables and secrets**.

| Nom | Type | Valeur |
|---|---|---|
| `GOOGLE_API_KEY` | **Secret** | votre clé Gemini |
| `ADMIN_API_KEY` | **Secret** | la clé générée ci-dessus |
| `CORS_ORIGINS` | Variable | `https://<votre-projet>.vercel.app` (à compléter après l'étape 2) |

> Sans `ADMIN_API_KEY`, les endpoints `/api/admin/*` répondent **404** : c'est le
> comportement par défaut voulu, une exposition publique n'expose alors rien.

### 1.3 Pousser le code

Le `Dockerfile` à la racine du dépôt est celui du Space (port 7860).

```bash
cd <racine-du-projet>

# Ajouter le Space comme dépôt distant (une seule fois)
git remote add space https://huggingface.co/spaces/<compte>/emc-helpline

# Pousser la branche courante vers la branche main du Space
git push space main:main
```

> Authentification : utilisez un **token d'accès** Hugging Face
> (Settings → Access Tokens → *Write*) comme mot de passe.

### 1.4 Suivre le build

Onglet **Logs** du Space. Le build dure **10 à 15 minutes** car il :

1. installe `torch` en version **CPU** (l'image par défaut embarque ~2 Go de CUDA inutile) ;
2. **pré-télécharge le modèle d'embeddings** (458 Mo) ;
3. **construit la base vectorielle** (`python -m backend.rag.embeddings`, 820 vecteurs).

Ces trois étapes ont lieu **pendant le build**, donc le premier utilisateur
n'attend jamais un téléchargement de 458 Mo.

### 1.5 Vérifier

```bash
curl https://<compte>-emc-helpline.hf.space/api/health
# {"status":"healthy","rag_status":"healthy","llm_status":"configured",...}

# L'administration doit être fermée sans clé :
curl -o /dev/null -w "%{http_code}\n" https://<compte>-emc-helpline.hf.space/api/admin/sessions
# 401  (ou 404 si ADMIN_API_KEY n'est pas configurée)
```

---

## 2. Frontend — Vercel

### 2.1 Renseigner l'URL du backend

Dans [`vercel.json`](../vercel.json), remplacer le marqueur `<space-url>` :

```json
"destination": "https://<compte>-emc-helpline.hf.space/api/:path*"
```

Ce *rewrite* sert l'API sur la **même origine** que le frontend : aucune
configuration CORS n'est nécessaire et la CSP stricte (`connect-src 'self'`)
reste valable. Commiter ce changement.

### 2.2 Importer le projet

1. <https://vercel.com/new> → importer le dépôt GitHub
2. **Framework Preset** : *Other* (la configuration vient de `vercel.json`)
3. Laisser **Root Directory** à la racine du dépôt
4. **Deploy**

Aucune variable d'environnement n'est requise : `VITE_API_BASE_URL` reste vide,
donc l'application appelle `/api/…` sur sa propre origine.

### 2.3 Boucler la configuration CORS

Reporter l'URL Vercel obtenue dans la variable `CORS_ORIGINS` du Space (étape 1.2),
puis redémarrer le Space (**Settings → Factory reboot**). C'est une ceinture de
sécurité : le trafic normal passe par le *rewrite* et reste en même origine.

---

## 3. Validation end-to-end

- [ ] La page d'accueil s'affiche et l'indicateur d'état indique **Service disponible**
- [ ] Une question en **français** reçoit une réponse avec ses sources
- [ ] Une question en **arabe** s'affiche correctement en RTL
- [ ] Une question en **darija arabizi** (`wach n9der ndir chi chikaya?`) reçoit une réponse en darija
- [ ] Un message d'urgence (« Je suis en danger ») déclenche le panneau rouge et les liens `tel:`
- [ ] Test sur **téléphone réel** (le composeur reste visible, la conversation défile)
- [ ] `/api/admin/sessions` renvoie **401** sans en-tête `X-Admin-Key`

---

## 4. Exploitation

### Mise en veille
Un Space gratuit s'endort après ~48 h d'inactivité ; le réveil prend 20 à 40 secondes.
**Ouvrir l'application 10 minutes avant la soutenance** pour la réchauffer.

Même endormi, le frontend (hébergé par Vercel, toujours disponible) affiche les
numéros d'urgence vérifiés : l'information vitale reste accessible.

### Mettre à jour
```bash
git push space main:main      # backend : rebuild automatique
git push origin main          # frontend : redéploiement Vercel automatique
```

### Revenir en arrière (*rollback*)
- **Vercel** : onglet *Deployments* → un déploiement précédent → *Promote to Production*
- **Hugging Face** : `git push space <commit-sha>:main --force`

### Plan de repli pour la démonstration
En cas de panne réseau le jour J :
```bash
venv/bin/python backend/demo_cli.py --auto
```
Démonstration en terminal des 4 scénarios clés, sans frontend ni réseau (hors Gemini).

---

## 5. Dépannage

| Symptôme | Cause probable | Correction |
|---|---|---|
| Build échoue sur `pip install` | Wheel CUDA tirée par défaut | Vérifier que la ligne `--index-url .../whl/cpu` est bien présente |
| `rag_status: "empty"` | Base vectorielle non construite | Vérifier l'étape `RUN python -m backend.rag.embeddings` dans les logs |
| `rag_status: "requires_model_download"` | Modèle absent de l'image | Vérifier l'étape `snapshot_download` |
| `llm_status: "unconfigured"` | Secret manquant | Ajouter `GOOGLE_API_KEY` puis *Factory reboot* |
| Erreur CORS en console | Appel cross-origin | Vérifier le *rewrite* `vercel.json` et `CORS_ORIGINS` |
| 429 sur `/api/chat` | Limite de 30 req/min par IP | Comportement normal ; message localisé déjà affiché |
| Première réponse très lente | Space endormi | Réchauffer avant la démonstration |

---

## 6. Évolutions (hors périmètre PFA)

1. **Embeddings via l'API Gemini** — supprime `torch` : image de ~1,8 Go → ~150 Mo,
   démarrage à froid de ~30 s → ~2 s, compatible avec tous les paliers gratuits.
   Nécessite une ré-ingestion **et un recalibrage de `SIMILARITY_THRESHOLD`**
   (calibré à 0.15 pour le modèle MiniLM actuel).
2. **Sessions dans Redis** — `REDIS_URL` et le service Redis sont déjà prévus dans
   `docker-compose.yml` ; il manque l'implémentation `RedisSessionStore`.
   Permettrait de survivre aux redémarrages et de passer à plusieurs instances.
3. **Limitation de débit partagée** — `slowapi` est actuellement en mémoire par processus.
