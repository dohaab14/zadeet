# init_db.py (A la racine du projet)
from app.db.database import engine, SessionLocal
from app.db import models # On importe depuis le nouveau dossier

# 1. CRÉATION DES TABLES
print("Création de la base de données...")
models.Base.metadata.create_all(bind=engine)

# 2. OUVERTURE DE LA SESSION
db = SessionLocal()

# 3. INSERTION DES DONNÉES
print("Insertion des données de test...")

# On vérifie si la catégorie existe déjà pour éviter les doublons
if not db.query(models.Category).first():
    # Création Parent
    cat_courses = models.Category(name="Courses", type="depense", parent_id=None)
    db.add(cat_courses)
    db.commit()
    db.refresh(cat_courses)

    # Création Enfant
    cat_boissons = models.Category(name="Boissons", type="depense", parent_id=cat_courses.id)
    db.add(cat_boissons)
    db.commit()

    # Création Transaction
    achat_jus = models.Transaction(amount=1.50, label="Jus d'orange", category_id=cat_boissons.id)
    db.add(achat_jus)
    db.commit()

    print("Données ajoutées avec succès !")
else:
    print("ℹLa base contient déjà des données.")

db.close()