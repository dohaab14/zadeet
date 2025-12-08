from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import extract
from typing import List

from app.db.database import SessionLocal
from app.db.models import Transaction
from app.db.schemas import Transaction, TransactionCreate, TransactionUpdate
from app.services import services_transactions as transaction_service
from app.services import services_categories as category_service
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/transactions", tags=["Transactions"])
templates = Jinja2Templates(directory="app/templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_class=HTMLResponse)
def transactions_page(request: Request, db: Session = Depends(get_db)):
    overview = transaction_service.get_transactions_overview(db)
    return templates.TemplateResponse("transactions.html", {
        "request": request,
        **overview
    })

"""@router.get("/", response_model=List[Transaction])
def list_transactions(category_id: int | None = None, db: Session = Depends(get_db)):
    return transaction_service.get_transactions(db, category_id)
"""



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
        category_id=category_id
    )
    transaction_service.create_transaction(db, data)
    return RedirectResponse(url="/transactions/page", status_code=303)


@router.post("/{transaction_id}")
def handle_transaction_form(transaction_id: int, method: str = Form(...), db: Session = Depends(get_db)):
    """
    Gère les formulaires HTML envoyés sur /transactions/{id}.
    Pour l'instant, on ne gère que la suppression via method=delete.
    """
    if method.lower() != "delete":
        raise HTTPException(status_code=405, detail="Méthode non supportée")

    txn = transaction_service.get_transaction(db, transaction_id)
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")

    transaction_service.delete_transaction(db, txn)
    return RedirectResponse(url="/transactions/page", status_code=303)


@router.put("/{transaction_id}", response_model=Transaction)
def update_transaction(transaction_id: int, data: TransactionUpdate, db: Session = Depends(get_db)):
    txn = transaction_service.get_transaction(db, transaction_id)
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")
    return transaction_service.update_transaction(db, txn, data)


@router.get("/monthly-transactions", response_model=List[Transaction])
def get_transactions_by_month_api(year: int, month: int, db: Session = Depends(get_db)):
    return db.query(Transaction).filter(
        extract('year', Transaction.date) == year,
        extract('month', Transaction.date) == month
    ).all()


@router.get("/recent-transactions", response_model=List[Transaction])
def get_recent_transactions_api(limit: int = 3, db: Session = Depends(get_db)):
    return db.query(Transaction).order_by(Transaction.date.desc()).limit(limit).all()
