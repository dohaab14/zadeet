"""
Service de gestion des plafonds budgétaires.

Ce fichier contient UNIQUEMENT la logique métier pour :
- Créer et gérer les mois comptables
- Gérer les plafonds par catégorie et par mois (CRUD)

ATTENTION : Les calculs de dépenses (sommes de transactions) 
sont du ressort de services_transactions.py
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime

from app.db.models import Mois, Plafond, Category


# ============================================================================
# GESTION DES MOIS
# ============================================================================

def get_or_create_mois(db: Session, mois_id: str, nom: str = None) -> Mois:
    """
    Récupère un mois existant ou le crée s'il n'existe pas.
    
    Args:
        db: Session de base de données
        mois_id: ID du mois au format 'YYYY-MM' (ex: '2025-12')
        nom: Nom affiché (ex: 'Décembre 2025'). Généré automatiquement si None.
    
    Returns:
        Mois: L'objet Mois (existant ou nouvellement créé)
    
    Raises:
        ValueError: Si le format mois_id est invalide
    
    Example:
        >>> mois = get_or_create_mois(db, "2025-12")
        >>> print(mois.nom)  # "Décembre 2025"
    """
    mois = db.query(Mois).filter(Mois.id == mois_id).first()
    
    if not mois:
        # Générer le nom automatiquement si non fourni
        if not nom:
            try:
                year, month = mois_id.split('-')
                month = int(month)
                if not (1 <= month <= 12):
                    raise ValueError(f"Mois invalide : {month}")
                    
                mois_names = [
                    "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
                    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
                ]
                nom = f"{mois_names[month - 1]} {year}"
            except (ValueError, IndexError):
                raise ValueError(f"Format de mois invalide : {mois_id}. Utilisez 'YYYY-MM'")
        
        mois = Mois(id=mois_id, nom=nom)
        db.add(mois)
        db.commit()
        db.refresh(mois)
    
    return mois


def get_all_mois(db: Session) -> List[Mois]:
    """
    Récupère tous les mois enregistrés, triés du plus récent au plus ancien.
    
    Args:
        db: Session de base de données
    
    Returns:
        List[Mois]: Liste des mois triés
    """
    return db.query(Mois).order_by(Mois.id.desc()).all()


def get_mois(db: Session, mois_id: str) -> Optional[Mois]:
    """
    Récupère un mois spécifique par son ID.
    
    Args:
        db: Session de base de données
        mois_id: ID du mois (format 'YYYY-MM')
    
    Returns:
        Optional[Mois]: Le mois trouvé ou None
    """
    return db.query(Mois).filter(Mois.id == mois_id).first()


# ============================================================================
# GESTION DES PLAFONDS (CRUD)
# ============================================================================

def get_plafond(db: Session, category_id: int, mois_id: str) -> Optional[Plafond]:
    """
    Récupère le plafond d'une catégorie pour un mois donné.
    
    Args:
        db: Session de base de données
        category_id: ID de la catégorie
        mois_id: ID du mois (format 'YYYY-MM')
    
    Returns:
        Optional[Plafond]: Le plafond trouvé ou None
    """
    return db.query(Plafond).filter(
        and_(
            Plafond.category_id == category_id,
            Plafond.mois_id == mois_id
        )
    ).first()


def get_plafond_by_id(db: Session, plafond_id: int) -> Optional[Plafond]:
    """
    Récupère un plafond par son ID interne (primary key).
    Utile pour les mises à jour/suppressions.
    
    Args:
        db: Session de base de données
        plafond_id: ID interne du plafond
    
    Returns:
        Optional[Plafond]: Le plafond trouvé ou None
    """
    return db.query(Plafond).filter(Plafond.id == plafond_id).first()


def get_plafonds_for_month(db: Session, mois_id: str) -> List[Plafond]:
    """
    Récupère tous les plafonds définis pour un mois donné.
    
    Args:
        db: Session de base de données
        mois_id: ID du mois
    
    Returns:
        List[Plafond]: Liste des plafonds
    """
    return db.query(Plafond).filter(Plafond.mois_id == mois_id).all()


def create_plafond(
    db: Session, 
    category_id: int, 
    mois_id: str, 
    montant_max: float
) -> Plafond:
    """
    Crée un nouveau plafond pour une catégorie et un mois donnés.
    
    Args:
        db: Session de base de données
        category_id: ID de la catégorie
        mois_id: ID du mois (format 'YYYY-MM')
        montant_max: Montant maximum du plafond
    
    Returns:
        Plafond: Le plafond créé
    
    Raises:
        ValueError: Si la catégorie n'existe pas, si le montant est négatif,
                   ou si le plafond existe déjà
    """
    # Validation du montant
    if montant_max < 0:
        raise ValueError("Le montant du plafond ne peut pas être négatif")
    
    # Vérifier que la catégorie existe
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise ValueError(f"Catégorie avec l'ID {category_id} introuvable")
    
    # S'assurer que le mois existe
    get_or_create_mois(db, mois_id)
    
    # Vérifier qu'il n'existe pas déjà
    existing = get_plafond(db, category_id, mois_id)
    if existing:
        raise ValueError(
            f"Un plafond existe déjà pour la catégorie {category_id} en {mois_id}"
        )
    
    # Création
    plafond = Plafond(
        category_id=category_id,
        mois_id=mois_id,
        montant_max=montant_max
    )
    db.add(plafond)
    db.commit()
    db.refresh(plafond)
    return plafond


def create_or_update_plafond(
    db: Session, 
    category_id: int, 
    mois_id: str, 
    montant_max: float
) -> Plafond:
    """
    Crée un nouveau plafond ou met à jour un plafond existant.
    C'est une variante "upsert" pour plus de flexibilité.
    
    Args:
        db: Session de base de données
        category_id: ID de la catégorie
        mois_id: ID du mois (format 'YYYY-MM')
        montant_max: Montant maximum du plafond
    
    Returns:
        Plafond: Le plafond créé ou mis à jour
    
    Raises:
        ValueError: Si la catégorie n'existe pas ou si le montant est négatif
    """
    # Validation du montant
    if montant_max < 0:
        raise ValueError("Le montant du plafond ne peut pas être négatif")
    
    # Vérifier que la catégorie existe
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise ValueError(f"Catégorie avec l'ID {category_id} introuvable")
    
    # S'assurer que le mois existe
    get_or_create_mois(db, mois_id)
    
    # Chercher un plafond existant
    plafond = get_plafond(db, category_id, mois_id)
    
    if plafond:
        # Mise à jour
        plafond.montant_max = montant_max
    else:
        # Création
        plafond = Plafond(
            category_id=category_id,
            mois_id=mois_id,
            montant_max=montant_max
        )
        db.add(plafond)
    
    db.commit()
    db.refresh(plafond)
    return plafond


def update_plafond(
    db: Session, 
    plafond_id: int, 
    montant_max: float
) -> Optional[Plafond]:
    """
    Met à jour le montant maximum d'un plafond par son ID interne.
    
    Args:
        db: Session de base de données
        plafond_id: ID interne du plafond
        montant_max: Nouveau montant maximum
    
    Returns:
        Optional[Plafond]: Le plafond mis à jour, None si introuvable
    
    Raises:
        ValueError: Si le montant est négatif
    """
    if montant_max < 0:
        raise ValueError("Le montant du plafond ne peut pas être négatif")
    
    plafond = get_plafond_by_id(db, plafond_id)
    
    if plafond:
        plafond.montant_max = montant_max
        db.commit()
        db.refresh(plafond)
    
    return plafond


def delete_plafond(db: Session, plafond_id: int) -> bool:
    """
    Supprime un plafond par son ID interne.
    
    Args:
        db: Session de base de données
        plafond_id: ID interne du plafond
    
    Returns:
        bool: True si supprimé, False si non trouvé
    """
    plafond = get_plafond_by_id(db, plafond_id)
    
    if plafond:
        db.delete(plafond)
        db.commit()
        return True
    
    return False


def delete_plafond_for_category_month(
    db: Session, 
    category_id: int, 
    mois_id: str
) -> bool:
    """
    Supprime le plafond d'une catégorie pour un mois donné.
    
    Args:
        db: Session de base de données
        category_id: ID de la catégorie
        mois_id: ID du mois
    
    Returns:
        bool: True si supprimé, False si non trouvé
    """
    plafond = get_plafond(db, category_id, mois_id)
    
    if plafond:
        db.delete(plafond)
        db.commit()
        return True
    
    return False
