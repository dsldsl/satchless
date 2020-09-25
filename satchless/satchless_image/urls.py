from django.conf.urls import *
from . import views

urlpatterns = [
    url(r'^thumbnail/(?P<image_id>\d+)/(?P<size>[^/]+)/$', views.thumbnail, name='satchless-image-thumbnail'),
]
