# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class disposable(models.Model):
    name=models.CharField(max_length=500)
    votes=models.CharField(max_length=9999)
