from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    type = Column(String) # "depense" ou "revenu"

    # Le plafond est intégré à la catégorie car il est considéré comme un attribut constant.
    monthly_cap = Column(Float, default=0.0) 
    # ------------------------------
    
    # Gestion de la hiérarchie des catégories
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    # Relations
    # Relation récursive pour les sous-catégories
    parent = relationship("Category", remote_side=[id], backref="subcategories")
    
    # Lien vers les transactions
    transactions = relationship("Transaction", back_populates="category")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    label = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
    
    # Lien vers la catégorie
    category_id = Column(Integer, ForeignKey("categories.id"))
    
    # Relation Many-to-One
    # Correction : Suppression de la virgule de fin qui causait l'erreur de syntaxe.
    category = relationship("Category", back_populates="transactions")