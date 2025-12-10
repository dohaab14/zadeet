# Fichier: api/routes_plafonds.py (Simplifié)

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, List
# Importez vos schémas (assurez-vous que l'import est correct pour votre structure)
from db.schemas import MoisDataSchema, PlafondUpdateSchema, CategorieSchema 

router = APIRouter()

# --- Simulation des Données (Mock Data) ---
# Ce dictionnaire fait office de "Base de Données" en mémoire.
MOCK_MONTHLY_DATA: Dict[str, MoisDataSchema] = {
    "2025-12": MoisDataSchema(
        nom="Décembre 2025",
        categories=[
            CategorieSchema(id="logement", nom="Logement", plafond=1200.0, depense=750.0),
            CategorieSchema(id="courses", nom="Courses", plafond=400.0, depense=410.0),
            CategorieSchema(id="transport", nom="Transport", plafond=150.0, depense=120.0),
            CategorieSchema(id="loisirs", nom="Loisirs", plafond=200.0, depense=50.0)
        ]
    ),
    "2025-11": MoisDataSchema(
        nom="Novembre 2025",
        categories=[
            CategorieSchema(id="logement", nom="Logement", plafond=1200.0, depense=1200.0),
            CategorieSchema(id="courses", nom="Courses", plafond=400.0, depense=350.0),
        ]
    )
}

# ----------------------------------------------------------------------
# ENDPOINT 1 : GET /data/{mois_id} (Lire les données du mois)
# ----------------------------------------------------------------------
@router.get("/data/{mois_id}", response_model=MoisDataSchema)
async def get_month_data(mois_id: str):
    """
    Récupère l'ensemble des catégories, plafonds et dépenses pour un mois donné.
    """
    data = MOCK_MONTHLY_DATA.get(mois_id)
    
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Mois '{mois_id}' non trouvé."
        )
    
    # Renvoyer une JSONResponse explicite pour assurer l'encodage UTF-8 (accents)
    return JSONResponse(
        content=data.model_dump(),
        media_type="application/json; charset=utf-8"
    )

# ----------------------------------------------------------------------
# ENDPOINT 2 : PUT /plafond/{mois_id}/{categorie_id} (Modifier le plafond)
# ----------------------------------------------------------------------
@router.put("/plafond/{mois_id}/{categorie_id}", status_code=status.HTTP_200_OK)
async def update_plafond(
    mois_id: str, 
    categorie_id: str, 
    update: PlafondUpdateSchema # Le corps de la requête doit contenir { "plafond": 123.45 }
):
    """
    Met à jour le plafond d'une catégorie spécifique.
    Ceci ne fonctionne que pour les catégories existantes.
    """
    if mois_id not in MOCK_MONTHLY_DATA:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mois non trouvé")
        
    mois_data = MOCK_MONTHLY_DATA[mois_id]
    
    # Recherche et modification de l'objet CategorieSchema en mémoire
    found = False
    for cat in mois_data.categories:
        if cat.id == categorie_id:
            # Simulation de la modification en BDD (modification de l'objet en mémoire)
            cat.plafond = update.plafond
            found = True
            break
            
    if not found:
        # Si la catégorie n'est pas trouvée, c'est une erreur 404.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Catégorie '{categorie_id}' non trouvée dans le mois {mois_id}")
        
    # Retourne une confirmation
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": f"Plafond de {categorie_id} mis à jour à {update.plafond}€ pour {mois_id}."}
    )
