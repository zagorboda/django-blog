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


class EmptyBlogMainPageTest(TestCase):
    """ Test module for Blog main page without posts """
    def test_empty_main_page(self):
        client = Client()
        response = client.get(reverse('blog_main_page'))

        posts = Post.objects.all()
        serializer = PostListSerializer(posts, many=True, context={'request': None})

        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetAllPostsTest(TestCase):
    """ Test module for get all Post objects if number of objects less than pagination_size"""

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

        Post.objects.create(
            title="Some new title",
            content="New content",
            author=user,
            slug='slug123',
            status=1
        )

        Post.objects.create(
            title="Hidden post",
            content="content",
            author=user,
            slug='hidden_slug',
            status=0
        )

    def test_get_posts(self):
        client = Client()
        response = client.get(reverse('blog_main_page'))

        # Url for post-detail and author stores in database as /api/blog/slug/, but client.get makes request to
        # test server, so it return absolute url http://testserver/api/blog/slug/. Following code trunc urls.
        # Example : (http://testserver/api/blog/slug/, http://testserver/api/user/profile/test_user/) --->
        # ---> (/api/blog/slug/, /api/user/profile/test_user/)
        # http://testserver is exact 17 characters # TODO universal code to trunc urls (e. g. https)
        truncated_urls = []
        for item in response.data['results']:
            truncated_urls.append((item['url'][17:], item['author'][17:]))
        for index, item in enumerate(response.data['results']):
            response.data['results'][index]['url'] = truncated_urls[index][0]
            response.data['results'][index]['author'] = truncated_urls[index][1]

        posts = Post.objects.all().filter(status=1)
        serializer = PostListSerializer(posts, many=True, context={'request': None})

        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetAllPostsOverPaginationTest(TestCase):
    """ Test module for get all Post objects if number of objects greater than pagination_size"""

    def setUp(self):
        user = User.objects.create_user(username='test_user',
                                        password='test_password')

        for i in range(30):

            Post.objects.create(
                title="Title{}".format(i),
                content="Content",
                author=user,
                slug='slug{}'.format(i),
                status=i%2  # half posts are active, half are drafts
            )

    def test_get_posts(self):
        result = []

        client = Client()
        response = client.get(reverse('blog_main_page'))

        truncated_urls = []
        for item in response.data['results']:
            truncated_urls.append((item['url'][17:], item['author'][17:]))
        for index, item in enumerate(response.data['results']):
            response.data['results'][index]['url'] = truncated_urls[index][0]
            response.data['results'][index]['author'] = truncated_urls[index][1]

        result.extend(response.data['results'])

        # Collect data from paginated pages
        while response.data['next']:
            response = client.get(response.data['next'])

            truncated_urls = []
            for item in response.data['results']:
                truncated_urls.append((item['url'][17:], item['author'][17:]))
            for index, item in enumerate(response.data['results']):
                response.data['results'][index]['url'] = truncated_urls[index][0]
                response.data['results'][index]['author'] = truncated_urls[index][1]

            result.extend(response.data['results'])

        posts = Post.objects.all().filter(status=1)
        serializer = PostListSerializer(posts, many=True, context={'request': None})

        self.assertEqual(result, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class MainPagePostRequestTest(TestCase):
    """ Test module for post request to blog_main_page.
        BlogMainPage inherits from generics.ListAPIView, which provides only get method"""

    def test_post_request(self):
        client = Client()
        response = client.post(reverse('blog_main_page'))

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

# def test_get_post_detail(self):
#     client = Client()
#     response = client.get(reverse('post-detail', kwargs={'slug': 'slug'}))
#
#     truncated_urls = [response.data['url'][17:],
#                       response.data['edit_url'][17:],
#                       response.data['author'][17:]]
#
#     response.data['url'] = truncated_urls[0]
#     response.data['edit_url'] = truncated_urls[1]
#     response.data['author'] = truncated_urls[2]
#
#     post = Post.objects.get(slug='slug')
#     serializer = PostDetailSerializer(post, context={'request': None})
#
#     self.assertEqual(response.data, serializer.data)
#     self.assertEqual(response.status_code, status.HTTP_200_OK)
