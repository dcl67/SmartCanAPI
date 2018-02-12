# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import *

# Register your models here.
admin.side.register(Disposables)
admin.site.register(Materials)
admin.site.register(WarningMessage)