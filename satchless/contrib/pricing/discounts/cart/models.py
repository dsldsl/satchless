from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist

from .....cart.models import Cart

class DiscountsCart(Cart):
    class Meta:
        proxy = True

    def get_item(self, variant, **kwargs):
        cart_item_class = self.get_cart_item_class()
        return cart_item_class.objects.get(cart=self, variant=variant, **kwargs)
