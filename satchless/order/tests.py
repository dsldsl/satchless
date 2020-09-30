# -*- coding: utf-8 -*-
from __future__ import absolute_import
import datetime
import mock
from decimal import Decimal
from django.db import models
import os
import six

from django.conf import settings
from django.test import Client

from ..payment.models import PaymentVariant
from ..pricing import handler, Price
from ..product.tests import DeadParrot
from ..product.tests.pricing import FiveZlotyPriceHandler
from .app import order_app
from .models import (
    DeliveryGroup,
    Order,
    OrderedItem,
    OrderManager,
    signals,
)
from .exceptions import EmptyCart
from ..cart.tests import TestCart

from ..util.tests import BaseTestCase

class TestOrder(Order):
    cart = models.ForeignKey(TestCart, blank=True, null=True, related_name='orders', on_delete=models.PROTECT)
    objects = OrderManager()

class OrderTest(BaseTestCase):
    def setUp(self):
        order_app.order_model = TestOrder
        self.macaw = DeadParrot.objects.create(slug='macaw',
                species="Hyacinth Macaw")
        self.cockatoo = DeadParrot.objects.create(slug='cockatoo',
                species="White Cockatoo")
        self.macaw_blue = self.macaw.variants.create(color='blue',
                                                     looks_alive=False)
        self.macaw_blue_fake = self.macaw.variants.create(color='blue',
                                                          looks_alive=True)
        self.cockatoo_white_a = self.cockatoo.variants.create(color='white',
                                                              looks_alive=True)
        self.cockatoo_white_d = self.cockatoo.variants.create(color='white',
                                                              looks_alive=False)
        self.cockatoo_blue_a = self.cockatoo.variants.create(color='blue',
                                                             looks_alive=True)
        self.cockatoo_blue_d = self.cockatoo.variants.create(color='blue',
                                                             looks_alive=False)

        self.original_handlers = settings.SATCHLESS_PRICING_HANDLERS
        handler.pricing_queue = handler.PricingQueue(FiveZlotyPriceHandler)

    def tearDown(self):
        handler.pricing_queue = handler.PricingQueue(*self.original_handlers)

    def test_get_from_empty_cart_raises(self):
        cart = TestCart.objects.create(typ='satchless.test_cart')
        with self.assertRaises(EmptyCart):
            TestOrder.objects.get_from_cart(cart)

    def test_order_is_updated_when_cart_content_changes(self):
        cart = TestCart.objects.create(typ='satchless.test_cart')
        cart.replace_item(self.macaw_blue, 1)

        order = order_app.order_model.objects.get_from_cart(cart)

        cart.replace_item(self.macaw_blue_fake, Decimal('2.45'))
        cart.replace_item(self.cockatoo_white_a, Decimal('2.45'))

        order_items = set()
        for group in order.groups.all():
            order_items.update(group.items.values_list('product_variant',
                                                       'quantity'))
        self.assertEqual(set(cart.items.values_list('variant', 'quantity')),
                         order_items)

    def test_str(self):
        order = TestOrder.objects.create(currency='USD')
        self.assertEqual(six.text_type(order), 'Order #%s' % order.pk)

    def test_billing_full_name(self):
        order = TestOrder(billing_first_name='Ada', billing_last_name='Lovelace')
        self.assertEqual(order.billing_full_name, 'Ada Lovelace')

    def test_set_status(self):
        order = TestOrder.objects.create(currency='USD')
        last_status_change = datetime.datetime.utcnow() - datetime.timedelta(hours=10)
        order.last_status_change = last_status_change
        order.save()
        with mock.patch.object(signals.order_status_changed, 'send'):
            order.set_status('fulfilled')
        self.assertEqual(order.status, 'fulfilled')
        self.assertTrue(order.last_status_change > last_status_change)

    def test_subtotal(self):
        cart = TestCart.objects.create(typ='satchless.test_cart')
        cart.replace_item(self.macaw_blue, 1)
        cart.replace_item(self.macaw_blue_fake, Decimal('2.45'))
        order = order_app.order_model.objects.get_from_cart(cart)
        self.assertEqual(order.subtotal(), Price(net=15, gross=15, currency='USD'))

    def test_payment_price(self):
        cart = TestCart.objects.create(typ='satchless.test_cart')
        cart.replace_item(self.macaw_blue, 1)
        cart.replace_item(self.macaw_blue_fake, Decimal('2.45'))
        order = order_app.order_model.objects.get_from_cart(cart)
        variant = PaymentVariant.objects.create(order=order, name='gold-pressed latinum', price=10, amount=10)
        self.assertEqual(order.payment_price(), Price(net=10, gross=10, currency='USD'))

    def test_total(self):
        cart = TestCart.objects.create(typ='satchless.test_cart')
        cart.replace_item(self.macaw_blue, 1)
        cart.replace_item(self.macaw_blue_fake, Decimal('2.45'))
        order = order_app.order_model.objects.get_from_cart(cart)
        self.assertEqual(order.total(), Price(net=15, gross=15, currency='USD'))

    def test_paymentvariant(self):
        order = TestOrder.objects.create(currency='USD')
        variant = PaymentVariant.objects.create(order=order, name='gold-pressed latinum', price=10, amount=10)
        self.assertEqual(order.paymentvariant, variant)


class OrderedItemTest(BaseTestCase):
    def setUp(self):
        order = TestOrder.objects.create(currency='USD')
        group = DeliveryGroup.objects.create(order=order)
        self.item = OrderedItem.objects.create(
            delivery_group=group,
            product_name='sherlock holmes holonovel',
            quantity=2,
            unit_price_net=Decimal('10'),
            unit_price_gross=Decimal('11'),
        )

    def test_unit_price(self):
        self.assertEqual(self.item.unit_price(), Price(net=10, gross=11, currency='USD'))

    def test_price(self):
        self.assertEqual(self.item.price(), Price(net=20, gross=22, currency='USD'))

