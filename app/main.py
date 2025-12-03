# main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db import models
from app.services import services_accueil , services_transaction
from fastapi.responses import JSONResponse

app = FastAPI()

# Dépendance pour avoir la BDD dans chaque route
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API Budget Team 6 !"}

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
