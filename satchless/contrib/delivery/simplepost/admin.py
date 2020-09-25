from __future__ import absolute_import
from django.contrib import admin

from . import models

class PostShippingTypeAdmin(admin.ModelAdmin):
    model = models.PostShippingType
    list_display = ('name',)
    prepopulated_fields = {'typ': ('name',)}

admin.site.register(models.PostShippingType, PostShippingTypeAdmin)
