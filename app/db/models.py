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
    
    # --- TA PARTIE : AJOUT DU PLAFOND ---
    monthly_cap = Column(Float, default=0.0) 
    # ------------------------------------
    
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
    
    category_id = Column(Integer, ForeignKey("categories.id"))
    
    category = relationship("Category", back_populates="transactions")