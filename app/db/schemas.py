from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List

# ==========================================
# 1. BASE SCHEMAS (STANDARD CRUD)
# ==========================================

class CategoryBase(BaseModel):
    name: str
    type: str
    parent_id: Optional[int] = None
    # J'ajoute le plafond (monthly_cap) ici car il dépend de la catégorie (Logique BDD)
    monthly_cap: float = Field(0.0, ge=0, description="Monthly spending limit")


class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category (name, type, or cap)."""
    name: Optional[str] = None
    type: Optional[str] = None
    parent_id: Optional[int] = None
    monthly_cap: Optional[float] = None


class Category(CategoryBase):
    """Standard API response schema."""
    id: int
    subcategories: List["Category"] = [] 
    transactions: List["Transaction"] = []

    class Config:
        from_attributes = True


class TransactionBase(BaseModel):
    label: str
    amount: float
    category_id: Optional[int] = None


class TransactionCreate(TransactionBase):
    date: datetime 


class TransactionUpdate(BaseModel):
    label: Optional[str] = None
    amount: Optional[float] = None
    category_id: Optional[int] = None
    date: Optional[datetime] = None


class Transaction(TransactionBase):
    id: int
    date: datetime

    class Config:
        from_attributes = True


# ==========================================
# 2. SPECIFIC SCHEMAS (Translatés de ton code)
# ==========================================

# Correspond à ton "PlafondUpdateSchema"
class CapUpdateSchema(BaseModel):
    """
    Input schema to update only the cap/limit of a category.
    """
    monthly_cap: float = Field(..., ge=0, description="New value for the monthly cap.")


# Correspond à ton "CategorieSchema" (version enrichie pour l'affichage)
class CategoryStatsSchema(BaseModel):
    """
    Output schema for a category including stats (spent vs cap).
    """
    # Adaptation de ton alias "nom_technique" -> "id"
    id: str = Field(..., alias="nom_technique", description="Technical ID for frontend.")
    
    name: str = Field(..., description="Display name of the category.")
    monthly_cap: float = Field(..., description="Monthly cap set.")
    spent: float = Field(..., description="Total spent amount.")
    
    class Config:
        from_attributes = True
        populate_by_name = True


# Correspond à ton "MoisDataSchema"
class MonthDataSchema(BaseModel):
    """
    Output schema for a full month view.
    """
    name: str = Field(..., description="Full name of the month (e.g. 'December 2025').")
    
    categories: List[CategoryStatsSchema] = Field(..., description="List of categories for this month.")
    
    class Config:
        from_attributes = True

# Résolution des références circulaires pour Category
Category.model_rebuild()