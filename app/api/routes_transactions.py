from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.api.deps import get_db
from app.services.transaction_service import (
    list_transactions,
    create_transaction,
    delete_transaction,
    total_expenses,
)
from app.services.category_service import list_categories
from app.schemas.transactions import TransactionCreate

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/", response_class=HTMLResponse)
def transactions_page(
    request: Request,
    db: Session = Depends(get_db),
):
    transactions = list_transactions(db)
    categories = list_categories(db)

    stats = {
        "total_expenses": total_expenses(db),
        "total_categories": len(categories),
        "total_transactions": len(transactions),
    }

    return templates.TemplateResponse(
        "transactions.html",
        {
            "request": request,
            "transactions": transactions,
            "categories": categories,
            **stats,
        },
    )


@router.post("/")
def add_transaction(
    request: Request,
    amount: float = Form(...),
    category_id: Optional[int] = Form(None),
    date_str: str = Form(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    tx_date = date.fromisoformat(date_str)

    data = TransactionCreate(
        amount=amount,
        is_expense=True,  # cette page ne gère que des dépenses
        category_id=category_id if category_id not in (None, 0, "") else None,
        date=tx_date,
        description=description,
    )
    create_transaction(db, data)
    return RedirectResponse(url="/transactions/", status_code=303)


@router.post("/{tx_id}/delete")
def remove_transaction(
    tx_id: int,
    db: Session = Depends(get_db),
):
    delete_transaction(db, tx_id)
    return RedirectResponse(url="/transactions/", status_code=303)
