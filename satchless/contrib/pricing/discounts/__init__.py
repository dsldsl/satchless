from decimal import Decimal

from ....pricing import PricingHandler, Price
from .models import Discount

class DiscountEligibilityHandler(object):
    def get_variant_discount_types(self, variant, discount_types, **context):
        raise NotImplementedError()


class DiscountApplicationHandler(object):
    def get_variant_discount(self, variant, discount, discount_types, price,
                             original_price, **context):
        raise NotImplementedError()


class DiscountPricingHandler(PricingHandler):
    def __init__(self, elig_queue=None, app_queue=None):
        from .queue import discount_eligibility_queue, \
            discount_application_queue

        self.elig_queue = elig_queue or discount_eligibility_queue
        self.app_queue = app_queue or discount_application_queue

    def get_product_price_range(self, product, currency, **kwargs):
        return kwargs.get('price_range')

    def get_variant_price(self, variant, currency, quantity=1, **kwargs):
        ordered_item = kwargs.get('ordered_item')

        discount_types = self.elig_queue.get_variant_discount_types(variant, [],
                                                                    **kwargs)

        price = kwargs.pop('price', Price(currency=currency))
        discount_total = Decimal('0')
        for discount_type in discount_types:
            discount = Discount(type=discount_type,
                                    deduction=Decimal('0'))
            type_total = self.app_queue.get_variant_discount(variant, discount,
                                                             discount_types,
                                                             price, price,
                                                             **kwargs)
            if ordered_item:
                discount.deduction = type_total
                discount.item = ordered_item
                discount.save()
            discount_total += type_total

        price = Price(net=price.net - discount_total, currency=currency)
        return price
