from django.utils.translation import ugettext

from satchless.contrib.delivery.simplepost import models, forms
from satchless.delivery import DeliveryProvider, DeliveryType


class PostDeliveryProvider(DeliveryProvider):
    def __unicode__(self):
        return ugettext("Post delivery")

    def enum_types(self, customer=None, delivery_group=None):
        for record in models.PostShippingType.objects.all():
          yield self, DeliveryType(typ=record.typ, name=record.name)

    def get_configuration_form(self, delivery_group, typ, data):
        typ = models.PostShippingType.objects.get(typ=typ)
        instance = models.PostShippingVariant(delivery_group=delivery_group,
                                              name=typ.name,
                                              price=typ.price)
        return forms.PostShippingVariantForm(data or None, instance=instance,
                                             prefix='delivery_group-%d' %
                                             delivery_group.pk)

    def create_variant(self, delivery_group, typ, form):
        return form.save()