from sqlalchemy.orm import Session
from sqlalchemy import extract
from datetime import datetime
from . import models
from services_transactions import *


def get_total_balance(db: Session):
    """
    Calcule le solde total : somme des revenus - somme des dépenses.
    """
    # Récupère toutes les transactions avec leur catégorie
    transactions = db.query(models.Transaction).join(models.Category).all()

    total = 0
    for t in transactions:
        if t.category.type == "revenu":
            total += t.amount
        elif t.category.type == "depense":
            total -= t.amount

    return total