# 2016 Stripe Connect project
#
# note that there is an historical stripe_provider module already contributed
# which may have been used in the past, so for this new Stripe Connect
# integration we are creating a separate payment variant
#
# this is a skeletal implementation because the styleseat repo's pay module
# now handles all of this work.

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from . import models
from ....payment import PaymentFailure

class PaymentForm(forms.ModelForm):
    class Meta:
        model = models.StripeConnectVariant
        fields = ()

    def clean(self):
        return super(PaymentForm, self).clean()

    def save(self, commit=True):
        return super(PaymentForm, self).save(commit)

class StripeConnectReceiptForm(forms.ModelForm):
    class Meta:
        model = models.StripeConnectReceipt

