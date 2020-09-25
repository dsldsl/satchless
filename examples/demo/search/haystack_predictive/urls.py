# -*- coding:utf-8 -*-
from __future__ import absolute_import
from django.conf.urls import *

from . import views

urlpatterns = patterns('haystack.views',
    url(r'^$', views.search_products, name='satchless-search-haystack-predictive'),
)
