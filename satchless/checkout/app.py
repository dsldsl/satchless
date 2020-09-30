from __future__ import absolute_import
from django.conf.urls import url
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST

from ..cart.models import Cart
from ..order import handler
from ..order.exceptions import EmptyCart
from ..order.models import Order
from ..order.signals import order_pre_confirm
from ..payment import PaymentFailure, ConfirmationFormNeeded
from ..core.app import SatchlessApp

class CheckoutApp(SatchlessApp):
    app_name = 'checkout'
    namespace = 'checkout'
    cart_model = Cart
    cart_type = 'cart'
    order_model = Order

    def get_order(self, request, order_token):
        user = request.user if request.user.is_authenticated() else None
        try:
            return self.order_model.objects.get(token=order_token, user=user)
        except self.order_model.DoesNotExist:
            return

    def checkout(self, request, order_token):
        raise NotImplementedError()
