from django.db import models

from .....product.models import ProductAbstract, Variant
from ..models import VariantStockLevelMixin

class StockedDeadParrot(ProductAbstract):
    species = models.CharField(max_length=20)

class StockedDeadParrotVariant(Variant, VariantStockLevelMixin):
    COLOR_CHOICES = (
        ('blue', 'blue'),
        ('white', 'white'),
        ('red', 'red'),
        ('green', 'green'),
    )
    product = models.ForeignKey(StockedDeadParrot, related_name='variants')
    color = models.CharField(max_length=10, choices=COLOR_CHOICES)
    looks_alive = models.BooleanField(default=False)

    class Meta:
        unique_together = ('product', 'color', 'looks_alive')

