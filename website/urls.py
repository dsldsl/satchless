from django.conf.urls import *

urlpatterns = [
    url(r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'index.html'}),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'static/'}),
]
