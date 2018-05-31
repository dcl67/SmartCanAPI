from typing import List, Tuple
from unittest.mock import patch

from django.contrib.auth.models import User
from django.conf import settings
from django.test import TestCase

from Config.models import CanInfo
from ..models import Category, Disposable, DisposableVote
from ..utils import send_rotate_to_can, votes_to_percentages


class SendRotateToCanTestCase(TestCase):
    BIN_NUM = 1
    CHANNEL_NAME = 'name'
    UUID = '00000000-0000-0000-0000-000000000000'

    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user(username=cls.UUID.replace('-', ''),
                                            password='')

    def setUp(self):
        _ = Category.objects.create(id=19, name='Landfill')
        CanInfo.objects.update_or_create(can_id=self.UUID,
                                         owner=self.USER,
                                         channel_name=self.CHANNEL_NAME)

    def test_user_is_none(self):
        """Does a None user return False"""
        self.assertFalse(send_rotate_to_can(None, self.BIN_NUM))

    def test_can_info_does_not_exist(self):
        """A CanInfo where a matching user cannot be found returns False"""
        fake_user = User(username='Fake', password='')
        self.assertFalse(send_rotate_to_can(fake_user, self.BIN_NUM))

    def test_request_channel_is_none(self):
        """When the channel on the CanInfo is None, return False"""
        CanInfo.objects.filter(can_id=self.UUID).update(channel_name=None)
        self.assertFalse(send_rotate_to_can(self.USER, self.BIN_NUM))

    # So it turns out you need to address where the funcends up, not where it
    # comes from. You also need to address this location in a way that this
    # file can find it, hence the VoteHandler prefix
    @patch('VoteHandler.utils.get_channel_layer')
    @patch('VoteHandler.utils.async_to_sync')
    def test_valid_input_succeeds(self, async_patch, chan_patch):
        """When called with valid input, the func returns True"""
        self.assertTrue(send_rotate_to_can(self.USER, self.BIN_NUM))
        async_patch.assert_called_once()
        chan_patch.assert_called_once()


class VotesToPercentagesTestCase(TestCase):
    CATEGORY_NAME = 'test_Category'
    DISPOSABLE_NAME = 'test_Disposable'

    @staticmethod
    def make_votes(vote_tuples: List[Tuple[Disposable, Category, int]]):
        """Convenience method for adding votes quickly"""
        for vote_tuple in vote_tuples:
            DisposableVote.objects.create(disposable=vote_tuple[0],
                                          category=vote_tuple[1],
                                          count=vote_tuple[2])

    def test_success(self):
        """Returns votes as a list sorted tuples"""
        disposable_under_min = Disposable.objects.create(name=self.DISPOSABLE_NAME + '_1')
        disposable_over_min = Disposable.objects.create(name=self.DISPOSABLE_NAME + '_2')
        category_1 = Category.objects.create(name=self.CATEGORY_NAME + '_1')
        category_2 = Category.objects.create(name=self.CATEGORY_NAME + '_2')
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

    def test_wrong_input_type(self):
        """If votes is not a QuerySet or contains the wrong model, TypeError is raised"""
        with self.assertRaises(TypeError):
            votes_to_percentages(['not', 'a', 'queryset'])
        with self.assertRaises(TypeError):
            votes_to_percentages(Disposable.objects.all())

    def test_empty_votes(self):
        """If votes is empty, a ValueError is raised"""
        with self.assertRaises(ValueError):
            votes_to_percentages(DisposableVote.objects.none())
