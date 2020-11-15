from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.test import Client

from .models import Post

from datetime import datetime


def create_new_user(username, password):
    user = User.objects.create(username=username)
    user.set_password(password)
    user.save()
    return user


def create_new_post(title, text, slug,  author, status=0):
    date = datetime.now()
    return Post.objects.create(title=title,
                               slug=slug,
                               content=text,
                               author=author,
                               status=status,
                               created_on=date)


class MainPageTests(TestCase):

    def test_main_page_status_code(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_by_name(self):
        response = self.client.get(reverse('blog_app:home'))
        self.assertEquals(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('blog_app:home'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog_app/index.html')

    def test_view_without_posts(self):
        response = self.client.get(reverse('blog_app:home'))
        self.assertEquals(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['post_list'],
            []
        )

    def test_published_posts(self):
        test_user = create_new_user('test_user',
                                    'test_password')
        test_post = create_new_post('New title',
                                    'Some text',
                                    'some-text',
                                    test_user,
                                    status=1)
        response = self.client.get(reverse('blog_app:home'))
        self.assertQuerysetEqual(
            response.context['post_list'],
            ['<Post: New title>']
        )

    def test_not_published_post(self):
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
        response = self.client.get(reverse('blog_app:post_detail', kwargs={'slug': 'no-existing-slug'}))
        self.assertEquals(response.status_code, 404)

    def test_view_uses_correct_template(self):
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
        test_user = create_new_user('test_user',
                                    'test_password')
        test_post = create_new_post('New title',
                                    'Some text',
                                    'some-text',
                                    test_user,
                                    status=1)
        response = self.client.get(reverse('blog_app:post_detail', kwargs={'slug': 'some-text'}))
        self.assertEquals(response.status_code, 200)

    def test_no_published_post(self):
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
        response = self.client.get(reverse('blog_app:new_post'))
        self.assertEquals(response.status_code, 302)

    def test_new_post_view_logged(self):
        self.user = create_new_user('test_user',
                                    'test_password')
        # self.client.force_login(self.user)
        foo = self.client.login(username='test_user', password='test_password')
        response = self.client.get(reverse('blog_app:new_post'))
        self.assertEquals(response.status_code, 200)

    # 200 or 302
    # def test_new_post_view_post_request(self):
    #     self.user = create_new_user('test_user',
    #                                 'test_password')
    #     self.client.force_login(self.user)
    #     data = {
    #         'title': 'Some new title',
    #         'content': 'Some new text'
    #     }
    #     response = self.client.post(reverse('blog_app:new_post'), json=data)
    #     print(response)
    #     print(User.objects.all())
    #     print(Post.objects.all())
    #     self.assertEquals(response.status_code, 200)


# TODO : show only published posts in user profile

