from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db.database import SessionLocal
from ..services import services_accueil

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    return {
        "balance": services_accueil.get_total_balance(db),
        "charts": {
            "bar": services_accueil.get_last_3_months_stats(db),
            "pie": services_accueil.get_category_pie_stats(db),
        },
        "category_totals": services_accueil.get_category_totals(db),
    }

@router.get("/category-totals/")
def get_dashboard_category_totals(
    period: str = "current_month",
    category_id: int | None = None,
    db: Session = Depends(get_db),
):
    return services_accueil.get_category_totals_filtered(db, period, category_id)
