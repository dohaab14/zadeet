from typing import List
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# 1. Base de Déclaration pour SQLAlchemy : classe de base dont tous les modèles hériteront.
class Base(DeclarativeBase):
    pass

# 2. Modèles de l'Application 

class Mois(Base):
    """
    Modèle représentant une période comptable (Mois et Année).
    Clé utilisée dans le JS : 'YYYY-MM' (ex: '2025-12').
    """
    __tablename__ = "mois"
    
    # Clé Primaire : l'ID du mois (ex: '2025-12')
    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    
    # Nom affiché (ex: 'Décembre 2025')
    nom: Mapped[str] = mapped_column(String, nullable=False)

    # Relation One-to-Many: un Mois a plusieurs Catégories
    categories: Mapped[List["Categorie"]] = relationship(
        back_populates="mois", 
        cascade="all, delete-orphan" # Supprime les catégories si le mois est supprimé
    )
    
    def __repr__(self) -> str:
        return f"Mois(id={self.id!r}, nom={self.nom!r})"


class Categorie(Base):
    """
    Modèle représentant le plafond et les dépenses réelles d'une catégorie
    pour un mois donné.
    """
    __tablename__ = "categorie"
    
    # Clé Primaire Auto-Incrémentée (ID interne de la BDD)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Nom technique de la catégorie (ex: 'logement', 'courses') - Utilisé comme ID dans le JS
    nom_technique: Mapped[str] = mapped_column(String, index=True) 

    # Nom affiché (ex: 'Logement', 'Courses')
    nom: Mapped[str] = mapped_column(String, nullable=False)
    
    # Plafond mensuel
    plafond: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Dépense réelle cumulée
    depense: Mapped[float] = mapped_column(Float, default=0.0)

    # Clé Étrangère : lie cette catégorie au Mois correspondant
    mois_id: Mapped[str] = mapped_column(ForeignKey("mois.id"))
    
    # Relation Many-to-One: la Catégorie appartient à un Mois
    mois: Mapped["Mois"] = relationship(back_populates="categories")
    