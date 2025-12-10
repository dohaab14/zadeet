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

from datetime import datetime, date, timedelta
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
    overview = transaction_service.get_transactions_overview(db)

    # 1. Récupérer les totaux des montants par category_id
    category_totals = transaction_service.get_total_amount_by_category(db)

    # 2. Enrichir la liste des catégories avec l'attribut total_amount
    categories_to_enrich = overview["categories"] 

    for cat in categories_to_enrich:
        # Ajout de l'attribut dynamique total_amount
        cat.total_amount = category_totals.get(cat.id, 0.0) 

    # 3. Assurez-vous que les transactions prennent en compte le filtre de recherche
    overview["transactions"] = transaction_service.get_transactions(db, search=search)

    return templates.TemplateResponse(
        "transactions.html",
        {
            "request": request,
            **overview,
            "search": search or "",
        }
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
# CRÉATION D’UNE TRANSACTION
# ---------------------------------------------------------
@router.post("/")
def create_transaction_from_form(
    label: str = Form(...),
    amount: float = Form(...),
    category_id: int | None = Form(None),
    date: str = Form(...),
    db: Session = Depends(get_db),
):
    # convertir "YYYY-MM-DD" en datetime
    date_obj = datetime.strptime(date, "%Y-%m-%d")

    data = TransactionCreate(
        label=label,
        amount=amount,
        category_id=category_id,
        date=date_obj,     # 🔥 date transférée au schéma
    )

    transaction_service.create_transaction(db, data)
    return RedirectResponse(url="/transactions/page", status_code=303)

# ---------------------------------------------------------
# SUPPRESSION
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
# MISE À JOUR VIA API (PUT)
# ---------------------------------------------------------
@router.put("/{transaction_id}", response_model=TransactionSchema)
def update_transaction(transaction_id: int, data: TransactionUpdate, db: Session = Depends(get_db)):
    txn = transaction_service.get_transaction(db, transaction_id)
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")

    return transaction_service.update_transaction(db, txn, data)

# ---------------------------------------------------------
# MISE À JOUR VIA FORMULAIRE (MODAL EDIT)
# ---------------------------------------------------------
@router.post("/{transaction_id}/update")
def update_transaction_from_form(
    transaction_id: int,
    label: str = Form(...),
    amount: float = Form(...),
    category_id: int | None = Form(None),
    date: str = Form(...),      # 🔥 maintenant récupérée
    db: Session = Depends(get_db),
):
    txn = transaction_service.get_transaction(db, transaction_id)
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")

    # convertir la date du formulaire
    date_obj = datetime.strptime(date, "%Y-%m-%d")

    data = TransactionUpdate(
        label=label,
        amount=amount,
        category_id=category_id,
        date=date_obj,   # 🔥 prise en compte
    )

    transaction_service.update_transaction(db, txn, data)
    return RedirectResponse(url="/transactions/page", status_code=303)

# ---------------------------------------------------------
# TRANSACTIONS PAR MOIS (API)
# ---------------------------------------------------------
@router.get("/monthly-transactions", response_model=List[TransactionSchema])
def get_transactions_by_month_api(year: int, month: int, db: Session = Depends(get_db)):
    return db.query(TransactionModel).filter(
        extract("year", TransactionModel.date) == year,
        extract("month", TransactionModel.date) == month,
    ).all()

# ---------------------------------------------------------
# RECENT TRANSACTIONS (API)
# ---------------------------------------------------------
@router.get("/recent-transactions", response_model=List[TransactionSchema])
def get_recent_transactions_api(limit: int = 3, db: Session = Depends(get_db)):
    return db.query(TransactionModel).order_by(TransactionModel.date.desc()).limit(limit).all()

# ---------------------------------------------------------
# FILTRE PAR CATÉGORIE / PÉRIODE
# ---------------------------------------------------------
@router.get("/filter")
def filter_transactions(
    category_id: int | None = None,
    period: str | None = "current_month",
    db: Session = Depends(get_db)
):
    query = db.query(TransactionModel).outerjoin(TransactionModel.category)
    today = date.today()

    if category_id:
        query = query.filter(TransactionModel.category_id == category_id)

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

    results = query.order_by(TransactionModel.date.desc()).all()

    return [
        {
            "label": t.label,
            "amount": t.amount,
            "date": t.date.strftime("%Y-%m-%d"),
            "category_name": t.category.name if t.category else "",
            "category_type": t.category.type if t.category else "depense"
        }
        for t in results
    ]