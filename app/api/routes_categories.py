from http.client import HTTPException
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.schemas import Category, CategoryCreate, CategoryUpdate
from app.services import services_categories as category_service
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/categories", tags=["Categories"])


def get_db():
    """
    Obtention d'une session de base de données
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@router.get("/", response_model=List[Category])
def list_categories(db: Session = Depends(get_db)):
    """
    Docstring pour list_categories
    
    :param db: Description
    :type db: Session
    """
    return category_service.get_categories(db)


@router.post("/", response_model=Category)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """
    Docstring pour create_category
    
    :param category: Description
    :type category: CategoryCreate
    :param db: Description
    :type db: Session
    """
    return category_service.create_category(db, category)


@router.put("/{category_id}", response_model=Category)
def update_category(category_id: int, category: CategoryUpdate, db: Session = Depends(get_db)):
    """
    Docstring pour update_category
    
    :param category_id: Description
    :type category_id: int
    :param category: Description
    :type category: CategoryUpdate
    :param db: Description
    :type db: Session
    """
    updated = category_service.update_category(db, category_id, category)
    if not updated:
        raise HTTPException(status_code=404, detail="Catégorie non trouvée")
    return updated


@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """
    Docstring pour delete_category
    
    :param category_id: Description
    :type category_id: int
    :param db: Description
    :type db: Session
    """
    success = category_service.delete_category(db, category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Catégorie non trouvée")
    return {"ok": True}


@router.get("/page", response_class=HTMLResponse)
def categories_page(request: Request, db: Session = Depends(get_db)):
    """
    Docstring pour categories_page
    
    :param request: Description
    :type request: Request
    :param db: Description
    :type db: Session
    """
    categories = category_service.get_categories(db)
    return templates.TemplateResponse("categories.html", {"request": request, "categories": categories})