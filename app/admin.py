# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from .models import User, mailAddress, Mail

admin.site.register(User)
admin.site.register(mailAddress)
admin.site.register(Mail)
