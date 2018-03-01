# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models

import uuid

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Disposable(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    def get_top_category(self):
        """
        Returns the Category that had the most votes on this Disposable.
        """
        #  select_related cache's these attributes when it does the query so we get the
        #  entry and the foreign fields we want to use later all in one query
        votes = DisposableVote.objects.filter(disposable=self.id).select_related('category')
        top_category, max_count = None, 0
        for vote in votes:
            if vote.count > max_count:
                top_category = vote.category
                max_count = vote.count
        return top_category

    def get_top_votes(self, slice_size=3):
        """
        Returns up to slice_size of the top votes for this Disposable as a list of tuples
        in the form ('category', count).
        """
        votes = DisposableVote.objects.filter(disposable=self.id).select_related('category')
        total = 0
        for vote in votes:
            total += v.count
        d = {v.category.name: v.count/total for v in votes} 
        return sorted(d.items(), key=lambda x: x[1]/total)[:slice_size]

    def save(self, *args, **kwargs):
        """Force name to be lowercase"""
        self.name = self.name.lower()
        return super(Disposable, self).save(*args, **kwargs)


class DisposableVote(models.Model):
    disposable = models.ForeignKey(Disposable, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('category','disposable')

    def __str__(self):
        return "\'{0}\' has {1} votes for \'{2}\'".format(
            self.disposable, self.count, self.category)
        # TODO: When Kevin fixes his venv to use Python 3.6 we can use this again
        # return f"{disposable} has {count} vote{count > 1 ? 's' : ''} for {category}"

