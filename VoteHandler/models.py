# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django_mysql.models import JSONField, Model


# Create your models here.
class WarningMessage(Model):
    msg = models.CharField(max_length=300, verbose_name='Warning Message')

    def __str__(self):
        return self.msg

class Disposable(Model):
    name = models.CharField(max_length=250)
    votes = JSONField()
    msg = models.ForeignKey(WarningMessage, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

class Material(Model):
    material=models.CharField(max_length=100)

    def __str__(self):
        return self.material
