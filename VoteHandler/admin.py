# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Category)
admin.site.register(models.Disposable)
admin.site.register(models.DisposableVote)
admin.site.register(models.Configuration)