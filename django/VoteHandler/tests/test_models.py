# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from unittest import skip

from django.core.exceptions import EmptyResultSet
from django.db import IntegrityError
from django.test import TestCase

from VoteHandler.models import Category, Disposable, DisposableVote


TEST_CATEGORY_NAME = 'test_Category'
TEST_DISPOSABLE_NAME = 'test_Disposable'


class CategoryTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name=TEST_CATEGORY_NAME)

    def test_categories_string(self):
        """String representation is correct on Category.objects.create objects"""
        self.assertEqual(str(self.category), TEST_CATEGORY_NAME)

    def test_category_name_unique(self):
        """Category.objects.create name uniqueness is enforced"""
        with self.assertRaises(IntegrityError):
            Category.objects.create(name=TEST_CATEGORY_NAME)


class DisposableTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.disposable = Disposable.objects.create(name=TEST_DISPOSABLE_NAME)
        cls.disposable_no_votes = Disposable.objects.create(name=TEST_DISPOSABLE_NAME + '_1')
        cls.category_1 = Category.objects.create(name=TEST_CATEGORY_NAME + '_1')
        cls.category_2 = Category.objects.create(name=TEST_CATEGORY_NAME + '_2')
        cls.votes_1 = DisposableVote.objects.create(disposable=cls.disposable,
                                                    category=cls.category_1,
                                                    count=1)
        cls.votes_2 = DisposableVote.objects.create(disposable=cls.disposable,
                                                    category=cls.category_2,
                                                    count=2)

    def test_disposable_string(self):
        """String representation is correct on Disposable objects"""
        self.assertEqual(str(self.disposable), TEST_DISPOSABLE_NAME.lower())

    def test_disposable_name_unique(self):
        """Name uniqueness is enforced"""
        with self.assertRaises(IntegrityError):
            Disposable.objects.create(name=TEST_DISPOSABLE_NAME)

    def test_disposable_get_top_category(self):
        """Correct top category is returned from valid call"""
        self.assertEqual(self.disposable.get_top_category(), self.category_2)

    @skip('Need to implement EmptyResultSet exception in function')
    def test_disposable_get_top_category_empty_filter(self):
        """Correct error is raised when top category is called but there are no votes"""
        with self.assertRaises(EmptyResultSet):
            self.disposable_no_votes.get_top_category()

    def test_disposable_get_top_votes(self):
        """Get top votes with varying slice size"""
        votes_list = [self.votes_1, self.votes_2]
        self.assertCountEqual(list(self.disposable.get_top_votes()), votes_list)
        self.assertCountEqual(list(self.disposable.get_top_votes(3)), votes_list[:3])
        self.assertCountEqual(list(self.disposable.get_top_votes(2)), votes_list[:2])
        self.assertCountEqual(list(self.disposable.get_top_votes(1)), votes_list[:1])

    @skip('Need to implement ValueError exception in function')
    def test_disposable_get_top_votes_bad_slice_size(self):
        """Get top votes when slice size is less than one or not an integer"""
        with self.assertRaises(ValueError):
            self.disposable.get_top_votes(0)
        with self.assertRaises(ValueError):
            self.disposable.get_top_votes(-1)
        with self.assertRaises(TypeError):
            self.disposable.get_top_votes('Not an int')

    @skip('Need to implement EmptyResultSet exception in function')
    def test_disposable_get_top_votes_empty_filter(self):
        """Correct error is raised when top votes is called but there are no votes"""
        with self.assertRaises(EmptyResultSet):
            self.disposable_no_votes.get_top_category()

    def test_disposable_save_lowercases_name(self):
        """Save lowercases the name field"""
        test_name = 'UPPER'
        new_disposable = Disposable.objects.create(name='someName')
        new_disposable.name = test_name
        # Check that there was originally at least one upper case chatacter
        self.assertIn(True, [s.isupper() for s in new_disposable.name])
        new_disposable.save()
        self.assertEqual(new_disposable.name, test_name.lower())


class DisposableVoteTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.disposable = Disposable.objects.create(name=TEST_DISPOSABLE_NAME)
        cls.category = Category.objects.create(name=TEST_CATEGORY_NAME)
        cls.votes = DisposableVote.objects.create(disposable=cls.disposable,
                                                  category=cls.category,
                                                  count=1)

    def setUp(self):
        # Restore votes to 1 in case we changed anything
        self.votes.count = 1
        self.votes.save()

    def test_disposablevote_string(self):
        """Proper string representation for DisposableVote"""
        string = f'{TEST_DISPOSABLE_NAME.lower()} has 1 votes for {TEST_CATEGORY_NAME}'
        self.assertEqual(str(self.votes), string)

    def test_disposablevote_add_votes_valid(self):
        """Correct number of votes are added when add_votes is called"""
        old_count = self.votes.count
        self.votes.add_votes(0)
        self.assertEqual(self.votes.count, old_count)
        self.votes.add_votes(1)
        self.assertEqual(self.votes.count, old_count + 1)
        self.votes.add_votes(10)
        self.assertEqual(self.votes.count, old_count + 1 + 10)

    @skip('Need to implement TypeError exception in function')
    def test_disposablevote_add_votes_bad(self):
        """Negative and non-integer inputs are handled for add_votes"""
        old_count = self.votes.count
        self.votes.add_votes(-1)
        self.assertEqual(self.votes.count, old_count)
        self.votes.add_votes(-100)
        self.assertEqual(self.votes.count, old_count)

        with self.assertRaises(TypeError):
            self.votes.add_votes('not an integer')
