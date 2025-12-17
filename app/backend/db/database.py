# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Le nom de ton fichier de base de données
SQLALCHEMY_DATABASE_URL = "sqlite:///./budget.db"

# Création du moteur (check_same_thread=False est nécessaire pour SQLite)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)