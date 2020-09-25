from __future__ import absolute_import
from django.template import Library
from satchless.order import handler

register = Library()

@register.filter
def delivery_type(typ):
    for provider, delivery_type in handler.delivery_queue.enum_types():
        if delivery_type.typ == typ:
            return delivery_type.name