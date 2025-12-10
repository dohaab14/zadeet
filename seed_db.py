"""
Seed de la base de données ZADEET :
- Création de catégories (revenu + dépense)
- Création de transactions
"""

from datetime import date
from app.db.database import SessionLocal
from app.db.models import Category, Transaction

db = SessionLocal()

print("\n-----------------------------")
print("   SEEDING DATABASE ZADEET")
print("-----------------------------\n")

# ---------------------------------------------
# 1) CATEGORIES (revenus + dépenses)
# ---------------------------------------------
categories_data = [
    {"name": "Salaire", "type": "revenu"},
    {"name": "Cadeaux / Parents", "type": "revenu"},
    {"name": "Logement", "type": "depense"},
    {"name": "Nourriture", "type": "depense"},
    {"name": "Transports", "type": "depense"},
    {"name": "Loisirs", "type": "depense"},
]

categories = {}

print("→ Création des catégories...")

for cat in categories_data:
    c = Category(**cat)
    db.add(c)
    db.commit()
    db.refresh(c)
    categories[cat["name"]] = c

print("✔️ Catégories créées.")

# ---------------------------------------------
# 2) TRANSACTIONS (avec dates)
# ---------------------------------------------
transactions_data = [
    # REVENUS
    {"label": "Salaire mensuel", "amount": 1200, "category": "Salaire", "date": date(2025, 1, 5)},
    {"label": "Argent de poche", "amount": 150, "category": "Cadeaux / Parents", "date": date(2025, 1, 12)},

    # DÉPENSES
    {"label": "Loyer", "amount": 500, "category": "Logement", "date": date(2025, 1, 3)},
    {"label": "Courses Carrefour", "amount": 85.90, "category": "Nourriture", "date": date(2025, 1, 8)},
    {"label": "Uber", "amount": 22.50, "category": "Transports", "date": date(2025, 1, 10)},
    {"label": "Cinéma", "amount": 12.00, "category": "Loisirs", "date": date(2025, 1, 15)},
]

print("→ Création des transactions...")

for t in transactions_data:
    txn = Transaction(
        label=t["label"],
        amount=t["amount"],
        category_id=categories[t["category"]].id,
        date=t["date"],
    )
    db.add(txn)

db.commit()

print("✔️ Transactions créées.")

print("\n-----------------------------")
print(" Seed terminé avec succès ! ")
print("-----------------------------\n")
