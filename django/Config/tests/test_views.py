from unittest.mock import patch
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.db import IntegrityError
from django.http import JsonResponse

from Config.models import Bin, CanInfo
from VoteHandler.models import Category
from Config.forms import CanConfigurationForm, ConfigurationForm
from Config.views import register

import json

UUID = '00000000-0000-0000-0000-100000000000'
user_UUID = '00000000000000000000000000000000'

class TestCategorization(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user('test_user', password='')

    def test_config_no_text(self):
        """ Text box is left empty """
        self.client.test_user = self.test_user
        self.client.force_login(self.test_user)
        resp = self.client.post(
            reverse('Config:configlist'),
            data={}
        )
        self.assertTemplateUsed(resp, 'landing.html')
        self.assertIsNotNone(resp.context['error_message'])


class TestHome(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user('test_user', password='')

    def test_home(self):
        """ Simple test for home template """
        resp = self.client.get(
            reverse('Config:config_home')
        )
        self.assertTemplateUsed(resp, 'landing.html')



class TestConfigureCan(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(user_UUID, password='')

    # def test_can_configure(self):
        # """ TODO: Test submitting CanConfigurationForm TODO: This isn't working """
        # can = CanInfo.objects.get_or_create(
        #     can_id=user_UUID,
        #     owner=self.user,
        #     channel_name=None,
        #     config=''
        # )
        # can_user = self.user
        # form = CanConfigurationForm({
        #     'can_id_id': "00000000000000000000000000000000",
        #     'owner': "00000000000000000000000000000000",
        #     'channel_name': "",
        #     'config': ""
        # })
        # self.assertTrue(form.is_valid())
        # canconfig = form.save()
        # self.assertEqual(canconfig.can_id, user_UUID)
        # self.assertEqual(canconfig.owner, can_user)

    def test_invalid_form_no_can_id(self):
        """ Form should be invalid due to no specified can_id """
        form = CanConfigurationForm({
            'can_id': '',
            'owner': self.user,
            'channel_name': None,
            'config': ''
        })
        self.assertFalse(form.is_valid())

    def test_invalid_form_no_owner(self):
        """ Form should be invalid due to no specified owner """
        form = CanConfigurationForm({
            'can_id': user_UUID,
            'owner': '',
            'channel_name': None,
            'config': ''
        })
        self.assertFalse(form.is_valid())


class TestBinInfo(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(user_UUID, password='')

    def test_bin_detail_view(self):
        """ Test that built-in detail view is rendering specified template """
        resp = self.client.get(
            reverse('Config:config_detail', kwargs={'pk':1})
        )
        self.assertTemplateUsed('info.html')

    # def test_bin_configure_form(self):
        #test_can = CanInfo.objects.get_or_create(
        #   can_id=user_UUID,
        #   owner=self.user,
        #   channel_name=None,
        #   config=''
        #)
        #test_category = Category.objects.create(
        #   name="test_category"
        # )
        #form=ConfigurationForm({
        #    's_id': test_can,
        #    'bin_num': 1,
        #     'category': test_category
        # })
        # self.assertTrue(form.is_valid())
        # binconfig = form.save()
        # self.assertEqual(binconfig.s_id, test_can)
        # self.assertEqual(binconfig.bin_num, 1)
        # self.assertEqual(binconfig.category, test_category)

    def test_no_s_id_bin_configure_form(self):
        """ Form should be invalid due to no specified s_id """
        test_category = Category.objects.create(name="test_category")
        form = ConfigurationForm({
            's_id': None,
            'bin_num': 1,
            'category': test_category
        })
        self.assertFalse(form.is_valid())

    def test_no_bin_num_configure_form(self):
        """ Form should be invalid due to no specified bin number """
        test_can = CanInfo.objects.get_or_create(
            can_id=user_UUID,
            owner=self.user,
            channel_name=None,
            config=''
        )
        test_category = Category.objects.create(name="test_category")
        form = ConfigurationForm({
            's_id': test_can,
            'bin_num': None,
            'category': test_category
        })
        self.assertFalse(form.is_valid())

    def test_no_category_configure_form(self):
        """ Form should be invalid due to no specified category """
        test_can = CanInfo.objects.get_or_create(
            can_id=user_UUID,
            owner=self.user,
            channel_name=None,
            config=''
        )
        test_category = Category.objects.create(name="test_category")
        form = ConfigurationForm({
            's_id': test_can,
            'bin_num': 1,
            'category': None
        })
        self.assertFalse(form.is_valid())


class TestRegistration(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(user_UUID, password='')

    # def test_can_registration(self):
    #     can_test = CanInfo.objects.get_or_create(can_id=UUID, owner=self.user, channel_name="test", config="test")
    #     try:
    #         test_user = User.objects.get(username=UUID)
    #         if test_user.exists():
    #             test_user.delete()
    #     except:
    #         self.client.user = self.user
    #         self.client.force_login(self.user)
    #         resp = self.client.post(reverse('Config:register', args=[UUID]))

    def test_already_created_registration(self):
        can_test = CanInfo.objects.get_or_create(can_id=UUID, owner=self.user, channel_name="test", config="test")
        try:
            test_user = User.objects.get(username=UUID)
            if test_user.exists():
                test_user.delete()
        except:
            self.client.user = self.user
            self.client.force_login(self.user)
            resp = self.client.post(reverse('Config:register', args=[UUID]))
            self.assertEqual(resp.json()['error'], "Can 00000000000000000000100000000000 is already registered")
