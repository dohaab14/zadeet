from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.schemas import Category
from app.services import services_categories as category_service

router = APIRouter(prefix="/categories", tags=["Categories"])


def get_db():
    """
    Obtention d'une session de base de données
    (même pattern que dans routes_transactions.py)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[Category])
def list_categories(db: Session = Depends(get_db)):
    """
    Renvoie la liste des catégories au format JSON.
    """
    return category_service.get_categories(db)
