# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os

from decimal import Decimal
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import Client

from .....checkout.tests import BaseCheckoutAppTests
from .....contrib.delivery.simplepost.models import PostShippingType
from .....order import handler as order_handler
from .....payment import ConfirmationFormNeeded
from .....payment.tests import TestPaymentProvider
from .....pricing import handler as pricing_handler
from .....product.tests import DeadParrot
from .....product.tests.pricing import FiveZlotyPriceHandler


from .. import app
from .....cart.tests import TestCart
from .....order.tests import TestOrder

class TestPaymentProviderWithConfirmation(TestPaymentProvider):
    def confirm(self, order, typ=None, variant=None):
        raise ConfirmationFormNeeded(action='http://test.payment.gateway.example.com')


class CheckoutTest(BaseCheckoutAppTests):
    checkout_app = app.checkout_app
    urls = BaseCheckoutAppTests.MockUrls(checkout_app=app.checkout_app)

    def setUp(self):
        self.checkout_app.cart_model = TestCart
        self.checkout_app.order_model = TestOrder
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

        test_dir = os.path.dirname(__file__)
        satchless_dir = os.path.join(test_dir, '..', '..', '..', '..')
        self.custom_settings = {
            'SATCHLESS_DJANGO_PAYMENT_TYPES': ['dummy'],
            'PAYMENT_VARIANTS': {'dummy': ('payments.dummy.DummyProvider', {'url': '/', })},
            'TEMPLATE_DIRS': (os.path.join(satchless_dir, 'category', 'templates'),
                              os.path.join(satchless_dir, 'order', 'templates'),
                              os.path.join(test_dir, '..', 'templates'),
                              os.path.join(test_dir, 'templates')),
            'TEMPLATE_LOADERS': (
                'django.template.loaders.filesystem.Loader',
            )
        }
        self.original_settings = self._setup_settings(self.custom_settings)
        order_handler.delivery_queue = order_handler.DeliveryQueue('satchless.contrib.delivery.simplepost.provider.PostDeliveryProvider')
        order_handler.payment_queue = order_handler.PaymentQueue(TestPaymentProviderWithConfirmation)
        order_handler.partitioner_queue = order_handler.PartitionerQueue('satchless.contrib.order.partitioner.simple.SimplePartitioner')

        self.anon_client = Client()

        PostShippingType.objects.create(price=12, typ='polecony', name='list polecony')
        PostShippingType.objects.create(price=20, typ='list', name='List zwykly')

        self.original_handlers = settings.SATCHLESS_PRICING_HANDLERS
        pricing_handler.pricing_queue = pricing_handler.PricingQueue(FiveZlotyPriceHandler)

    def tearDown(self):
        self._teardown_settings(self.original_settings, self.custom_settings)
        pricing_handler.pricing_queue = pricing_handler.PricingQueue(*self.original_handlers)

    def test_order_from_cart_view_creates_proper_order(self):
        cart = self._get_or_create_cart_for_client(self.anon_client)
        cart.replace_item(self.macaw_blue, 1)
        cart.replace_item(self.macaw_blue_fake, Decimal('2.45'))
        cart.replace_item(self.cockatoo_white_a, Decimal('2.45'))

        order = self._get_order_from_session(self.anon_client.session)
        self.assertNotEqual(order, None)
        order_items = self._get_order_items(order)
        self.assertEqual(set(cart.items.values_list('variant', 'quantity')),
                         order_items)

    def test_order_is_updated_after_cart_changes(self):
        cart = self._get_or_create_cart_for_client(self.anon_client)

        cart.replace_item(self.macaw_blue, 1)
        cart.replace_item(self.macaw_blue_fake, Decimal('2.45'))
        cart.replace_item(self.cockatoo_white_a, Decimal('2.45'))

        order = self._get_order_from_session(self.anon_client.session)
        order_items = self._get_order_items(order)
        # compare cart and order
        self.assertEqual(set(cart.items.values_list('variant', 'quantity')),
                         order_items)

        # update cart
        cart.add_item(self.macaw_blue, 100)
        cart.add_item(self.macaw_blue_fake, 100)

        old_order = order
        order = self._get_order_from_session(self.anon_client.session)
        # order should be reused
        self.assertEqual(old_order.pk, order.pk)
        self.assertNotEqual(order, None)
        order_items = self._get_order_items(order)
        # compare cart and order
        self.assertEqual(set(cart.items.values_list('variant', 'quantity')), order_items)

    def test_order_is_deleted_when_all_cart_items_are_deleted(self):
        order = self._create_order(self.anon_client)
        for cart_item in order.cart.get_all_items():
            self.assertTrue(self.checkout_app.order_model.objects.filter(pk=order.pk).exists())
            order.cart.replace_item(cart_item.variant, 0)
        self.assertFalse(self.checkout_app.order_model.objects.filter(pk=order.pk).exists())
