from app.db import models
from app.db.schemas import CategoryCreate, CategoryUpdate
from sqlalchemy.orm import Session

def get_categories(db: Session):
    return db.query(models.Category).all()


def create_category(db: Session, category: CategoryCreate) -> models.Category:
    """
    Docstring pour create_category
    
    :param db: Description
    :type db: Session
    :param category: Description
    :type category: CategoryCreate
    :return: Description
    :rtype: models.Category
    """
    db_category = models.Category(
        name=category.name,
        type=category.type,
        parent_id=category.parent_id
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def update_category(db: Session, category_id: int, category: CategoryUpdate) -> models.Category | None: 
    """
    Docstring pour update_category
    
    :param db: Description
    :type db: Session
    :param category_id: Description
    :type category_id: int
    :param category: Description
    :type category: CategoryUpdate
    :return: Description
    :rtype: models.Category | None
    """
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not db_category:
        return None

    if category.name is not None:
        db_category.name = category.name
    if category.type is not None:
        db_category.type = category.type
    if category.parent_id is not None:
        db_category.parent_id = category.parent_id

    db.commit()
    db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int) -> bool:
    """
    Docstring pour delete_category
    
    :param db: Description
    :type db: Session
    :param category_id: Description
    :type category_id: int
    :return: Description
    :rtype: bool
    """
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        return False
    db.delete(category)
    db.commit()
    return True


def get_categories_par_depense(db: Session) -> list[dict]:
    """
    Docstring pour get_categories_par_depense
    
    :param db: Description
    :type db: Session
    :return: Description
    :rtype: list[dict]
    """
    categories = db.query(models.Category).all()
    result = []
    for c in categories:
        #calule des depenses totales pour les categories et sous-scategories
        total = sum(t.amount for t in c.transactions)
        for sub in c.subcategories:
            total += sum(t.amount for t in sub.transactions)
        result.append({
            "id": c.id,
            "name": c.name,
            "type": c.type,
            "subcategories": c.subcategories,
            "transactions": c.transactions,
            "spent": total
        })
    return result



