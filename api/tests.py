from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
# from rest_framework.request import Request
# from rest_framework.test import APIRequestFactory
import json

from .serializers import PostListSerializer, PostDetailSerializer
from blog_app.models import Post
from . import views
from . import urls


class GetAllPostsTest(TestCase):
    """ Test module for GET all Post objects"""

    def setUp(self):
        user = User.objects.create_user(username='test_user',
                                        password='test_password')

        Post.objects.create(
            title="Title",
            content="Content",
            author=user,
            slug='slug',
            status=1
        )

        # Post.objects.create(
        #     title="Some new title",
        #     content="New content",
        #     author=user,
        #     slug='slug123',
        #     status=1
        # )

    def test_get_posts(self):
        client = Client()
        response = client.get(reverse('blog_main_page'))

        # Url for post-detail and author stores in database as /api/blog/slug/, but client.get makes request to
        # test server, so it return absolute url http://testserver/api/blog/slug/. Following code trunc urls.
        # Example : (http://testserver/api/blog/slug/, http://testserver/api/user/profile/test_user/) --->
        # ---> (/api/blog/slug/, /api/user/profile/test_user/)
        truncated_urls = []
        for item in response.data['results']:
            truncated_urls.append((item['url'][17:], item['author'][17:]))
        for index, item in enumerate(response.data['results']):
            response.data['results'][index]['url'] = truncated_urls[index][0]
            response.data['results'][index]['author'] = truncated_urls[index][1]

        posts = Post.objects.all()
        serializer = PostListSerializer(posts, many=True, context={'request': None})

        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_post_detail(self):
        client = Client()
        response = client.get(reverse('post-detail', kwargs={'slug': 'slug'}))

        truncated_urls = [response.data['url'][17:],
                          response.data['edit_url'][17:],
                          response.data['author'][17:]]

        response.data['url'] = truncated_urls[0]
        response.data['edit_url'] = truncated_urls[1]
        response.data['author'] = truncated_urls[2]

        post = Post.objects.get(slug='slug')
        serializer = PostDetailSerializer(post, context={'request': None})

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
