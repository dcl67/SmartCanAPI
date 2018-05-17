# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import EmptyResultSet
from django.db import IntegrityError
from django.test import TestCase
from django.contrib.auth.models import User

from Config.models import CanInfo, Bin
from VoteHandler.models import Category

# Constants for testing
TEST_CAN_ID = '00000000-0000-0000-0000-000000000000'
TEST_CHANNEL = '1234567890'
TEST_CONFIG = 'config'
# Test constants for Bin objects
TEST_BIN_NUMBER_0 = '0'
TEST_BIN_NUMBER_1 = '1'
TEST_BIN_NUMBER_2 = '2'
# From the VoteHandler.category class
TEST_CATEGORY = 'test_category'
TEST_CATEGORY_2 = 'test_category_2'
TEST_CATEGORY_LIST = [
    Category.objects.get(name='Landfill'),
    Category.objects.get(name='Organic'),
    Category.objects.get(name='Unknown')
]


class TestCanInfo(TestCase):
    """ Testing the CanInfo models """
    @classmethod
    def setUpTestData(cls):
        cls.caninfo = CanInfo.objects.create(
            can_id=TEST_CAN_ID,
            owner=User.objects.create_user(username=TEST_CAN_ID,email='testcan@email.com',password=''),
            channel_name=TEST_CHANNEL,
            config=TEST_CONFIG
        )
    
    def test_can_uuid(self):
        """ Testing the UUID of the can """
        self.assertEqual(str(self.caninfo.can_id), TEST_CAN_ID)

    def test_unique_uuid(self):
        """ Testing uniqueness """
        with self.assertRaises(IntegrityError):
            CanInfo.objects.create(
                name=TEST_CAN_ID,
                owner=User.objects.create_user(username=TEST_CAN_ID,email='testcan@email.com',password=''),
                channel_name=TEST_CHANNEL,
                config=TEST_CONFIG)

    def test_user(self):
        """ Testing that the associated user is indeed the can's user """
        self.assertEqual(str(self.caninfo.owner), (User.objects.get(username=TEST_CAN_ID)).username)

    def test_channel_name(self):
        self.assertEqual(str(self.caninfo.channel_name), TEST_CHANNEL)

    def test_config(self):
        self.assertEqual(str(self.caninfo.config), TEST_CONFIG)


class TestBin(TestCase):
    @classmethod
    def setUpTestData(cls):
        can_with_bins = CanInfo.objects.create(
            can_id=TEST_CAN_ID,
            owner=User.objects.create_user(username=TEST_CAN_ID,email='testcan@email.com',password=''),
            channel_name=TEST_CHANNEL,
            config=TEST_CONFIG
        )
        test_category = Category.objects.create(name=TEST_CATEGORY)
        cls.bin = Bin.objects.create(
            s_id = CanInfo.objects.get(can_id=TEST_CAN_ID,),
            bin_num = TEST_BIN_NUMBER_0,
            category = test_category
        )

    def test_bin_number(self):
        self.assertEqual(str(self.bin.bin_num),TEST_BIN_NUMBER_0)

    def test_bins_category(self):
        self.assertEqual(str(self.bin.category), Category.objects.get(name=TEST_CATEGORY).name)

    def test_unique_together(self):
        with self.assertRaises(IntegrityError):
            my_category = Category.objects.create(name=TEST_CATEGORY)
            bin1 = Bin.objects.create(
                s_id = CanInfo.objects.get(can_id=TEST_CAN_ID,),
                bin_num = TEST_BIN_NUMBER_1,
                category = my_category
            )
            bin2 = Bin.objects.create(
                s_id = CanInfo.objects.get(can_id=TEST_CAN_ID,),
                bin_num = TEST_BIN_NUMBER_2,
                category = my_category
            )

    def test_default_categories(self):
        my_category = Category.objects.create(name=TEST_CATEGORY_2)
        test_bin = Bin.objects.create(
            s_id = CanInfo.objects.get(can_id=TEST_CAN_ID,),
            bin_num = TEST_BIN_NUMBER_1,
            category = my_category
        )
        self.assertEquals(test_bin.DEFAULT_CATEGORIES,TEST_CATEGORY_LIST)
