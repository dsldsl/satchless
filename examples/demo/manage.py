#!/usr/bin/env python
from __future__ import absolute_import
import os

from django.core.management import execute_from_command_line

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

if __name__ == "__main__":
    execute_from_command_line()
