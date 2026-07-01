# Tâche 3 — Intégration Frontend-Backend et tests end-to-end

## Assigné à
**Salma Said** & **Mohamed Tamzirt** (travail collaboratif)

## Objectif
Réaliser l'intégration complète entre le frontend React et le backend FastAPI, configurer le déploiement, et valider le fonctionnement end-to-end du chatbot.

## Étapes d'implémentation

1. **Configuration de la communication Frontend-Backend**
   - Finaliser la configuration CORS sur FastAPI
   - Connecter le service API React aux endpoints FastAPI
   - Gérer les erreurs réseau côté frontend
   - Implémenter le retry automatique

2. **Tests d'intégration** *(Salma)*
   - Tester le flux complet : message → détection langue → RAG → LLM → réponse
   - Vérifier l'affichage correct des réponses en FR et AR
   - Tester le changement de langue en cours de conversation
   - Tester les cas limites (messages vides, très longs, caractères spéciaux)

3. **Optimisation des performances** *(Mohamed)*
   - Mesurer le temps de réponse bout-en-bout
   - Optimiser le chargement du frontend (lazy loading, code splitting)
   - Implémenter le caching côté backend (réponses fréquentes)
   - Compresser les réponses API (gzip)

4. **Configuration du déploiement**
   - Créer les fichiers Docker (Dockerfile frontend + backend)
   - Configurer `docker-compose.yml` pour le développement local
   - Préparer la configuration de production (Vercel + Cloud)

5. **Tests de compatibilité navigateur**
   - Chrome, Firefox, Safari, Edge
   - Responsive : mobile, tablette, desktop
   - Tests RTL sur différents navigateurs

## Outils et ressources
- Docker et docker-compose
- Outils de test (Postman, curl, navigateur)
- Lighthouse pour les audits de performance
- Vercel CLI pour le déploiement frontend

## Livrable attendu
- Application intégrée fonctionnelle avec :
  - Communication frontend-backend validée
  - `docker-compose.yml` pour le lancement local
  - Rapport de tests d'intégration
  - Guide de déploiement

## Critères de validation
- [ ] Le flux complet fonctionne de bout en bout
- [ ] Le temps de réponse total est < 5 secondes
- [ ] L'application fonctionne sur les 4 navigateurs principaux
- [ ] Le déploiement Docker fonctionne avec `docker-compose up`
- [ ] Les tests d'intégration passent tous
- [ ] Durée : **Semaine 5-6** (fin de sprint)
