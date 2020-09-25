from __future__ import absolute_import
from orders.models import DemoOrder
from carts.models import DemoCart
from satchless.contrib.checkout.multistep import app

class CheckoutApp(app.MulitStepCheckoutApp):

    cart_model = DemoCart
    order_model = DemoOrder

checkout_app = CheckoutApp()
