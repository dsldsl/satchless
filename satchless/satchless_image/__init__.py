from __future__ import absolute_import
from django.conf import settings

IMAGE_SIZES = getattr(settings, 'SATCHLESS_IMAGE_SIZES', {})
