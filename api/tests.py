from django.test import TestCase, Client
from django.contrib.auth.models import User, AnonymousUser
from django.urls import reverse
from rest_framework import status
# from rest_framework.test import APIRequestFactory
from django.test.client import RequestFactory
from rest_framework.authtoken.models import Token
from rest_framework.request import Request
import json

from .serializers import PostListSerializer, PostDetailSerializer, CommentSerializer, UserSerializer
from blog_app.models import Post, Comment
from .views import UserDetail


class EmptyBlogMainPageTest(TestCase):
    """ Test module for Blog main page without posts """
    def test_empty_main_page(self):
        """ Get method without posts """
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
        """ Get all active posts from main page """
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
                status=i % 2  # half posts are active, half are drafts
            )

    def test_get_posts(self):
        """ Get all active posts from all pages """
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
        while response.data['links']['next']:
            response = client.get(response.data['links']['next'])

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
        """ Testing not allowed POST method """
        client = Client()
        response = client.post(reverse('blog_main_page'))

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class PostDetailTest(TestCase):
    """ Test module for post detail page"""

    def setUp(self):
        user1 = User.objects.create_user(username='test_user')
        user1.set_password('test_password')
        user1.save()

        self.test_user = User.objects.create(
            username='some_user'
        )
        self.password = 'test_password'
        self.test_user.set_password(self.password)

        self.post1 = Post.objects.create(
            title="Title",
            content="Content",
            author=user1,
            slug='slug',
            status=1
        )

        self.post2 = Post.objects.create(
            title="Draft Title",
            content="Content",
            author=self.test_user,
            slug='draft-slug',
            status=0
        )

        self.post_with_single_comment = Post.objects.create(
            title="Title comment",
            content="Comment",
            author=self.test_user,
            slug='single-comment-slug',
            status=1
        )

        self.post_with_several_comments = Post.objects.create(
            title="Title comments",
            content="Comments",
            author=self.test_user,
            slug='several-comments-slug',
            status=1
        )

    def test_get_post_detail(self):
        """ Get detail for existing active post """
        client = Client()
        response = client.get(reverse('post-detail', kwargs={'slug': 'slug'}))

        response.data['url'] = response.data['url'][17:]
        response.data['edit_url'] = response.data['edit_url'][17:]
        response.data['author'] = response.data['author'][17:]

        post = Post.objects.get(slug='slug')
        serializer = PostDetailSerializer(post, context={'request': None})

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_invalid_post_detail(self):
        """ Get detail for not existing post """
        client = Client()
        response = client.get(reverse('post-detail', kwargs={'slug': 'slug1'}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_draft_post_detail(self):
        """ Get detail for existing draft(not active) post """
        client = Client()
        response = client.get(reverse('post-detail', kwargs={'slug': 'draft-slug'}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_request_post_detail(self):
        """ Make POST request (create new comment) to post detail page by unauthorized user"""
        client = Client()
        response = client.post(reverse('post-detail', kwargs={'slug': 'slug'}))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_comment_post_detail(self):
        """ Make POST request (create new comment) to post detail page by authorized user"""
        client = Client()

        client.login(username=self.test_user.username, password=self.password)
        token = Token.objects.create(user=self.test_user)

        response = client.post(
            reverse('post-detail', kwargs={'slug': 'slug'}),
            HTTP_AUTHORIZATION='Token {}'.format(token),
            data=json.dumps({'body': "test"}),
            content_type='application/json'
        )

        response.data['author'] = response.data['author'][17:]

        comment = Comment.objects.get(post=self.post1)
        serializer = CommentSerializer(comment, context={'request': None})

        number_of_comments = Comment.objects.all().count()

        self.assertEqual(serializer.data, response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(number_of_comments, 1)

    def test_invalid_comment_post_detail(self):
        """ Make POST request by authorized user with invalid data (empty body)"""
        client = Client()

        client.login(username=self.test_user.username, password=self.password)
        token = Token.objects.create(user=self.test_user)

        response = client.post(
            reverse('post-detail', kwargs={'slug': 'slug'}),
            HTTP_AUTHORIZATION='Token {}'.format(token),
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_with_single_comment(self):
        """ Get post with comments """

        Comment.objects.create(
            post=self.post_with_single_comment,
            author=self.test_user,
            body='Some new comment',
            active=True
        )

        client = Client()
        response = client.get(reverse('post-detail', kwargs={'slug': 'single-comment-slug'}))

        response.data['url'] = response.data['url'][17:]
        response.data['edit_url'] = response.data['edit_url'][17:]
        response.data['author'] = response.data['author'][17:]
        response.data['comments'][0]['author'] = response.data['comments'][0]['author'][17:]

        post = Post.objects.get(slug='single-comment-slug')
        serializer = PostDetailSerializer(post, context={'request': None})

        number_of_comments = Comment.objects.all().filter(post=post).count()

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(number_of_comments, 1)

    def test_post_with_several_comments(self):
        """ Get post with several comments """

        for i in range(10):
            Comment.objects.create(
                post=self.post_with_several_comments,
                author=self.test_user,
                body='Some new comment {}'.format(i),
                active=i % 2
            )

        client = Client()
        response = client.get(reverse('post-detail', kwargs={'slug': 'several-comments-slug'}))

        response.data['url'] = response.data['url'][17:]
        response.data['edit_url'] = response.data['edit_url'][17:]
        response.data['author'] = response.data['author'][17:]

        for comment in response.data['comments']:
            comment['author'] = comment['author'][17:]

        post = Post.objects.get(slug='several-comments-slug')
        serializer = PostDetailSerializer(post, context={'request': None})

        number_of_comments = Comment.objects.all().filter(post=post).count()

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(number_of_comments, 10)


class UserDetailTest(TestCase):
    """ Test module for user detail page """
    #  In this module I test User page. To get user data from db I need to use UserSerializer,
    #  which inherits from HyperlinkedModelSerializer. HyperlinkedModelSerializer requires request
    #  when initiating, and in UserSerializer I use self.context['request'].user == user, so I somehow
    #  need a request to be passed to serializer. To make request I use RequestFactory(), then pass this
    #  request into Request() class and then pass it to serializer.

    def setUp(self):
        self.factory = RequestFactory()

        self.password = 'test_password'
        self.user = User.objects.create_user(username='test_user')
        self.user.set_password(self.password)
        self.user.save()

    def test_get_existing_user_detail(self):
        """ Get detail for existing user without posts and comments"""
        client = Client()
        response = client.get(reverse('user-detail', kwargs={'username': 'test_user'}))

        # view = UserDetail.as_view()

        request = self.factory.get(reverse('user-detail', kwargs={'username': 'test_user'}))
        # response = view(request, username='test_user')

        test_request = Request(request)
        # test_request.user = AnonymousUser()

        user = User.objects.get(username='test_user')
        serializer = UserSerializer(user, context={'request': test_request})

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_not_existing_user_detail(self):
        """ Get detail for not existing user"""
        client = Client()
        response = client.get(reverse('user-detail', kwargs={'username': 'not_existing_user'}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_request_to_user_detail(self):
        client = Client()
        response = client.post(reverse('user-detail', kwargs={'username': 'not_existing_user'}))

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_user_with_posts(self):
        """ Test user with several active posts """
        Post.objects.create(
            title="Title",
            content="Content",
            author=self.user,
            slug='slug',
            status=1
        )
        Post.objects.create(
            title="Title1",
            content="Content1",
            author=self.user,
            slug='slug1',
            status=1
        )

        client = Client()
        response = client.get(reverse('user-detail', kwargs={'username': 'test_user'}))

        request = self.factory.get(reverse('user-detail', kwargs={'username': 'test_user'}))

        test_request = Request(request)
        # test_request.user = self.user

        user = User.objects.get(username='test_user')
        serializer = UserSerializer(user, context={'request': test_request})

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_with_different_posts(self):
        """ Test user with active and draft posts. """
        #  Factory request.user and Client request.user is AnonymousUser,
        #  so data will include only single active post
        Post.objects.create(
            title="Title",
            content="Content",
            author=self.user,
            slug='slug',
            status=1
        )
        Post.objects.create(
            title="Title1",
            content="Content1",
            author=self.user,
            slug='slug1',
            status=0
        )

        client = Client()
        response = client.get(reverse('user-detail', kwargs={'username': 'test_user'}))

        request = self.factory.get(reverse('user-detail', kwargs={'username': 'test_user'}))

        test_request = Request(request)

        user = User.objects.get(username='test_user')
        serializer = UserSerializer(user, context={'request': test_request})

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_with_comments_request_by_owner(self):
        """ Test user with active and draft comments.
        Comments shows only for owner, so client must be logged as owner"""
        test_post = Post.objects.create(
            title="Title",
            content="Content",
            author=self.user,
            slug='slug',
            status=1
        )

        Comment.objects.create(
            body="test comment",
            post=test_post,
            author=self.user,
            active=1
        )

        Comment.objects.create(
            body="test comment",
            post=test_post,
            author=self.user,
            active=0
        )

        client = Client()
        client.login(username=self.user.username, password=self.password)
        token = Token.objects.create(user=self.user)

        response = client.get(
            reverse('user-detail', kwargs={'username': 'test_user'}),
            HTTP_AUTHORIZATION='Token {}'.format(token)
        )

        request = self.factory.get(reverse('user-detail', kwargs={'username': 'test_user'}))

        test_request = Request(request)
        test_request.user = self.user

        user = User.objects.get(username='test_user')
        serializer = UserSerializer(user, context={'request': test_request})

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_with_comments_request_by_other_user(self):
        """ Test user with active and draft comments.
        Comments must be hidden for other users """
        test_post = Post.objects.create(
            title="Title",
            content="Content",
            author=self.user,
            slug='slug',
            status=1
        )

        Comment.objects.create(
            body="test comment",
            post=test_post,
            author=self.user,
            active=1
        )

        client = Client()
        response = client.get(
            reverse('user-detail', kwargs={'username': 'test_user'})
        )

        request = self.factory.get(reverse('user-detail', kwargs={'username': 'test_user'}))
        test_request = Request(request)

        user = User.objects.get(username='test_user')
        serializer = UserSerializer(user, context={'request': test_request})

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

