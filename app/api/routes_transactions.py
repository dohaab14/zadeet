"""
Utilisation ici des données via schemas.py pour gérer les routes liées aux transactions
"""

from fastapi import APIRouter, Depends, HTTPException,Form
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.schemas import Transaction, TransactionCreate, TransactionUpdate
from sqlalchemy import extract
from app.db import models
from typing import List
from app.services import services_transactions as transaction_service
from app.services import services_categories as category_service
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from fastapi.responses import HTMLResponse
from fastapi import Request

router = APIRouter(prefix="/transactions", tags=["Transactions"])
templates = Jinja2Templates(directory="app/templates")


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
    return transaction_service.get_transactions(db, category_id)


# ---------------------------------------------------------------------

# routes_transactions.py

@router.post("/")
def create_transaction_from_form(
    label: str = Form(...),
    amount: float = Form(...),
    category_id: int | None = Form(None),
    date: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Crée une nouvelle transaction depuis le formulaire HTML.
    Pour l'instant, on ignore la date envoyée et on utilise la date par défaut côté modèle.
    """
    data = TransactionCreate(
        label=label,
        amount=amount,
        category_id=category_id,
    )

    transaction_service.create_transaction(db, data)

    # Après création, on revient sur la page des transactions
    return RedirectResponse(
        url="/transactions/transactions-page",
        status_code=303,
    )



# ---------------------------------------------------------------------

@router.put("/{transaction_id}", response_model=Transaction)
def update_transaction(transaction_id: int, data: TransactionUpdate, db: Session = Depends(get_db)):
    """
    Met à jour une transaction existante
    """
    txn = transaction_service.get_transaction(db, transaction_id)

    if not txn:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")

    return transaction_service.update_transaction(db, txn, data)


# ---------------------------------------------------------------------

@router.delete("/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """
    Supprime une transaction existante"""
    txn = transaction_service.get_transaction(db, transaction_id)

    if not txn:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")

    transaction_service.delete_transaction(db, txn)
    return RedirectResponse(url="/transactions/transactions-page", status_code=303)

@router.post("/{transaction_id}")
def handle_transaction_form(
    transaction_id: int,
    method: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Gère les formulaires HTML envoyés sur /transactions/{id}.
    Pour l'instant, on ne gère que la suppression via method=delete.
    """
    if method.lower() == "delete":
        txn = transaction_service.get_transaction(db, transaction_id)
        if not txn:
            raise HTTPException(status_code=404, detail="Transaction non trouvée")

        transaction_service.delete_transaction(db, txn)
        return RedirectResponse(
            url="/transactions/transactions-page",
            status_code=303,
        )

    # Si on tombe ici, _method n'est pas géré
    raise HTTPException(status_code=405, detail="Méthode de formulaire non supportée")


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


# -------------------------------------------------------------------
@router.get("/transactions-page", response_class=HTMLResponse)
def transactions_page(request: Request, db: Session = Depends(get_db)):
    overview = transaction_service.get_transactions_overview(db)
    return templates.TemplateResponse("transactions.html", {
        "request": request,
        **overview
    })