"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from __future__ import absolute_import
import datetime
from django import forms
from django.test import TestCase

from . import models
from . import PaymentProvider, PaymentType


class TestPaymentProvider(PaymentProvider):
    def enum_types(self, order=None, customer=None):
        yield self, PaymentType('gold', 'gold')

    def get_configuration_form(self, order, data, typ=None):
        return None

    def create_variant(self, order, form, typ=None):
        typ = typ or order.payment_type
        payment_variant = models.PaymentVariant.objects.create(order=order,
                                                            price=0,
                                                            amount=0,
                                                            name='test')
        return payment_variant

    def confirm(self, order, typ=None, variant=None):
        pass
