"""
Logique du code pour les transactions
Ici utilisation de models.py pour interagir avec la bdd
"""
import models
from sqlalchemy.orm import Session
from datetime import datetime
from models import Transaction
from schemas import TransactionCreate, TransactionUpdate


def create_transaction(db: Session, data: TransactionCreate):
    """
    Creation d'une transaction
    return: la transaction créée
    """
    txn = Transaction(**data.dict())
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn


def update_transaction(db: Session, transaction: Transaction, data: TransactionUpdate):
    """
    Modification d'une transaction
    return: la transaction modifiée
    """

    for key, value in data.dict(exclude_unset=True).items():
        setattr(transaction, key, value)

    db.commit()
    db.refresh(transaction)
    return transaction


def delete_transaction(db: Session, transaction: Transaction):
    """
    Suppression d'une transaction
    return: True si la suppression a réussi, False sinon
    """
    db.delete(transaction)
    db.commit()
    return True


def get_transactions(db: Session, category_id: int | None = None):
    """
    Récupère toutes les transactions ou les transactions d'une catégorie spécifique
    return: liste des transactions
    """
    query = db.query(Transaction)

    if category_id is not None:
        query = query.filter(Transaction.category_id == category_id)

    return query.all()


def get_transaction(db: Session, transaction_id: int):
    """
    Récupère une transaction par son ID
    return: la transaction, None si elle n'existe pas
    """
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()



def get_transactions_by_month(db: Session, year: int, month: int):
    """
    Récupère toutes les transactions d'un mois précis.
    Utile pour les graphiques du dashboard.
    """
    return db.query(models.Transaction.filter(extract('year', models.Transaction.date) == year).filter(extract('month', models.Transaction.date) == month)).all()

def get_recent_transactions(db: Session, limit: int = 3):
    """
    Récupère les dernières transactions pour l'aperçu.
    """
    return db.query(models.Transaction).order_by(models.Transaction.date.desc()).limit(limit).all()