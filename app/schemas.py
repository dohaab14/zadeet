from pydantic import BaseModel, Field, AliasPath
from typing import List

# -----------------------------------------------------------
# 1. Schéma d'entrée (Input) : Pour le front-end
# -----------------------------------------------------------

class PlafondUpdateSchema(BaseModel):
    """
    Définit la structure des données que le front-end envoie 
    lors de la modification d'un plafond (méthode PUT).
    """
    plafond: float = Field(..., ge=0, description="Nouvelle valeur du plafond à enregistrer.")

class PlafondCreateSchema(BaseModel):
    """
    Définit la structure des données nécessaires pour créer une nouvelle
    catégorie (plafond) pour un mois donné (méthode POST).
    """
    nom_technique: str = Field(..., min_length=1, max_length=50, description="ID technique (ex: 'vetements').")
    nom: str = Field(..., min_length=1, max_length=50, description="Nom affiché (ex: 'Vêtements').")
    plafond: float = Field(..., ge=0, description="Le montant maximum alloué à cette catégorie.")
    mois_id: str = Field(..., description="Le mois au format 'YYYY-MM'.")


# Schéma interne pour le Service (pour la création)
# Ce schéma est utilisé par plafond_service.py pour créer l'objet BDD complet
class CategorieCreate(PlafondCreateSchema):
    depense: float = Field(0.0, ge=0)


# -----------------------------------------------------------
# 2. Schéma de sortie (Output) : Pour le back-end
# -----------------------------------------------------------

class CategorieSchema(BaseModel):
    """
    Définit la structure des données d'une catégorie telle qu'elle sera renvoyée au front-end.
    L'ID technique de la BDD (nom_technique) est exposé sous le champ 'id' pour le JS.
    """
    # Mappe models.Categorie.nom_technique à schemas.CategorieSchema.id
    id: str = Field(
        ..., 
        alias="nom_technique", 
        description="Identifiant technique (ex: 'logement', 'courses') utilisé par le front-end."
    )
    
    nom: str = Field(..., description="Nom affiché de la catégorie.")
    plafond: float = Field(..., description="Plafond mensuel fixé.")
    depense: float = Field(..., description="Total des dépenses enregistrées.")
    
    # L'ID BDD interne est aussi souvent utile
    internal_id: int = Field(..., alias="id", description="ID interne de la BDD pour les opérations de modification/suppression.")
    
    class Config:
        from_attributes = True
        populate_by_name = True

class MoisDataSchema(BaseModel):
    """
    Définit la structure complète d'un mois, qui contient la liste des catégories.
    """
    nom: str = Field(..., description="Nom complet du mois (ex: 'Décembre 2025').")
    
    categories: List[CategorieSchema] = Field(..., description="Liste des catégories de dépenses pour ce mois.")
    
    class Config:
        from_attributes = True