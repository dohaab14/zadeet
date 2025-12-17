import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# On importe les routeurs situés dans backend/api/
from .api import back_routes_transactions, back_routes_categories, back_routes_acc

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
    

# 1. On récupère le chemin absolu du dossier où se trouve ce fichier main.py
# Exemple : /home/aude/Bureau/test/app/backend
backend_dir = os.path.dirname(os.path.abspath(__file__))

# 2. On reconstruit le chemin vers le dossier 'frontend' proprement
# On remonte d'un cran (..) pour sortir de 'backend', puis on va dans 'frontend'
frontend_dir = os.path.join(backend_dir, "../frontend")

# 3. MONTAGE DES FICHIERS STATIQUES
# Il faut monter JS et STATIC (CSS) avant le ROOT "/" sinon ils seront masqués

# Pour que <script src="/js/app.js"> fonctionne :
app.mount("/js", StaticFiles(directory=os.path.join(frontend_dir, "js")), name="js")

# Pour que <link href="/static/style.css"> fonctionne :
app.mount("/static", StaticFiles(directory=os.path.join(frontend_dir, "static")), name="static_files")

# Pour servir les pages HTML (templates) à la racine "/"
# ATTENTION : Doit toujours être en dernier car il capture tout le reste
app.mount("/", StaticFiles(directory=os.path.join(frontend_dir, "templates"), html=True), name="templates")