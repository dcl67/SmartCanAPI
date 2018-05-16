from typing import List, Tuple

from django.conf import settings
from django.test import TestCase

from ..models import Category, Disposable, DisposableVote
from ..utils import votes_to_percentages


TEST_CATEGORY_NAME = 'test_Category'
TEST_DISPOSABLE_NAME = 'test_Disposable'


class UtilsTestCase(TestCase):
    @staticmethod
    def make_votes(vote_tuples: List[Tuple[Disposable, Category, int]]):
        for vote_tuple in vote_tuples:
            DisposableVote.objects.create(disposable=vote_tuple[0],
                                          category=vote_tuple[1],
                                          count=vote_tuple[2])

    def test_votes_to_percentages(self):
        """Returns votes as a list sorted tuples"""
        disposable_under_min = Disposable.objects.create(name=TEST_DISPOSABLE_NAME + '_1')
        disposable_over_min = Disposable.objects.create(name=TEST_DISPOSABLE_NAME + '_2')
        category_1 = Category.objects.create(name=TEST_CATEGORY_NAME + '_1')
        category_2 = Category.objects.create(name=TEST_CATEGORY_NAME + '_2')
        votes = [
            (disposable_under_min, category_1, settings.MIN_NORMALIZE_COUNT/100),
            (disposable_under_min, category_2, settings.MIN_NORMALIZE_COUNT/50),
            (disposable_over_min, category_1, settings.MIN_NORMALIZE_COUNT),
            (disposable_over_min, category_2, settings.MIN_NORMALIZE_COUNT*3)
        ]
        self.make_votes(votes)

        # test when total votes is less than settings.MIN_NORMALIZE_COUNT
        votes_under = DisposableVote.objects.filter(disposable=disposable_under_min)
        tuples_under = votes_to_percentages(votes_under)
        expected_under = [(category_2.name, settings.MIN_NORMALIZE_COUNT/50),
                          (category_1.name, settings.MIN_NORMALIZE_COUNT/100)]
        self.assertEqual(expected_under, tuples_under)
        # test when total votes is greater than settings.MIN_NORMALIZE_COUNT
        votes_over = DisposableVote.objects.filter(disposable=disposable_over_min)
        tuples_over = votes_to_percentages(votes_over)
        expected_over = [(category_2.name, 3/4*100), (category_1.name, 1/4*100)]
        self.assertEqual(expected_over, tuples_over)

    def test_votes_to_percentages_wrong_input_type(self):
        """If votes is not a QuerySet or contains the wrong model, TypeError is raised"""
        with self.assertRaises(TypeError):
            votes_to_percentages(['not', 'a', 'queryset'])
        with self.assertRaises(TypeError):
            votes_to_percentages(Disposable.objects.all())

    def test_votes_to_percentages_empty_votes(self):
        """If votes is empty, a ValueError is raised"""
        with self.assertRaises(ValueError):
            votes_to_percentages(DisposableVote.objects.none())
