"""Tests for VoteHandler's views"""
from unittest.mock import patch
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from Config.models import Bin, CanInfo
from ..models import Category, Disposable, DisposableVote


BIN_NUM = 0
UUID = '00000000-0000-0000-0000-000000000000'


class ViewsBaseObjectsMixin:
    """Provides some basic objects and performs login"""
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('someone', password='')

    def setUp(self):
        self.client.force_login(self.user)
        self.disposable, _ = Disposable.objects.update_or_create(name='test')
        self.category, _ = Category.objects.update_or_create(name='whatever')
        self.vote_1, _ = DisposableVote.objects.update_or_create(
            disposable=self.disposable, category=self.category, count=1
        )


class CategorizeTestCase(ViewsBaseObjectsMixin, TestCase):
    def test_disposable_not_in_db(self):
        """Renders an error but no table when the disposable does not exist"""
        resp = self.client.get(
            reverse('VoteHandler:categorize', kwargs={'disposable_name': 'not in db'})
        )
        self.assertIsNotNone(resp.context['error_message'])
        self.assertIsNone(resp.context['votes'])
        self.assertTemplateUsed(resp, 'VoteHandler/categorize.html')

    def test_disposable_has_no_votes(self):
        """Renders no error and no table when the disposable has no votes"""
        DisposableVote.objects.all().delete()
        resp = self.client.get(
            reverse('VoteHandler:categorize', kwargs={'disposable_name': self.disposable.name})
        )
        self.assertIsNone(resp.context['error_message'])
        self.assertIsNone(resp.context['votes'])
        self.assertTemplateUsed(resp, 'VoteHandler/categorize.html')

    def test_success_has_votes(self):
        """Renders a table but no error when the disposable has votes"""
        resp = self.client.get(
            reverse('VoteHandler:categorize', kwargs={'disposable_name': self.disposable.name})
        )
        self.assertIsNone(resp.context['error_message'])
        self.assertIsNotNone(resp.context['votes'])
        self.assertContains(resp, self.category.name)
        self.assertTemplateUsed(resp, 'VoteHandler/categorize.html')


class CarouselVoteTestCase(ViewsBaseObjectsMixin, TestCase):
    def test_disposable_not_found(self):
        """DoesNotExist error when disposable doesn't exist"""
        data = {'disp_item': 'does not exist', 'vote': self.category.name}
        with self.assertRaises(Disposable.DoesNotExist):
            self.client.post(reverse('VoteHandler:carousel_vote'), data)

    def test_category_not_found(self):
        """DoesNotExist error when category doesn't exist"""
        data = {'disp_item': self.disposable, 'vote': 'does not exist'}
        with self.assertRaises(Category.DoesNotExist):
            self.client.post(reverse('VoteHandler:carousel_vote'), data)

    def test_disposable_does_not_exist(self):
        """When there are no votes, initialize to 0 votes, increment, and go home"""
        DisposableVote.objects.all().delete()

        data = {'disp_item': self.disposable, 'vote': self.category}
        resp = self.client.post(reverse('VoteHandler:carousel_vote'), data, follow=True)
        vote_count = DisposableVote.objects.get(disposable=self.disposable).count
        self.assertEqual(settings.CATEGORIZE_VOTE_WEIGHT, vote_count)
        self.assertRedirects(resp, reverse('VoteHandler:home'))

    def test_disposable_existed(self):
        """When there are already votes, increment and go home"""
        old_count = self.vote_1.count
        data = {'disp_item': self.disposable, 'vote': self.category}
        resp = self.client.post(reverse('VoteHandler:carousel_vote'), data, follow=True)
        new_count = DisposableVote.objects.get(disposable=self.disposable).count
        self.assertEqual(old_count + settings.CATEGORIZE_VOTE_WEIGHT, new_count)
        self.assertRedirects(resp, reverse('VoteHandler:home'))


class DisposeTestCase(ViewsBaseObjectsMixin, TestCase):
    def test_no_text_input(self):
        """Redirect to home with an error msg when the user did not enter text"""
        resp = self.client.post(reverse('VoteHandler:dispose'), data={})
        self.assertTemplateUsed(resp, 'VoteHandler/home.html')
        self.assertIsNotNone(resp.context['error_message'])

    def test_disposable_not_found(self):
        """Create the object and redirect to categorize when the disposable didn't exist"""
        text = 'disposable_that_does_not_exist'
        resp = self.client.post(
            reverse('VoteHandler:dispose'), data={'disposable_item': text}, follow=True
        )

        self.assertRedirects(resp, reverse('VoteHandler:categorize', args=[text]))
        self.assertTemplateUsed(resp, 'VoteHandler/categorize.html')

    def test_disposable_has_no_votes(self):
        """Redirect to categorize when the disposable has no votes"""
        DisposableVote.objects.all().delete()

        resp = self.client.post(
            reverse('VoteHandler:dispose'),
            data={'disposable_item': self.disposable.name},
            follow=True
        )

        self.assertRedirects(resp, reverse('VoteHandler:categorize', args=[self.disposable.name]))
        self.assertTemplateUsed(resp, 'VoteHandler/categorize.html')

    def test_votes_not_confident(self):
        """Redirect to categorize when the disposable has too few votes"""
        percentage = self.vote_1.count / settings.MIN_NORMALIZE_COUNT
        self.assertGreaterEqual(settings.MIN_CONFIDENCE, percentage, 'test invalid')
        resp = self.client.post(
            reverse('VoteHandler:dispose'),
            data={'disposable_item': self.disposable.name},
            follow=True
        )

        self.assertRedirects(resp, reverse('VoteHandler:categorize', args=[self.disposable.name]))
        self.assertTemplateUsed(resp, 'VoteHandler/categorize.html')

    @patch('VoteHandler.views.send_rotate_to_can')
    def test_success(self, rotate_mock):
        """Send rotate cmd and render the results page when there are enough votes"""
        self.vote_1.count = settings.MIN_NORMALIZE_COUNT * 2
        self.vote_1.save()

        percentage = self.vote_1.count / settings.MIN_NORMALIZE_COUNT
        self.assertLess(settings.MIN_CONFIDENCE, percentage, 'test invalid')
        resp = self.client.post(
            reverse('VoteHandler:dispose'),
            data={'disposable_item': self.disposable.name},
            follow=True
        )

        args = (self.disposable.id, self.category.id)
        params = urlencode([(self.category, 100.0)])
        url = f"{reverse('VoteHandler:result', args=args)}?{params}"
        self.assertRedirects(resp, url)
        self.assertTemplateUsed(resp, 'VoteHandler/result.html')
        rotate_mock.assert_called_once()


class HomeTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(UUID.replace('-', ''), password='')

    def setUp(self):
        # update_or_create returns a tuple where the element is at index 0
        _ = Category.objects.create(id=19, name='Landfill')
        self.can_info, _ = CanInfo.objects.update_or_create(
            can_id=UUID, owner=self.user, channel_name=None
        )
        self.bin, _ = Bin.objects.update_or_create(
            s_id=self.can_info, bin_num=BIN_NUM, category=None
        )

    def test_success(self):
        """Display bin on page if user is logged in and has a bin"""
        self.client.user = self.user
        self.client.force_login(self.user)
        response = self.client.get('/api/')
        self.assertTemplateUsed(response=response, template_name='VoteHandler/home.html')
        self.assertContains(response, f'Bin {BIN_NUM}')

    def test_user_not_logged_in(self):
        """Is login enforced"""
        response = self.client.get('/api/')
        self.assertTemplateNotUsed(response=response, template_name='VoteHandler/home.html')
        self.assertEqual(response.status_code, 302)

    def test_user_logged_in_no_can_info(self):
        """Do not display a bin on page if user is logged in and has no bins"""
        CanInfo.objects.all().delete()
        self.client.user = self.user
        self.client.force_login(self.user)
        response = self.client.get('/api/')
        self.assertTemplateUsed(response=response, template_name='VoteHandler/home.html')
        self.assertNotContains(response, f'Bin {BIN_NUM}')


class ManualRotateTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(UUID.replace('-', ''), password='')
        self.client.force_login(self.user)
        self.category = Category.objects.create(id=19, name='Landfill')
        can_info = CanInfo.objects.create(can_id=UUID, owner=self.user, channel_name='')
        self.bin = Bin.objects.create(s_id=can_info, bin_num=0, category=self.category)

    @patch('VoteHandler.views.send_rotate_to_can')
    def test_bin_does_not_exist(self, rotate_mock):
        """When the bin doesn't exist, redirect to home and do not send rotate"""
        resp = self.client.post(reverse('VoteHandler:manual_rotate'))
        self.assertRedirects(resp, reverse('VoteHandler:home'))
        rotate_mock.assert_not_called()

    @patch('VoteHandler.views.send_rotate_to_can')
    def test_success(self, rotate_mock):
        """When the bin exists, redirect to home and send the rotate command"""
        data = {'bin': self.bin.bin_num}
        resp = self.client.post(reverse('VoteHandler:manual_rotate'), data=data)
        self.assertRedirects(resp, reverse('VoteHandler:home'))
        rotate_mock.assert_called_once()


class ResultTestCase(ViewsBaseObjectsMixin, TestCase):
    def test_success(self):
        """Calls template with correct info from get"""
        kwargs = {
            'disposable_id': self.disposable.id,
            'category_id': self.category.id
        }
        votes = [(self.category.name, str(float(self.vote_1.count)))]
        resp = self.client.get(reverse('VoteHandler:result', kwargs=kwargs), data=votes)
        self.assertTemplateUsed(resp, 'VoteHandler/result.html')
        self.assertEqual(self.disposable.name, resp.context['disposable_name'])
        self.assertEqual(self.category.name, resp.context['category_name'])
        self.assertEqual(votes, resp.context['votes'])
