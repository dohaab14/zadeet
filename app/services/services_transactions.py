"""
Logique du code pour les transactions
Ici utilisation de models.py pour interagir avec la bdd
"""

from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models import Transaction
from app.db.schemas import TransactionCreate, TransactionUpdate
from . import services_categories
from sqlalchemy import func, extract
from app.db.models import Transaction as TransactionModel, Category


def create_transaction(db: Session, data: TransactionCreate):
    """
    Creation d'une transaction
    return: la transaction créée
    """
    txn = Transaction(**data.dict())
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn


def update_transaction(db: Session, transaction: Transaction, data: TransactionUpdate):
    """
    Modification d'une transaction
    return: la transaction modifiée
    """

    for key, value in data.dict(exclude_unset=True).items():
        setattr(transaction, key, value)

    db.commit()
    db.refresh(transaction)
    return transaction


def delete_transaction(db: Session, transaction: Transaction):
    """
    Suppression d'une transaction
    return: True si la suppression a réussi, False sinon
    """
    db.delete(transaction)
    db.commit()
    return True


def get_transactions(
    db: Session,
    category_id: int | None = None,
    search: str | None = None,
):
    """
    Récupère les transactions avec filtrage intelligent :
    - Si category_id est un Parent, récupère aussi les transactions des Enfants.
    """
    # On fait une jointure explicite pour pouvoir filtrer sur le parent
    query = db.query(Transaction).join(Category, Transaction.category_id == Category.id)

    if category_id is not None:
        # La magie est ici : On prend la transaction SI :
        # 1. C'est exactement cette catégorie (ex: Je filtre sur 'Courses')
        # 2. OU c'est un enfant de cette catégorie (ex: Je filtre sur 'Alimentation')
        query = query.filter(
            or_(
                Transaction.category_id == category_id,
                Category.parent_id == category_id
            )
        )

    if search:
        query = query.filter(TransactionModel.label.op("REGEXP")(search))


    return query.all()


def get_transaction(db: Session, transaction_id: int):
    """
    Récupère une transaction par son ID
    return: la transaction, None si elle n'existe pas
    """
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()


def get_transactions_by_month(db: Session, year: int, month: int):
    """
    Récupère toutes les transactions d'un mois précis.
    Utile pour les graphiques du dashboard.
    """
    return db.query(Transaction).filter(extract('year', Transaction.date) == year).filter(extract('month', Transaction.date) == month).all()

def get_recent_transactions(db: Session, limit: int = 3):
    """
    Récupère les dernières transactions pour l'aperçu.
    """
    return db.query(Transaction).order_by(Transaction.date.desc()).limit(limit).all()

def get_transactions_overview(db: Session):
    """
    Retourne toutes les données nécessaires pour la page transactions :
    - transactions
    - catégories
    - total_transactions
    - total_categories
    - total_expenses
    - total_revenues
    """
    transactions = get_transactions(db)
    categories = services_categories.get_categories(db)
    total_transactions = len(transactions)
    total_categories = len(categories)
    total_expenses = sum(
        t.amount for t in transactions if t.category and t.category.type == "depense"
    )
    total_revenues = sum(
        t.amount for t in transactions
        if t.category and t.category.type == "revenu"
    )

    return {
        "transactions": transactions,
        "categories": categories,
        "total_transactions": total_transactions,
        "total_categories": total_categories,
        "total_expenses": total_expenses,
        "total_revenues": total_revenues,
    }

# -----------------------------------------------------
# NOUVELLE FONCTION POUR LE CALCUL PAR CATÉGORIE
# -----------------------------------------------------
def get_total_amount_by_category(db: Session):
    """
    Calcule la somme des montants pour chaque catégorie.
    Retourne un dictionnaire {category_id: total_amount}
    """
    totals = (
        db.query(
            TransactionModel.category_id,
            func.sum(TransactionModel.amount).label("total_amount"),
        )
        .join(Category, TransactionModel.category_id == Category.id)
        .group_by(TransactionModel.category_id)
        .all()
    )

    # Convertit la liste de tuples en dictionnaire pour un accès facile
    totals_map = {category_id: total for category_id, total in totals}
    return totals_map

# -----------------------------------------------------
# ANCIENNE FONCTION INUTILE MAIS CONSERVÉE SI ELLE EST UTILISÉE AILLEURS
# -----------------------------------------------------
def get_categories_with_totals(db: Session):
    """
    Retourne la liste des catégories avec un attribut supplémentaire :
    - total_amount : somme des montants des transactions de cette catégorie
    """
    categories = db.query(Category).all()

    # Récupérer les sommes groupées par category_id
    totals = (
        db.query(
            Transaction.category_id,
            func.sum(Transaction.amount).label("total_amount"),
        )
        .group_by(Transaction.category_id)
        .all()
    )

    totals_map = {cat_id: total for cat_id, total in totals}

    # On ajoute un attribut dynamique sur chaque objet Category
    for c in categories:
        c.total_amount = float(totals_map.get(c.id, 0.0))

    return categories