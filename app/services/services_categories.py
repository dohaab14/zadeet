from app.db import models
from sqlalchemy.orm import Session

def get_categories(db: Session):
    return db.query(models.Category).all()
