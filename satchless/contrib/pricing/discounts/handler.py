from decimal import Decimal
from django.conf import settings

from ....core.handler import QueueHandler
from ....pricing import PricingHandler, Price
from . import DiscountEligibilityHandler, DiscountApplicationHandler
from .models import Discount

class DiscountEligibilityQueue(DiscountEligibilityHandler, QueueHandler):
    def get_variant_discount_types(self, variant, discount_types, **context):
        if discount_types is None:
            discount_types = []
        for handler in self.queue:
            discount_types = handler.get_variant_discount_types(
                                                variant,
                                                discount_types,
                                                **context)
        return discount_types


class DiscountApplicationQueue(DiscountApplicationHandler, QueueHandler):
    def get_variant_discount(self, variant, discount, discount_types, price,
                             original_price, **context):
        total_deduction = Decimal('0')
        for handler in self.queue:
            deduction = handler.get_variant_discount(variant, discount,
                                                     discount_types, price,
                                                     original_price, **context)
            total_deduction += deduction
            price = Price(net=price.net - deduction)
        return total_deduction


discount_eligibility_handlers = getattr(settings, 'SATCHLESS_DISCOUNT_ELIGIBILITY_HANDLERS', [])
discount_eligibility_queue = DiscountEligibilityQueue(*discount_eligibility_handlers)

discount_application_handlers = getattr(settings, 'SATCHLESS_DISCOUNT_APPLICATION_HANDLERS', [])
discount_application_queue = DiscountApplicationQueue(*discount_application_handlers)


class DiscountPricingHandler(PricingHandler):
    def __init__(self, elig_queue=discount_eligibility_queue,
                 app_queue=discount_application_queue):
        self.elig_queue = elig_queue
        self.app_queue = app_queue

    def get_product_price_range(self, product, currency, **kwargs):
        return kwargs.get('price_range')

    def get_variant_price(self, variant, currency, quantity=1, **kwargs):
        # cartitem is passed when transferring items from the cart to the order
        cartitem = kwargs.get('cartitem')

        discount_types = self.elig_queue.get_variant_discount_types(variant, [],
                                                                    **kwargs)

        price = kwargs.get('price')
        discount_total = Decimal('0')
        for discount_type in discount_types:
            discount = Discount(type=discount_type,
                                    deduction=Decimal('0'))
            type_total = self.app_queue.get_variant_discount(variant, discount,
                                                             discount_types,
                                                             price, price)
            if cartitem:
                discount.deduction = type_total
                discount.save()
            discount_total += type_total

        price = Price(net=price.gross - discount_total)
        return price

