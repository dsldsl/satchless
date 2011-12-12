from . import models
from .....cart.app import CartApp

class DiscountsCartApp(CartApp):
    cart_model = models.DiscountsCart
