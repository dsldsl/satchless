# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.conf import settings
from django.test import TestCase

class BaseTestCase(TestCase):
    def _setup_settings(self, custom_settings):
        original_settings = {}
        for setting_name, value in custom_settings.items():
            if hasattr(settings, setting_name):
                original_settings[setting_name] = getattr(settings,
                                                          setting_name)
            setattr(settings, setting_name, value)
        return original_settings

    def _teardown_settings(self, original_settings, custom_settings=None):
        custom_settings = custom_settings or {}
        for setting_name, value in original_settings.items():
            setattr(settings, setting_name, value)
            if setting_name in custom_settings:
                del custom_settings[setting_name]
        for setting_name, value in custom_settings.items():
            delattr(settings, setting_name)
