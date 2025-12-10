from pydantic import BaseModel, Field, AliasPath
from typing import List

# -----------------------------------------------------------
# 1. Schéma d'entrée (Input) : Pour mettre à jour un plafond
# -----------------------------------------------------------

class PlafondUpdateSchema(BaseModel):
    """
    Définit la structure des données que le front-end envoie 
    lors de la modification d'un plafond (méthode PUT).
    """
    plafond: float = Field(..., ge=0, description="Nouvelle valeur du plafond à enregistrer.")


# -----------------------------------------------------------
# 2. Schéma de sortie (Output) : Pour renvoyer une Catégorie
# -----------------------------------------------------------

class CategorieSchema(BaseModel):
    """
    Définit la structure des données d'une catégorie telle qu'elle sera renvoyée au front-end.
    L'ID technique de la BDD (nom_technique) est exposé sous le champ 'id' pour le JS.
    """
    # Utiliser un Alias Pydantic pour mapper models.Categorie.nom_technique à schemas.CategorieSchema.id
    id: str = Field(
        ..., 
        alias="nom_technique", # L'alias indique l'attribut de l'objet SQLAlchemy à lire
        description="Identifiant technique (ex: 'logement', 'courses') utilisé par le front-end."
    )
    
    nom: str = Field(..., description="Nom affiché de la catégorie.")
    plafond: float = Field(..., description="Plafond mensuel fixé.")
    depense: float = Field(..., description="Total des dépenses enregistrées.")
    
    class Config:
        from_attributes = True
        populate_by_name = True # Autorise l'initialisation par le nom du champ ou par l'alias


# -----------------------------------------------------------
# 3. Schéma de sortie (Output) : Pour renvoyer les données d'un Mois complet
# -----------------------------------------------------------

class MoisDataSchema(BaseModel):
    """
    Définit la structure complète d'un mois, qui contient la liste des catégories.
    """
    nom: str = Field(..., description="Nom complet du mois (ex: 'Décembre 2025').")
    
    categories: List[CategorieSchema] = Field(..., description="Liste des catégories de dépenses pour ce mois.")
    
    class Config:
        from_attributes = True