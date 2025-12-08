from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import extract
from typing import List
from typing import Optional

from app.db.database import SessionLocal
from app.db.models import Transaction as TransactionModel   # <-- FIX 1 : alias modèle SQLA
from app.db.schemas import Transaction as TransactionSchema # <-- FIX 1 : alias schéma Pydantic
from app.db.schemas import TransactionCreate, TransactionUpdate

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


# ---------------------------------------------------------
# PAGE HTML PRINCIPALE
# ---------------------------------------------------------

@router.get("/page", response_class=HTMLResponse)
def transactions_page(
    request: Request,
    search: Optional[str] = None,          # <-- récupère ?search=...
    db: Session = Depends(get_db),
):
    """
    Affiche la page HTML des transactions avec aperçu et stats,
    avec possibilité de filtrer par nom de dépense.
    """
    # 1) Récupérer l'overview (totaux, etc.)
    overview = transaction_service.get_transactions_overview(db)

    # 2) Forcer la liste des catégories à être complète
    categories = category_service.get_categories(db)
    overview["categories"] = categories

    # 3) Récupérer les transactions FILTRÉES
    filtered_txns = transaction_service.get_transactions(
        db=db,
        search=search,   # <-- ICI on passe bien le search
    )
    overview["transactions"] = filtered_txns  

    # 4) Passer 'search' au template pour pré-remplir l'input
    return templates.TemplateResponse(
        "transactions.html",
        {
            "request": request,
            **overview,
            "search": search or "",
        }
    )

# ---------------------------------------------------------
# API JSON : toutes les transactions
# ---------------------------------------------------------
@router.get("/", response_model=List[TransactionSchema])
def list_transactions(category_id: int | None = None, db: Session = Depends(get_db)):
    return transaction_service.get_transactions(db, category_id,search=search,)


# ---------------------------------------------------------
# CRÉATION FORMULAIRE (depuis modal)
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
        category_id=category_id
    )
    transaction_service.create_transaction(db, data)
    return RedirectResponse(url="/transactions/page", status_code=303)


# ---------------------------------------------------------
# FORMULAIRE DE SUPPRESSION
# ---------------------------------------------------------
@router.post("/{transaction_id}")
def handle_transaction_form(transaction_id: int, method: str = Form(...), db: Session = Depends(get_db)):

    if method.lower() != "delete":
        raise HTTPException(status_code=405, detail="Méthode non supportée")

    txn = transaction_service.get_transaction(db, transaction_id)
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")

    transaction_service.delete_transaction(db, txn)
    return RedirectResponse(url="/transactions/page", status_code=303)


# ---------------------------------------------------------
# MISE À JOUR API
# ---------------------------------------------------------
@router.put("/{transaction_id}", response_model=TransactionSchema)
def update_transaction(transaction_id: int, data: TransactionUpdate, db: Session = Depends(get_db)):
    txn = transaction_service.get_transaction(db, transaction_id)
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")
    return transaction_service.update_transaction(db, txn, data)


# ---------------------------------------------------------
# API PAR MOIS
# ---------------------------------------------------------
@router.get("/monthly-transactions", response_model=List[TransactionSchema])
def get_transactions_by_month_api(year: int, month: int, db: Session = Depends(get_db)):
    return db.query(TransactionModel).filter(
        extract('year', TransactionModel.date) == year,
        extract('month', TransactionModel.date) == month
    ).all()


# ---------------------------------------------------------
# API DERNIÈRES TRANSACTIONS
# ---------------------------------------------------------
@router.get("/recent-transactions", response_model=List[TransactionSchema])
def get_recent_transactions_api(limit: int = 3, db: Session = Depends(get_db)):
    return db.query(TransactionModel).order_by(TransactionModel.date.desc()).limit(limit).all()
