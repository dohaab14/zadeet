# main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
import app.db.models

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