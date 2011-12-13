from decimal import Decimal
from django.test import TestCase
from django.db import models as django_models

from . import models, DiscountApplicationHandler, DiscountEligibilityHandler,\
    DiscountPricingHandler
from .queue import DiscountApplicationQueue, DiscountEligibilityQueue
from ....product.tests import DeadParrot
from ....cart.models import Cart, CartItem
from ....pricing import Price, PricingHandler
from ....pricing.handler import PricingQueue

class DiscountApplicationTest(TestCase):
    class OneDollarOffApplicationHandler(DiscountApplicationHandler):
        def get_variant_discount(self, variant, discount, discount_types,
                                 price, original_price, **kwargs):
            return Decimal('1')


    class CustomOffApplicationHandler(DiscountApplicationHandler):
        def get_variant_discount(self, variant, discount, discount_types,
                                 price, original_price,
                                 **context):
            return context.get('deduction', Decimal('0'))


    class CustomPercentOffApplicationHandler(DiscountApplicationHandler):
        def get_variant_discount(self, variant, discount, discount_types,
                                 price, original_price,
                                 **context):
            return context.get('percent', Decimal('0')) * price.gross


    def setUp(self):
        self.product = DeadParrot.objects.create(species='Fjord Piner')
        self.variant = self.product.variants.create(color='blue',
                                                    looks_alive=False)

    def test_context_passed(self):
        original_price = Decimal('10')
        price = Price(net=original_price)
        app_queue = DiscountApplicationQueue(self.CustomOffApplicationHandler)
        discount = app_queue.get_variant_discount(self.product, None, None,
                                                  price, price,
                                                  deduction=Decimal('8'))
        self.assertEqual(discount, Decimal('8'))

    def test_static_amount_deduction(self):
        original_price = Decimal('10')
        price = Price(net=original_price)
        app_queue = DiscountApplicationQueue(
            self.OneDollarOffApplicationHandler)
        discount = app_queue.get_variant_discount(self.product, None, None,
                                                  price, price)
        self.assertEqual(discount, Decimal('1'))

    def test_static_amount_deduction_stack(self):
        original_price = Decimal('10')
        price = Price(net=original_price)
        app_queue = DiscountApplicationQueue(
            self.OneDollarOffApplicationHandler,
            self.CustomOffApplicationHandler)
        discount = app_queue.get_variant_discount(self.product, None, None,
                                                  price, price,
                                                  deduction=Decimal('8'))
        self.assertEqual(discount, Decimal('9'))

    def test_percent_deduction(self):
        original_price = Decimal('10')
        price = Price(net=original_price)
        app_queue = DiscountApplicationQueue(
            self.CustomPercentOffApplicationHandler)
        discount = app_queue.get_variant_discount(self.variant, None, None,
                                                  price, price,
                                                  percent=Decimal('0.1'))
        self.assertEqual(discount, Decimal('1'))

    def test_percent_deduction_stack(self):
        original_price = Decimal('10')
        price = Price(net=original_price)
        app_queue = DiscountApplicationQueue(
            self.CustomPercentOffApplicationHandler,
            self.CustomPercentOffApplicationHandler)
        discount = app_queue.get_variant_discount(self.product, None, None,
                                                  price, price,
                                                  percent=Decimal('0.1'))
        self.assertEqual(discount, Decimal('1.90'))


class DiscountEligibilityTest(TestCase):
    def setUp(self):
        self.product = DeadParrot.objects.create(species='Slug')
        self.variant = self.product.variants.create(color='blue',
                                                    looks_alive=False)

        self.discount_type_1_off = models.DiscountType.objects.create(
            name='1.00 off')
        self.discount_type_5_off = models.DiscountType.objects.create(
            name='5.00 off')
        self.discount_type_original = models.DiscountType.objects.create(
            name='Awesome discount')
        self.discount_type_exclusive = models.DiscountType.objects.create(
            name='New discount')

    def _create_append_handler(self, append_types=None):
        class CustomAppendEligibilityHandler(DiscountApplicationHandler):
            def get_variant_discount_types(self, variant, discount_types,
                                           **context):
                return discount_types + append_types or []
        return CustomAppendEligibilityHandler

    def test_context_passed(self):
        class ContextEligibilityHandler(DiscountEligibilityHandler):
            def get_variant_discount_types(self, variant, discount_types,
                                           **context):
                if context.get('discount_type'):
                    discount_types.append(context['discount_type'])
                return discount_types

        discount_type = self.discount_type_1_off
        elig_queue = DiscountEligibilityQueue(ContextEligibilityHandler)
        discount_types = elig_queue.get_variant_discount_types(self.product, [],
            discount_type=discount_type)
        self.assertEqual(discount_types, [discount_type])

    def test_discount_types_passed(self):
        scope = self
        def create_check_handler(check_types=None):
            class CheckTypeEligibilityHandler(DiscountApplicationHandler):
                def get_variant_discount_types(self, variant, discount_types,
                                               **context):
                    for check_type in check_types:
                        scope.assertTrue(check_type in discount_types,
                            '%s not found in %s' % (check_type, discount_types))
                    return discount_types
            return CheckTypeEligibilityHandler

        elig_queue = DiscountEligibilityQueue(
            self._create_append_handler([self.discount_type_1_off]),
            self._create_append_handler([self.discount_type_5_off]),
            create_check_handler([self.discount_type_1_off,
                                  self.discount_type_5_off]),
            self._create_append_handler([self.discount_type_original]))

        discount_types = elig_queue.get_variant_discount_types(self.product, [])
        self.assertEqual(discount_types, [self.discount_type_1_off,
                                          self.discount_type_5_off,
                                          self.discount_type_original])

    def test_exclusivity(self):
        scope = self
        class NewDiscountEligibilityHandler(DiscountEligibilityHandler):
            def get_variant_discount_types(self, variant, discount_types,
                                           **context):
                if scope.discount_type_original in discount_types:
                    discount_types.remove(scope.discount_type_original)
                discount_types.append(scope.discount_type_exclusive)
                return discount_types

        elig_queue = DiscountEligibilityQueue(
            self._create_append_handler([self.discount_type_original]),
            NewDiscountEligibilityHandler)
        discount_types = elig_queue.get_variant_discount_types(self.product, [])
        self.assertEqual(discount_types, [self.discount_type_exclusive])


class DiscountPricingHandlerTest(TestCase):
    ORIGINAL_PRICE = 15
    DISCOUNT_AMOUNT = 10

    class TestCartItem(CartItem):
        cart = django_models.ForeignKey(Cart)

    def setUp(self):
        self.product = DeadParrot.objects.create(species='Norwegian Blue')
        self.variant = self.product.variants.create(color='blue',
                                                    looks_alive=False)

        discount_type = models.DiscountType.objects.create(name='test')

        scope = self
        class TestEligibilityHandler(DiscountEligibilityHandler):
            def get_variant_discount_types(self, variant, discount_types,
                                           **context):
                discount_types.append(discount_type)
                return discount_types

        class TestApplicationHandler(DiscountApplicationHandler):
            def get_variant_discount(self, variant, discount, discount_types,
                                     price, original_price, **context):
                return Decimal(scope.DISCOUNT_AMOUNT)

        class TestSimplePricingHandler(PricingHandler):
            def get_variant_price(self, variant, currency, quantity=1, **kwargs):
                return Price(net=scope.ORIGINAL_PRICE)

        elig_queue = DiscountEligibilityQueue(TestEligibilityHandler())
        app_queue = DiscountApplicationQueue(TestApplicationHandler())
        self.pricing_handler = DiscountPricingHandler(elig_queue=elig_queue,
                                                      app_queue=app_queue)
        
        self.pricing_queue = PricingQueue(TestSimplePricingHandler,
                                          self.pricing_handler)

    def test_discount_objects_not_created_before_order(self):
        original_discounts_count = models.Discount.objects.count()
        price = self.pricing_queue.get_variant_price(self.variant)
        discounts_count = models.Discount.objects.count()

        self.assertEqual(price.gross, self.ORIGINAL_PRICE - self.DISCOUNT_AMOUNT,
                         'Price incorrectly calculated (got %.2f, expected %.2f)'
                         % (price.gross,
                            self.ORIGINAL_PRICE - self.DISCOUNT_AMOUNT))
        self.assertEqual(original_discounts_count, discounts_count,
                         'Discount objects incorrectly created before'
                         '`cartitem` passed.')

    def test_discount_objects_created_for_order(self):
        cart = Cart.objects.create()
        cartitem = self.TestCartItem.objects.create(variant=self.variant,
                                                    quantity=1, cart=cart)
        try:
            original_discounts_count = models.Discount.objects.count()
            price = self.pricing_queue.get_variant_price(self.variant,
                                                         cartitem=cartitem)
            discounts_count = models.Discount.objects.count()

            self.assertEqual(price.gross, self.ORIGINAL_PRICE - self.DISCOUNT_AMOUNT,
                             'Price incorrectly calculated (got %.2f, expected %.2f)'
                             % (price.gross,
                                self.ORIGINAL_PRICE - self.DISCOUNT_AMOUNT))
            self.assertEqual(original_discounts_count + 1, discounts_count,
                             'Discount object not created when `cartitem` passed.')
        finally:
            cart.delete()
            cartitem.delete()
