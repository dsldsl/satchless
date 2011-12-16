from django.db import models
from ....util.models import Subtyped
from ....order.models import Order, OrderedItem

class DiscountType(Subtyped):
    name = models.CharField(max_length=128, unique=True)

    def __unicode__(self):
        return self.name


class Discount(Subtyped):
    type = models.ForeignKey(DiscountType, related_name='discounts')
    item = models.ForeignKey(OrderedItem, related_name='discounts')
    deduction = models.DecimalField(max_digits=12, decimal_places=4)

    def __unicode__(self):
        return u'%.2f off %s' % (self.deduction, self.item)


class DiscountOrder(Order):
    class Meta:
        proxy = True

    def create_ordered_item(self, delivery_group, item, **context):
        variant = item.variant.get_subtype_instance()
        name = unicode(variant)
        ordered_item_class = self.get_ordered_item_class(**context)
        ordered_item = ordered_item_class(delivery_group=delivery_group,
                                          product_variant=item.variant,
                                          product_name=name,
                                          quantity=item.quantity,
                                          unit_price_net=-1,
                                          unit_price_gross=-1,
                                          **context)
        # Save the ordered_item, because its ID will be needed in the Discount
        # instance's `item` foreign key.
        ordered_item.save()

        price = item.get_unit_price(delivery_group=delivery_group,
                                    ordered_item=ordered_item, **context)
        ordered_item.unit_price_net = price.net
        ordered_item.unit_price_gross = price.gross

        return ordered_item
