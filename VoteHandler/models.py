# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

class Disposable(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class DisposableVote(models.Model):
    disposable = models.ForeignKey(Disposable, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    count = models.IntegerField()

    class Meta:
        unique_together = ('category','disposable')

    def __str__(self):
        return "{0} has {1} votes for {2}".format(disposable, count, category)
        # When Kevin fixes his venv to use Python 3.6 we can use this again
        # return f"{disposable} has {count} vote{count > 1 ? 's' : ''} for {category}"
