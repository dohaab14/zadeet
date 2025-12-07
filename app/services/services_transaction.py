from sqlalchemy.orm import Session
from sqlalchemy import extract
from datetime import datetime
from app.db import models

def get_transactions_by_month(db: Session, year: int, month: int):
    """
    Récupère toutes les transactions d'un mois précis.
    Utile pour les graphiques du dashboard.
    """
    return db.query(models.Transaction)\
             .filter(extract('year', models.Transaction.date) == year)\
             .filter(extract('month', models.Transaction.date) == month)\
             .all()

def get_recent_transactions(db: Session, limit: int = 3):
    """
    Récupère les dernières transactions pour l'aperçu.
    """
    return db.query(models.Transaction)\
             .order_by(models.Transaction.date.desc())\
             .limit(limit)\
             .all()

def search_by_amount(db: Session, amount: float, tolerance: float = 0.01):
    """
    Recherche les transactions correspondant à un montant donné.
    
    Args:
        db: Session SQLAlchemy
        amount: Montant à rechercher
        tolerance: Marge d'erreur acceptée (par défaut 0.01€)
    
    Returns:
        Liste des transactions trouvées
    """
    return db.query(models.Transaction)\
        .filter(models.Transaction.amount >= amount - tolerance)\
        .filter(models.Transaction.amount <= amount + tolerance)\
        .all()

