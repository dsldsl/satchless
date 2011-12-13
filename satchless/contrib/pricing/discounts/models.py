from django.db import models
from ....util.models import Subtyped
from ....order.models import OrderedItem

class DiscountType(Subtyped):
    name = models.CharField(max_length=128, unique=True)

    def __unicode__(self):
        return self.name


class Discount(Subtyped):
    type = models.ForeignKey(DiscountType, related_name='discounts')
    item = models.ForeignKey(OrderedItem, null=True, blank=True,
                             related_name='discounts')
    deduction = models.DecimalField(max_digits=12, decimal_places=4)

    def __unicode__(self):
        return u'%.2f off %s' % (self.deduction, self.item)
