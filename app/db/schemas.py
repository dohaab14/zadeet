"""
Ce fichier définit les schémas Pydantic pour la validation et la sérialisation
des données (Pydantic V2 syntaxe).
"""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List

# ==============================================================================
# 1. CATEGORIES (CRUD Standard & Plafonds)
# ==============================================================================

class CategoryBase(BaseModel):
    name: str
    type: str
    parent_id: Optional[int] = None
    # Intégration du plafond (Cap)
    monthly_cap: float = Field(0.0, ge=0, description="Monthly spending limit")


class CategoryCreate(CategoryBase):
    """Schéma utilisé pour créer une nouvelle catégorie."""
    pass


class CategoryUpdate(BaseModel):
    """Schéma pour modification partielle (inclut la mise à jour du plafond)."""
    name: Optional[str] = None
    type: Optional[str] = None
    parent_id: Optional[int] = None
    monthly_cap: Optional[float] = None


class Category(CategoryBase):
    """
    Schéma renvoyé dans les réponses API (lecture DB).
    Permet d'inclure les relations (sous-catégories et transactions).
    """
    id: int
    subcategories: List["Category"] = [] 
    transactions: List["Transaction"] = [] # Référence à la classe Transaction ci-dessous

    class Config:
        from_attributes = True # Syntaxe Pydantic V2


# ==============================================================================
# 2. TRANSACTIONS (CRUD Standard)
# ==============================================================================

class TransactionBase(BaseModel):
    label: str
    amount: float
    category_id: Optional[int] = None


class TransactionCreate(TransactionBase):
    """Schéma utilisé pour créer une transaction, inclut la date."""
    date: datetime 


class TransactionUpdate(BaseModel):
    """Mise à jour partielle d'une transaction."""
    label: Optional[str] = None
    amount: Optional[float] = None
    category_id: Optional[int] = None
    date: Optional[datetime] = None


class Transaction(TransactionBase):
    """Schéma renvoyé par l'API pour une transaction (lecture DB)."""
    id: int
    date: datetime

    class Config:
        from_attributes = True


# ==============================================================================
# 3. SCHÉMAS SPÉCIFIQUES & ANALYTIQUES
# ==============================================================================

class CapUpdateSchema(BaseModel):
    """Schéma d'entrée pour modifier uniquement le plafond."""
    monthly_cap: float = Field(..., ge=0, description="New value for the monthly cap.")


class CategoryStatsSchema(BaseModel):
    """
    Schéma de sortie enrichi pour l'affichage (inclut les dépenses calculées).
    """
    # L'alias permet de mapper l'attribut de la DB (ex: nom_technique) à l'ID de l'API
    id: str = Field(..., alias="nom_technique", description="Technical ID for frontend.")
    
    name: str = Field(..., description="Display name of the category.")
    monthly_cap: float = Field(..., description="Monthly cap set.")
    spent: float = Field(..., description="Total spent amount.")
    
    class Config:
        from_attributes = True
        populate_by_name = True # Permet d'initialiser via 'id' ou 'nom_technique'


class MonthDataSchema(BaseModel):
    """Schéma de sortie pour une vue complète du mois (tableau de bord)."""
    name: str = Field(..., description="Full name of the month (e.g. 'December 2025').")
    
    categories: List[CategoryStatsSchema] = Field(..., description="Liste des catégories de dépenses pour ce mois.")
    
    class Config:
        from_attributes = True


# ==============================================================================
# RÉSOLUTION DES RÉFÉRENCES CIRCULAIRES
# ==============================================================================
# Nécessaire pour les relations récursives (Category -> List[Category])
Category.model_rebuild()