from __future__ import absolute_import
from satchless.category import app

from .models import Category

class CategorizedProductApp(app.CategorizedProductApp):
    category_model = Category


product_app = CategorizedProductApp()