# -*- coding: utf-8 -*-
from __future__ import absolute_import
from decimal import Decimal
from django.db import models
import os

from django.conf import settings
from django.test import Client

from ..pricing import handler
from ..product.tests import DeadParrot
from ..product.tests.pricing import FiveZlotyPriceHandler
from .app import order_app
from .models import Order, OrderManager
from ..cart.tests import TestCart

from ..util.tests import ViewsTestCase

class TestOrder(Order):
    cart = models.ForeignKey(TestCart, blank=True, null=True, related_name='orders', on_delete=models.PROTECT)
    objects = OrderManager()

class OrderTest(ViewsTestCase):
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
        app_dir = os.path.dirname(__file__)
        self.custom_settings = {
            'SATCHLESS_PRODUCT_VIEW_HANDLERS': ('satchless.cart.handler.add_to_cart_handler',),
            'TEMPLATE_DIRS': [os.path.join(app_dir, 'templates'),
                              os.path.join(app_dir, '..', 'product',
                                           'tests', 'templates')]
        }
        self.original_settings = self._setup_settings(self.custom_settings)

    def tearDown(self):
        handler.pricing_queue = handler.PricingQueue(*self.original_handlers)
        self._teardown_settings(self.original_settings,
                                self.custom_settings)

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

