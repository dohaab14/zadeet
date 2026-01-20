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
## Partie Kubernetes avec Rancher
Pour information, toutes nos ressources sont déployées dans le namespace : `u-grp3`

### 1. Vérifier les images Docker (amd64)
- dohaab14/zadeet-backend:latest
- dohaab14/zadeet-frontend:latest
### 2. Ajouter les secrets de la base de données
```
kubectl -n u-grp3 create secret generic zadeet-secrets --from-literal=DATABASE_USER=zadeet_user  --from-literal=DATABASE_PASSWORD=(le mdp) --from-literal=DATABASE_NAME=zadeet_db
```

### 3. Déployer les manifests k8s 
/!\ faire la commande de puis le folder k8s\
`kubectl apply -R -f k8s/ `

### 4. Test de l'application

`kubectl port-forward -n u-grp3 svc/frontend 8080:80`

## Structure du Projet

```text 
└──
    ├── docker-compose.yml
    ├── init_db.py
    ├── nginx.conf
    ├── requirements.txt
    ├── seed_db.py
    └── app/
        ├── schemas.py
        ├── api/
        │   └── routes_plafonds.py
        ├── backend/
        │   ├── Dockerfile
        │   ├── main.py
        │   ├── api/
        │   │   ├── back_routes_acc.py
        │   │   ├── back_routes_categories.py
        │   │   └── back_routes_transactions.py
        │   ├── db/
        │   │   ├── database.py
        │   │   ├── models.py
        │   │   └── schemas.py
        │   └── services/
        │       ├── services_accueil.py
        │       ├── services_categories.py
        │       ├── services_plafonds.py
        │       └── services_transactions.py
        ├── frontend/
        │   ├── Dockerfile
        │   ├── js/
        │   │   └── app.js
        │   ├── static/
        │   │   └── style.css
        │   └── templates/
        │       ├── categories.html
        │       ├── index.html
        │       └── transactions.html
        ├── k8s/
        │   ├── 01-configmap.yaml
        │   ├── 02-secret.yaml
        │   ├── backend/
        │   │   ├── 01-backend-deployment.yaml
        │   │   └── 02-backend-service.yaml
        │   ├── db/
        │   │   ├── 01-postegres-pvc.yaml
        │   │   ├── 02-postgres-deployment.yaml
        │   │   └── 03-postgres-service.yaml
        │   └── front/
        │       ├── 01-nginx-configmap.yaml
        │       ├── 02-frontend-deployment.yaml
        │       └── 03-frontend-service.yaml
        └── templates/
            ├── base.html
            ├── home.html
            └── navbar.html

```




Auteurs
Zadeet Team – Développement Fullstack

Dernière mise à jour : Ajout de la partie Kubernetes
