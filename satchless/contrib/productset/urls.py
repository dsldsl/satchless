from __future__ import absolute_import
from django.conf.urls import *
from . import views

urlpatterns = [
    url(r'(?P<slug>[a-z0-9_-]+)/$', views.details, name='satchless-product-set'),
    url(r'$', views.index, name='satchless-product-set-index'),
]
