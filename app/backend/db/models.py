"""
Ce fichier définit les modèles de base de données pour les catégories et les transactions
dans une application de gestion de budget. Il utilise SQLAlchemy pour mapper les
tables de la base de données aux classes Python.

info: Ce fichier est différent du fichier schemas.py qui permet de mapper les données entrantes/sortantes et 
permet de ne pas exposer la bdd directement via l'API.
"""


from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
# @TODO: ajouter le modèle pour les plafonds
Base = declarative_base()

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    type = Column(String) # "depense" ou "revenu"
    
    # C'est ici que la magie opère : une catégorie peut avoir un parent
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    # Relations
    parent = relationship("Category", remote_side=[id], backref="subcategories")
    transactions = relationship("Transaction", back_populates="category")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    label = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
    
    # Lien vers la catégorie (on lie souvent à la sous-catégorie directement)
    category_id = Column(Integer, ForeignKey("categories.id"))
    
    category = relationship("Category", back_populates="transactions")