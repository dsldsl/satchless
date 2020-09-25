from __future__ import absolute_import
from django.contrib import admin
from satchless.product.admin import ProductAdmin

from . import models

class DummyVariantInline(admin.TabularInline):
    model = models.DummyVariant

class DummyImageInline(admin.TabularInline):
    model = models.DummyImage
    sortable_field_name = 'sort'

class DummyAdmin(ProductAdmin):
    inlines = [
        DummyImageInline,
        DummyVariantInline,
    ]

admin.site.register(models.Dummy, DummyAdmin)
