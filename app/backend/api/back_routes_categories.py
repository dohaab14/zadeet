from fastapi import APIRouter, Depends, HTTPException, status
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
def list_categories(db: Session = Depends(get_db)):
    """Affiche toutes les catégories (incluant l'arbre hiérarchique)"""
    return services_categories.get_categories(db)

@router.post("/", response_model=schemas.Category, status_code=status.HTTP_201_CREATED)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    """Crée une nouvelle catégorie ou sous-catégorie"""
    return services_categories.create_category(db, category)


@router.put("/{category_id}", response_model=schemas.Category)
def update_category(category_id: int, category: schemas.CategoryUpdate, db: Session = Depends(get_db)):
    updated = services_categories.update_category(db, category_id, category)
    if not updated:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Catégorie non trouvée")
    return updated

@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    success = services_categories.delete_category(db, category_id)
    if not success:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Catégorie non trouvée")
    return {"message": "Supprimé avec succès"}