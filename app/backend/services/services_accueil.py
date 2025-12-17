from sqlalchemy.orm import Session
from sqlalchemy import extract, func
from datetime import datetime, timedelta
from app.backend.db import models 
from .services_transactions import *
from collections import defaultdict

def get_category_totals(db: Session):
    """
    Totaux par catégorie (et type) sur tout l'historique.
    Retourne une liste de dicts.
    """
    rows = (
        db.query(
            models.Category.id.label("category_id"),
            models.Category.name.label("category_name"),
            models.Category.type.label("category_type"),
            func.sum(models.Transaction.amount).label("total"),
        )
        .join(models.Transaction, models.Transaction.category_id == models.Category.id)
        .group_by(models.Category.id, models.Category.name, models.Category.type)
        .all()
    )

    return [
        {
            "category_id": r.category_id,
            "category_name": r.category_name,
            "category_type": r.category_type,
            "total": float(r.total or 0),
        }
        for r in rows
    ]

def get_parent_category_totals(db: Session):
    """
    Totaux par catégorie parent (ou par catégorie elle‑même si pas de parent).
    """
    rows = (
        db.query(
            func.coalesce(models.Category.parent_id, models.Category.id).label("group_id"),
            func.coalesce(models.Category.parent_id, models.Category.id),
            func.coalesce(models.Category.parent_id, models.Category.id),
            func.coalesce(models.Category.parent.has().name, models.Category.name),
        )
    )


def get_total_balance(db: Session):
    """
    Calcule le solde total : somme des revenus - somme des dépenses.
    """
    # Récupère toutes les transactions avec leur catégorie
    transactions = db.query(models.Transaction).join(models.Category).all()

    total = 0
    for t in transactions:
        if t.category.type == "revenu":
            total += t.amount
        elif t.category.type == "depense":
            total -= t.amount

    return total

def get_last_3_months_stats(db: Session):
    """
    Prépare les données pour le Graphique 1 (Bâtons) : 3 derniers mois.
    Retourne : { "labels": ["Oct", "Nov", "Dec"], "revenus": [..], "depenses": [..] }
    """
    today = datetime.now()
    labels = []
    data_revenus = []
    data_depenses = []

    # On boucle sur les 3 derniers mois (2 mois avant puis le mois précédent puis le mois actuel => ordre du graphique)
    for i in range(2, -1, -1):
        date_target = today - timedelta(days=i*30) # ajd - 30j = mois précédent
        month = date_target.month
        year = date_target.year
        
        # Nom du mois pour l'étiquette (ex: "12/2025")
        labels.append(f"{month:02d}/{year}")

        # Requête aggrégée pour aller vite
        # Somme des transactions du mois filtrées par type => Select SUM(...) WHERE month=.. AND type=revenu/depense
        revenu = db.query(func.sum(models.Transaction.amount))\
            .join(models.Category)\
            .filter(extract('year', models.Transaction.date) == year)\
            .filter(extract('month', models.Transaction.date) == month)\
            .filter(models.Category.type == 'revenu')\
            .scalar() or 0 # .scalar() retourne la valeur ou None

        depense = db.query(func.sum(models.Transaction.amount))\
            .join(models.Category)\
            .filter(extract('year', models.Transaction.date) == year)\
            .filter(extract('month', models.Transaction.date) == month)\
            .filter(models.Category.type == 'depense')\
            .scalar() or 0

        data_revenus.append(revenu)
        data_depenses.append(depense)

    return {
        "labels": labels,
        "revenus": data_revenus,
        "depenses": data_depenses
    }

def get_category_pie_stats(db: Session):
    """
    Prépare le Graphique 2 (Camembert) : Dépenses du mois actuel par Parent.
    Gère le détail pour le survol (tooltip).
    """
    today = datetime.now()
    
    # Récupère toutes les dépenses du mois actuel avec leurs catégories
    transactions = db.query(models.Transaction)\
        .join(models.Category)\
        .filter(extract('year', models.Transaction.date) == today.year)\
        .filter(extract('month', models.Transaction.date) == today.month)\
        .filter(models.Category.type == 'depense')\
        .all()

    # Structure : { "ParentName": { "total": 0, "details": {"SubName": 0} } } exemple : { "Alimentation": { "total": 100, "details": {"Courses": 70, "Restaurant": 30} } }
    stats = defaultdict(lambda: {"total": 0, "details": defaultdict(int)})

    for t in transactions:
        amount = t.amount
        # Si parent existe, on groupe sous le parent, sinon sous la catégorie elle-même
        if t.category.parent:
            parent_name = t.category.parent.name
            sub_name = t.category.name
        else:
            parent_name = t.category.name
            sub_name = "Autre"
        
        stats[parent_name]["total"] += amount
        stats[parent_name]["details"][sub_name] += amount

    # Formatage pour le JSON
    labels = []
    data = []
    tooltips = [] # Liste de strings pour le survol

    for parent, info in stats.items():
        labels.append(parent)
        data.append(info["total"])
        
        # Création du texte de détail : "Courses: 70€, Restaurant: 30€"
        detail_txt = ", ".join([f"{k}: {v}€" for k, v in info["details"].items()])
        tooltips.append(detail_txt)

    return {
        "labels": labels,
        "data": data,
        "tooltips": tooltips
    }