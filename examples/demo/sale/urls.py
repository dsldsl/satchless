# -*- coding:utf-8 -*-
from django.conf.urls import *

from . import views

urlpatterns = [
    url(r'^$', views.index, name='sale'),
    url(r'^(?P<category_slugs>(([a-z0-9_-]+/)*[a-z0-9_-]+))/$',
        views.index, name='sale'),
]
