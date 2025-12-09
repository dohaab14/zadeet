"""
Ce fichier définit les schémas Pydantic utilisés pour valider les données
entrantes (POST, PUT) et les données sortantes (réponses API).

Les schémas permettent d’éviter d’exposer directement la structure de la base
de données et d’assurer une validation automatique des données.
"""

from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

#TODO: ajouter les schémas pour les plafonds


class CategoryBase(BaseModel):
    name: str
    type: str
    parent_id: Optional[int] = None


class CategoryCreate(CategoryBase):
    """
    Schéma utilisé pour créer une nouvelle catégorie.
    """
    pass


class CategoryUpdate(BaseModel):
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
        orm_mode = True


class TransactionBase(BaseModel):
    label: str
    amount: float
    category_id: int | None = None



class TransactionCreate(TransactionBase):
    """
    Schéma utilisé pour créer une transaction.
    """
    pass


class TransactionUpdate(BaseModel):
    """
    Mise à jour partielle d'une transaction.
    """
    label: Optional[str] = None
    amount: Optional[float] = None
    category_id: Optional[int] = None


class Transaction(TransactionBase):
    """
    Schéma renvoyé par l'API.
    """
    id: int
    date: datetime

    class Config:
        orm_mode = True
