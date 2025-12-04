# main.py
from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db import models
from app.services import services_accueil , services_transaction

from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")

app = FastAPI()

# Dépendance pour avoir la BDD dans chaque route
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    """
    Affiche la page Dashboard HTML au lieu d'un JSON.
    """
    # 1. On récupère les 3 dernières transactions pour l'aperçu en bas de page
    recent = services_transaction.get_recent_transactions(db, limit=3)

    # 2. On retourne le template HTML avec les données (Contexte)
    return templates.TemplateResponse("home.html", {
        "request": request,                  # Obligatoire pour Jinja2
        "recent_transactions": recent        # Nos données pour la boucle HTML
    })



@app.get("/transactions")
def get_transactions(db: Session = Depends(get_db)):
    return db.query(models.Transaction).all()

@app.get("/api/dashboard-charts")
def get_charts_data(db: Session = Depends(get_db)):
    # 1. Données Graphique Bâtons (3 mois)
    bar_data = services_accueil.get_last_3_months_stats(db)
    
    # 2. Données Camembert (Parents + Détails)
    pie_data = services_accueil.get_category_pie_stats(db)
    
    return {
        "bar_chart": bar_data,
        "pie_chart": pie_data
    }

@app.get("/api/total-balance")
def get_total_balance(db: Session = Depends(get_db)):
    total_balance = services_accueil.get_total_balance(db)
    return JSONResponse(content={"total_balance": total_balance})

@app.get("/api/recent-transactions")
def get_recent_transactions(db: Session = Depends(get_db)):
    recent_transactions = services_transactions.get_recent_transactions(db)
    return recent_transactions
