from sqlalchemy.orm import Session
from sqlalchemy import extract
from datetime import datetime
from . import models

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
