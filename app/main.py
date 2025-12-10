from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import du router depuis ton dossier api/routes.py
#from app.api.routes_plafonds import router as api_router

# Initialisation
app = FastAPI(
    title="Gestion de Budget API",
    version="1.0.0"
)

# Configuration CORS (Indispensable pour que ton HTML parle à l'API)
origins = ["*"] # Pour le dev, on accepte tout. En prod, mets l'URL de ton site.

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- INCLUSION DU ROUTER ---
# On ajoute le préfixe "/api" ici. 
# Donc les routes deviennent /api/data/... et /api/plafond/...
#app.include_router(api_router, prefix="/api")

# Route racine pour tester
@app.get("/")
async def root():
    return {"message": "API en ligne. Routes disponibles sous /api/"}
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles

from app.api import routes_transactions, routes_categories
from app.services import services_accueil, services_transactions, services_categories
from app.db.database import SessionLocal

templates = Jinja2Templates(directory="app/templates")
app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(routes_transactions.router)
app.include_router(routes_categories.router)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    recent = services_transactions.get_recent_transactions(db, limit=3)
    categories = services_categories.get_categories(db)
    return templates.TemplateResponse("home.html", {
        "request": request,
        "recent_transactions": recent,
        "categories": categories
    })


@app.get("/api/dashboard-charts")
def get_charts_data(db: Session = Depends(get_db)):
    bar_data = services_accueil.get_last_3_months_stats(db)
    pie_data = services_accueil.get_category_pie_stats(db)
    return {
        "bar_chart": bar_data,
        "pie_chart": pie_data
    }


@app.get("/api/total-balance")
def get_total_balance(db: Session = Depends(get_db)):
    total_balance = services_accueil.get_total_balance(db)
    return {
        "total_balance": total_balance or 0.0
    }


@app.get("/api/recent-transactions")
def get_recent_transactions_api(db: Session = Depends(get_db)):
    recent_transactions = services_transactions.get_recent_transactions(db)
    return recent_transactions
