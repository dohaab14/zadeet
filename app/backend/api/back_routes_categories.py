from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from ..db.database import SessionLocal
from ..services import services_categories
from ..db import schemas

router = APIRouter(prefix="/api/categories", tags=["Categories"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[schemas.Category])
def get_categories_tree(db: Session = Depends(get_db)):
    """
    Renvoie l'arbre des catégories (Parents incluant leurs sous-catégories).
    Le frontend utilisera ça pour construire le <select> hiérarchique.
    """
    return services_categories.get_categories(db)