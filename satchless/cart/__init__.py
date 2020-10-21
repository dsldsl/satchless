from __future__ import absolute_import
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

if not getattr(settings, 'SATCHLESS_DEFAULT_CURRENCY', None):
    raise ImproperlyConfigured('You need to configure '
                               'SATCHLESS_DEFAULT_CURRENCY')