from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import extract, func
from typing import List, Optional

from app.db.database import SessionLocal
from app.db.models import Transaction as TransactionModel
from app.db.schemas import (
    Transaction as TransactionSchema,
    TransactionCreate,
    TransactionUpdate,
)
from app.services import services_transactions as transaction_service
from app.services import services_categories as category_service
from fastapi.templating import Jinja2Templates
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


router = APIRouter(prefix="/transactions", tags=["Transactions"])
templates = Jinja2Templates(directory="app/templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------
# PAGE HTML PRINCIPALE AVEC RECHERCHE
# ---------------------------------------------------------
@router.get("/page", response_class=HTMLResponse)
def transactions_page(
    request: Request,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Page HTML des transactions avec filtrage facultatif."""
    
    # Overview (stats globales)
    overview = transaction_service.get_transactions_overview(db)

    # Categories (mise à jour complète)
    overview["categories"] = category_service.get_categories(db)

    # Transactions filtrées
    filtered_txns = transaction_service.get_transactions(
        db=db,
        search=search,
    )
    overview["transactions"] = filtered_txns

    return templates.TemplateResponse(
        "transactions.html",
        {"request": request, **overview, "search": search or ""},
    )


# ---------------------------------------------------------
# API JSON – LISTE DES TRANSACTIONS
# ---------------------------------------------------------
@router.get("/", response_model=List[TransactionSchema])
def list_transactions(
    category_id: int | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    return transaction_service.get_transactions(
        db=db,
        category_id=category_id,
        search=search,
    )


# ---------------------------------------------------------
# CRÉATION DE TRANSACTION (FORMULAIRE)
# ---------------------------------------------------------
@router.post("/")
def create_transaction_from_form(
    label: str = Form(...),
    amount: float = Form(...),
    category_id: int | None = Form(None),
    date: str = Form(...),
    db: Session = Depends(get_db),
):
    data = TransactionCreate(
        label=label,
        amount=amount,
        category_id=category_id,
    )
    transaction_service.create_transaction(db, data)
    return RedirectResponse(url="/transactions/page", status_code=303)


# ---------------------------------------------------------
# SUPPRESSION VIA FORMULAIRE
# ---------------------------------------------------------
@router.post("/{transaction_id}")
def handle_transaction_form(
    transaction_id: int,
    method: str = Form(...),
    db: Session = Depends(get_db),
):
    if method.lower() != "delete":
        raise HTTPException(status_code=405, detail="Méthode non supportée")

    txn = transaction_service.get_transaction(db, transaction_id)
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")

    transaction_service.delete_transaction(db, txn)
    return RedirectResponse(url="/transactions/page", status_code=303)


# ---------------------------------------------------------
# API – MISE À JOUR
# ---------------------------------------------------------
@router.put("/{transaction_id}", response_model=TransactionSchema)
def update_transaction(
    transaction_id: int,
    data: TransactionUpdate,
    db: Session = Depends(get_db),
):
    txn = transaction_service.get_transaction(db, transaction_id)
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")

    return transaction_service.update_transaction(db, txn, data)


# ---------------------------------------------------------
# API – TRANSACTIONS PAR MOIS
# ---------------------------------------------------------
@router.get("/monthly-transactions", response_model=List[TransactionSchema])
def get_transactions_by_month_api(
    year: int,
    month: int,
    db: Session = Depends(get_db),
):
    return db.query(TransactionModel).filter(
        extract("year", TransactionModel.date) == year,
        extract("month", TransactionModel.date) == month,
    ).all()


# ---------------------------------------------------------
# API – TROIS DERNIÈRES TRANSACTIONS
# ---------------------------------------------------------
@router.get("/recent-transactions", response_model=List[TransactionSchema])
def get_recent_transactions_api(
    limit: int = 3,
    db: Session = Depends(get_db),
):
    return (
        db.query(TransactionModel)
        .order_by(TransactionModel.date.desc())
        .limit(limit)
        .all()
    )


# ajout du filtre par cartégoie et période ref au filtre de home.html

@router.get("/filter")
def filter_transactions(
    category_id: int | None = None,
    period: str | None = "current_month",
    db: Session = Depends(get_db)
):
    from datetime import date, timedelta
    from dateutil.relativedelta import relativedelta

    query = db.query(TransactionModel).outerjoin(TransactionModel.category)
    today = date.today()

    # Filtre catégorie
    if category_id:
        query = query.filter(TransactionModel.category_id == category_id)

    # Filtre période
    if period == "current_month":
        start = today.replace(day=1)
        query = query.filter(TransactionModel.date >= start)
    elif period == "last_month":
        start = (today.replace(day=1) - relativedelta(months=1))
        end = today.replace(day=1) - timedelta(days=1)
        query = query.filter(TransactionModel.date.between(start, end))
    elif period == "last_3_months":
        start = today - relativedelta(months=3)
        query = query.filter(TransactionModel.date >= start)
    elif period == "all":
        pass

    results = query.order_by(TransactionModel.date.desc()).all()

    # Générer un JSON sûr pour le JS
    output = []
    for t in results:
        output.append({
            "label": t.label,
            "amount": t.amount,
            "date": t.date.strftime("%Y-%m-%d"),
            "category_name": t.category.name if t.category else "",
            "category_type": t.category.type if t.category else "depense"
        })
    return output

