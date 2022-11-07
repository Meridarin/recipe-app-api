"""
Test for the admin modifications
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client


class AdminSiteTests(TestCase):
    """Test for admin site modifications"""

    def setUp(self):
        """Create user and client"""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='test1234'
        )

        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
            name='Test User'
        )

    def test_users_list(self):
        """Test that users are listed on page."""
        url = reverse('admin:core_user_changelist')
        print(url)
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """Test that the edit user page exists"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        print(url)
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_add_user_page(self):
        """Test user add page"""
        url = reverse('admin:core_user_add')
        print(url)
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
