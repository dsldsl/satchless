# 2016 Stripe Connect project
#
# note that there is an historical stripe_provider module already contributed
# which may have been used in the past, so for this new Stripe Connect
# integration we are creating a separate payment variant
#
# this is a skeletal implementation because the styleseat repo's pay module
# now handles all of this work, including all communication with Stripe.

from decimal import Decimal
import urllib2
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from ....payment import PaymentProvider, PaymentFailure, PaymentType
from . import forms
from . import models

import stripe
import datetime

class StripeConnectProvider(PaymentProvider):
    form_class = forms.PaymentForm

    def enum_types(self, order=None, customer=None):
        yield self, PaymentType(typ='stripe_connect', name='connect.stripe.com')

    def get_configuration_form(self, order, typ, data):
        instance = models.StripeVariant(order=order, price=Decimal('0.0000'))
        return self.form_class(data or None, instance=instance)

    def create_variant(self, order, form, typ=None):
        if form.is_valid():
            return form.save()
        raise PaymentFailure(_("Could not create Stripe Connect Variant"))

    def confirm(self, order, typ=None, variant=None):
        if not variant:
            variant = order.paymentvariant
        v = variant.get_subtype_instance()

        # normally this is where the paymnentvariant would charge the customer,
        # but we do that in the styleseat/pay package instead.

        # So this is a NOOP that just needs to write out some records to keep
        # satchless from exploding.
        
        receipt_form = forms.StripeReceiptForm(data)
        if receipt_form.is_valid():
            v.receipt = receipt_form.save()
            v.save()
