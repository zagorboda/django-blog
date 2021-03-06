from django.test import TestCase, Client
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
# from rest_framework.test import APIRequestFactory
from django.test.client import RequestFactory
# from rest_framework.authtoken.models import Token
from rest_framework.request import Request
import json

# from rest_framework.test import APIClient

from .serializers import PostListSerializer, PostDetailSerializer, CommentSerializer, UserSerializer
from blog_app.models import Post, Comment
from .views import UserDetail


class EmptyBlogMainPageTest(TestCase):
    """ Test module for Blog main page without posts """
    def test_empty_main_page(self):
        """ Get method without posts """
        client = Client()
        response = client.get(reverse('api:blog_main_page'))

        posts = Post.objects.all()
        serializer = PostListSerializer(posts, many=True, context={'request': None})

        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class BlogMainPageTest(TestCase):
    """ Test module for get all Post objects if number of objects less than pagination_size"""

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
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
        response = client.get(reverse('api:blog_main_page'))

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

    def test_post_request(self):
        """ Testing not allowed POST method """
        client = Client()
        response = client.post(reverse('api:blog_main_page'))

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class BlogMainPagePaginationTest(TestCase):
    """ Test module for get all Post objects if number of objects greater than pagination_size"""

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
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
        response = client.get(reverse('api:blog_main_page'))

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


class PostDetailTest(TestCase):
    """ Test module for post detail page"""

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()

        client = Client()

        cls.user1 = User.objects.create_user(username='test_user')
        cls.password1 = 'test_password'
        cls.user1.set_password(cls.password1)
        cls.user1.save()

        response = client.post(
            reverse('api:token_obtain_pair'),
            data=json.dumps({'username': cls.user1.username, 'password': cls.password1}),
            content_type='application/json'
        )

        cls.auth_token1 = response.data['access']

        cls.test_user = User.objects.create(
            username='some_user'
        )
        cls.test_password = 'test_password'
        cls.test_user.set_password(cls.test_password)
        cls.test_user.save()

        response = client.post(
            reverse('api:token_obtain_pair'),
            data=json.dumps({'username': cls.test_user.username, 'password': cls.test_password}),
            content_type='application/json'
        )

        cls.test_auth_token = response.data['access']

        cls.post1 = Post.objects.create(
            title="Title",
            content="Content",
            author=cls.user1,
            slug='slug',
            status=1
        )

        cls.post2 = Post.objects.create(
            title="Draft Title",
            content="Content",
            author=cls.test_user,
            slug='draft-slug',
            status=0
        )

        cls.post_with_single_comment = Post.objects.create(
            title="Title comment",
            content="Comment",
            author=cls.test_user,
            slug='single-comment-slug',
            status=1
        )

        cls.post_with_several_comments = Post.objects.create(
            title="Title comments",
            content="Comments",
            author=cls.test_user,
            slug='several-comments-slug',
            status=1
        )

    def test_get_post_detail(self):
        """ Get detail for existing active post by unauthorized user (different edit_url) """
        client = Client()
        response = client.get(
            reverse('api:post-detail', kwargs={'slug': 'slug'}),
            # HTTP_AUTHORIZATION='Token {}'.format(self.token1)
        )

        factory = RequestFactory()

        request = factory.get(
            reverse('api:post-detail', kwargs={'slug': 'slug'})
        )
        test_request = Request(request)

        post = Post.objects.get(slug='slug')
        serializer = PostDetailSerializer(post, context={'request': test_request})

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_invalid_post_detail(self):
        """ Get detail for not existing post """
        client = Client()
        response = client.get(reverse('api:post-detail', kwargs={'slug': 'slug1'}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_draft_post_detail(self):
        """ Get detail for existing draft(not active) post """
        client = Client()
        response = client.get(reverse('api:post-detail', kwargs={'slug': 'draft-slug'}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_request_post_detail(self):
        """ Make POST request (create new comment) to post comments page by unauthorized user"""
        client = Client()
        response = client.post(reverse('api:post-comments', kwargs={'slug': 'slug'}))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_comment_post_detail(self):
        """ Make POST request (create new comment) to post comments page by authorized user"""
        client = Client()

        response = client.post(
            reverse('api:post-comments', kwargs={'slug': 'slug'}),
            HTTP_AUTHORIZATION='JWT {}'.format(self.test_auth_token),
            data=json.dumps({'body': "test"}),
            content_type='application/json'
        )

        response.data['author'] = response.data['author'][17:]
        response.data['report_url'] = response.data['report_url'][17:]
        response.data['post_url'] = response.data['post_url'][17:]
        response.data['url'] = response.data['url'][17:]

        comment = Comment.objects.get(post=self.post1)
        serializer = CommentSerializer(comment, context={'request': None})

        number_of_comments = Comment.objects.all().count()

        self.assertEqual(serializer.data, response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(number_of_comments, 1)

    def test_invalid_comment_post_detail(self):
        """ Make POST request by authorized user with invalid data (empty body)"""
        client = Client()

        response = client.post(
            reverse('api:post-comments', kwargs={'slug': 'slug'}),
            HTTP_AUTHORIZATION='JWT {}'.format(self.test_auth_token),
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
            status=1
        )

        client = Client()
        response = client.get(reverse('api:post-detail', kwargs={'slug': 'single-comment-slug'}))

        factory = RequestFactory()

        request = factory.get(
            reverse('api:post-detail', kwargs={'slug': 'single-comment-slug'})
        )
        test_request = Request(request)

        post = Post.objects.get(slug='single-comment-slug')
        serializer = PostDetailSerializer(post, context={'request': test_request})

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
                status=i % 2
            )

        client = Client()
        response = client.get(reverse('api:post-comments', kwargs={'slug': 'several-comments-slug'}))

        response_results = []
        for i in range(len(response.data['results'])):
            response.data['results'][i]['url'] = response.data['results'][i]['url'][17:]
            response.data['results'][i]['author'] = response.data['results'][i]['author'][17:]
            response.data['results'][i]['report_url'] = response.data['results'][i]['report_url'][17:]
            response.data['results'][i]['post_url'] = response.data['results'][i]['post_url'][17:]
        response_results.extend(response.data['results'])
        next_page = response.data['next']
        while next_page:
            for i in range(len(response.data['results'])):
                response.data['results'][i]['url'] = response.data['results'][i]['url'][17:]
                response.data['results'][i]['author'] = response.data['results'][i]['author'][17:]
                response.data['results'][i]['report_url'] = response.data['results'][i]['report_url'][17:]
                response.data['results'][i]['post_url'] = response.data['results'][i]['post_url'][17:]

            response_results.extend(response.data['results'])
            response = client.get(next_page)
            next_page = response.data['next']

        post = Post.objects.get(slug='several-comments-slug')
        comments = Comment.objects.filter(post=post, status=1)
        serializer = CommentSerializer(comments, many=True, context={'request': None})

        number_of_comments = Comment.objects.all().filter(post=post).count()

        self.assertEqual(response_results, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(number_of_comments, 10)


class UserDetailTest(TestCase):
    """ Test module for user detail page """
    #  In this module I test User page. To get user data from db I need to use UserSerializer,
    #  which inherits from HyperlinkedModelSerializer. HyperlinkedModelSerializer requires request
    #  when initiating, and in UserSerializer I use self.context['request'].user == user, so I somehow
    #  need a request to be passed to serializer. To create request I use RequestFactory() and
    #  Request() class.

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()

        cls.factory = RequestFactory()

        cls.password = 'test_password'
        cls.user = User.objects.create_user(username='test_user')
        cls.user.set_password(cls.password)
        cls.user.save()

        client = Client()

        response = client.post(
            reverse('api:token_obtain_pair'),
            data=json.dumps({'username': cls.user.username, 'password': cls.password}),
            content_type='application/json'
        )

        cls.auth_token = response.data['access']

    def test_get_existing_user_detail(self):
        """ Get detail for existing user without posts and comments"""
        client = Client()
        response = client.get(reverse('api:user-detail', kwargs={'username': 'test_user'}))
        request = self.factory.get(reverse('api:user-detail', kwargs={'username': 'test_user'}))

        test_request = Request(request)

        User = get_user_model()

        user = User.objects.get(username='test_user')
        serializer = UserSerializer(user, context={'request': test_request, 'kwargs': {'username': 'test_user'}})

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_not_existing_user_detail(self):
        """ Get detail for not existing user"""
        client = Client()
        response = client.get(reverse('api:user-detail', kwargs={'username': 'not_existing_user'}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_request_to_user_detail(self):
        client = Client()
        response = client.post(reverse('api:user-detail', kwargs={'username': 'not_existing_user'}))

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class UserObjectsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()

        cls.factory = RequestFactory()

        cls.password = 'test_password'
        cls.user = cls.User.objects.create_user(username='test_user')
        cls.user.set_password(cls.password)
        cls.user.save()

        client = Client()

        response = client.post(
            reverse('api:token_obtain_pair'),
            data=json.dumps({'username': cls.user.username, 'password': cls.password}),
            content_type='application/json'
        )

        cls.auth_token = response.data['access']

    def test_get_posts(self):
        """ Test user objects list with several active posts """
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
        response = client.get(reverse('api:user-objects', kwargs={'username': 'test_user', 'object_type': 'posts'}))

        request = self.factory.get(reverse('api:user-objects', kwargs={'username': 'test_user', 'object_type': 'posts'}))
        test_request = Request(request)

        author = self.User.objects.get(username='test_user')
        posts = Post.objects.filter(author=author)
        serializer = PostListSerializer(posts, many=True, context={'request': test_request})

        response_results = []
        response_results.extend(response.data['results'])
        next_page = response.data['next']
        while next_page:
            response_results.extend(response.data['results'])
            response = client.get(next_page)
            next_page = response.data['next']

        self.assertEqual(response_results, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_different_posts(self):
        """ Test user objects list with active and draft posts
        Factory request.user and Client request.user is AnonymousUser,
        so data will include only single active post """
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
        response = client.get(reverse('api:user-objects', kwargs={'username': 'test_user', 'object_type': 'posts'}))

        request = self.factory.get(reverse('api:user-objects', kwargs={'username': 'test_user', 'object_type': 'posts'}))

        test_request = Request(request)

        author = self.User.objects.get(username='test_user')
        posts = Post.objects.filter(author=author, status=1)
        serializer = PostListSerializer(posts, many=True, context={'request': test_request})

        response_results = []
        response_results.extend(response.data['results'])
        next_page = response.data['next']
        while next_page:
            response_results.extend(response.data['results'])
            response = client.get(next_page)
            next_page = response.data['next']

        self.assertEqual(response_results, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_comments_by_owner(self):
        """ Test user objects list with active and draft comments."""
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
            status=1
        )

        Comment.objects.create(
            body="test comment",
            post=test_post,
            author=self.user,
            status=0
        )

        client = Client()

        response = client.get(
            reverse('api:user-objects', kwargs={'username': 'test_user', 'object_type': 'comments'}),
            HTTP_AUTHORIZATION='JWT {}'.format(self.auth_token)
        )

        request = self.factory.get(
            reverse('api:user-objects', kwargs={'username': 'test_user', 'object_type': 'comments'}),
            HTTP_AUTHORIZATION='JWT {}'.format(self.auth_token)
        )

        test_request = Request(request)
        test_request.user = self.user

        author = self.User.objects.get(username='test_user')
        comments = Comment.objects.filter(author=author)
        serializer = CommentSerializer(comments, many=True, context={'request': test_request})

        response_results = []
        response_results.extend(response.data['results'])
        next_page = response.data['next']
        while next_page:
            response_results.extend(response.data['results'])
            response = client.get(next_page)
            next_page = response.data['next']

        self.assertEqual(response_results, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_comments(self):
        """ Test user with active and draft comments.
        Draft comments must be hidden for other users """
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
            status=0
        )

        client = Client()
        response = client.get(
            reverse('api:user-objects', kwargs={'username': 'test_user', 'object_type': 'comments'})
        )

        request = self.factory.get(reverse('api:user-objects', kwargs={'username': 'test_user', 'object_type': 'comments'}))
        test_request = Request(request)

        author = self.User.objects.get(username='test_user')
        comments = Comment.objects.filter(author=author, status=1)
        serializer = CommentSerializer(comments, many=True, context={'request': test_request})

        response_results = []
        response_results.extend(response.data['results'])
        next_page = response.data['next']
        while next_page:
            response_results.extend(response.data['results'])
            response = client.get(next_page)
            next_page = response.data['next']

        self.assertEqual(response_results, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CreateNewPost(TestCase):

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()

        cls.factory = RequestFactory()

        cls.password = 'test_password'
        cls.user = User.objects.create_user(username='test_user')
        cls.user.set_password(cls.password)
        cls.user.save()

        client = Client()

        response = client.post(
            reverse('api:token_obtain_pair'),
            data=json.dumps({'username': cls.user.username, 'password': cls.password}),
            content_type='application/json'
        )

        cls.auth_token = response.data['access']

    def test_post_request_by_unauthorized_user(self):
        """ Make POST request by unauthorized user """
        client = Client()

        response = client.post(
            reverse('api:new-post'),
            data=json.dumps({}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_request_with_empty_data(self):
        """ Make POST request without data """
        client = Client()

        client.login(username=self.user.username, password=self.password)

        response = client.post(
            reverse('api:new-post'),
            HTTP_AUTHORIZATION='JWT {}'.format(self.auth_token),
            data=json.dumps({}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_request_with_valid_data(self):
        """ Make POST request with valid data """
        client = Client()

        # client.login(username=self.user.username, password=self.password)

        response = client.post(
            reverse('api:new-post'),
            HTTP_AUTHORIZATION='JWT {}'.format(self.auth_token),
            data=json.dumps({"title": "Test title", "content": "Test content"}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_request_with_extra_fields(self):
        """ Make POST request with valid data and several extra fields """
        client = Client()

        client.login(username=self.user.username, password=self.password)
        header = {'content-type': 'multipart/form-data'}
        response = client.post(
            reverse('api:new-post'),
            HTTP_AUTHORIZATION='JWT {}'.format(self.auth_token),
            data=json.dumps({"title": "Test title", "content": "Test content",
                             "some_extra_field": "test value", "status": 1}),
            content_type='application/json'
        )
        post = Post.objects.all()[0]

        self.assertEqual(post.status, 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class UserLoginApiTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()

        cls.factory = RequestFactory()

        cls.password = 'test_password'
        cls.user = User.objects.create_user(username='test_user')
        cls.user.set_password(cls.password)
        cls.user.save()

    def test_not_allowed_request(self):
        """ Make GET request (ObtainAuthToken process only POST request) """
        client = Client()
        response = client.get(reverse('api:token_obtain_pair'))

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_with_invalid_username(self):
        """ Make POST request with invalid username """
        client = Client()

        response = client.post(
            reverse('api:token_obtain_pair'),
            data=json.dumps({"username": "not_existing_username", "password": "some_password"}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_with_invalid_password(self):
        """ Make POST request with invalid password """
        client = Client()

        response = client.post(
            reverse('api:token_obtain_pair'),
            data=json.dumps({"username": self.user.username, "password": "invalid_password"}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_with_valid_credentials(self):
        """ Make POST request with valid credentials for existing user """
        client = Client()

        response = client.post(
            reverse('api:token_obtain_pair'),
            data=json.dumps({"username": self.user.username, "password": self.password}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserCreateApiTest(TestCase):
    def test_get_request(self):
        """ Make GET request """
        client = Client()
        response = client.get(reverse('api:signup'))

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_post_request_with_invalid_data(self):
        """ Make POST request with invalid username """
        client = Client()

        response = client.post(
            reverse('api:signup'),
            data=json.dumps({"username": "!@#$%^&*()_+-=", "password": "test_password"}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_request_with_valid_data(self):
        """ Make POST request with valid data """
        client = Client()

        response = client.post(
            reverse('api:signup'),
            data=json.dumps(
                {"username": "valid_username", "password": "valid_password", "email": "valid_email@test.com"}
            ),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_sign_up_existing_user(self):
        """ Make POST request with existing username """
        User = get_user_model()

        password = 'test_password'
        user = User.objects.create_user(username='test_user')
        user.set_password(password)
        user.save()

        client = Client()

        response = client.post(
            reverse('api:signup'),
            data=json.dumps({"username": "test_user", "password": "some_Valid_Safe_password_2345dsS-dsaD"}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sign_up_with_common_password(self):
        """ Make POST request with common password """
        client = Client()

        response = client.post(
            reverse('api:signup'),
            data=json.dumps({"username": "test_user", "password": "12345678"}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class EditPostTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()

        cls.password = 'test_password'
        cls.user = User.objects.create_user(username='test_user')
        cls.user.set_password(cls.password)
        cls.user.save()

        client = Client()

        response = client.post(
            reverse('api:token_obtain_pair'),
            data=json.dumps({'username': cls.user.username, 'password': cls.password}),
            content_type='application/json'
        )

        cls.auth_token = response.data['access']

        cls.test_post = Post.objects.create(
            title="Title",
            content="Content",
            author=cls.user,
            slug='slug',
            status=1
        )

    def test_patch_request_to_existing_post_patch_all_fields(self):
        """ Make PATCH request to existing post, patch title and content"""
        client = Client()

        response = client.patch(
            reverse('api:post-detail', kwargs={'slug': 'slug'}),
            HTTP_AUTHORIZATION='JWT {}'.format(self.auth_token),
            data=json.dumps({"title": "Test title", "content": "Test content"}),
            content_type='application/json'
        )

        patched_post = Post.objects.all()[0]

        self.assertEqual(response.data['slug'], patched_post.slug)
        self.assertEqual(response.data['title'], patched_post.title)
        self.assertEqual(response.data['content'], patched_post.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_request_to_existing_post_patch_title(self):
        """ Make PATCH request to existing post, patch title"""
        client = Client()

        response = client.patch(
            reverse('api:post-detail', kwargs={'slug': 'slug'}),
            HTTP_AUTHORIZATION='JWT {}'.format(self.auth_token),
            data=json.dumps({"title": "Test title", "content": self.test_post.content}),
            content_type='application/json'
        )

        patched_post = Post.objects.all()[0]

        self.assertEqual(response.data['slug'], patched_post.slug)
        self.assertEqual(response.data['title'], patched_post.title)
        self.assertEqual(response.data['content'], patched_post.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_request_to_existing_post_patch_content(self):
        """ Make PATCH request to existing post, patch content"""
        client = Client()

        response = client.patch(
            reverse('api:post-detail', kwargs={'slug': 'slug'}),
            HTTP_AUTHORIZATION='JWT {}'.format(self.auth_token),
            data=json.dumps({"content": "Test content", "title": self.test_post.title}),
            content_type='application/json'
        )

        patched_post = Post.objects.all()[0]

        self.assertEqual(response.data['slug'], patched_post.slug)
        self.assertEqual(response.data['title'], patched_post.title)
        self.assertEqual(response.data['content'], patched_post.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_request_to_existing_post(self):
        """ Make GET request to existing post"""
        client = Client()

        response = client.get(
            reverse('api:post-detail', kwargs={'slug': 'slug'}),
            HTTP_AUTHORIZATION='JWT {}'.format(self.auth_token),
        )

        patched_post = Post.objects.all()[0]

        self.assertEqual(response.data['title'], patched_post.title)
        self.assertEqual(response.data['content'], patched_post.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_request_to_existing_post_by_unauthorized_user(self):
        """ Make PATCH request to existing post by unauthorized user"""
        client = Client()

        response = client.patch(
            reverse('api:post-detail', kwargs={'slug': 'slug'}),
            data=json.dumps({"content": "Test content", "title": self.test_post.title}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_request_to_existing_post_by_not_owner(self):
        """ Make GET request to existing post by not owner"""
        User = get_user_model()

        password = 'test_password'
        user = User.objects.create_user(username='new_user')
        user.set_password(password)
        user.save()

        client = Client()

        User = get_user_model()

        password = 'test_password'
        another_user = User.objects.create_user(username='another_user')
        another_user.set_password(self.password)
        another_user.save()

        response = client.post(
            reverse('api:token_obtain_pair'),
            data=json.dumps({'username': another_user.username, 'password': password}),
            content_type='application/json'
        )

        another_auth_token = response.data['access']

        response = client.patch(
            reverse('api:post-detail', kwargs={'slug': 'slug'}),
            HTTP_AUTHORIZATION='JWT {}'.format(another_auth_token),
            data=json.dumps({"content": "Test content", "title": "test title"})
        )

        self.assertEqual(response.data['detail'], 'You do not have permission to perform this action.')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SearchPostTest(TestCase):

    def test_search_without_posts(self):
        """ Make search request without any post created """
        client = Client()
        response = client.get(
            '{}{}'.format(reverse('api:blog_main_page'), '?search=some_test_search')
        )

        self.assertEqual(response.data['results'], [])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_without_result(self):
        """ Make search request with query, that doesn't match any existing post """
        User = get_user_model()

        test_user = User.objects.create_user(username='test_user')

        test_post = Post.objects.create(
            title="Title",
            content="Content",
            author=test_user,
            slug='slug',
            status=1
        )
        client = Client()
        response = client.get(
            '{}{}'.format(reverse('api:blog_main_page'), '?search=not_matching_pattern')
        )

        self.assertEqual(response.data['results'], [])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_with_single_result(self):
        """ Make search request with query, that match single existing post """
        User = get_user_model()

        test_user = User.objects.create_user(username='test_user')

        test_post = Post.objects.create(
            title="Title",
            content="Content",
            author=test_user,
            slug='slug',
            status=1
        )
        client = Client()
        response = client.get(
            '{}{}'.format(reverse('api:blog_main_page'), '?search=title')
        )

        response.data['results'][0]['url'] = response.data['results'][0]['url'][17:]
        response.data['results'][0]['author'] = response.data['results'][0]['author'][17:]

        posts = Post.objects.filter(title__icontains='title', status=1)
        serializer = PostListSerializer(posts, many=True, context={'request': None})

        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_with_active_and_draft_results(self):
        """ Make search request with query, that match both active and draft posts """
        User = get_user_model()

        test_user = User.objects.create_user(username='test_user')

        test_post = Post.objects.create(
            title="Title",
            content="Content",
            author=test_user,
            slug='slug',
            status=1
        )
        test_post = Post.objects.create(
            title="Title",
            content="draft",
            author=test_user,
            slug='draft-slug',
            status=0
        )
        client = Client()
        response = client.get(
            '{}{}'.format(reverse('api:blog_main_page'), '?search=title')
        )

        response.data['results'][0]['url'] = response.data['results'][0]['url'][17:]
        response.data['results'][0]['author'] = response.data['results'][0]['author'][17:]

        posts = Post.objects.filter(title__icontains='title', status=1)
        serializer = PostListSerializer(posts, many=True, context={'request': None})

        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_with_several_results(self):
        """ Make search request with query, that match several posts """
        User = get_user_model()

        test_user = User.objects.create_user(username='test_user')

        test_post = Post.objects.create(
            title="Title",
            content="Content",
            author=test_user,
            slug='slug',
            status=1
        )
        test_post = Post.objects.create(
            title="Title",
            content="draft",
            author=test_user,
            slug='draft-slug',
            status=1
        )
        client = Client()
        response = client.get(
            '{}{}'.format(reverse('api:blog_main_page'), '?search=title')
        )

        for i in range(len(response.data['results'])):
            response.data['results'][i]['url'] = response.data['results'][i]['url'][17:]
            response.data['results'][i]['author'] = response.data['results'][i]['author'][17:]

        posts = Post.objects.filter(title__icontains='title', status=1)
        serializer = PostListSerializer(posts, many=True, context={'request': None})

        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_with_results_over_pagination(self):
        """ Make search request with query, that match number of posts, greater than page size """
        User = get_user_model()

        test_user = User.objects.create_user(username='test_user')

        for i in range(15):
            Post.objects.create(
                title="Title{}".format(i),
                content="Content{}".format(i),
                author=test_user,
                slug='slug{}'.format(i),
                status=1
            )

        client = Client()
        response = client.get(
            '{}{}'.format(reverse('api:blog_main_page'), '?search=title')
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Truncate urls in result
        for i in range(len(response.data['results'])):
            response.data['results'][i]['url'] = response.data['results'][i]['url'][17:]
            response.data['results'][i]['author'] = response.data['results'][i]['author'][17:]

        result = [] # Collect data from response
        result.extend(response.data['results'])

        while response.data['links']['next']:
            # Make request to next page if next page exists
            response = client.get(response.data['links']['next'])
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # Truncate urls in result
            for i in range(len(response.data['results'])):
                response.data['results'][i]['url'] = response.data['results'][i]['url'][17:]
                response.data['results'][i]['author'] = response.data['results'][i]['author'][17:]

            # Collect data from response
            result.extend(response.data['results'])

        posts = Post.objects.filter(title__icontains='title', status=1)
        serializer = PostListSerializer(posts, many=True, context={'request': None})

        self.assertEqual(result, serializer.data)


class PostLikesTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()

        cls.password = 'test_password'
        cls.user = User.objects.create_user(username='test_user')
        cls.user.set_password(cls.password)
        cls.user.save()

        client = Client()

        response = client.post(
            reverse('api:token_obtain_pair'),
            data=json.dumps({'username': cls.user.username, 'password': cls.password}),
            content_type='application/json'
        )

        cls.auth_token = response.data['access']

        # self.token = Token.objects.create(user=self.user)

        cls.post = Post.objects.create(
            title="Title",
            content="Content",
            author=cls.user,
            slug='slug',
            status=1
        )

        cls.client = Client()

    def test_no_likes(self):
        response = self.client.get(
            reverse('api:post-detail', kwargs={'slug': 'slug'}),
        )
        self.assertEqual(response.data['total_likes'], 0)

    def test_like_url_with_invalid_slug(self):
        response = self.client.get(
            reverse('api:post-like', kwargs={'slug': 'invalid_slug'}),
            HTTP_AUTHORIZATION='JWT {}'.format(self.auth_token),
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_like_url_with_unauthorised_user(self):
        client = Client()
        response = client.get(
            reverse('api:post-like', kwargs={'slug': 'slug'}),
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_like_url_with_authorised_user(self):
        response = self.client.get(
            reverse('api:post-like', kwargs={'slug': 'slug'}),
            HTTP_AUTHORIZATION='JWT {}'.format(self.auth_token),
        )

        post = Post.objects.get(slug='slug')
        self.assertEqual(post.likes.count(), 1)
        self.assertEqual(response.data, {'updated': True, 'liked': True})
        response = self.client.get(
            reverse('api:post-detail', kwargs={'slug': 'slug'}),
        )
        self.assertEqual(response.data['total_likes'], 1)

    def test_like_url_with_several_get_request(self):
        response = self.client.get(  # First request
            reverse('api:post-like', kwargs={'slug': 'slug'}),
            HTTP_AUTHORIZATION='JWT {}'.format(self.auth_token),
        )
        self.assertEqual(response.data, {'updated': True, 'liked': True})

        post = Post.objects.get(slug='slug')
        self.assertEqual(post.likes.count(), 1)

        response = self.client.get(
            reverse('api:post-detail', kwargs={'slug': 'slug'}),
        )
        self.assertEqual(response.data['total_likes'], 1)

        response = self.client.get(  # Second request
            reverse('api:post-like', kwargs={'slug': 'slug'}),
            HTTP_AUTHORIZATION='JWT {}'.format(self.auth_token),
        )
        self.assertEqual(response.data, {'updated': True, 'liked': False})

        post = Post.objects.get(slug='slug')
        self.assertEqual(post.likes.count(), 0)

        response = self.client.get(
            reverse('api:post-detail', kwargs={'slug': 'slug'}),
        )
        self.assertEqual(response.data['total_likes'], 0)
