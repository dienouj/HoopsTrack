# Stratégie DevOps pour HoopTrack

Ce document décrit la stratégie DevOps mise en place pour le projet HoopTrack, incluant le workflow Git, les environnements de déploiement et les pratiques CI/CD.

## Workflow Git (GitFlow)

Notre projet suit une version adaptée du modèle GitFlow avec les branches suivantes :

### Branches principales
- `master` : Représente le code en production. Seules les fusions depuis `staging` ou les `hotfixes` sont autorisées.
- `develop` : Branche principale de développement. C'est ici que les fonctionnalités sont intégrées avant d'être promues.
- `staging` : Environnement de préproduction pour tester les fonctionnalités avant la mise en production.
- `production` : Miroir de la production actuelle, utilisée pour les hotfixes et les tests de déploiement.

### Branches temporaires
- `feature/*` : Pour développer de nouvelles fonctionnalités (ex: `feature/authentication`).
- `hotfix/*` : Pour corriger rapidement des bugs critiques en production (ex: `hotfix/security-patch`).
- `release/*` : Pour préparer une nouvelle version avec tests et documentation (ex: `release/v1.0.0`).

## Règles de contribution

1. **Nouvelles fonctionnalités** :
   ```
   git checkout develop
   git checkout -b feature/nom-fonctionnalite
   # Travail sur la fonctionnalité
   git commit -m "Description détaillée"
   # Pousser et créer une Pull Request vers develop
   ```

2. **Corrections de bugs** :
   ```
   git checkout develop
   git checkout -b bugfix/description-bug
   # Correction du bug
   git commit -m "Fix: Description détaillée"
   # Pousser et créer une Pull Request vers develop
   ```

3. **Corrections urgentes (hotfix)** :
   ```
   git checkout production
   git checkout -b hotfix/description-fix
   # Correction du problème critique
   git commit -m "Hotfix: Description détaillée"
   # Pousser et créer des Pull Requests vers master ET develop
   ```

## Environnements de déploiement

### Développement
- Branche: `develop`
- URL: `dev.hooptrack.com`
- Déploiement: Automatique à chaque fusion dans `develop`
- Base de données: Clone de production avec données anonymisées

### Préproduction (Staging)
- Branche: `staging`
- URL: `staging.hooptrack.com`
- Déploiement: Manuel après validation QA sur `develop`
- Base de données: Clone de production avec données anonymisées

### Production
- Branche: `master`
- URL: `hooptrack.com`
- Déploiement: Manuel après validation en staging
- Base de données: Production

## Pipeline CI/CD

Notre pipeline CI/CD est configuré avec GitHub Actions et comprend les étapes suivantes :

1. **Build & Tests** : Pour chaque PR et push sur `develop`, `staging`, et `master`
   - Lint du code
   - Tests unitaires
   - Tests d'intégration
   - Analyse de sécurité

2. **Déploiement vers Développement** :
   - Automatique pour chaque fusion dans `develop`
   - Construction de l'image Docker
   - Déploiement sur l'environnement de développement AWS

3. **Déploiement vers Staging** :
   - Manuel via l'interface GitHub Actions
   - Construction de l'image Docker avec tag spécifique
   - Déploiement sur l'environnement de staging AWS

4. **Déploiement vers Production** :
   - Manuel via l'interface GitHub Actions
   - Approbation requise
   - Construction de l'image Docker avec tag de release
   - Déploiement sur l'environnement de production AWS

## Infrastructure as Code (IaC)

L'infrastructure du projet est gérée via Terraform avec des modules pour :
- VPC et réseau AWS
- ECS pour les conteneurs
- RDS pour la base de données PostgreSQL
- S3 pour le stockage des médias
- CloudFront pour la distribution des contenus statiques

Les fichiers de configuration Terraform se trouvent dans le dossier `/terraform` du projet.

## Monitoring et Observabilité

- **Logs** : Centralisés dans CloudWatch
- **Métriques** : Prometheus + Grafana
- **Alertes** : Configurées dans CloudWatch et PagerDuty
- **Traçage** : AWS X-Ray

## Sécurité

- Scans automatiques de vulnérabilités avec OWASP ZAP
- Analyse statique de code avec SonarQube
- Analyse des dépendances avec Dependabot
- Tests de pénétration programmés trimestriellement

## Procédure de mise en production

1. Créer une PR de `develop` vers `staging`
2. Exécuter les tests d'intégration complets
3. Déployer en staging et effectuer des tests manuels
4. Créer une PR de `staging` vers `master`
5. Obtenir les approbations requises
6. Fusionner et déclencher le déploiement en production
7. Vérifier le bon fonctionnement via les tests de smoke
8. Surveiller les métriques clés pendant les 24 premières heures
