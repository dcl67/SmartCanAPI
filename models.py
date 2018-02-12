# -*- coding: utf-8 -*-
from __future__ import unicode_literals
#from django.db import models
from django_mysql.models import JSONField, model


# Create your models here.
class Disposables(Models.model):
    name = models.CharField(max_length=250)
    votes = JSONField(default={})
    msg = models.ForeignKey(WarningMessage, on_delete=model.CASCADE)

class Materials(Models.model):
    material=models.CharField(max_length=100)

class WarningMessage(Models.model):
        msg = models.CharField(max_length=300, verbose_name='Warning Message')
