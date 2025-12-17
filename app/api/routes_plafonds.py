from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request # Ajout de HTTPException et Request
from sqlalchemy.orm import Session

# Attention : SessionLocal DOIT être importé du fichier où il est défini (database.py)
from app.db.database import SessionLocal # Assurez-vous que c'est le bon chemin
from app.db.schemas import Category, CategoryCreate, CategoryUpdate
# Assurez-vous que les services sont importables
from app.services import services_categories, services_transactions, services_accueil 

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

# -------------------------------------------------------------
# DÉPENDANCE DE BASE DE DONNÉES
# -------------------------------------------------------------

# L'initialisation doit être faite en dehors de la fonction get_db (probablement dans database.py)
# Si SessionLocal est défini dans database.py, l'import ci-dessus est correct.

def get_db():
    """Dépendance FastAPI pour obtenir une session de DB."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------------------------------------------
# INITIALISATION DU ROUTEUR ET DES TEMPLATES
# -------------------------------------------------------------
templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/categories", tags=["Categories"])


# =============================================================
# ROUTES VUES HTML (ACCUEIL)
# =============================================================

@router.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    """Affiche la page d'accueil du budget (accessible via /categories)."""
    
    # NOTE: Ces services ne sont pas liés aux 'categories', ils devraient 
    # normalement se trouver dans un routeur 'accueil' ou 'dashboard'.
    recent = services_transactions.get_recent_transactions(db, limit=3)
    categories = services_categories.get_categories(db)
    
    return templates.TemplateResponse("home.html", {
        "request": request,
        "recent_transactions": recent,
        "categories": categories
    })


# =============================================================
# ROUTES API POUR LE DASHBOARD (Doivent utiliser le prefixe /categories)
# =============================================================

# Le chemin final sera : /categories/api/dashboard-charts
@router.get("/api/dashboard-charts")
def get_charts_data(db: Session = Depends(get_db)):
    """Récupère les données pour les graphiques du tableau de bord."""
    bar_data = services_accueil.get_last_3_months_stats(db)
    pie_data = services_accueil.get_category_pie_stats(db)
    return {
        "bar_chart": bar_data,
        "pie_chart": pie_data
    }


# Le chemin final sera : /categories/api/total-balance
@router.get("/api/total-balance")
def get_total_balance(db: Session = Depends(get_db)):
    """Récupère le solde total."""
    total_balance = services_accueil.get_total_balance(db)
    return {
        "total_balance": total_balance or 0.0
    }


# Le chemin final sera : /categories/api/recent-transactions
@router.get("/api/recent-transactions")
def get_recent_transactions_api(db: Session = Depends(get_db)):
    """Récupère les transactions récentes."""
    recent_transactions = services_transactions.get_recent_transactions(db)
    return recent_transactions