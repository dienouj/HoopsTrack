# HoopTrack API

HoopTrack est une application de suivi de statistiques de basketball permettant aux entraîneurs, joueurs et statisticiens de gérer et d'analyser les performances des équipes et des joueurs.

## Fonctionnalités

- Gestion des utilisateurs (inscription, authentification, autorisations)
- Gestion des équipes et des joueurs
- Enregistrement et analyse des statistiques de match
- Suivi des performances individuelles et d'équipe
- Interface API RESTful complète

## Prérequis

- Python 3.8+
- Django 5.1+
- PostgreSQL (recommandé pour la production)

## Installation

1. Cloner le dépôt :
```bash
git clone https://github.com/votre-utilisateur/hooptrack.git
cd hooptrack
```

2. Créer un environnement virtuel et l'activer :
```bash
python -m venv venv
source venv/bin/activate  # Sur Linux/Mac
venv\Scripts\activate     # Sur Windows
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Configurer la base de données :
```bash
python manage.py migrate
```

5. Créer un superutilisateur :
```bash
python manage.py createsuperuser
```

6. Lancer le serveur de développement :
```bash
python manage.py runserver
```

## Documentation de l'API

Une fois le serveur lancé, la documentation de l'API est disponible aux URLs suivantes :

- Swagger UI : http://localhost:8000/api/docs/
- ReDoc : http://localhost:8000/api/redoc/

## Endpoints API

### Authentification
- `/api/v1/auth/` - Interface d'authentification DRF
- Login via JWT : `/api/v1/users/token/`

### Utilisateurs
- `/api/v1/users/` - Liste des utilisateurs
- `/api/v1/users/me/` - Informations sur l'utilisateur connecté
- `/api/v1/users/register/` - Inscription d'un nouvel utilisateur

### Équipes et Joueurs
- `/api/v1/teams/` - Gestion des équipes
- `/api/v1/players/` - Gestion des joueurs
- `/api/v1/teams/{id}/players/` - Joueurs d'une équipe spécifique

### Statistiques
- `/api/v1/games/` - Matchs
- `/api/v1/performances/` - Performances individuelles des joueurs
- `/api/v1/team-performances/` - Performances d'équipe

## Modèles de données

### User
- Rôles : Coach, Joueur, Statisticien
- Informations personnelles

### Team
- Nom, logo, entraîneur

### Player
- Utilisateur associé, équipe, poste, numéro de maillot

### Game
- Équipe à domicile, équipe visiteuse, date, score

### Performance
- Joueur, match, statistiques (points, rebonds, passes, etc.)

### TeamPerformance
- Équipe, match, statistiques d'équipe

## Déploiement en production

Pour déployer l'application en production sur AWS :

1. Configurer les variables d'environnement (SECRET_KEY, DATABASE_URL, etc.)
2. Collecter les fichiers statiques : `python manage.py collectstatic`
3. Utiliser Gunicorn comme serveur WSGI
4. Configurer Nginx comme proxy inverse
5. Configurer un SSL avec Let's Encrypt

## Sécurité

- Authentification via JWT
- Permissions par rôle (Coach, Joueur, Statisticien)
- Protections CSRF
- Configuration CORS sécurisée en production

## Licence

MIT
