# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django import template

register = template.Library()

@register.filter
def product_url(product, category=None):
    return product.get_absolute_url(category=category)
