from django.db import models
from ....util.models import Subtyped
from ....order.models import OrderedItem

class DiscountType(Subtyped):
    name = models.CharField(max_length=128)

    def __unicode__(self):
        return self.name


class Discount(Subtyped):
    type = models.ForeignKey(DiscountType)
    item = models.ForeignKey(OrderedItem, null=True, blank=True)
    deduction = models.DecimalField(max_digits=12, decimal_places=4)

    def __unicode__(self):
        return u'%.2f off %s' % (self.deduction, self.item)
