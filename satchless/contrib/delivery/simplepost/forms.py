from __future__ import absolute_import
from django import forms

from . import models

class PostShippingVariantForm(forms.ModelForm):
    class Meta:
        model = models.PostShippingVariant
        exclude = ('delivery_group', 'name', 'description', 'price')
