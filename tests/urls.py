# -*- coding:utf-8 -*-
from django.conf.urls import patterns, url, include

from satchless.cart.app import cart_app
from satchless.category.app import product_app as category_app
from satchless.product.app import product_app
from satchless.order.app import order_app

urlpatterns = patterns('',
    url(r'^category/', include(category_app.urls)),
    url(r'^product/', include(product_app.urls)),
    url(r'^cart/', include(cart_app.urls)),
    url(r'^contact/', include('satchless.contact.urls')),
    url(r'^order/', include(order_app.urls)),
    url(r'^image/', include('satchless.satchless_image.urls')),
)
