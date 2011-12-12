class DiscountEligibilityHandler(object):
    def get_variant_discount_types(self, variant, discount_types, **context):
        raise NotImplementedError()

class DiscountApplicationHandler(object):
    def get_variant_discount(self, variant, discount, discount_types, price,
                             original_price, **context):
        raise NotImplementedError()
