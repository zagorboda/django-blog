from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
# from django.contrib.auth import login
# from django.test import Client

from .models import Post

from datetime import datetime


def create_new_user(username, password):
    """ Create new user """
    User = get_user_model()

    user = User.objects.create(username=username)
    user.set_password(password)
    user.save()
    return user


def create_new_post(title, text, slug,  author, status=0):
    """ Create new post """
    date = datetime.now()
    post = Post.objects.create(title=title,
                               slug=slug,
                               content=text,
                               author=author,
                               status=status,
                               created_on=date)
    return post


class MainPageTests(TestCase):

    def test_main_page_status_code(self):
        """ GET request to main page """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_by_name(self):
        """ GET request to main page by view name """
        response = self.client.get(reverse('blog_app:home'))
        self.assertEquals(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """ Check if blog_app:home view use correct template """
        response = self.client.get(reverse('blog_app:home'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog_app/index.html')

    def test_view_without_posts(self):
        """ GET request to main page without any posts """
        response = self.client.get(reverse('blog_app:home'))
        self.assertEquals(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['post_list'],
            []
        )

    def test_published_posts(self):
        """ GET request to main page with single post """
        test_user = create_new_user('test_user',
                                    'test_password')
        test_post = create_new_post('New title',
                                    'Some text',
                                    'some-text',
                                    test_user,
                                    status=1)
        response = self.client.get(reverse('blog_app:home'))
        posts = Post.objects.filter(status=1).order_by('-created_on')
        self.assertQuerysetEqual(
            response.context['post_list'],
            map(repr, posts)
        )

    def test_not_published_post(self):
        """ GET request to main page without published posts """
        test_user = create_new_user('test_user',
                                    'test_password')
        test_post = create_new_post('New title',
                                    'Some text',
                                    'some-text',
                                    test_user,
                                    status=0)
        response = self.client.get(reverse('blog_app:home'))
        self.assertQuerysetEqual(
            response.context['post_list'],
            []
        )


class PostDetailPageTests(TestCase):

    def test_no_existing_post(self):
        """ GET request to invalid url """
        response = self.client.get(reverse('blog_app:post_detail', kwargs={'slug': 'no-existing-slug'}))
        self.assertEquals(response.status_code, 404)

    def test_view_uses_correct_template(self):
        """ Check if view use correct template """
        test_user = create_new_user('test_user',
                                    'test_password')
        test_post = create_new_post('New title',
                                    'Some text',
                                    'some-text',
                                    test_user,
                                    status=1)
        response = self.client.get(reverse('blog_app:post_detail', kwargs={'slug': 'some-text'}))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog_app/post_detail.html')

    def test_existing_post(self):
        """ GET request to existing post """
        test_user = create_new_user('test_user',
                                    'test_password')
        test_post = create_new_post('New title',
                                    'Some text',
                                    'some-text',
                                    test_user,
                                    status=1)
        response = self.client.get(reverse('blog_app:post_detail', kwargs={'slug': 'some-text'}))
        self.assertEquals(response.status_code, 200)

    def test_draft_post(self):
        """ GET request to draft post """
        test_user = create_new_user('test_user',
                                    'test_password')
        test_post = create_new_post('New title',
                                    'Some text',
                                    'some-text',
                                    test_user,
                                    status=0)

        response = self.client.get(reverse('blog_app:post_detail', kwargs={'slug': 'some-text'}))

        self.assertEquals(response.status_code, 404)


class NewPostPageTests(TestCase):
    def test_new_post_view_not_logged(self):
        """ GET request to new post view by unauthorised user """
        response = self.client.get(reverse('blog_app:new_post'))
        self.assertEquals(response.status_code, 302)

    def test_new_post_view_logged(self):
        """ GET request to new post view by authorised user """
        self.user = create_new_user('test_user',
                                    'test_password')
        # self.client.force_login(self.user)
        foo = self.client.login(username='test_user', password='test_password')
        response = self.client.get(reverse('blog_app:new_post'))
        self.assertEquals(response.status_code, 200)

    # 200 or 302
    # def test_new_post_view_post_request(self):
    #     """ POST request to create new post """
    #     self.user = create_new_user('test_user',
    #                                 'test_password')
    #     self.client.force_login(self.user)
    #     data = {
    #         'title': 'Some new title',
    #         'content': 'Some new text'
    #     }
    #     response = self.client.post(reverse('blog_app:new_post'), json=data)
    #     self.assertEquals(response.status_code, 200)


class PostSearchTests(TestCase):
    def setUp(self):
        self.test_user = create_new_user('test_user',
                                         'test_password')

        test_post = create_new_post('New title',
                                    'Some text',
                                    'some-text',
                                    self.test_user,
                                    status=1)

    def test_published_post(self):
        """ Search single published post """
        response = self.client.get("{}{}".format(reverse('blog_app:search'), "?q=title"))
        post_list = response.context['post_list']

        posts = Post.objects.filter(status=1).order_by('-created_on')

        self.assertQuerysetEqual(
            post_list,
            map(repr, posts)
        )

    def test_not_existing_post(self):
        """ Search not existing post """
        response = self.client.get("{}{}".format(reverse('blog_app:search'), "?q=not_existing_title"))
        post_list = response.context['post_list']

        self.assertQuerysetEqual(
            post_list,
            []
        )

    def test_draft_post(self):
        """ Search draft post """
        create_new_post('draft',
                        'Some draft',
                        'draft',
                        self.test_user,
                        status=0)

        response = self.client.get("{}{}".format(reverse('blog_app:search'), "?q=draft"))
        post_list = response.context['post_list']

        self.assertQuerysetEqual(
            post_list,
            []
        )

    def test_several_published_posts(self):
        """ Search several published posts """
        test_post = create_new_post('New title1',
                                    'Some text1',
                                    'some-text1',
                                    self.test_user,
                                    status=1)

        test_post = create_new_post('New title2',
                                    'Some text2',
                                    'some-text2',
                                    self.test_user,
                                    status=1)

        response = self.client.get("{}{}".format(reverse('blog_app:search'), "?q=title"))
        post_list = response.context['post_list']

        posts = Post.objects.filter(status=1).order_by('-created_on')

        self.assertQuerysetEqual(
            post_list,
            map(repr, posts)
        )

    def test_empty_query(self):
        """ Search with empty query """
        response = self.client.get("{}{}".format(reverse('blog_app:search'), "?q="))
        try:
            response.context['post_list']
        except Exception as e:
            self.assertEquals(
                type(e),
                KeyError
            )

    def test_published_posts_with_pagination(self):
        """ Search with number of posts greater than page size """
        create_new_post('New title1',
                        'Some text1',
                        'some-text1',
                        self.test_user,
                        status=1)

        create_new_post('New title2',
                        'Some text2',
                        'some-text2',
                        self.test_user,
                        status=1)

        create_new_post('New title3',
                        'Some text3',
                        'some-text3',
                        self.test_user,
                        status=1)

        create_new_post('New title4',
                        'Some text4',
                        'some-text4',
                        self.test_user,
                        status=1)

        response = self.client.get("{}{}".format(reverse('blog_app:search'), "?q=title"))

        post_list = response.context['post_list']
        result = post_list[:]

        page_number = post_list.paginator.num_pages

        for i in range(1, page_number):
            response = self.client.get("{}{}{}{}".format(reverse('blog_app:search'), "?q=title", "&page=", str(i+1)))
            post_list = response.context['post_list']

            result.extend(post_list)

        posts = Post.objects.filter(status=1).order_by('-created_on')

        self.assertQuerysetEqual(
            result,
            map(repr, posts)
        )
