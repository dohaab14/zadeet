from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import List
from sqlalchemy.orm import Session

from app.api import routes_transactions,routes_categories
from app.services import services_accueil, services_transactions
from app.db.schemas import Transaction
from app.db.database import SessionLocal  

templates = Jinja2Templates(directory="app/templates")

app = FastAPI()

app.include_router(routes_transactions.router)
app.include_router(routes_categories.router)

def get_db():
    """
    Fournit une session de DB pour les dépendances
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    """
    Page d'accueil / dashboard.
    Récupère les 3 dernières transactions via le service et la DB.
    """
    recent: List[Transaction] = services_transactions.get_recent_transactions(db, limit=3)

    return templates.TemplateResponse("home.html", {
        "request": request,
        "recent_transactions": recent
    })


# -------------------------------------------------------------------

@app.get("/api/dashboard-charts")
def get_charts_data(db: Session = Depends(get_db)):
    """
    Retourne les données pour les graphiques du dashboard.
    """
    # Graphique bâtons (3 derniers mois)
    bar_data = services_accueil.get_last_3_months_stats(db)
    # Graphique camembert (parents + détails)
    pie_data = services_accueil.get_category_pie_stats(db)

    return {
        "bar_chart": bar_data,
        "pie_chart": pie_data
    }


# -------------------------------------------------------------------

@app.get("/api/total-balance")
def get_total_balance(db: Session = Depends(get_db)):
    """
    Retourne le solde total
    """
    total_balance = services_accueil.get_total_balance(db)
    return JSONResponse(content={"total_balance": total_balance})
