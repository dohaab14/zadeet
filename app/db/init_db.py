# init_db.py
from database import engine, SessionLocal
from models import Base, Category, Transaction

# 1. CRÉATION DES TABLES
# Cette ligne magique crée le fichier budget.db et toutes les tables vides
print("Création de la base de données...")
Base.metadata.create_all(bind=engine)

# 2. OUVERTURE DE LA SESSION
db = SessionLocal()

# 3. INSERTION DES DONNÉES (Ton code adapté)
print("Insertion des données de test...")

# Vérification pour ne pas créer des doublons si on relance le script
if not db.query(Category).first():
    # --- Ton code commence ici ---
    # 1. On crée le parent
    cat_courses = Category(name="Courses", type="depense", parent_id=None)
    db.add(cat_courses)
    db.commit() 
    db.refresh(cat_courses)

    # 2. On crée l'enfant (Sous-catégorie)
    cat_boissons = Category(name="Boissons", type="depense", parent_id=cat_courses.id)
    db.add(cat_boissons)
    db.commit()

    # 3. On crée une transaction
    achat_jus = Transaction(amount=1.50, label="Jus d'orange", category_id=cat_boissons.id)
    db.add(achat_jus)
    db.commit()

    cat_sorties = Category(name="Sortie", type="depense", parent_id=None)
    db.add(cat_sorties)
    db.commit() 
    db.refresh(cat_sorties)

    cat_resto = Category(name="Restaurants", type="depense", parent_id=cat_sorties.id)
    db.add(cat_resto)
    db.commit()

    resto_it = Transaction(amount=40.50, label="Date au restaurant Italien", category_id=cat_resto.id)
    db.add(resto_it)
    db.commit()
    # --- Fin de ton code ---
    
    print("Données ajoutées avec succès !")
else:
    print("La base contient déjà des données.")

db.close()