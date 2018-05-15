"""Models for the /api/ that handle categorization and disposal

    Models:
        Category -- the various waste categories
        Disposable -- an item that can be disposed of
        DisposableVote -- the total votes an object has recieved for a category
"""

from __future__ import unicode_literals

from django.core.exceptions import EmptyResultSet
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import QuerySet

# Create your models here.
class Category(models.Model):
    """Model representing the various waste categories

    Attriburtes:
        name {str} -- The name of the category. Ex. Metal
    """

    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Disposable(models.Model):
    """Model representing an item that can be disposed of

    Arguments:
        models {[type]} -- [description]
    """

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    def get_top_category(self) -> Category:
        """Returns the Category that had the most votes on this Disposable

        Returns:
            Category -- Disposable with the most votes
        """
        #  select_related caches these attributes when it does the query so we
        #  get the entry and the foreign fields we want to use later all in one
        #  query
        votes_set = DisposableVote.objects.filter(disposable=self.id)

        if not votes_set.exists():
            raise EmptyResultSet
        votes_set.select_related('category')

        top_category = None
        max_count = 0
        for vote in votes_set:
            if vote.count > max_count:
                top_category = vote.category
                max_count = vote.count
        return top_category

    def get_top_votes(self, slice_size: int = None) -> QuerySet:
        """Returns up to slice_size of the top vote counts for this disposable

        Keyword Arguments:
            slice_size {int} -- The number of items to take from the front of
                the list. (default: {None})

        Returns:
            QuerySet[Disposable] -- The slice of disposables with the most votes
        """
        if slice_size is not None:
            try:
                slice_size = int(slice_size)
            except (ValueError, TypeError):
                raise TypeError('slice_size must be convertible to an int')

            if slice_size < 1:
                raise IndexError('slice_size must at least 1')

        votes_set = DisposableVote.objects.filter(disposable=self.id)
        if not votes_set.exists():
            raise EmptyResultSet

        votes = votes_set.select_related('category').order_by('count')
        if slice_size is not None:
            return votes[:slice_size]
        return votes

    def save(self, *args, **kwargs):
        """Forces name to be lowercase"""
        self.name = self.name.lower()
        return super(Disposable, self).save(*args, **kwargs)


class DisposableVote(models.Model):
    """Model representing the total votes an object has recieved for a category

    Attributes:
        disposable {Disposable} -- The item that received votes
        category {Cateogry} -- The category that was voted for
        count {int} -- The total number of votes for this combination

    Restrictions:
        category and disposable are unique_together
    """

    disposable = models.ForeignKey(Disposable, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    class Meta:
        unique_together = ('category', 'disposable')

    def __str__(self):
        return f"{self.disposable} has {self.count} votes for {self.category}"

    def add_votes(self, count) -> None:
        """Adds the number to this objects count then save.

        Arguments:
            count {int} -- The number of votes to add to the count

        Returns:
            None
        """
        if count < 0:
            count = 0
        self.count += count
        self.save()
