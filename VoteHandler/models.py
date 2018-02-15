# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models

import uuid

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
    count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('category','disposable')

    def __str__(self):
        return "{0} has {1} votes for {2}".format(disposable, count, category)
        # TODO: When Kevin fixes his venv to use Python 3.6 we can use this again
        # return f"{disposable} has {count} vote{count > 1 ? 's' : ''} for {category}"

class Configuration(models.Model):
    can_id = models.UUIDField(verbose_name='Smartcan ID')
    config = models.TextField(max_length=4096)

    @staticmethod
    def new_can_id():
        """Returns a random uuid that is not alredy being used as an ID"""
        id = uuid.uuid4();
        # Odds are astronomically low of this actually colliding. Do we need this check?
        while Configuration.objects.filter(can_id=uuid).exists():
            id = uuid.uuid4()
        return id

    def __str__(self):
        return self.can_id