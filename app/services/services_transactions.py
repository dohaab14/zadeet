"""
Logique du code pour les transactions
Ici utilisation de models.py pour interagir avec la bdd
"""

from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models import Transaction
from app.db.schemas import TransactionCreate, TransactionUpdate
from . import services_categories
from sqlalchemy import func
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
    Récupère les transactions, avec filtres optionnels :
    - category_id : filtre par catégorie
    - search      : filtre sur le label (contient, insensible à la casse)
    """
    query = db.query(TransactionModel)

    if category_id is not None:
        query = query.filter(TransactionModel.category_id == category_id)

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            func.lower(TransactionModel.label).like(func.lower(pattern))
        )

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

from . import services_categories

def get_transactions_overview(db: Session):
    """
    Retourne toutes les données nécessaires pour la page transactions :
    - transactions
    - catégories
    - total_transactions
    - total_categories
    - total_expenses
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

# à sauter lors du merge mais jsp où c utilisé ?  @TODO: vérifier si utilisé quelque part

def search_by_amount_and_category(db: Session, amount: float, category_name: str, tolerance: float = 0.01):
    """
    Recherche les transactions par montant et catégorie.
    
    Args:
        db: Session SQLAlchemy
        amount: Montant à rechercher
        category_name: Nom de la catégorie
        tolerance: Marge d'erreur sur le montant (par défaut 0.01€)
    
    Returns:
        Liste des transactions correspondantes
    """
    return db.query(TransactionModel)\
        .join(Category, TransactionModel.category_id == Category.id)\
        .filter(TransactionModel.amount >= amount - tolerance)\
        .filter(TransactionModel.amount <= amount + tolerance)\
        .filter(Category.name == category_name)\
        .all()