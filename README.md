# Zadeet

**Zadeet** est une application web de gestion de dépenses personnelles conçue pour suivre, catégoriser et analyser votre budget mensuel.

L'application repose sur une architecture conteneurisée séparant le **Frontend** (statique servi par Nginx), le **Backend** (API Python) et la **Base de données** (PostgreSQL).

---

## Architecture Technique

Le projet est divisé en trois services Docker distincts :

- **Frontend** : Interface utilisateur (HTML/CSS/JS) servie par **Nginx** (Port `80`)
- **Backend** : API REST développée en **Python 3.11** (avec Uvicorn), accessible sur le port `8000`
- **Database** : Base de données **PostgreSQL 15**

---

## Prérequis

- **Docker** installé sur votre machine
- **Git** pour cloner le projet

---

## Installation et Démarrage

### 1. Cloner le projet

```bash
git clone https://github.com/votre-compte/zadeet.git
cd zadeet
```

### 2. Lancer l'application
Utilisez Docker Compose pour construire les images et démarrer les conteneurs :

```bash
docker-compose up -d --build
```

### 3. Initialiser la Base de Données (Premier lancement uniquement)
Une fois les conteneurs lancés, vous devez initialiser les tables et les données de base :

```bash
docker exec -it backend_container python init_db.py
```

Utilisation
Une fois l'application démarrée :

Application Web : http://localhost/

Documentation API (Swagger) : http://localhost:8000/docs (si configuré dans FastAPI)

Commandes Utiles

``` bash
#Arrêter l'application
docker-compose down

#Voir les logs (en cas de problème)

# Pour le backend
docker logs -f backend_container

# Pour tous les services
docker-compose logs -f

```
Nettoyer l'environnement (repartir à zéro)
Attention : cette action supprime toutes les données.

```bash
docker-compose down -v
```


## Structure du Projet

```text 
.
├── app/
│   ├── backend/          # Code source de l'API Python
│   │   ├── api/          # Routes (transactions, catégories...)
│   │   ├── db/           # Modèles et schémas BDD
│   │   ├── services/     # Logique métier
│   │   ├── main.py       # Point d'entrée Backend
│   │   └── Dockerfile
│   │
│   └── frontend/         # Code source Interface
│       ├── templates/    # Fichiers HTML
│       ├── static/       # CSS, images
│       ├── js/           # Scripts JavaScript
│       └── Dockerfile
│
├── docker-compose.yml    # Orchestration des services
├── nginx.conf            # Configuration du serveur web
├── requirements.txt      # Dépendances Python
└── init_db.py            # Script d'initialisation BDD
```




Auteurs
Zadeet Team – Développement Fullstack

Dernière mise à jour : Architecture Dockerisée (Frontend / Backend séparés).
