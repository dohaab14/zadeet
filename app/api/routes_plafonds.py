# Fichier: api/routes_plafonds.py (Simplifié)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import SessionLocal
from app.services import services_plafonds, services_transactions
from app.db.schemas import MonthDataSchema, PlafondUpdateSchema, CategorieSchema, PlafondCreateSchema

# =====================================================================
# Dépendance pour la Session de Base de Données
# =====================================================================

def get_db():
    """Crée et ferme automatiquement la session de base de données."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =====================================================================
# Définition du Router FastAPI
# =====================================================================

router = APIRouter(
    prefix="/api/plafonds",
    tags=["Gestion des Plafonds (CRUD BDD)"]
)


# =====================================================================
# ENDPOINT 1 : GET /api/plafonds/data/{mois_id} (Lire les données du mois)
# =====================================================================
@router.get("/data/{mois_id}", response_model=MoisDataSchema)
def get_month_data(
    mois_id: str,
    db: Session = Depends(get_db)
):
    """
    Récupère l'ensemble des catégories, plafonds et dépenses pour un mois donné.
    
    Returns:
        MoisDataSchema: Nom du mois + liste des catégories avec plafonds et dépenses
    """
    # Vérifier que le mois existe
    mois = services_plafonds.get_mois(db, mois_id)
    if not mois:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mois '{mois_id}' non trouvé."
        )
    
    # Récupérer tous les plafonds du mois
    plafonds = services_plafonds.get_plafonds_for_month(db, mois_id)
    
    # Calculer les dépenses par catégorie
    depenses_dict = services_transactions.calculate_depenses_by_category(db, mois_id)
    
    # Construire la liste des catégories avec plafonds et dépenses
    categories_data = []
    for plafond in plafonds:
        depense = depenses_dict.get(plafond.category_id, 0.0)
        
        categories_data.append(
            CategorieSchema(
                id=plafond.category.name.lower().replace(" ", "_"),
                nom=plafond.category.name,
                plafond=plafond.montant_max,
                depense=depense,
                internal_id=plafond.id
            )
        )
    
    return MoisDataSchema(
        nom=mois.nom,
        categories=categories_data
    )


# =====================================================================
# ENDPOINT 2 : POST /api/plafonds/ (Créer un plafond) - CREATE
# =====================================================================
@router.post("/", response_model=CategorieSchema, status_code=status.HTTP_201_CREATED)
def create_plafond(
    plafond_data: PlafondCreateSchema,
    db: Session = Depends(get_db)
):
    """
    Crée un nouveau plafond pour une catégorie et un mois donnés.
    
    Args:
        plafond_data: Données du plafond (nom_technique, nom, plafond, mois_id)
    
    Returns:
        CategorieSchema: Le plafond créé
    """
    try:
        # Appel au service pour créer le plafond
        # Note: on suppose que nom_technique correspond à un ID de catégorie ou au nom de la catégorie
        # Pour l'instant, nous cherchons la catégorie par son nom
        from app.services import services_categories
        
        category = services_categories.get_category_by_name(db, plafond_data.nom)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Catégorie '{plafond_data.nom}' non trouvée."
            )
        
        plafond = services_plafonds.create_plafond(
            db,
            category_id=category.id,
            mois_id=plafond_data.mois_id,
            montant_max=plafond_data.plafond
        )
        
        depense = services_transactions.calculate_depense_for_category(
            db, category.id, plafond_data.mois_id
        )
        
        return CategorieSchema(
            id=plafond.category.name.lower().replace(" ", "_"),
            nom=plafond.category.name,
            plafond=plafond.montant_max,
            depense=depense,
            internal_id=plafond.id
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


# =====================================================================
# ENDPOINT 3 : PUT /api/plafonds/{plafond_id} (Modifier un plafond) - UPDATE
# =====================================================================
@router.put("/{plafond_id}", response_model=CategorieSchema)
def update_plafond_db(
    plafond_id: int,
    update: PlafondUpdateSchema,
    db: Session = Depends(get_db)
):
    """
    Met à jour le montant maximum d'un plafond existant.
    
    Args:
        plafond_id: ID interne du plafond
        update: Nouvelles données du plafond (plafond: float)
    
    Returns:
        CategorieSchema: Le plafond mis à jour
    """
    try:
        plafond = services_plafonds.update_plafond(db, plafond_id, update.plafond)
        
        if plafond is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plafond avec ID {plafond_id} introuvable."
            )
        
        depense = services_transactions.calculate_depense_for_category(
            db, plafond.category_id, plafond.mois_id
        )
        
        return CategorieSchema(
            id=plafond.category.name.lower().replace(" ", "_"),
            nom=plafond.category.name,
            plafond=plafond.montant_max,
            depense=depense,
            internal_id=plafond.id
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# =====================================================================
# ENDPOINT 4 : DELETE /api/plafonds/{plafond_id} (Supprimer un plafond) - DELETE
# =====================================================================
@router.delete("/{plafond_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plafond_db(
    plafond_id: int,
    db: Session = Depends(get_db)
):
    """
    Supprime un plafond par son ID interne.
    
    Args:
        plafond_id: ID interne du plafond
    """
    success = services_plafonds.delete_plafond(db, plafond_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plafond avec ID {plafond_id} introuvable."
        )