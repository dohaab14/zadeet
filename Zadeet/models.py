
from django.conf import settings
from django.db import models


class Category(models.Model):
    nom_category = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategories'
    )

    def __str__(self):
        if self.parent:
            return f"{self.parent} > {self.nom_category}"
        return self.nom_category


class Transaction(models.Model):
    SENS_CHOICES = [
        ('depense', 'Dépense'),
        ('revenu', 'Revenu'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.RESTRICT,
        related_name='transactions'
    )
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    sens = models.CharField(max_length=10, choices=SENS_CHOICES)
    date_transaction = models.DateField()

    def __str__(self):
        return f"{self.user} - {self.sens} {self.montant}€ ({self.category})"


class Budget(models.Model):
    PERIODICITE_CHOICES = [
        ('mensuel', 'Mensuel'),
        ('hebdomadaire', 'Hebdomadaire'),
        ('annuel', 'Annuel'),
        ('quotidien', 'Quotidien'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='budgets'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.RESTRICT,
        related_name='budgets'
    )
    periodicite = models.CharField(max_length=20, choices=PERIODICITE_CHOICES)
    montant_max = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('user', 'category', 'periodicite')

    def __str__(self):
        return f"Budget {self.user} - {self.category} ({self.periodicite})"
