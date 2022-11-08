"""
Test tag apis
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag

from recipe.serializers import TagSerializer

TAG_URL = reverse('recipe:tag-list')


def create_user(**params):
    """Create and return new user"""
    return get_user_model().objects.create_user(**params)


def create_tag(user, name):
    """Create and return new Tag object"""
    return Tag.objects.create(user=user, name=name)


def detail_url(tag_id):
    """Create and return a tag detail URL."""
    return reverse('recipe:tag-detail', args=[tag_id])


class PublicTagApiTests(TestCase):
    """Test unauthenticated API request"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test returns 401 unauthorized
        when logging without user credentials"""
        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTests(TestCase):
    """Private tag api tests"""

    def setUp(self):
        self.user = create_user(
            email='user@example.com',
            name='Test User',
            password='test1234',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tag_list(self):
        """Test get list api"""
        create_tag(self.user, "TESTTAG")
        create_tag(self.user, "ANOTHERTESTTAG")

        res = self.client.get(TAG_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test return tags limited to user"""
        other_user = create_user(email="other_user", password="otherpass")

        create_tag(self.user, "TESTTAG")
        create_tag(self.user, "ANOTHERTESTTAG")
        create_tag(other_user, "OTHERTAG")

        res = self.client.get(TAG_URL)

        tags = Tag.objects.filter(user=self.user).order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_partial_update(self):
        """Test partial update for recipe"""
        original_name = "ORIGINAL NAME"
        tag = create_tag(
            user=self.user,
            name=original_name
        )

        payload = {
            'name': 'new_name'
        }

        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()

        self.assertEqual(tag.name, payload['name'])

    def test_full_update(self):
        """Test full update for tag"""
        original_name = "ORIGINAL_NAME"
        tag = create_tag(
            user=self.user,
            name=original_name
        )

        payload = {
            "name": "new name"
        }

        url = detail_url(tag.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        tag.refresh_from_db()

        self.assertEqual(tag.name, payload["name"])

    def test_udpate_user_retruns_error(self):
        """Test changing tag user results in error"""
        new_user = create_user(email='new@example.com', password='newpass')
        tag = create_tag(user=self.user, name="test tag")

        payload = {
            'user': new_user,
        }

        url = detail_url(tag.id)
        self.client.patch(url, payload)

        tag.refresh_from_db()

        self.assertEqual(tag.user, self.user)

    def test_delete_tag(self):
        """Test deleting tag"""
        tag = create_tag(user=self.user, name='test tag')

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(id=tag.id).exists())

        with self.assertRaises(Tag.DoesNotExist):
            Tag.objects.get(id=tag.id)
