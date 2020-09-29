from __future__ import absolute_import
from django.test import TestCase



class VariantStockLevelTest(TestCase):
    def setUp(self):
        from .models import StockedDeadParrot
        self.cockatoo = StockedDeadParrot.objects.create(slug='cockatoo', species='White Cockatoo')
        self.cockatoo_white_a = self.cockatoo.variants.create(color='white', looks_alive=True, stock_level=2)

    def test_stocklevels(self):
        from .....cart.models import Cart
        cart = Cart.objects.create(typ='satchless.test.cart')
        cart.replace_item(self.cockatoo_white_a, 2)
        self.assertEqual(cart.get_quantity(self.cockatoo_white_a), 2)
        cart.add_item(self.cockatoo_white_a, 1)
        self.assertEqual(cart.get_quantity(self.cockatoo_white_a), 2)
