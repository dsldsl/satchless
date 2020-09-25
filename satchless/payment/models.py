from __future__ import absolute_import
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..order.models import Order
from ..util.models import Subtyped


class PaymentVariant(Subtyped):
    '''
    Base class for all payment variants. This is what gets assigned to an
    order at the checkout step.
    '''
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    name = models.CharField(_('name'), max_length=128)
    description = models.TextField(_('description'), blank=True)
    price = models.DecimalField(_('unit price'),
                                max_digits=12, decimal_places=4)
    amount = models.DecimalField(_('payment applied'),
                                 max_digits=12, decimal_places=4)

    def __unicode__(self):
        return self.name
