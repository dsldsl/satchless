from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from . import models

class PaymentForm(forms.ModelForm):
    pg_client_token = forms.CharField(max_length=50, required=False,
                                      label=_('PaymentsGateway Client Token'))
    pg_payment_token = forms.CharField(max_length=50, required=False,
                                       label=_('PaymentsGateway Payment Method Token'))
    token_first_name = forms.CharField(max_length=50, required=False,
                                       label=_('PaymentsGateway Token First Name'))
    token_last_name = forms.CharField(max_length=50, required=False,
                                      label=_('PaymentsGateway Token Last Name'))

    class Meta:
        model = models.PaymentsGatewayVariant
        fields = ('amount', 'pg_client_token', 'pg_payment_token',
                  'description', 'token_first_name', 'token_last_name')

    def clean(self):
        if not self.cleaned_data.get('pg_client_token') \
           and not self.cleaned_data.get('pg_payment_token'):
            raise ValidationError(_("Either a Payment Method or Client is required"))
        if self.cleaned_data.get('pg_client_token') \
           and self.cleaned_data.get('pg_payment_token'):
            raise ValidationError(_("Cannot use both Payment Method and Client"))
        if self.cleaned_data.get('pg_payment_token') and not \
            (self.cleaned_data.get('token_first_name') and self.cleaned_data.get('token_last_name')):
            raise ValidationError(_("If paying by method token, First and Last Names are required."))
        return super(PaymentForm, self).clean()

class PaymentsGatewayReceiptForm(forms.ModelForm):
    class Meta:
        model = models.PaymentsGatewayReceipt
