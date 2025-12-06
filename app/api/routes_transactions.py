"""
Utilisation ici des données via schemas.py pour gérer les routes liées aux transactions
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from schemas import Transaction, TransactionCreate, TransactionUpdate
import services_transactions as service
from sqlalchemy import extract
from app.db import models
from typing import List

router = APIRouter(prefix="/transactions", tags=["Transactions"])


def get_db():
    """
    Obtention d'une session de base de données
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------
@router.get("/", response_model=list[Transaction])
def list_transactions(category_id: int | None = None, db: Session = Depends(get_db)):
    """
    Récupère toutes les transactions ou celles d'une catégorie spécifique
    """
    return service.get_transactions(db, category_id)


# ---------------------------------------------------------------------

@router.post("/", response_model=Transaction)
def create_transaction(data: TransactionCreate, db: Session = Depends(get_db)):
    """
    Crée une nouvelle transaction
    """
    return service.create_transaction(db, data)


# ---------------------------------------------------------------------

@router.put("/{transaction_id}", response_model=Transaction)
def update_transaction(transaction_id: int, data: TransactionUpdate, db: Session = Depends(get_db)):
    """
    Met à jour une transaction existante
    """
    txn = service.get_transaction(db, transaction_id)

    if not txn:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")

    return service.update_transaction(db, txn, data)


# ---------------------------------------------------------------------

@router.delete("/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """
    Supprime une transaction existante"""
    txn = service.get_transaction(db, transaction_id)

    if not txn:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")

    service.delete_transaction(db, txn)
    return {"message": "Transaction supprimée"}


# -------------------------------------------------------------------
@router.get("/monthly-transactions", response_model=List[Transaction])
def get_transactions_by_month_api(year: int, month: int, db: Session = Depends(get_db)):
    """
    Récupère toutes les transactions d'un mois précis.
    """
    transactions = db.query(models.Transaction).filter(
        extract('year', models.Transaction.date) == year
    ).filter(
        extract('month', models.Transaction.date) == month
    ).all()

    return transactions


# -------------------------------------------------------------------
@router.get("/recent-transactions", response_model=List[Transaction])
def get_recent_transactions_api(limit: int = 3, db: Session = Depends(get_db)):
    """
    Récupère les dernières transactions pour l'aperçu.
    """
    transactions = db.query(models.Transaction).order_by(
        models.Transaction.date.desc()
    ).limit(limit).all()

    return transactions