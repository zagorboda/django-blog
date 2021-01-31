from django.test import TestCase, Client
from django.contrib.auth.models import User, AnonymousUser
from django.urls import reverse
from rest_framework import status
# from rest_framework.test import APIRequestFactory
from django.test.client import RequestFactory
from rest_framework.authtoken.models import Token
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
        self.user1 = User.objects.create_user(username='test_user')
        self.password1 = 'test_password'
        self.user1.set_password(self.password1)
        self.user1.save()

        self.test_user = User.objects.create(
            username='some_user'
        )
        self.test_password = 'test_password'
        self.test_user.set_password(self.test_password)
        self.test_user.save()

        self.token1 = Token.objects.create(user=self.user1)
        # self.test_token = Token.objects.create(user=self.test_user)

        self.post1 = Post.objects.create(
            title="Title",
            content="Content",
            author=self.user1,
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
        """ Get detail for existing active post by unauthorized user (different edit_url) """
        client = Client()
        response = client.get(
            reverse('post-detail', kwargs={'slug': 'slug'}),
            # HTTP_AUTHORIZATION='Token {}'.format(self.token1)
        )

        factory = RequestFactory()
        # factory.login(username=self.user1, password=self.password1)
        # factory.credentials(HTTP_AUTHORIZATION='Token {}'.format(self.token1))

        request = factory.get(
            reverse('post-detail', kwargs={'slug': 'slug'})
        )
        test_request = Request(request)

        # response.data['url'] = response.data['url'][17:]
        # response.data['edit_url'] = response.data['edit_url'][17:]
        # response.data['author'] = response.data['author'][17:]
        # response.data['like_url'] = response.data['like_url'][17:]

        post = Post.objects.get(slug='slug')
        serializer = PostDetailSerializer(post, context={'request': test_request})  # response.wsgi_request

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

        client.login(username=self.test_user.username, password=self.test_password)
        token = Token.objects.create(user=self.test_user)

        response = client.post(
            reverse('post-detail', kwargs={'slug': 'slug'}),
            HTTP_AUTHORIZATION='Token {}'.format(token),
            data=json.dumps({'body': "test"}),
            content_type='application/json'
        )

        response.data['author'] = response.data['author'][17:]

        comment = Comment.objects.get(post=self.post1)
        serializer = CommentSerializer(comment, context={'request': None})  # request None?

        number_of_comments = Comment.objects.all().count()

        self.assertEqual(serializer.data, response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(number_of_comments, 1)

    def test_invalid_comment_post_detail(self):
        """ Make POST request by authorized user with invalid data (empty body)"""
        client = Client()

        client.login(username=self.test_user.username, password=self.test_password)
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

        # response.data['url'] = response.data['url'][17:]
        # response.data['edit_url'] = response.data['edit_url'][17:]
        # response.data['author'] = response.data['author'][17:]
        # response.data['comments'][0]['author'] = response.data['comments'][0]['author'][17:]
        # response.data['like_url'] = response.data['like_url'][17:]

        factory = RequestFactory()

        request = factory.get(
            reverse('post-detail', kwargs={'slug': 'single-comment-slug'})
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
                active=i % 2
            )

        client = Client()
        response = client.get(reverse('post-detail', kwargs={'slug': 'several-comments-slug'}))

        response.data['url'] = response.data['url'][17:]
        # response.data['edit_url'] = response.data['edit_url'][17:]
        response.data['author'] = response.data['author'][17:]
        response.data['like_url'] = response.data['like_url'][17:]

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


class CreateNewPost(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.password = 'test_password'
        self.user = User.objects.create_user(username='test_user')
        self.user.set_password(self.password)
        self.user.save()

        self.token = Token.objects.create(user=self.user)

    def test_post_request_by_unauthorized_user(self):
        """ Make POST request by unauthorized user """
        client = Client()

        response = client.post(
            reverse('new-post'),
            data=json.dumps({}),
            content_type='multipart/form-data'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_request_with_empty_data(self):
        """ Make POST request without data """
        client = Client()

        client.login(username=self.user.username, password=self.password)

        response = client.post(
            reverse('new-post'),
            HTTP_AUTHORIZATION='Token {}'.format(self.token),
            data=json.dumps({}),
            content_type='multipart/form-data'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_request_with_valid_data(self):
        """ Make POST request with valid data """
        client = Client()

        client.login(username=self.user.username, password=self.password)

        response = client.post(
            reverse('new-post'),
            HTTP_AUTHORIZATION='Token {}'.format(self.token),
            data=json.dumps({"title": "Test title", "content": "Test content"}),
            content_type='multipart/form-data'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_request_with_extra_fields(self):
        """ Make POST request with valid data and several extra fields """
        client = Client()

        client.login(username=self.user.username, password=self.password)
        header = {'content-type': 'multipart/form-data'}
        response = client.post(
            reverse('new-post'),
            HTTP_AUTHORIZATION='Token {}'.format(self.token),
            data=json.dumps({"title": "Test title", "content": "Test content",
                             "some_extra_field": "test value", "status": 1}),
            content_type='multipart/form-data'
        )
        post = Post.objects.all()[0]

        self.assertEqual(post.status, 0)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class UserLoginApiTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.password = 'test_password'
        self.user = User.objects.create_user(username='test_user')
        self.user.set_password(self.password)
        self.user.save()

        self.token = Token.objects.create(user=self.user)

    def test_not_allowed_request(self):
        """ Make GET request (ObtainAuthToken process only POST request) """
        client = Client()
        response = client.get(reverse('login'))

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_with_invalid_username(self):
        """ Make POST request with invalid username """
        client = Client()

        response = client.post(
            reverse('login'),
            data=json.dumps({"username": "not_existing_username", "password": "some_password"}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_invalid_password(self):
        """ Make POST request with invalid password """
        client = Client()

        response = client.post(
            reverse('login'),
            data=json.dumps({"username": self.user.username, "password": "invalid_password"}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_valid_credentials(self):
        """ Make POST request with valid credentials for existing user """
        client = Client()

        response = client.post(
            reverse('login'),
            data=json.dumps({"username": self.user.username, "password": self.password}),
            content_type='application/json'
        )

        self.assertEqual(Token.objects.all()[0].key, response.data['token'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserCreateApiTest(TestCase):
    def test_get_request(self):
        """ Make GET request """
        client = Client()
        response = client.get(reverse('signup'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_request_with_invalid_data(self):
        """ Make POST request with invalid username """
        client = Client()

        response = client.post(
            reverse('signup'),
            data=json.dumps({"username": "!@#$%^&*()_+-=", "password": "test_password"}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_request_with_valid_data(self):
        """ Make POST request with valid data """
        client = Client()

        response = client.post(
            reverse('signup'),
            data=json.dumps({"username": "valid_username", "password": "valid_password"}),
            content_type='application/json'
        )

        user = User.objects.get(username='valid_username')
        token = Token.objects.get(user=user)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], user.username)
        self.assertEqual(response.data['token'], token.key)

    def test_sign_up_existing_user(self):
        """ Make POST request with existing username """
        password = 'test_password'
        user = User.objects.create_user(username='test_user')
        user.set_password(password)
        user.save()

        client = Client()

        response = client.post(
            reverse('signup'),
            data=json.dumps({"username": "test_user", "password": "some_Valid_Safe_password_2345dsS-dsaD"}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sign_up_with_common_password(self):
        """ Make POST request with common password """
        client = Client()

        response = client.post(
            reverse('signup'),
            data=json.dumps({"username": "test_user", "password": "12345678"}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class EditPostTest(TestCase):
    def setUp(self):
        self.password = 'test_password'
        self.user = User.objects.create_user(username='test_user')
        self.user.set_password(self.password)
        self.user.save()

        self.token = Token.objects.create(user=self.user)

        self.test_post = Post.objects.create(
            title="Title",
            content="Content",
            author=self.user,
            slug='slug',
            status=1
        )

    def test_patch_request_to_existing_post_patch_all_fields(self):
        """ Make PATCH request to existing post, patch title and content"""
        client = Client()

        response = client.patch(
            reverse('edit-post', kwargs={'slug': 'slug'}),
            HTTP_AUTHORIZATION='Token {}'.format(self.token),
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
            reverse('edit-post', kwargs={'slug': 'slug'}),
            HTTP_AUTHORIZATION='Token {}'.format(self.token),
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
            reverse('edit-post', kwargs={'slug': 'slug'}),
            HTTP_AUTHORIZATION='Token {}'.format(self.token),
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
            reverse('edit-post', kwargs={'slug': 'slug'}),
            HTTP_AUTHORIZATION='Token {}'.format(self.token)
        )

        patched_post = Post.objects.all()[0]

        self.assertEqual(response.data['title'], patched_post.title)
        self.assertEqual(response.data['content'], patched_post.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_request_to_existing_post_by_unauthorized_user(self):
        """ Make PATCH request to existing post by unauthorized user"""
        client = Client()

        response = client.patch(
            reverse('edit-post', kwargs={'slug': 'slug'}),
            data=json.dumps({"content": "Test content", "title": self.test_post.title}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_request_to_existing_post_by_not_owner(self):
        """ Make GET request to existing post by not owner"""
        password = 'test_password'
        user = User.objects.create_user(username='new_user')
        user.set_password(password)
        user.save()

        token = Token.objects.create(user=user)

        client = Client()

        response = client.get(
            reverse('edit-post', kwargs={'slug': 'slug'}),
            HTTP_AUTHORIZATION='Token {}'.format(token)
        )

        self.assertEqual(response.data['detail'], "You don't have permission to edit this post")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SearchPostTest(TestCase):

    def test_search_without_posts(self):
        """ Make search request without any post created """
        client = Client()
        response = client.get(
            '{}{}'.format(reverse('blog_main_page'), '?search=some_test_search')
        )

        self.assertEqual(response.data['results'], [])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_without_result(self):
        """ Make search request with query, that doesn't match any existing post """
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
            '{}{}'.format(reverse('blog_main_page'), '?search=not_matching_pattern')
        )

        self.assertEqual(response.data['results'], [])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_with_single_result(self):
        """ Make search request with query, that match single existing post """
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
            '{}{}'.format(reverse('blog_main_page'), '?search=title')
        )

        response.data['results'][0]['url'] = response.data['results'][0]['url'][17:]
        response.data['results'][0]['author'] = response.data['results'][0]['author'][17:]

        posts = Post.objects.filter(title__icontains='title', status=1)
        serializer = PostListSerializer(posts, many=True, context={'request': None})

        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_with_active_and_draft_results(self):
        """ Make search request with query, that match both active and draft posts """
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
            '{}{}'.format(reverse('blog_main_page'), '?search=title')
        )

        response.data['results'][0]['url'] = response.data['results'][0]['url'][17:]
        response.data['results'][0]['author'] = response.data['results'][0]['author'][17:]

        posts = Post.objects.filter(title__icontains='title', status=1)
        serializer = PostListSerializer(posts, many=True, context={'request': None})

        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_with_several_results(self):
        """ Make search request with query, that match several posts """
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
            '{}{}'.format(reverse('blog_main_page'), '?search=title')
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
            '{}{}'.format(reverse('blog_main_page'), '?search=title')
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
    def setUp(self):
        self.password = 'test_password'
        self.user = User.objects.create_user(username='test_user')
        self.user.set_password(self.password)
        self.user.save()

        self.token = Token.objects.create(user=self.user)

        self.post = Post.objects.create(
            title="Title",
            content="Content",
            author=self.user,
            slug='slug',
            status=1
        )

        self.client = Client()

    def test_no_likes(self):
        response = self.client.get(
            reverse('post-detail', kwargs={'slug': 'slug'}),
        )
        self.assertEqual(response.data['total_likes'], 0)

    def test_like_url_with_invalid_slug(self):
        response = self.client.get(
            reverse('post-like', kwargs={'slug': 'invalid_slug'}),
            HTTP_AUTHORIZATION='Token {}'.format(self.token),
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_like_url_with_unauthorised_user(self):
        client = Client()
        response = client.get(
            reverse('post-like', kwargs={'slug': 'slug'}),
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_like_url_with_authorised_user(self):
        response = self.client.get(
            reverse('post-like', kwargs={'slug': 'slug'}),
            HTTP_AUTHORIZATION='Token {}'.format(self.token),
        )

        post = Post.objects.get(slug='slug')
        self.assertEqual(post.likes.count(), 1)
        self.assertEqual(response.data, {'updated': True, 'liked': True})
        response = self.client.get(
            reverse('post-detail', kwargs={'slug': 'slug'}),
        )
        self.assertEqual(response.data['total_likes'], 1)

    def test_like_url_with_several_get_request(self):
        response = self.client.get(  # First request
            reverse('post-like', kwargs={'slug': 'slug'}),
            HTTP_AUTHORIZATION='Token {}'.format(self.token),
        )
        self.assertEqual(response.data, {'updated': True, 'liked': True})

        post = Post.objects.get(slug='slug')
        self.assertEqual(post.likes.count(), 1)

        response = self.client.get(
            reverse('post-detail', kwargs={'slug': 'slug'}),
        )
        self.assertEqual(response.data['total_likes'], 1)

        response = self.client.get(  # Second request
            reverse('post-like', kwargs={'slug': 'slug'}),
            HTTP_AUTHORIZATION='Token {}'.format(self.token),
        )
        self.assertEqual(response.data, {'updated': True, 'liked': False})

        post = Post.objects.get(slug='slug')
        self.assertEqual(post.likes.count(), 0)

        response = self.client.get(
            reverse('post-detail', kwargs={'slug': 'slug'}),
        )
        self.assertEqual(response.data['total_likes'], 0)
