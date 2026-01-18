# database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 1. Configuration de l'URL de connexion
# On récupère la variable "DATABASE_URL" définie dans le docker-compose.
# Si elle n'existe pas (ex: test hors docker), on utilise une valeur par défaut locale.
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL")

# 2. Création du Moteur (Engine)
# Contrairement à SQLite, PostgreSQL gère le multi-thread nativement.
# Nous n'avons donc plus besoin de l'option connect_args={"check_same_thread": False}.
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 3. Création de la Session
# C'est l'usine qui va fabriquer des sessions de connexion pour chaque requête.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Base déclarative
# Toutes tes tables (dans models.py) hériteront de cette classe Base.
Base = declarative_base()