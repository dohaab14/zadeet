from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import List
from fastapi import Depends

from app.routes import routes_transactions  # ton router transactions
from app.services import services_accueil, services_transactions
from app.schemas import Transaction

templates = Jinja2Templates(directory="app/templates")

app = FastAPI()


app.include_router(routes_transactions.router)



@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    """
    Page d'accueil / dashboard.
    Récupère les 3 dernières transactions via le service existant,
    sans accéder directement à la DB depuis main.py.
    """
    # On appelle le service pour récupérer les transactions
    recent: List[Transaction] = services_transactions.get_recent_transactions(limit=3)

    return templates.TemplateResponse("home.html", {
        "request": request,
        "recent_transactions": recent
    })


# -------------------------------------------------------------------

@app.get("/api/dashboard-charts")
def get_charts_data():
    """
    Retourne les données pour les graphiques du dashboard.
    """
    # Graphique bâtons (3 derniers mois)
    bar_data = services_accueil.get_last_3_months_stats()
    # Graphique camembert (parents + détails)
    pie_data = services_accueil.get_category_pie_stats()

    return {
        "bar_chart": bar_data,
        "pie_chart": pie_data
    }


# -------------------------------------------------------------------

@app.get("/api/total-balance")
def get_total_balance():
    """
    Retourne le solde total
    """
    total_balance = services_accueil.get_total_balance()
    return JSONResponse(content={"total_balance": total_balance})
