from __future__ import absolute_import
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from satchless.core.handler import QueueHandler
from satchless.payment import PaymentFailure

from ..payment import PaymentProvider, PaymentType
from ..payment.models import PaymentVariant
from . import Partitioner

from decimal import Decimal

### PARTITIONERS
class PartitionerQueue(Partitioner, QueueHandler):
    element_class = Partitioner

    def partition(self, cart, items=None):
        groups = []
        remaining_items = items or list(cart.items.all())
        for handler in self.queue:
            handled_groups, remaining_items = handler.partition(cart,
                                                                remaining_items)
            groups += handled_groups
        if remaining_items:
            raise ImproperlyConfigured('Unhandled items remaining in cart.')
        return groups


partitioners = getattr(settings, 'SATCHLESS_ORDER_PARTITIONERS', [
    'satchless.contrib.order.partitioner.simple.SimplePartitioner',
])
partitioner_queue = PartitionerQueue(*partitioners)


### PAYMENT PROVIDERS
class PaymentQueue(PaymentProvider, QueueHandler):
    element_class = PaymentProvider

    def enum_types(self, order=None, customer=None):
        for provider in self.queue:
            types = provider.enum_types(order=order, customer=customer)
            for provider, typ in types:
                yield provider, typ

    def _get_provider(self, order, typ):
        for provider, payment_type in self.enum_types(order):
            if payment_type.typ == typ:
                return provider
        raise ValueError('Unable to find a payment provider for type %s' %
                         (typ,))

    def get_configuration_form(self, order, data, typ=None):
        typ = typ or order.payment_type
        provider = self._get_provider(order, typ)
        return provider.get_configuration_form(order=order, data=data, typ=typ)

    def get_configuration_forms(self, order, data):
        config_forms = [(k, self.get_configuration_form(order, v, typ=k))
                for k, v in data]

        return config_forms

    def create_variant(self, order, form, typ=None, clear=False):
        typ = typ or order.payment_type
        provider = self._get_provider(order, typ)
        if clear:
            order.paymentvariant_set.all().delete()
        return provider.create_variant(order=order, form=form, typ=typ)

    def create_variants(self, order, forms, clear=False):
        variants = []
        if clear:
            order.paymentvariant_set.all().delete()
        for index, (typ, form) in enumerate(forms):
            variants.append((typ, self.create_variant(order, form, typ, clear=False)))
        return variants

    def confirm(self, order, typ=None, variant=None):
        typ = typ or order.payment_type
        provider = self._get_provider(order, typ)
        return provider.confirm(order=order, typ=typ, variant=variant)

    def confirms(self, order, variants):
        total_collected = Decimal("0.00")
        for typ, variant in variants:
            self.confirm(order, typ=typ, variant=variant)
            total_collected += variant.amount
        if total_collected != order.total().gross:
            raise PaymentFailure("Amount collected does not match order total.")

payment_providers = getattr(settings, 'SATCHLESS_PAYMENT_PROVIDERS', [])
payment_queue = PaymentQueue(*payment_providers)

