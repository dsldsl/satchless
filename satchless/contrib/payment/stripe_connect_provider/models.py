# 2016 Stripe Connect project
#
# the styleseat repo's pay module now writes its own records of Stripe payments
# so we really don't need these records except to jury-rig Satchless to work...
# anything we stored here would duplicate information in those payments records
#
# note that if this were in the same repo as our pay module I would have
# the records here link to the payment record created in that module, but
# since they don't... not going to try to fake django out by storing ids
# in non-FK fields. The records can be related through ss_order_id, and
# we may store the paymentvariant id in the payment record; we shall see

from ....payment.models import PaymentVariant
from django.db import models

class StripeConnectReceipt(models.Model):
    """
    Exists to fulfill Satchless requirements only.

    Actual details of card charges will be handled by code in the StyleSeat
    repo, specifically payment.py and _stripe.py in the styleseat/pay module
    """
    creation_time = models.DateTimeField(auto_now_add=True)
    modification_time = models.DateTimeField(auto_now=True)


class StripeConnectVariant(PaymentVariant):
    receipt = models.ForeignKey(StripeConnectReceipt, blank=True, null=True)
