# -*- coding:utf-8 -*-
from __future__ import absolute_import
from django import forms

from satchless.product.forms import BaseVariantForm, variant_form_for_product

from . import models
from six.moves import filter
from six.moves import zip

has_side_effects = True

def _get_existing_variants_choices(queryset, field_names):
    existing_choices = {}
    existing_variants = queryset.values_list(*field_names)

    if existing_variants:
        for index, existing_field_choices in enumerate(zip(*existing_variants)):
            field_name = field_names[index]
            original_choices = queryset.model._meta.get_field(field_name).choices
            flt = lambda choice: choice[0] in existing_field_choices
            existing_choices[field_names[index]] = list(filter(flt,
                                                          original_choices))
    else:
        for field_name in field_names:
            existing_choices[field_name] = []
    return existing_choices

class VariantWithSizeAndColorForm(BaseVariantForm):
    color = forms.CharField(max_length=10,
            widget=forms.Select(choices=models.ColoredVariant.COLOR_CHOICES))

    def __init__(self, *args, **kwargs):
        super(VariantWithSizeAndColorForm, self).__init__(*args, **kwargs)
        all_variants = self.product.variants.all()
        existing_choices = _get_existing_variants_choices(all_variants,
                                                          ('color', 'size'))
        for field_name, choices in existing_choices.items():
            self.fields[field_name].widget.choices = choices

    def _get_variant_queryset(self):
        color = self.cleaned_data.get('color')
        size = self.cleaned_data.get('size')
        return self.product.variants.filter(color=color, size=size)

    def clean(self):
        if not self._get_variant_queryset().exists():
            raise forms.ValidationError("Variant does not exist")
        return self.cleaned_data

    def get_variant(self):
        return self._get_variant_queryset().get()

@variant_form_for_product(models.Cardigan)
class CardiganVariantForm(VariantWithSizeAndColorForm):
    size = forms.CharField(max_length=10,
            widget=forms.Select(choices=models.CardiganVariant.SIZE_CHOICES))

@variant_form_for_product(models.Dress)
class DressVariantForm(VariantWithSizeAndColorForm):
    size = forms.CharField(max_length=10,
            widget=forms.Select(choices=models.DressVariant.SIZE_CHOICES))

@variant_form_for_product(models.Hat)
class HatVariantForm(BaseVariantForm):
    def get_variant(self):
        return self.product.variants.get()

@variant_form_for_product(models.Jacket)
class JacketVariantForm(VariantWithSizeAndColorForm):
    size = forms.CharField(max_length=10,
            widget=forms.Select(choices=models.JacketVariant.SIZE_CHOICES))

@variant_form_for_product(models.Shirt)
class ShirtVariantForm(VariantWithSizeAndColorForm):
    size = forms.CharField(max_length=10,
            widget=forms.Select(choices=models.ShirtVariant.SIZE_CHOICES))

@variant_form_for_product(models.TShirt)
class TShirtVariantForm(VariantWithSizeAndColorForm):
    size = forms.CharField(max_length=10,
            widget=forms.Select(choices=models.TShirtVariant.SIZE_CHOICES))

@variant_form_for_product(models.Trousers)
class TrousersVariantForm(VariantWithSizeAndColorForm):
    size = forms.CharField(max_length=10,
            widget=forms.Select(choices=models.TrousersVariant.SIZE_CHOICES))
