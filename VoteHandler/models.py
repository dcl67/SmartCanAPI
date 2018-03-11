# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import uuid

from django.core.validators import MinValueValidator
from django.db import models

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

    def get_top_votes(self, slice_size=None):
        """
        Returns up to slice_size of the top vote counts for this Disposable 
        as a QuerySet of Disposeable.
        """
        votes = DisposableVote.objects.filter(disposable=self.id).select_related('category')
        if slice_size:
            return votes[:slice_size]
        else:
            return votes

    def save(self, *args, **kwargs):
        """Force name to be lowercase"""
        self.name = self.name.lower()
        return super(Disposable, self).save(*args, **kwargs)


class DisposableVote(models.Model):
    disposable = models.ForeignKey(Disposable, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    class Meta:
        unique_together = ('category','disposable')

    def __str__(self):
        return "\'{0}\' has {1} votes for \'{2}\'".format(
            self.disposable, self.count, self.category)
        # TODO: When Kevin fixes his venv to use Python 3.6 we can use this again
        # return f"{disposable} has {count} vote{count > 1 ? 's' : ''} for {category}"

    def add_votes(self, count):
        """Adds the number to this objects count then save. Returns nothing."""
        if count < 0:
            count = 0
        self.count += count
        self.save()

