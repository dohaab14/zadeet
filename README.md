# ZADEET — Gestionnaire de Budget 

## Présentation du projet

ZADEET est une application web de gestion de budget développée dans le cadre du cours Architecture Logicielle. Elle permet de suivre facilement ses dépenses, revenus, catégories, ainsi que de visualiser un tableau de bord avec statistiques.

Le projet combine :
* **FastAPI** (backend)
* **Jinja2** (templates HTML)
* **SQLAlchemy + SQLite** (base de données)
* **Bootstrap 5** (UI)
* **Chart.js** (graphique)
* **Python 3.12**

---

## Fonctionnalités

### Gestion des transactions
* Ajouter une dépense ou un revenu
* Modifier une transaction (depuis un modal)
* Supprimer une transaction
* Choisir la date librement
* Liaison à une catégorie (dépense/revenu)
* Recherche par mot-clé (label)
* Regroupement automatique par catégorie
* Totaux : total dépenses / total revenus

**Note** : Filtrage avancé par catégorie + période prévu pour la suite.

### Gestion des catégories
* Ajouter une catégorie
* Supprimer une catégorie
* Deux types possibles :
  * `depense`
  * `revenu`
* Affichage du nombre total de catégories

### Tableau de bord
* Solde actuel (revenus − dépenses)
* Dernières transactions (3 dernières)
* Graphique "Revenus vs Dépenses"
* Graphique de répartition par catégorie
* Formulaire d'accès rapide aux filtres

### Base de données
* Base SQLite : `budget.db`
* Création automatique des tables via `init_db.py`
* Script d'insertion de données de démo via `seed_db.py`

---

## Architecture du projet
```
zadeet/
│
├── app/
│   ├── api/
│   │   ├── routes_transactions.py
│   │   └── routes_categories.py
│   ├── db/
│   │   ├── database.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── services/
│   │   ├── services_transactions.py
│   │   └── services_categories.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── categories.html
│   │   └── transactions.html
│   └── static/
│       └── style.css
│
├── init_db.py
├── seed_db.py
├── budget.db
├── requirements.txt
└── README.md
```

---

## Installation

### 1. Cloner le projet
```bash
git clone https://github.com/.../zadeet.git
cd zadeet
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Créer la base de données
```bash
python3 init_db.py
```

### 4. (Facultatif) Ajouter des données de démonstration
```bash
python3 seed_db.py
```

### 5. Lancer l'application
```bash
uvicorn app.backend.main:app --reload
```

**Accéder à l'application** : [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

