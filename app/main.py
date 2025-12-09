from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles

from app.api import routes_transactions, routes_categories
from app.services import services_accueil, services_transactions
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

    return templates.TemplateResponse("home.html", {
        "request": request,
        "recent_transactions": recent
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
    return JSONResponse(content={"total_balance": total_balance})


@app.get("/api/recent-transactions")
def get_recent_transactions_api(db: Session = Depends(get_db)):
    recent_transactions = services_transactions.get_recent_transactions(db)
    return recent_transactions
