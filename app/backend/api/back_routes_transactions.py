from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import or_

from ..db.database import SessionLocal
from ..db import models, schemas
from ..services import services_transactions

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[dict])
def get_transactions_filtered(
    category_id: int | None = None,
    period: str | None = "current_month",
    db: Session = Depends(get_db)
):
    """
    API unique pour lister et filtrer les transactions.
    """
    query = db.query(models.Transaction).join(models.Category)
    
    if category_id:
        query = query.filter(
            or_(
                models.Transaction.category_id == category_id,
                models.Category.parent_id == category_id
            )
        )

    today = date.today()
    if period == "current_month":
        start = today.replace(day=1)
        query = query.filter(models.Transaction.date >= start)
    elif period == "last_month":
        start = (today.replace(day=1) - relativedelta(months=1))
        end = today.replace(day=1) - timedelta(days=1)
        query = query.filter(models.Transaction.date.between(start, end))
    elif period == "last_3_months":
        start = today - relativedelta(months=3)
        query = query.filter(models.Transaction.date >= start)
    elif period == "all":
        pass 

    results = query.order_by(models.Transaction.date.desc()).all()

    output = []
    for t in results:
        parent_name = "Autre"
        if t.category:
            parent_name = t.category.parent.name if t.category.parent else t.category.name

        output.append({
            "id": t.id,
            "label": t.label,
            "amount": t.amount,
            "date": t.date.strftime("%d/%m/%Y"), # Format affichage FR
            "category_name": t.category.name if t.category else "Autre",
            "parent_name": parent_name,
            "category_type": t.category.type if t.category else "depense",
            "category_id": t.category_id,
            "date_raw": t.date 
        })
    return output

@router.post("/", status_code=201)
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    """Création"""
    return services_transactions.create_transaction(db, transaction)


@router.put("/{transaction_id}")
def update_transaction(transaction_id: int, transaction: schemas.TransactionUpdate, db: Session = Depends(get_db)):
    """Modification"""
    db_transaction = services_transactions.get_transaction(db, transaction_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction introuvable")
    
    return services_transactions.update_transaction(db, db_transaction, transaction)

@router.delete("/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Suppression"""
    db_transaction = services_transactions.get_transaction(db, transaction_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction introuvable")
    
    services_transactions.delete_transaction(db, db_transaction)
    return {"message": "Transaction supprimée"}