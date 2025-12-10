"""
Ce fichier définit les schémas Pydantic utilisés pour valider les données
entrantes (POST, PUT) et les données sortantes (réponses API).

Les schémas permettent d’éviter d’exposer directement la structure de la base
de données et d’assurer une validation automatique des données.
"""

from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List


class CategoryBase(BaseModel):
    name: str
    type: str
    parent_id: Optional[int] = None
    # J'ajoute le plafond (monthly_cap) ici car il dépend de la catégorie (Logique BDD)
    monthly_cap: float = Field(0.0, ge=0, description="Monthly spending limit")


class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""


class CategoryCreate(CategoryBase):
    """
    Schéma utilisé pour créer une nouvelle catégorie.
    """
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category (name, type, or cap)."""
    name: Optional[str] = None
    type: Optional[str] = None
    parent_id: Optional[int] = None
    monthly_cap: Optional[float] = None


class Category(CategoryBase):
    """Standard API response schema."""
    """
    Schéma utilisé pour modifier une catégorie existante.
    Tous les champs sont optionnels pour permettre des mises à jour partielles.
    """
    name: Optional[str] = None
    type: Optional[str] = None
    parent_id: Optional[int] = None


class Category(CategoryBase):
    """
    Schéma renvoyé dans les réponses API.
    Ajoute l'id et permet d’inclure les sous-catégories et transactions.
    
    """
    id: int
    subcategories: List["Category"] = [] 
    transactions: List["Transaction"] = []

    class Config:
        from_attributes = True
        orm_mode = True


class TransactionBase(BaseModel):
    label: str
    amount: float
    category_id: Optional[int] = None


class TransactionCreate(TransactionBase):
    category_id: int | None = None



class TransactionCreate(TransactionBase):
    """
    Schéma utilisé pour créer une transaction.
    """
    date: datetime 


class TransactionUpdate(BaseModel):
    """
    Mise à jour partielle d'une transaction.
    """
    label: Optional[str] = None
    amount: Optional[float] = None
    category_id: Optional[int] = None
    date: Optional[datetime] = None


class Transaction(TransactionBase):
    """
    Schéma renvoyé par l'API.
    """
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
        orm_mode = True
