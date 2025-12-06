from app.db.database import engine, SessionLocal
from app.db import models
from datetime import datetime, timedelta
import random

# 1. CRÉATION DES TABLES
print("Création de la base de données...")
models.Base.metadata.drop_all(bind=engine) # On supprime tout pour repartir propre
models.Base.metadata.create_all(bind=engine) # On recrée tout

db = SessionLocal()

print("Insertion des données de test...")

# --- FONCTIONS UTILITAIRES POUR LES DATES DYNAMIQUES ---
# Ces fonctions garantissent que les données sont toujours visibles, peu importe la date de ton PC
def get_date_current_month(day=1):
    """Retourne une date du mois ACTUEL avec le jour demandé"""
    today = datetime.now()
    try:
        return today.replace(day=day)
    except ValueError:
        return today.replace(day=28) # Sécurité pour février

def get_date_last_month(day=1):
    """Retourne une date du MOIS DERNIER"""
    today = datetime.now()
    first = today.replace(day=1)
    last_month = first - timedelta(days=1)
    try:
        return last_month.replace(day=day)
    except ValueError:
        return last_month.replace(day=28)

def get_date_two_months_ago(day=1):
    """Retourne une date d'il y a 2 MOIS"""
    today = datetime.now()
    first = today.replace(day=1)
    last_month = first - timedelta(days=1)
    first_last = last_month.replace(day=1)
    two_months = first_last - timedelta(days=1)
    try:
        return two_months.replace(day=day)
    except ValueError:
        return two_months.replace(day=28)

# 1. CRÉATION DES CATÉGORIES (Parents & Enfants)
# Revenus
cat_salaire = models.Category(name="Salaire", type="revenu")
cat_freelance = models.Category(name="Freelance", type="revenu")

# Dépenses Parents
cat_alim = models.Category(name="Alimentation", type="depense")
cat_logement = models.Category(name="Logement", type="depense")
cat_loisirs = models.Category(name="Loisirs", type="depense")
cat_transport = models.Category(name="Transport", type="depense")

db.add_all([cat_salaire, cat_freelance, cat_alim, cat_logement, cat_loisirs, cat_transport])
db.commit()

# Dépenses Enfants (Sous-catégories)
cat_courses = models.Category(name="Courses", type="depense", parent_id=cat_alim.id)
cat_resto = models.Category(name="Restaurant", type="depense", parent_id=cat_alim.id)
cat_loyer = models.Category(name="Loyer", type="depense", parent_id=cat_logement.id)
cat_netflix = models.Category(name="Streaming", type="depense", parent_id=cat_loisirs.id)
cat_essence = models.Category(name="Essence", type="depense", parent_id=cat_transport.id)

db.add_all([cat_courses, cat_resto, cat_loyer, cat_netflix, cat_essence])
db.commit()

# 2. CRÉATION DES TRANSACTIONS DYNAMIQUES
transactions = []

# --- CE MOIS-CI (Le dashboard les affichera en premier) ---
# On utilise get_date_current_month() au lieu de dates fixes
transactions.append(models.Transaction(amount=1500, label="Salaire", date=get_date_current_month(1), category_id=cat_salaire.id))
transactions.append(models.Transaction(amount=800, label="Loyer", date=get_date_current_month(5), category_id=cat_loyer.id))
transactions.append(models.Transaction(amount=50, label="Plein Essence", date=get_date_current_month(6), category_id=cat_essence.id))
transactions.append(models.Transaction(amount=45.50, label="Carrefour City", date=get_date_current_month(10), category_id=cat_courses.id))
transactions.append(models.Transaction(amount=15.99, label="Netflix", date=get_date_current_month(2), category_id=cat_netflix.id))

# --- LE MOIS DERNIER ---
transactions.append(models.Transaction(amount=1500, label="Salaire", date=get_date_last_month(1), category_id=cat_salaire.id))
transactions.append(models.Transaction(amount=60, label="Resto Italien", date=get_date_last_month(10), category_id=cat_resto.id))
transactions.append(models.Transaction(amount=120, label="Courses mois dernier", date=get_date_last_month(5), category_id=cat_courses.id))
transactions.append(models.Transaction(amount=800, label="Loyer", date=get_date_last_month(1), category_id=cat_loyer.id))

# --- IL Y A 2 MOIS ---
transactions.append(models.Transaction(amount=1500, label="Salaire", date=get_date_two_months_ago(1), category_id=cat_salaire.id))
transactions.append(models.Transaction(amount=800, label="Loyer", date=get_date_two_months_ago(1), category_id=cat_loyer.id))

db.add_all(transactions)

db.commit()

print("Base de données réinitialisée et remplie avec succès (Dates dynamiques) !")
db.close()