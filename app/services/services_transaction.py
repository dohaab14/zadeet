from typing import List
from sqlalchemy.orm import Session

from app.db import models
from app.schemas.transactions import TransactionCreate


def create_transaction(db: Session, data: TransactionCreate) -> models.Transaction:
    """
    Crée une nouvelle transaction en base.
    """
    tx = models.Transaction(
        amount=data.amount,
        is_expense=data.is_expense,
        date=data.date,
        description=data.description,
        category_id=data.category_id,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


def list_transactions(db: Session) -> List[models.Transaction]:
    """
    Retourne la liste des transactions, triées de la plus récente à la plus ancienne.
    """
    return (
        db.query(models.Transaction)
        .order_by(models.Transaction.date.desc(), models.Transaction.id.desc())
        .all()
    )


def delete_transaction(db: Session, tx_id: int) -> None:
    """
    Supprime une transaction par son id.
    """
    tx = db.query(models.Transaction).filter(models.Transaction.id == tx_id).first()
    if tx:
        db.delete(tx)
        db.commit()


def total_expenses(db: Session) -> float:
    """
    Calcule le total des dépenses (is_expense = True).
    """
    rows = (
        db.query(models.Transaction.amount)
        .filter(models.Transaction.is_expense == True)  # noqa: E712
        .all()
    )
    return sum(r[0] for r in rows) if rows else 0.0


def total_transactions_count(db: Session) -> int:
    """
    Retourne le nombre total de transactions (toutes).
    """
    return db.query(models.Transaction).count()
