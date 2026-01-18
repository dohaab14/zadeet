import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# On importe les routeurs situés dans backend/api/
from .api import back_routes_transactions, back_routes_categories, back_routes_acc

from .db import models          
from .db.database import engine 

# Création automatique des tables si elles n'existent pas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Zadeet API")

# --- CONFIGURATION CORS ---
origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://localhost:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- INCLUSION DES ROUTES ---
app.include_router(back_routes_transactions.router)
app.include_router(back_routes_categories.router)
app.include_router(back_routes_acc.router)

# --- ROUTE DE VÉRIFICATION ---
@app.get("/api/health")
def read_root():
    return {"status": "online", "message": "API Zadeet fonctionnelle"}
    
