from decimal import Decimal
from django.conf import settings

from ....pricing import Price
from ....core.handler import QueueHandler
from .  import DiscountEligibilityHandler, DiscountApplicationHandler

__all__ = ['DiscountEligibilityQueue', 'DiscountApplicationQueue']

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

discount_eligibility_handlers = getattr(settings,
    'SATCHLESS_DISCOUNT_ELIGIBILITY_HANDLERS', [])
discount_eligibility_queue = DiscountEligibilityQueue(
    *discount_eligibility_handlers)

discount_application_handlers = getattr(settings,
    'SATCHLESS_DISCOUNT_APPLICATION_HANDLERS', [])
discount_application_queue = DiscountApplicationQueue(
    *discount_application_handlers)