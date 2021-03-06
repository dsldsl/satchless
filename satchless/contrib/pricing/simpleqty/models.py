from __future__ import absolute_import
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ....product.models import Product, Variant
import six

class ProductPrice(models.Model):
    QTY_MODE_CHOICES = (
        ('product', _("per product")),
        ('variant', _("per variant"))
    )
    product = models.OneToOneField(Product, on_delete=models.PROTECT)
    qty_mode = models.CharField(_("Quantity pricing mode"), max_length=10,
                                choices=QTY_MODE_CHOICES, default='variant',
                                help_text=_("In 'per variant' mode the unit "
                                            "price will depend on quantity "
                                            "of single variant being sold. In "
                                            "'per product' mode, total "
                                            "quantity of all product's "
                                            "variants will be used."))
    price = models.DecimalField(_("base price"), max_digits=12, decimal_places=4)

    def __str__(self):
        return six.text_type(self.product)


class PriceQtyOverride(models.Model):
    """
    Overrides price of product unit, depending of total quantity being sold.
    """
    base_price = models.ForeignKey(ProductPrice, related_name='qty_overrides', on_delete=models.PROTECT)
    min_qty = models.DecimalField(_("minimal quantity"), max_digits=10, decimal_places=4)
    price = models.DecimalField(_("unit price"), max_digits=12, decimal_places=4)

    class Meta:
        ordering = ('min_qty',)


class VariantPriceOffset(models.Model):
    """
    Holds optional price offset for a variant. Does not depend on quantity.
    """
    base_price = models.ForeignKey(ProductPrice, related_name='offsets', on_delete=models.PROTECT)
    variant = models.OneToOneField(Variant, on_delete=models.PROTECT)
    price_offset = models.DecimalField(_("unit price offset"), max_digits=12, decimal_places=4)
